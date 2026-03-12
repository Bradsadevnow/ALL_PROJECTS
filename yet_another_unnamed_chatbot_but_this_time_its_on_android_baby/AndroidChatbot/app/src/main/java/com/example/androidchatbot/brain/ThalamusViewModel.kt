package com.example.androidchatbot.brain

import android.content.Context
import android.util.Log
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.util.UUID

class ThalamusViewModel(context: Context) : ViewModel() {
    private val TAG = "Thalamus"
    private val cortex = Cortex()
    
    // Explicit applicationContext to prevent memory leaks in ViewModel
    private val appContext = context.applicationContext
    private val embeddingService = EmbeddingService(appContext)
    
    // Lazy DB initialization tied to ViewModel
    private val db = AppDatabase.getDatabase(appContext)
    private val hippocampus = Hippocampus(db.memoryDao(), embeddingService)

    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState: StateFlow<ChatUiState> = _uiState.asStateFlow()

    private val _memories = MutableStateFlow<List<MemoryEntity>>(emptyList())
    val memories: StateFlow<List<MemoryEntity>> = _memories.asStateFlow()

    init {
        viewModelScope.launch {
            Log.w(TAG, "Booting up Android Brain Systems...")
            _uiState.update { it.copy(isBooting = true) }
            
            // Initialize on-device ML systems
            embeddingService.initialize()
            cortex.initialize()
            
            _uiState.update { it.copy(isBooting = false, systemMessage = "System Online.") }
            Log.w(TAG, "All systems initialized.")
            loadMemories()
        }
    }

    fun loadMemories() {
        viewModelScope.launch {
            _memories.value = db.memoryDao().getAllLTMMemories()
        }
    }

    fun handleUserInteraction(userQuery: String) {
        if (userQuery.isBlank() || _uiState.value.isThinking) return
        
        val turnId = UUID.randomUUID().toString()
        val userTurn = ChatTurn(id = "user_$turnId", text = userQuery, isUser = true)

        _uiState.update { state ->
            state.copy(
                turns = state.turns + userTurn,
                isThinking = true
            )
        }

        viewModelScope.launch {
            // 1. Clear embedding cache
            embeddingService.clearCache()
            
            // 2. Embed user query
            val queryEmbedding = embeddingService.embed(userQuery, "query_$turnId")
            
            // 3. Retrieve similar semantic memories via cosine similarity
            var memoryContext = ""
            if (queryEmbedding != null) {
                val memories = hippocampus.retrieveMemories(userQuery, queryEmbedding, limit = 5)
                memoryContext = memories.joinToString("\n") { "- ${it.text.take(300)}" }
                Log.w(TAG, "Retrieved ${memories.size} relevant baseline memories.")
            } else {
                Log.w(TAG, "Failed to embed user query, skipping memory retrieval.")
            }

            // 4. Get Short-Term Context (Recent UI turns)
            val stmContext = _uiState.value.turns
                .takeLast(6)
                .joinToString("\n") { "${if (it.isUser) "User" else "Steve"}: ${it.text}" }

            // 5. Query Cortex Stream
            val botTurnId = "bot_$turnId"
            var activeBotTurn = ChatTurn(
                id = botTurnId,
                text = "",
                isUser = false,
                reflection = ""
            )

            _uiState.update { state ->
                state.copy(
                    turns = state.turns + activeBotTurn,
                    // Keep the spinner active until stream is complete
                    isThinking = true 
                )
            }

            cortex.respondStream(
                userQuery = userQuery,
                recentTurns = stmContext,
                retrievedMemories = memoryContext
            ).collect { streamState ->
                activeBotTurn = activeBotTurn.copy(
                    text = streamState.response,
                    reflection = streamState.reflection
                )
                
                _uiState.update { state ->
                    val updatedTurns = state.turns.map { if (it.id == botTurnId) activeBotTurn else it }
                    state.copy(
                        turns = updatedTurns,
                        isThinking = streamState.isThinking
                    )
                }

                if (streamState.isDone) {
                    Log.w(TAG, "Final Reflection: ${streamState.reflection} | Response: ${streamState.response}")
                    
                    // 6. Asynchronous commit to memory
                    hippocampus.commitSessionMemory(
                        userQuery = userQuery,
                        reflection = streamState.reflection,
                        response = streamState.response,
                        turnId = turnId
                    )
                    
                    // 7. Refresh memories list
                    loadMemories()
                }
            }
        }
    }
}

data class ChatUiState(
    val isBooting: Boolean = true,
    val isThinking: Boolean = false,
    val systemMessage: String = "Initializing Neural Engram...",
    val turns: List<ChatTurn> = emptyList()
)

data class ChatTurn(
    val id: String,
    val text: String,
    val isUser: Boolean,
    val reflection: String? = null
)
