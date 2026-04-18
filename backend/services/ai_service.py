"""
AI Service Module
Integrates with OpenRouter API for AI-powered code explanations
"""
import os
import json
import httpx
from typing import Dict, Any, Optional
from prompts.templates import (
    EXPLANATION_PROMPT,
    IMPROVEMENT_PROMPT,
    VISUALIZATION_PROMPT,
    create_explanation_prompt,
    create_improvement_prompt,
    create_visualization_prompt
)


class AIService:
    """AI service using OpenRouter API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = "openrouter/auto"
        self._mock_mode = False
    
    def _call_api(self, messages: list, temperature: float = 0.7) -> Dict[str, Any]:
        """Make API call to OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "AI Python Visualizer"
        }
        
        payload = {
            "model": self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2000
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON from AI response"""
        try:
            return json.loads(text)
        except:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return {"result": text}
    
    def explain_code(self, code: str, execution_result: Optional[Dict] = None) -> str:
        """Generate beginner-friendly explanation of the code"""
        prompt = create_explanation_prompt(code, execution_result)
        
        messages = [
            {"role": "system", "content": "You are a patient coding tutor helping beginners understand Python. Always explain in simple, clear language."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_api(messages)
            return response['choices'][0]['message']['content']
        except Exception as e:
            return f"Explanation unavailable: {str(e)}"
    
    def improve_code(self, code: str, error: Optional[str] = None) -> str:
        """Generate improved version of the code"""
        prompt = create_improvement_prompt(code, error)
        
        messages = [
            {"role": "system", "content": "You are a Python expert. Provide clean, well-documented, and optimized code with explanations."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_api(messages)
            return response['choices'][0]['message']['content']
        except Exception as e:
            return f"Improved code unavailable: {str(e)}"
    
    def generate_visualization(self, code: str, execution_result: Dict) -> Dict[str, Any]:
        """Generate visualization data (flow, steps)"""
        prompt = create_visualization_prompt(code, execution_result)
        
        messages = [
            {"role": "system", "content": "You are a code visualization expert. Generate structured JSON for visualizing code execution flow."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_api(messages, temperature=0.3)
            return self._parse_json_response(response['choices'][0]['message']['content'])
        except Exception as e:
            return {
                "flow": ["Start", "Execute", "End"],
                "steps": [],
                "error": str(e)
            }
    
    def analyze_complete(self, code: str, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete analysis: explanation + improvement + visualization"""
        error = execution_result.get('error')
        
        explanation = self.explain_code(code, execution_result)
        fixed_code = self.improve_code(code, error)
        visualization = self.generate_visualization(code, execution_result)
        
        return {
            "explanation": explanation,
            "fixed_code": fixed_code,
            "visualization": visualization,
            "execution": execution_result.get('execution', []),
            "output": execution_result.get('output', []),
            "error": error
        }


def create_ai_service() -> AIService:
    """Factory function to create AI service instance"""
    return AIService()