package com.example.androidchatbot.brain

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query

@Dao
interface MemoryDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertMemory(memory: MemoryEntity)

    @Query("SELECT * FROM memories WHERE type = 'LTM'")
    suspend fun getAllLTMMemories(): List<MemoryEntity>

    @Query("SELECT * FROM memories WHERE type = 'STM' ORDER BY timestamp DESC LIMIT :limit")
    suspend fun getRecentSTMMemories(limit: Int): List<MemoryEntity>
    
    @Query("DELETE FROM memories WHERE type = 'STM' AND id NOT IN (SELECT id FROM memories WHERE type = 'STM' ORDER BY timestamp DESC LIMIT :keepLimit)")
    suspend fun pruneOldSTMMemories(keepLimit: Int)
}
