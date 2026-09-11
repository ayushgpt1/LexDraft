import json

from backend.models.schemas import CaseInformation


class ExtractionAgent:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def run(self, case_text):
        schema = CaseInformation.model_json_schema()

        system_prompt = f"""
You are a legal document information extraction agent.

Extract information ONLY from the supplied source document.

Important rules:
1. Do not invent information.
2. Preserve names, dates, numbers and organisation names exactly.
3. If information is not provided, use null where allowed.
4. Identify the respondent on whose behalf the affidavit is filed.
5. Classify each reply point using only the allowed move types.
6. Return ONLY valid JSON.
7. The JSON must follow this schema:

{json.dumps(schema, indent=2)}
"""

        user_prompt = f"""
Extract the structured case information from this document:

--- CASE INFORMATION ---
{case_text}
--- END DOCUMENT ---
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0
        )

        return response.choices[0].message.content