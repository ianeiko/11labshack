import openai
from anthropic import Anthropic
import google.generativeai as genai
from config import settings

class LLMService:
    def __init__(self):
        # OpenAI
        if settings.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)

        # Anthropic
        if settings.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=settings.anthropic_api_key)

        # Gemini
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')

        # Grok (via OpenAI compatible endpoint)
        if settings.grok_api_key:
            self.grok_client = openai.OpenAI(
                api_key=settings.grok_api_key,
                base_url=settings.grok_base_url
            )

    async def generate_response(self, provider: str, model: str | None, system_prompt: str, user_prompt: str) -> str:
        try:
            if provider == 'openai':
                if not getattr(self, 'openai_client', None):
                    return "Error: OpenAI API key not configured."
                response = self.openai_client.chat.completions.create(
                    model=model or "gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return response.choices[0].message.content

            elif provider == 'claude':
                if not getattr(self, 'anthropic_client', None):
                    return "Error: Anthropic API key not configured."
                message = self.anthropic_client.messages.create(
                    model=model or "claude-3-opus-20240229",
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return message.content[0].text

            elif provider == 'gemini':
                if not getattr(self, 'gemini_model', None):
                    return "Error: Gemini API key not configured."
                # Gemini 1.5 allows system instructions in model config, but simple concatenation is safer across versions
                # unless we use the specific generation_config.
                # Let's stick to concat for safety unless we're sure of the library version capabilities for system instruction.
                # Actually, gemini-1.5-pro supports system_instruction argument in GenerativeModel constructor, but we initialized it globally.
                # We'll use the chat/content method with a system-like preamble.
                full_prompt = f"System Instruction: {system_prompt}\n\nUser Question: {user_prompt}"
                response = self.gemini_model.generate_content(full_prompt)
                return response.text

            elif provider == 'grok':
                if not getattr(self, 'grok_client', None):
                    return "Error: Grok API key not configured."
                response = self.grok_client.chat.completions.create(
                    model=model or "grok-beta",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return response.choices[0].message.content

            else:
                return f"Error: Unknown provider {provider}"

        except Exception as e:
            return f"Error generating response from {provider}: {str(e)}"

llm_service = LLMService()
