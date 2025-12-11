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
            self.gemini_model = genai.GenerativeModel('gemini-pro')

        # Grok (assuming OpenAI compatible endpoint or just checking key)
        if settings.grok_api_key:
            # Placeholder for Grok: using separate OpenAI client if base_url provided, or just generic request
            # For now, we'll assume standard OpenAI client configuration can handle it if base_url is changed,
            # but without a specific Grok SDK, we might stub it or use OpenAI client with Grok base URL.
            # Let's assume Grok uses OpenAI SDK with a different base URL or model name.
            pass

    async def generate_response(self, provider: str, model: str | None, system_prompt: str, user_prompt: str) -> str:
        try:
            if provider == 'openai':
                if not getattr(self, 'openai_client', None):
                    return "Error: OpenAI API key not configured."
                response = self.openai_client.chat.completions.create(
                    model=model or "gpt-3.5-turbo", # Default or specified
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
                # Gemini typically takes system prompt in config or as first part of chat
                # Simpler: just concat
                full_prompt = f"System: {system_prompt}\nUser: {user_prompt}"
                response = self.gemini_model.generate_content(full_prompt)
                return response.text

            elif provider == 'grok':
                 # Placeholder
                 return "Grok response placeholder (SDK not fully configured)"

            else:
                return f"Error: Unknown provider {provider}"

        except Exception as e:
            return f"Error generation response from {provider}: {str(e)}"

llm_service = LLMService()
