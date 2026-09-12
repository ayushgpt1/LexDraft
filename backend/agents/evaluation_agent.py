import json

from google.genai import types

from backend.core.llm_output import clean_json_output
from backend.models.schemas import EvaluationReport


class EvaluationAgent:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def run(self, case_data, reference_text, generated_text):

        schema = EvaluationReport.model_json_schema()

        system_prompt = f"""
You are a legal document evaluation agent.

Your task is to evaluate a generated Affidavit in Reply.

You must evaluate ONLY against:
1. The supplied structured case information.
2. The supplied reference affidavit format.
3. The generated affidavit.

Do NOT perform independent legal research.
Do NOT introduce outside facts.
Do NOT assume facts that are not present in the supplied inputs.

Evaluate the generated affidavit using these five criteria:

1. ENTITY ACCURACY
Check whether important entities and factual identifiers are accurate:
- petitioner
- respondents
- answering respondent
- deponent
- organisation
- case number
- year
- dates
- place
- exhibit references

2. COMPLETENESS
Check whether the generated affidavit contains the important information
and reply points present in the structured case information.

3. SEMANTIC FAITHFULNESS
Check whether the generated affidavit preserves the meaning of the supplied
case information without materially changing the intended statements.

4. HALLUCINATION
Identify facts, allegations, events, dates, documents, legal positions,
or other substantive information introduced by the generated affidavit
that are not supported by the supplied case information.

A document should receive a HIGH hallucination score when there are
few or no unsupported additions.

5. TEMPLATE FIDELITY
Compare the generated affidavit against the supplied reference format.
Check:
- required sections
- section order
- affidavit title
- deponent clause
- numbered paragraphs
- prayer
- jurat
- verification
- terminology and overall structure

The deterministic validation results are separate from this evaluation.
Do not assume that deterministic checks passing means the semantic
evaluation must receive a high score.

SCORING:
- 90-100: Excellent
- 75-89: Good
- 60-74: Needs improvement
- Below 60: Poor

For HALLUCINATION, the score represents the quality of the document
with respect to avoiding hallucinations:
- 90-100 = no or almost no unsupported information
- 75-89 = minor unsupported additions
- 60-74 = several unsupported additions
- Below 60 = significant hallucinated content

Return ONLY valid JSON following this schema:

{json.dumps(schema, indent=2)}
"""

        user_prompt = f"""
=== STRUCTURED CASE INFORMATION ===

{case_data.model_dump_json(indent=2)}

=== END CASE INFORMATION ===


=== REFERENCE AFFIDAVIT FORMAT ===

{reference_text}

=== END REFERENCE FORMAT ===


=== GENERATED AFFIDAVIT ===

{generated_text}

=== END GENERATED AFFIDAVIT ===


Evaluate the generated affidavit using the five criteria.
Provide a score and specific issues for each criterion.

If there are no issues for a criterion, return an empty issues list.

Return ONLY the JSON evaluation report.
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

        return clean_json_output(response.text)