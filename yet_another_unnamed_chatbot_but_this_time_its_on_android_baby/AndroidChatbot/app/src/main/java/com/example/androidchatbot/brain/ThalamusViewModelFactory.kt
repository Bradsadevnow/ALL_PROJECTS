package com.example.androidchatbot.brain

import android.content.Context
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider

class ThalamusViewModelFactory(private val context: Context) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(ThalamusViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return ThalamusViewModel(context) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
