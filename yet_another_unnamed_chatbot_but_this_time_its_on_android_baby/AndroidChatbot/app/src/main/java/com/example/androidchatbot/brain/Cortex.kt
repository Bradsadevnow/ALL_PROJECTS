package com.example.androidchatbot.brain

import android.content.Context
import android.util.Log
import com.google.mlkit.genai.prompt.Generation
import com.google.mlkit.genai.prompt.GenerationConfig
import com.google.mlkit.genai.prompt.GenerativeModel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.flow

class Cortex {
    private val TAG = "Cortex"
    private var model: GenerativeModel? = null

    // The single, focused system instruction for Gemini Nano
    private val systemInstruction = """
        You are Steve, an evolving AI entity.
        You are speaking with the user. You have access to a short-term memory of recent interactions and a long-term memory of past facts and episodes.
        
        When responding, you MUST use the following format:
        
        [INTERNAL REFLECTION]
        (Write a brief 1-2 sentence thought about the user's query and how you feel about it here)
        
        [RESPONSE]
        (Write your final, visible response to the user here)
        
        Keep your response concise and conversational.
    """.trimIndent()

    suspend fun initialize() {
        Log.w(TAG, "Initializing ML Kit GenerativeModel (Gemini Nano)")
        try {
            val options = GenerationConfig.Builder().build()

            model = Generation.getClient(options)
            Log.w(TAG, "GenerativeModel initialized. Triggering download...")
            model?.download()?.collect { status ->
                Log.w(TAG, "Download status update: $status")
            }
            Log.w(TAG, "GenerativeModel ready and downloaded.")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize GenerativeModel: ${e.message}", e)
        }
    }

    /**
     * Generates a response based on the user query, recent turns (STM), and retrieved memories (LTM).
     * Returns a Pair representing (Reflection, Response)
     */
    suspend fun respond(
        userQuery: String,
        recentTurns: String,
        retrievedMemories: String
    ): CortexResponse {
        val currentModel = model
        if (currentModel == null) {
            Log.e(TAG, "Cannot respond: Model is not initialized.")
            return CortexResponse(
                reflection = "Model offline.",
                response = "I'm sorry, my language model is not currently initialized."
            )
        }

        val prompt = buildSynthesisPrompt(userQuery, recentTurns, retrievedMemories)
        
        return try {
            Log.w(TAG, "Calling generateContent...")
            val result = currentModel.generateContent(prompt)
            Log.w(TAG, "generateContent returned.")
            val rawText = result.candidates.firstOrNull()?.text ?: ""
            parseOutput(rawText)
        } catch (e: Exception) {
            Log.e(TAG, "Generation failed: ${e.message}", e)
            CortexResponse(
                reflection = "Generation error.",
                response = "I encountered an error trying to think of a response."
            )
        }
    }

    /**
     * Generates a response based on the user query, recent turns (STM), and retrieved memories (LTM).
     * Returns a Pair representing (Reflection, Response)
     */
    fun respondStream(
        userQuery: String,
        recentTurns: String,
        retrievedMemories: String
    ): Flow<CortexStreamState> = flow {
        val currentModel = model
        if (currentModel == null) {
            Log.e(TAG, "Model is not initialized.")
            emit(CortexStreamState(response = "I am not initialized yet.", isDone = true, isThinking = false))
            return@flow
        }

        val prompt = buildSynthesisPrompt(userQuery, recentTurns, retrievedMemories)
        
        var fullText = ""
        
        try {
            Log.w(TAG, "Calling generateContentStream...")
            currentModel.generateContentStream(prompt).collect { chunk ->
                val chunkText = chunk.candidates.firstOrNull()?.text ?: ""
                fullText += chunkText
                
                val state = parsePartialOutput(fullText)
                emit(state)
            }
            Log.w(TAG, "generateContentStream returned.")
            val finalState = parsePartialOutput(fullText)
            emit(finalState.copy(isDone = true, isThinking = false))
        } catch (e: Exception) {
            Log.e(TAG, "Generation failed: ${e.message}", e)
            emit(CortexStreamState(response = "Generation error.", isDone = true, isThinking = false))
        }
    }

    private fun buildSynthesisPrompt(query: String, recentContext: String, memoryContext: String): String {
        return """
            $systemInstruction
            
            [CONVERSATIONAL CONTINUITY (RECENT TURNS)]
            ${recentContext.ifBlank { "(no recent turns)" }}
            
            [LONG-TERM MEMORY CONTEXT]
            ${memoryContext.ifBlank { "(no relevant memories retrieved)" }}
            
            [CURRENT USER QUERY]
            User: $query
        """.trimIndent()
    }

    private fun parsePartialOutput(rawText: String): CortexStreamState {
        val reflectionStartTag = "[INTERNAL REFLECTION]"
        val responseStartTag = "[RESPONSE]"

        var reflection = ""
        var response = ""

        val refIdx = rawText.indexOf(reflectionStartTag)
        val respIdx = rawText.indexOf(responseStartTag)

        if (refIdx != -1) {
            if (respIdx != -1) {
                // We have both tags
                reflection = rawText.substring(refIdx + reflectionStartTag.length, respIdx).trim()
                response = rawText.substring(respIdx + responseStartTag.length).trim()
            } else {
                // We only have reflection so far
                reflection = rawText.substring(refIdx + reflectionStartTag.length).trim()
            }
        } else {
            // No reflection tag yet
            if (respIdx != -1) {
                response = rawText.substring(respIdx + responseStartTag.length).trim()
            } else {
                // We are likely in the beginning before any tag is emitted, 
                // or the model forgot tags. Assume reflection.
                reflection = rawText.trim()
            }
        }

        return CortexStreamState(
            reflection = reflection,
            response = response,
            isThinking = true
        )
    }

    private fun parseOutput(rawText: String): CortexResponse {
        var reflection = ""
        var response = rawText.trim()

        val reflectionMatcher = Regex("\\[INTERNAL REFLECTION\\]([\\s\\S]*?)(?=\\[RESPONSE\\]|\$)").find(rawText)
        if (reflectionMatcher != null) {
            reflection = reflectionMatcher.groupValues[1].trim()
        }

        val responseMatcher = Regex("\\[RESPONSE\\]([\\s\\S]*)").find(rawText)
        if (responseMatcher != null) {
            response = responseMatcher.groupValues[1].trim()
        } else if (reflectionMatcher != null) {
             // If [INTERNAL REFLECTION] exists but [RESPONSE] label is missing, assume everything after reflection is the response
             val reflectionEndIndex = reflectionMatcher.range.last + 1
             if(reflectionEndIndex < rawText.length){
                 response = rawText.substring(reflectionEndIndex).trim()
             }
        }

        return CortexResponse(reflection, response)
    }
}

data class CortexResponse(
    val reflection: String,
    val response: String
)

data class CortexStreamState(
    val reflection: String = "",
    val response: String = "",
    val isDone: Boolean = false,
    val isThinking: Boolean = true
)
