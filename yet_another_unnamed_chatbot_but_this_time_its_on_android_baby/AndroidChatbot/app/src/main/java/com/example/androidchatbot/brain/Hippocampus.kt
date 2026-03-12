package com.example.androidchatbot.brain

import android.util.Log
import java.time.Instant
import java.util.UUID
import kotlin.math.sqrt

class Hippocampus(
    private val memoryDao: MemoryDao,
    private val embeddingService: EmbeddingService
) {
    private val TAG = "Hippocampus"

    suspend fun retrieveMemories(query: String, queryVector: FloatArray, limit: Int = 10): List<MemoryEntity> {
        Log.d(TAG, "Retrieving LTM memories for query: '$query'")
        
        // Fetch all LTMs from Room
        val allMemories = memoryDao.getAllLTMMemories()
        
        if (allMemories.isEmpty()) {
            return emptyList()
        }

        // Brute force cosine similarity
        val scoredMemories = allMemories.mapNotNull { memory ->
            val memVector = stringToFloatArray(memory.vector)
            if (memVector.size != queryVector.size) {
                Log.e(TAG, "Vector dimension mismatch. Mem: ${memVector.size}, Query: ${queryVector.size}")
                return@mapNotNull null
            }

            val score = cosineSimilarity(queryVector, memVector)
            Pair(score, memory)
        }

        // Sort descending by score, take top N
        return scoredMemories
            .sortedByDescending { it.first }
            .take(limit)
            .map { it.second }
    }

    suspend fun commitSessionMemory(userQuery: String, reflection: String, response: String, turnId: String) {
        val fusedText = """
            USER: $userQuery
            REFLECTION: $reflection
            RESPONSE: $response
        """.trimIndent()

        // Generate embedding using MediaPipe Task
        val vector = embeddingService.embed(fusedText, cacheKey = turnId) ?: return

        val memoryEntity = MemoryEntity(
            id = turnId,
            text = fusedText,
            vector = floatArrayToString(vector),
            timestamp = Instant.now().toString(),
            type = "LTM" // Committing directly to LTM semantic memory
        )

        memoryDao.insertMemory(memoryEntity)
        Log.d(TAG, "Saved new memory to Room: ${fusedText.take(40)}...")
    }

    // Helper functions for Brute Force math
    private fun cosineSimilarity(v1: FloatArray, v2: FloatArray): Float {
        var dotProduct = 0f
        var normA = 0f
        var normB = 0f
        for (i in v1.indices) {
            dotProduct += v1[i] * v2[i]
            normA += v1[i] * v1[i]
            normB += v2[i] * v2[i]
        }
        return if (normA == 0f || normB == 0f) 0f else dotProduct / (sqrt(normA) * sqrt(normB))
    }

    private fun floatArrayToString(array: FloatArray): String {
        return array.joinToString(separator = ",")
    }

    private fun stringToFloatArray(str: String): FloatArray {
        if (str.isBlank()) return FloatArray(0)
        return str.split(",").map { it.toFloat() }.toFloatArray()
    }
}
