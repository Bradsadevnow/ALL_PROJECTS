package com.example.androidchatbot

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.androidchatbot.brain.ChatTurn
import com.example.androidchatbot.brain.ThalamusViewModel
import com.example.androidchatbot.brain.ThalamusViewModelFactory
import com.example.androidchatbot.ui.theme.AndroidChatbotTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AndroidChatbotTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val viewModel: ThalamusViewModel = viewModel(
                        factory = ThalamusViewModelFactory(applicationContext)
                    )
                    MainScreen(viewModel = viewModel)
                }
            }
        }
    }
}

enum class NavigationTab {
    CHAT,
    RESONANCE
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(viewModel: ThalamusViewModel) {
    var selectedTab by remember { mutableStateOf(NavigationTab.CHAT) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(if (selectedTab == NavigationTab.CHAT) "Steve (Gemini Nano)" else "Resonance (Memories)") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        },
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    icon = { Icon(Icons.Default.Send, contentDescription = "Chat") },
                    label = { Text("Chat") },
                    selected = selectedTab == NavigationTab.CHAT,
                    onClick = { selectedTab = NavigationTab.CHAT }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Default.List, contentDescription = "Resonance") },
                    label = { Text("Resonance") },
                    selected = selectedTab == NavigationTab.RESONANCE,
                    onClick = {
                        selectedTab = NavigationTab.RESONANCE
                        viewModel.loadMemories()
                    }
                )
            }
        }
    ) { paddingValues ->
        Box(modifier = Modifier.padding(paddingValues)) {
            when (selectedTab) {
                NavigationTab.CHAT -> ChatScreen(viewModel = viewModel)
                NavigationTab.RESONANCE -> ResonanceScreen(viewModel = viewModel)
            }
        }
    }
}

@Composable
fun ResonanceScreen(viewModel: ThalamusViewModel) {
    val memories by viewModel.memories.collectAsState()

    if (memories.isEmpty()) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text("No baseline memories available.", color = Color.Gray)
        }
    } else {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            items(memories.reversed()) { memory ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = memory.timestamp,
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f),
                            modifier = Modifier.padding(bottom = 8.dp)
                        )
                        Text(
                            text = memory.text,
                            style = MaterialTheme.typography.bodyMedium,
                            maxLines = 10,
                            overflow = TextOverflow.Ellipsis
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun ChatScreen(viewModel: ThalamusViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    var inputText by remember { mutableStateOf("") }

    Scaffold { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            if (uiState.isBooting) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                    Text(
                        uiState.systemMessage,
                        modifier = Modifier.padding(top = 64.dp),
                        style = MaterialTheme.typography.bodyLarge
                    )
                }
            } else {
                LazyColumn(
                    modifier = Modifier
                        .weight(1f)
                        .padding(horizontal = 16.dp),
                    contentPadding = PaddingValues(vertical = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    items(uiState.turns) { turn ->
                        ChatBubble(turn)
                    }
                    if (uiState.isThinking) {
                        item {
                            Text("Steve is thinking...", color = Color.Gray)
                        }
                    }
                }

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    OutlinedTextField(
                        value = inputText,
                        onValueChange = { inputText = it },
                        modifier = Modifier.weight(1f),
                        placeholder = { Text("Type a message...") },
                        enabled = !uiState.isThinking
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    IconButton(
                        onClick = {
                            if (inputText.isNotBlank()) {
                                viewModel.handleUserInteraction(inputText)
                                inputText = ""
                            }
                        },
                        enabled = !uiState.isThinking && inputText.isNotBlank()
                    ) {
                        Icon(Icons.Default.Send, contentDescription = "Send")
                    }
                }
            }
        }
    }
}

@Composable
fun ChatBubble(turn: ChatTurn) {
    val isUser = turn.isUser
    val backgroundColor = if (isUser) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.secondaryContainer
    val textColor = if (isUser) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSecondaryContainer
    val alignment = if (isUser) Alignment.CenterEnd else Alignment.CenterStart

    Box(
        modifier = Modifier.fillMaxWidth(),
        contentAlignment = alignment
    ) {
        Column(
            modifier = Modifier
                .background(
                    color = backgroundColor,
                    shape = RoundedCornerShape(16.dp)
                )
                .padding(12.dp)
                .fillMaxWidth(0.8f) // max 80% width
        ) {
            if (!isUser && turn.reflection != null && turn.reflection.isNotBlank()) {
                Text(
                    text = "Internal: ${turn.reflection}",
                    color = textColor.copy(alpha = 0.6f),
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(bottom = 4.dp)
                )
            }
            Text(
                text = turn.text,
                color = textColor,
                style = MaterialTheme.typography.bodyLarge
            )
        }
    }
}
