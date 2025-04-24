import os
import json
#import openai  # <-- Add this import
from openai import OpenAI


class AIGeneratedAnalyzer:
    def __init__(self):
        #openai.api_key = os.getenv('OPENAI_API_KEY')  # Set your OpenAI API key
        self.client = OpenAI(api_key="YOUR_DEEPSEEK_KEY",base_url="https://api.deepseek.com")

    def analyze_text(self, text):
        prompt = f"""Analyze provided text for AI generation indicators. You are an expert AI-generated text analyzer. And you are given a text. MUST Provide following information:
            1. AI Score (0-100)
            2. Very Clear conclusion
            3. Specific technical patterns with explanations
            
            Text: {text}
            
            Format response EXACTLY like:
            ## AI Score: [score]/100
            ## Conclusion: [conclusion in Chinese]
            ## Patterns:
            - [Pattern Name in Chinese]: [Description in Chinese] (Confidence: High/Medium/Low)
            - [Pattern Name in Chinese]: [Description in Chinese] (Confidence: High/Medium/Low)
            ..."""

        # Call OpenAI ChatGPT API instead of AWS Bedrock
        response = self.client.chat.completions.create(
            model="deepseek-chat",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are an expert AI-generated text analyzer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
            temperature=0.2
        )
        # Extract the generated content
        result = response.choices[0].message.content
        return self._parse_response(result)

    def _parse_response(self, result):
        analysis = {
            'score': None,
            'conclusion': None,
            'patterns': []
        }

        # parse the response => create analysis report in dictionary format 
        for line in result.split('\n'):
            line = line.strip()
            if line.startswith('## AI Score:'):
                analysis['score'] = int(line.split(':')[-1].split('/')[0].strip())
            elif line.startswith('## Conclusion:'):
                analysis['conclusion'] = line.split(':')[-1].strip()
            elif line.startswith('-'):
                parts = line.split(':', 1)
                if len(parts) > 1:
                    pattern_name = parts[0][2:].strip()  # Remove leading '-'
                    description = parts[1].split('(Confidence:')[0].strip()
                    confidence = parts[1].split('Confidence:')[-1].replace(')', '').strip()
                    analysis['patterns'].append({
                        'pattern': pattern_name,
                        'description': description,
                        'confidence': confidence
                    })

        return analysis
