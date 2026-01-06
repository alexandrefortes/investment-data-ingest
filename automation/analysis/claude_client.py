from anthropic import Anthropic
from automation.config import ANTHROPIC_API_KEY
import json

class ClaudeClient:
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        
    def analyze_report(self, prompt, model="claude-sonnet-4-20250514", temperature=0.7, max_tokens=8192):
        message = self.client.messages.create(
            max_tokens=max_tokens,
            temperature=temperature,
            model=model,
            system="Você é um especialista em investimentos de longo prazo. Responda apenas em JSON.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        result = message.content[0].text
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # Try to extract JSON from text if it's wrapped in markdown or has extra text
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                try:
                    return json.loads(result[start_idx:end_idx])
                except:
                    pass
            return result

    def convert_spreadsheet(self, prompt, model="claude-sonnet-4-20250514", temperature=0, max_tokens=8192):
        message = self.client.messages.create(
            max_tokens=max_tokens,
            temperature=temperature,
            model=model,
            system="Você é um especialista em planilhas extremamente meticuloso.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
