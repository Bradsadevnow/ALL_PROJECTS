package com.example.androidchatbot.brain

import android.content.Context
import android.util.Log
import com.google.mediapipe.tasks.core.BaseOptions
import com.google.mediapipe.tasks.text.textembedder.TextEmbedder
import com.google.mediapipe.tasks.text.textembedder.TextEmbedder.TextEmbedderOptions
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class EmbeddingService(private val context: Context) {
    private val TAG = "EmbeddingService"
    private var textEmbedder: TextEmbedder? = null
    private val cache = mutableMapOf<String, FloatArray>()

    fun initialize() {
        Log.d(TAG, "Initializing MediaPipe TextEmbedder")
        try {
            // We expect the model to be placed in the assets folder as "embedding_model.tflite"
            val baseOptions = BaseOptions.builder()
                .setModelAssetPath("embedding_model.tflite")
                .build()

            val options = TextEmbedderOptions.builder()
                .setBaseOptions(baseOptions)
                // L2 normalization is often preferred for cosine similarity
                .setL2Normalize(true) 
                .setQuantize(false)
                .build()

            textEmbedder = TextEmbedder.createFromOptions(context, options)
            Log.d(TAG, "MediaPipe TextEmbedder initialized successfully.")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize TextEmbedder: ${e.message}", e)
        }
    }

    suspend fun embed(text: String, cacheKey: String? = null): FloatArray? {
        if (cacheKey != null && cache.containsKey(cacheKey)) {
            return cache[cacheKey]
        }

        val embedder = textEmbedder
        if (embedder == null) {
            Log.e(TAG, "TextEmbedder is not initialized.")
            return null
        }

        return withContext(Dispatchers.Default) {
            try {
                // MediaPipe text embedder returns a list of embeddings (usually just 1 for a single string input)
                val result = embedder.embed(text)
                
                // Extract the float array from the first result
                val embeddingArray = result.embeddingResult().embeddings().firstOrNull()?.floatEmbedding()
                
                if (embeddingArray != null && cacheKey != null) {
                    cache[cacheKey] = embeddingArray
                }
                
                embeddingArray
            } catch (e: Exception) {
                Log.e(TAG, "Embedding generation failed: ${e.message}", e)
                null
            }
        }
    }

    fun clearCache() {
        cache.clear()
    }
}
