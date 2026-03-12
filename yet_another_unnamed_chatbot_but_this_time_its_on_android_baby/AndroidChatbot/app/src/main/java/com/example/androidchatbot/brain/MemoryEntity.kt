package com.example.androidchatbot.brain

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "memories")
data class MemoryEntity(
    @PrimaryKey
    val id: String,
    val text: String,
    val vector: String, // Stored as a comma-separated string for brute force parsing
    val timestamp: String,
    val type: String // "STM" or "LTM"
)
