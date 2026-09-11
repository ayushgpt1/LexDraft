import json

from backend.models.schemas import GeneratedParagraphs


class GenerationAgent:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def run(self, reference_rules, mapped_content):

        system_prompt = f"""
You are a constrained legal document drafting agent.

Your task is to draft ONLY the numbered body paragraphs
of an Affidavit in Reply.

You MUST follow these rules:

1. Use ONLY facts explicitly present in MAPPED CASE INFORMATION.

2. Do NOT introduce new facts, allegations, legal provisions,
dates, events, documents, rights, authorities, or reliefs.

3. Do NOT copy generic factual allegations from the reference
template unless they are explicitly supported by the case data.

4. The REFERENCE RULES are a structural and linguistic guide.
They are NOT additional case facts.

5. Preserve names, respondent numbers, dates, organisations,
documents and exhibit references exactly.

6. Each numbered paragraph must correspond to the supplied
mapped reply point with the same paragraph number.

7. Do not create additional substantive paragraphs.

8. Paragraph 7 must be a short closing paragraph based only
on the supplied prayer and case information.

9. Do not generate the Prayer, Jurat or Verification.
Those will be generated programmatically.

10. Return ONLY valid JSON in this format:

{{
    "paragraphs": [
        {{
            "paragraph_number": 1,
            "content": "..."
        }}
    ]
}}

REFERENCE RULES:
{json.dumps(reference_rules, indent=2)}

MAPPED CASE INFORMATION:
{json.dumps(mapped_content, indent=2)}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                }
            ],
            temperature=0
        )

        return response.choices[0].message.content