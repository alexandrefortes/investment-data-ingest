from openai import OpenAI
from automation.config import OPENAI_API_KEY
import json

class AnalysisClient:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def analyze_report(self, prompt, model="gpt-4.1", temperature=0.7, max_tokens=4096):
        response = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Você é um especialista em investimentos de longo prazo."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return result

    def convert_spreadsheet(self, prompt, model="gpt-4.1", temperature=0, max_tokens=10000):
        # Original code used gpt-4.1 which might be a typo or custom model alias, defaulting to gpt-4.1 or user specific model
        # Using model passed in argument
        response = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": "Você é um especialista em planilhas extremamente meticuloso."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
