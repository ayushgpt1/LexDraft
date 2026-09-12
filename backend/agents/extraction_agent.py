import json

from google.genai import types

from backend.core.llm_output import clean_json_output
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

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                user_prompt
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0
            )
        )

        raw_output = response.text

        return clean_json_output(raw_output)