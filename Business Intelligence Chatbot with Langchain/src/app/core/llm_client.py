"""LLM client for generating responses"""

import streamlit as st
from typing import Optional, List, Dict
from openai import OpenAI
from anthropic import Anthropic
from config import OPENAI_API_KEY, ANTHROPIC_API_KEY


class LLMClient:
    """Handle interactions with language models"""
    
    def __init__(self, model_choice: str):
        """
        Initialize LLM client
        
        Args:
            model_choice: Name of the model to use
        """
        self.model_choice = model_choice
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate API client based on model choice"""
        if self.model_choice in ["GPT-4o", "GPT-4.1"]:
            return OpenAI(api_key=OPENAI_API_KEY)
        else:
            return Anthropic(api_key=ANTHROPIC_API_KEY)
    
    def generate_response(
        self, 
        question: str, 
        system_prompt: str, 
        history: Optional[List[Dict[str, str]]] = None
    ) -> Optional[str]:
        """
        Generate a response from the LLM
        
        Args:
            question: User question
            system_prompt: System prompt for the LLM
            history: Conversation history (optional)
            
        Returns:
            Generated response text or None if error
        """
        try:
            if self.model_choice == "GPT-4o":
                return self._generate_openai_response(question, system_prompt, "gpt-4o", history)
            elif self.model_choice == "GPT-4.1":
                return self._generate_openai_response(question, system_prompt, "gpt-4.1", history)
            else:
                return self._generate_anthropic_response(question, system_prompt, history)
        except Exception as e:
            st.error(f"Error with model API: {e}")
            return None
    
    def _generate_openai_response(
        self, 
        question: str, 
        system_prompt: str, 
        model_name: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response using OpenAI API"""
        messages = [{"role": "system", "content": system_prompt}]
        
        if history:
            messages.extend(history)
        
        messages.append({"role": "user", "content": question})
        
        response = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=4000
        )
        return response.choices[0].message.content
    
    def _generate_anthropic_response(
        self, 
        question: str, 
        system_prompt: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response using Anthropic API"""
        messages = []
        
        if history:
            messages.extend(history)
        
        messages.append({"role": "user", "content": question})
        
        # Determine the model name
        model_name = "claude-sonnet-4-20250514" if self.model_choice == "Claude Sonnet 4" else "claude-3-7-sonnet-20250219"
        
        response = self.client.messages.create(
            model=model_name,
            system=system_prompt,
            messages=messages,
            max_tokens=4000
        )
        return response.content[0].text
