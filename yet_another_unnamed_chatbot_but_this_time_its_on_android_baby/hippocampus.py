import os
import time
import json
import uuid
import hashlib
import datetime
import logging
import chromadb

logger = logging.getLogger(__name__)

class Hippocampus:
    def __init__(self, embedding_service):
        self.embedding_service = embedding_service
        self.last_commit_time = 0

        # Setup ChromaDB persistent client
        runtime_dir = os.environ.get("STEVE_RUNTIME_DIR", "runtime")
        chroma_path = os.path.join(runtime_dir, "chroma_db")
        os.makedirs(chroma_path, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection_name = os.environ.get("CHROMA_COLLECTION", "hal_memory")
        
        # We handle embeddings via EmbeddingService, so we don't need Chroma's default embedding function
        self.col_episodic = self.client.get_or_create_collection(
            name="hal_episodic",
            metadata={"hnsw:space": "cosine"}
        )
        self.col_semantic = self.client.get_or_create_collection(
            name="hal_semantic",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Connected to ChromaDB at {chroma_path}, collections: hal_episodic, hal_semantic")

    def _stable_id_for_fused_text(self, fused_text: str, prefix: str = "") -> str:
        digest = hashlib.sha1(fused_text.encode("utf-8")).digest()
        base_id = str(uuid.UUID(bytes=digest[:16]))
        return f"{prefix}_{base_id}" if prefix else base_id

    def _dedupe_memories(self, memories):
        unique = {}
        for m in memories:
            key = m["text"].strip()
            if key not in unique or m["weight"] > unique[key]["weight"]:
                unique[key] = m
        return list(unique.values())

    def recall_with_context(self, query: str, keywords: list = None, n_results: int = 25, search_mode: str = "hybrid"):
        now = datetime.datetime.now()
        
        search_text = " ".join(keywords) if keywords else query
        
        content_vec = self.embedding_service.embed(search_text, cache_key=f"content:{search_text}")
        
        emotional_query = f"[Emotional context] How does this make me feel? {search_text}"
        emotional_vec = self.embedding_service.embed(emotional_query, cache_key=f"emotional:{search_text}")

        merged_rows = []

        # 1. Episodic Content Search
        if search_mode in ["content", "hybrid"]:
            try:
                results = self.col_episodic.query(
                    query_embeddings=[content_vec],
                    n_results=n_results,
                    where={"vector_type": "content"},
                    include=["metadatas", "distances"]
                )
                self._harvest_results(results, "episodic", "content", merged_rows, now)
            except Exception as e:
                logger.warning(f"Episodic Content search failed: {e}")

        # 2. Episodic Emotional Search
        if search_mode in ["emotional", "hybrid"] and emotional_vec:
            try:
                results = self.col_episodic.query(
                    query_embeddings=[emotional_vec],
                    n_results=n_results,
                    where={"vector_type": "emotional"},
                    include=["metadatas", "distances"]
                )
                self._harvest_results(results, "episodic", "emotional", merged_rows, now)
            except Exception as e:
                logger.warning(f"Episodic Emotional search failed: {e}")

        # 3. Semantic Fact Search
        if search_mode in ["semantic", "hybrid"]:
            try:
                results = self.col_semantic.query(
                    query_embeddings=[content_vec],
                    n_results=n_results,
                    include=["metadatas", "distances"]
                )
                self._harvest_results(results, "semantic", "fact", merged_rows, now)
            except Exception as e:
                logger.warning(f"Semantic search failed: {e}")

        merged_rows = self._dedupe_memories(merged_rows)
        merged_rows.sort(key=lambda m: m["weight"], reverse=True)
        merged_rows = merged_rows[:n_results]

        logger.info(f"Retrieved {len(merged_rows)} memories via {search_mode} search.")
        return merged_rows

    def _harvest_results(self, results, memory_kind, source_label, merged_rows, now):
        if not results["ids"] or not results["ids"][0]:
            return
            
        update_ids = []
        update_metadatas = []
        
        for i, doc_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i] or {}
            # Chroma returns distance (0 is perfect match for cosine).
            distance = results["distances"][0][i]
            
            ts_str = meta.get("timestamp")
            try:
                ts = datetime.datetime.fromisoformat(ts_str)
                age_days = (now - ts).total_seconds() / 86400.0
                decay_rate = 7.0 if memory_kind == "episodic" else 30.0
                decay = max(0.1, 1 - (age_days / decay_rate))
            except Exception:
                age_days = 0.0
                decay = 1.0

            manual_weight = float(meta.get("manual_weight", 1.0))
            importance = float(meta.get("importance", 1.0))
            similarity = 1.5 - distance
            
            # Convert distance to similarity weight
            base_weight = importance * similarity * decay * manual_weight
            reinforced_decay = min(1.0, decay * 1.05)
            
            # Increment rehearsal count and persist
            meta["rehearsal_count"] = int(meta.get("rehearsal_count", 0)) + 1
            
            update_ids.append(doc_id)
            update_metadatas.append(meta)

            merged_rows.append({
                "id": doc_id,
                "memory_id": meta.get("memory_id", doc_id),
                "memory_kind": memory_kind,
                "text": meta.get("fused_text") or meta.get("fact") or "Text Unavailable",
                "weight": base_weight,
                "timestamp": ts_str,
                "distance": distance,
                "similarity": similarity,
                "decay": reinforced_decay,
                "age_days": age_days,
                "source": source_label,
            })
            
        if update_ids:
            collection = self.col_episodic if memory_kind == "episodic" else self.col_semantic
            try:
                collection.update(
                    ids=update_ids,
                    metadatas=update_metadatas
                )
            except Exception as e:
                logger.error(f"Failed to persist rehearsal count updates: {e}")

    def delayed_commit(self, user_query: str, reflection: str, response: str, state_json: dict, metadata: dict):
        try:
            if time.time() - getattr(self, "last_commit_time", 0) < 3:
                time.sleep(1.5)

            reflection_text = (reflection or "").strip()
            response_text = (response or "").strip()

            fused_text = (
                f"USER QUERY:\n{user_query.strip()}\n\n"
                f"REFLECTION:\n{reflection_text}\n\n"
                f"FINAL RESPONSE:\n{response_text}"
            )

            base_id = self._stable_id_for_fused_text(fused_text)
            content_id = self._stable_id_for_fused_text(fused_text, prefix="content")
            emotional_id = self._stable_id_for_fused_text(fused_text, prefix="emotional")

            # Check existence via content_id
            try:
                existing = self.col_episodic.get(ids=[content_id])
                if existing and existing["ids"]:
                    logger.info(f"Duplicate memory {content_id[:8]}... detected — skipping add.")
                    self.last_commit_time = time.time()
                    return
            except Exception:
                pass

            content_embedding = self.embedding_service.embed(fused_text, cache_key=f"content:{user_query}")
            
            emotional_text = (
                f"[Emotional Context] "
                f"User felt: {user_query.strip()} "
                f"I felt: {reflection_text} "
                f"I expressed: {response_text}"
            )
            emotional_embedding = self.embedding_service.embed(emotional_text, cache_key=f"emotional:{user_query}")
            
            if not content_embedding or not emotional_embedding:
                raise RuntimeError("EmbeddingService.embed() returned no data.")

            base_meta = {
                "memory_id": base_id,
                "memory_kind": "episodic",
                "turn_id": metadata.get("turn_id", "N/A"),
                "task_id": metadata.get("task_id", "N/A"),
                "timestamp": datetime.datetime.now().isoformat(),
                "reflection": reflection_text[:1000], # Chroma has metadata size limits
                "response_preview": response_text[:256],
                "summary": f"Fusion of query + reflection @ {metadata.get('turn_id', 'N/A')}",
                "manual_weight": 1.0,
                "importance": 1.0,
                "rehearsal_count": 0,
                "fused_text": fused_text
            }

            # Flatten states for metadata
            all_states = state_json.get("emotions", [])
            emotive_count = 0
            cognitive_count = 0
            for state in all_states:
                stype = state.get("type")
                if stype == "emotive" and emotive_count < 3:
                    base_meta[f"emo_{emotive_count+1}_name"] = state.get("name")
                    base_meta[f"emo_{emotive_count+1}_intensity"] = float(state.get("intensity") or 0.0)
                    emotive_count += 1
                elif stype == "cognitive" and cognitive_count < 3:
                    base_meta[f"cog_{cognitive_count+1}_name"] = state.get("name")
                    base_meta[f"cog_{cognitive_count+1}_intensity"] = float(state.get("intensity") or 0.0)
                    cognitive_count += 1

            for i, kw in enumerate((metadata or {}).get("keywords", [])[:10]):
                base_meta[f"keyword_{i+1}"] = kw

            # Insert Content Document
            content_meta = base_meta.copy()
            content_meta["vector_type"] = "content"
            
            # Insert Emotional Document
            emotional_meta = base_meta.copy()
            emotional_meta["vector_type"] = "emotional"

            self.col_episodic.upsert(
                ids=[content_id, emotional_id],
                embeddings=[content_embedding, emotional_embedding],
                metadatas=[content_meta, emotional_meta],
                documents=[fused_text, emotional_text] # Store raw text as document
            )

            self.last_commit_time = time.time()
            logger.info(f"Saved memory (content + emotional) :: {content_meta.get('summary')}")

        except Exception as e:
            logger.error(f"Error during commit: {e}", exc_info=True)

    def adjust_weight(self, mem_id: str, weight: float):
        try:
            new_weight = max(1.0, float(weight))
            existing = self.col_episodic.get(ids=[mem_id], include=["metadatas"])
            if not existing or not existing["metadatas"]:
                existing = self.col_semantic.get(ids=[mem_id], include=["metadatas"])
                collection = self.col_semantic
            else:
                collection = self.col_episodic
                
            if existing and existing["metadatas"]:
                meta = existing["metadatas"][0]
                meta["manual_weight"] = new_weight
                collection.update(
                    ids=[mem_id],
                    metadatas=[meta]
                )
                logger.info(f"Set {mem_id[:8]}... manual_weight={new_weight}")
        except Exception as e:
            logger.error(f"Error adjusting weight: {e}")

    def commit_semantic(self, fact: str, importance: float = 1.0):
        try:
            fact_text = fact.strip()
            fact_embedding = self.embedding_service.embed(fact_text, cache_key=f"semantic:{fact_text}")
            
            if not fact_embedding:
                logger.error("Failed to generate embedding for semantic fact.")
                return
            
            # Deduplication: query existing semantics
            results = self.col_semantic.query(
                query_embeddings=[fact_embedding],
                n_results=1,
                include=["distances", "metadatas"]
            )
            
            if results and results["ids"] and results["ids"][0]:
                top_id = results["ids"][0][0]
                top_distance = results["distances"][0][0]
                
                # If similarity > 1.3 (distance < 0.2), it's basically the same fact
                if top_distance < 0.2:
                    logger.info(f"Semantic match {top_distance:.2f} for '{fact_text[:30]}...' -> boosting existing.")
                    meta = results["metadatas"][0][0]
                    # Boost existing importance, capped at 1.0
                    current_importance = float(meta.get("importance", 1.0))
                    meta["importance"] = min(1.0, current_importance + (importance * 0.5))
                    meta["rehearsal_count"] = int(meta.get("rehearsal_count", 0)) + 1
                    
                    self.col_semantic.update(
                        ids=[top_id],
                        metadatas=[meta]
                    )
                    return
            
            # No close match, insert new fact
            fact_id = self._stable_id_for_fused_text(fact_text, prefix="semantic")
            
            meta = {
                "memory_id": fact_id,
                "memory_kind": "semantic",
                "timestamp": datetime.datetime.now().isoformat(),
                "importance": float(importance),
                "manual_weight": 1.0,
                "rehearsal_count": 0,
                "fact": fact_text
            }
            
            self.col_semantic.upsert(
                ids=[fact_id],
                embeddings=[fact_embedding],
                metadatas=[meta],
                documents=[fact_text]
            )
            logger.info(f"Saved Semantic Fact [{importance}]: {fact_text[:40]}...")
            
        except Exception as e:
            logger.error(f"Failed to commit semantic memory: {e}")
