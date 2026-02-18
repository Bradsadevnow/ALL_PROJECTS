import requests
import json
import time
from typing import List, Dict, Any, Optional, Generator
import logging

logger = logging.getLogger(__name__)

class LMStudioClient:
    """Client for communicating with LM Studio's local API."""
    
    def __init__(self, base_url: str = "http://192.168.1.128:1234", timeout: int = 120):
        """
        Initialize the LM Studio client.
        
        Args:
            base_url: The base URL for LM Studio API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'GPT-OSS-Chat-Client/1.0'
        })
    
    def test_connection(self) -> bool:
        """Test connection to LM Studio."""
        try:
            response = self.session.get(f"{self.base_url}/v1/models", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_models(self) -> List[str]:
        """Get list of available models."""
        try:
            response = self.session.get(f"{self.base_url}/v1/models", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                return [model['id'] for model in data.get('data', [])]
            else:
                logger.error(f"Failed to get models: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-oss-20b",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        stream: bool = True
    ) -> Generator[str, None, None]:
        """
        Generate chat completion using streaming.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream responses
        
        Yields:
            Response chunks as they arrive
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout,
                stream=stream
            )
            
            if response.status_code == 200:
                if stream:
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith('data: '):
                                data_str = line_str[6:]  # Remove 'data: ' prefix
                                if data_str.strip() == '[DONE]':
                                    break
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and len(data['choices']) > 0:
                                        content = data['choices'][0].get('delta', {}).get('content', '')
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    continue
                else:
                    data = response.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        content = data['choices'][0].get('message', {}).get('content', '')
                        yield content
            else:
                logger.error(f"Chat completion failed: {response.status_code}")
                yield f"Error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            yield f"Error: {str(e)}"
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        try:
            response = self.session.get(f"{self.base_url}/v1/models/{model_id}", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get model info: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {}