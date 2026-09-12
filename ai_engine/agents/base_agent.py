"""
CropMind - Base Agent
Abstract base class for all AI agents in the CropMind system

Author: CropMind Team
Date: 2026
"""
import os
import json
import pathlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
import warnings
from dotenv import load_dotenv

warnings.filterwarnings('ignore')

env_path = pathlib.Path(__file__).parents[2] / ".env"
load_dotenv(env_path, override=True)

class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in CropMind.
    Provides common functionality for LLM integration and logging.
    """
    
    def __init__(
        self,
        agent_name: str,
        description: str,
        groq_api_key: Optional[str] = None,
        model: str = "openai/gpt-oss-120b",
        temperature: float = 0.7
    ):
        self.agent_name = agent_name
        self.description = description
        self.model = model
        self.temperature = temperature
        self.llm = None
        self.is_initialized = False
        
        # Get API key from parameter or environment
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        
        # Debug: Print first 10 chars of API key
        if self.groq_api_key:
            print(f"[{self.agent_name}] 🔑 API Key: {self.groq_api_key[:10]}... (length: {len(self.groq_api_key)})")
        else:
            print(f"[{self.agent_name}] ❌ No API Key found!")
        
        if not self.groq_api_key:
            self.log("⚠️ GROQ_API_KEY not found in environment")
            self.log("   Please set GROQ_API_KEY in .env file")
        else:
            self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """Initialize the LangChain ChatGroq instance."""
        try:
            from langchain_groq import ChatGroq
            
            print(f"[{self.agent_name}] 🔄 Initializing ChatGroq with model: {self.model}")
            
            self.llm = ChatGroq(
                groq_api_key=self.groq_api_key,
                model_name=self.model,
                temperature=self.temperature,
                timeout=30,
                max_retries=2
            )
            self.is_initialized = True
            print(f"[{self.agent_name}] ✅ LLM initialized successfully with Groq")
            
            # Test the connection with a simple call
            try:
                test_response = self.llm.invoke("Say hello in one word")
                print(f"[{self.agent_name}] ✅ LLM test successful: {test_response.content[:50]}...")
            except Exception as test_error:
                print(f"[{self.agent_name}] ❌ LLM test failed: {test_error}")
                
        except ImportError as e:
            print(f"[{self.agent_name}] ❌ LangChain import error: {e}")
            print("   Please install: pip install langchain-groq langchain-core")
            self.is_initialized = False
        except Exception as e:
            print(f"[{self.agent_name}] ❌ LLM initialization error: {e}")
            self.is_initialized = False
    
    def think(self, prompt: str) -> str:
        """
        Send a prompt to the LLM and return the response.
        """
        if not self.is_initialized or self.llm is None:
            print(f"[{self.agent_name}] ⚠️ LLM not initialized. Falling back to rule-based response.")
            return self._fallback_response(prompt)
        
        try:
            print(f"[{self.agent_name}] 💭 Sending prompt to Groq LLM...")
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"[{self.agent_name}] ❌ LLM error: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        return f"[{self.agent_name}] LLM temporarily unavailable. Please try again later."
    
    def log(self, message: str) -> None:
        print(f"[{self.agent_name}] {message}")
    
    def format_response(
        self,
        data: Dict[str, Any],
        status: str = "success"
    ) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "status": status,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    def format_error(self, error: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "status": "error",
            "error": error,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
    
    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.agent_name,
            "description": self.description,
            "model": self.model,
            "initialized": self.is_initialized,
            "llm_available": self.llm is not None,
            "groq_api_key_set": bool(self.groq_api_key)
        }
