import os
import vertexai
from langchain_google_genai import ChatGoogleGenerativeAI
from data_science.utils.config import config, load_env_variables
from langchain.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List, Optional
import json
import asyncio

# Initialize Vertex AI
# vertexai.init(
#     project=os.getenv("GOOGLE_CLOUD_PROJECT"),
#     location="us-central1"
# )

# Load environment variables and get the API key for Google
env_name = load_env_variables()
api_key = getattr(config[env_name], 'GOOGLE_API_KEY', os.getenv('GOOGLE_API_KEY'))

class StreamingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for streaming responses"""
    
    def __init__(self, websocket=None, queue=None):
        self.websocket = websocket
        self.queue = queue
        self.current_agent = None
        self.current_task = None
        self.buffer = []  # Add buffer to collect tokens
        self.stream_func = None  # Function to handle streaming
    
    def set_stream_function(self, stream_func):
        """Set the streaming function for async operations"""
        self.stream_func = stream_func
    
    def reset_buffer(self):
        """Reset the token buffer"""
        self.buffer = []
    
    def get_buffer_content(self):
        """Get accumulated buffer content"""
        return ''.join(self.buffer)
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """Called when LLM starts generating"""
        self.reset_buffer()  # Reset buffer at start
        
        if self.websocket:
            try:
                message = {
                    "type": "llm_start",
                    "agent": self.current_agent,
                    "task": self.current_task
                }
                self.websocket.send_text(json.dumps(message))
            except:
                pass
    
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Called when a new token is generated"""
        # Add token to buffer
        self.buffer.append(token)
        
        # Handle websocket streaming
        if self.websocket:
            try:
                message = {
                    "type": "token",
                    "content": token,
                    "agent": self.current_agent,
                    "task": self.current_task
                }
                self.websocket.send_text(json.dumps(message))
            except:
                pass
        
        # Handle queue streaming
        if self.queue:
            try:
                self.queue.put({
                    "type": "token",
                    "content": token,
                    "agent": self.current_agent,
                    "task": self.current_task
                })
            except:
                pass
        
        # Handle async function streaming
        if self.stream_func:
            try:
                # Create the streaming data
                token_data = {
                    'type': 'token', 
                    'data': {
                        'token': token, 
                        'agent': self.current_agent or "Unknown",
                        'task': self.current_task or "Unknown"
                    }
                }
                # Note: We can't directly await here since this might not be in async context
                # The streaming crew will handle this appropriately
                pass
            except Exception as e:
                print(f"Stream function error: {e}")
    
    def on_llm_end(self, response, **kwargs: Any) -> None:
        """Called when LLM finishes generating"""
        if self.websocket:
            try:
                message = {
                    "type": "llm_end",
                    "agent": self.current_agent,
                    "task": self.current_task,
                    "content": self.get_buffer_content()
                }
                self.websocket.send_text(json.dumps(message))
            except:
                pass
    
    def on_agent_action(self, action, **kwargs: Any) -> None:
        """Called when agent takes an action"""
        if self.websocket:
            try:
                message = {
                    "type": "agent_action",
                    "action": str(action.tool),
                    "agent": self.current_agent
                }
                self.websocket.send_text(json.dumps(message))
            except:
                pass
    
    def set_current_context(self, agent=None, task=None):
        """Set the current agent and task context"""
        self.current_agent = agent
        self.current_task = task

class LLMManager:
    """
    Singleton class to manage the initialization and usage of the LLM (Large Language Model).
    Now uses Google Gemini 1.5 Flash instead of OpenAI.
    Ensures only one instance of the LLM is created and reused throughout the application.
    """
    _instance = None  # Class variable to hold the singleton instance
    
    def __new__(cls):
        # Ensure only one instance is created 
        if cls._instance is None:
            cls._instance = super(LLMManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        
        if not hasattr(self, 'initialized'):
            self.api_key = api_key  # Store the API key
            # Initialize the ChatGoogleGenerativeAI LLM with desired parameters
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash-001",  # Use Gemini 1.5 Flash model
                temperature=0, 
                google_api_key=self.api_key,
                disabled_streaming=False,
            )
            self.streaming_callback = None
            self.initialized = True  # Mark as initialized
    
    def set_streaming_callback(self, callback_handler):
        """Set the streaming callback handler"""
        self.streaming_callback = callback_handler
    
    def get_streaming_llm(self, callback_handler=None):
        """Get LLM instance configured for streaming"""
        if callback_handler:
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash-001", 
                temperature=0, 
                google_api_key=self.api_key,
                streaming=True,
                callbacks=[callback_handler]
            )
        return self.llm
    
    def invoke(self, prompt, **kwargs):
        """
        Invoke the LLM with a prompt template and optional arguments.
        Args:
            prompt: A prompt template (e.g., from langchain)
            **kwargs: Arguments to fill the prompt template
        Returns:
            str: The content of the LLM's response
        """
        chain = prompt | self.llm  # Create a chain with the prompt and LLM
        response = chain.invoke(kwargs)  # Invoke the chain with arguments
        return response.content  # Return only the content part of the response
    
    def stream(self, prompt, callback_handler=None, **kwargs):
        """
        Stream the LLM response with a callback handler.
        Args:
            prompt: A prompt template (e.g., from langchain)
            callback_handler: Custom callback handler for streaming
            **kwargs: Arguments to fill the prompt template
        Returns:
            Generator yielding tokens
        """
        streaming_llm = self.get_streaming_llm(callback_handler)
        chain = prompt | streaming_llm
        
        for chunk in chain.stream(kwargs):
            if hasattr(chunk, 'content'):
                yield chunk.content
            else:
                yield str(chunk)
    
    def get_llm(self):
        """
        Return the LLM instance for use in other components.
        For ADK compatibility, return the model string.
        Returns:
            str: The model name for ADK Agent
        """
        return "gemini-1.5-flash-001"
    
    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of LLMManager.

        Returns:
            LLMManager: The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance