import json

from google.genai import types

from backend.core.llm_output import clean_json_output


class GenerationAgent:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def run(self, reference_rules, mapped_content):

        # The closing paragraph is never a fixed number.
        # It is always the final numbered paragraph,
        # immediately after the last reply-point paragraph.

        reply_points = mapped_content.get(
            "reply_points",
            []
        )

        closing_paragraph_number = len(reply_points) + 1

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

6a. Paragraph 1 is the identity and perusal paragraph. It MUST
follow the reference format's prescribed identity formulation
closely:

"I say that I am [the Respondent No.__ / the [DESIGNATION] of the
Respondent No.__] in the above [PROCEEDING TYPE] and am well
acquainted with the facts and circumstances of the case. I have
perused the Petition and the documents annexed thereto and am
competent to affirm this Affidavit in Reply."

Adapt ONLY the bracketed case-specific portions using information
explicitly supported by MAPPED CASE INFORMATION. For an
organisation/authority respondent, use the designation form:
"the [DESIGNATION] of the Respondent No.__ above named". For a
person respondent, use "the Respondent No.__ above named". Do NOT
invent age, occupation, documents, facts, allegations, legal
positions, or qualifications that are not present in the mapped
case information. Do NOT copy sample-specific factual details
from the reference sample.

7. Do not create additional substantive paragraphs.

8. Paragraph {closing_paragraph_number} must be a short closing paragraph
based only on the supplied case information. It is a concluding
statement in the reference closing form ("In the premises aforesaid,
I say that the [PROCEEDING TYPE] deserves to be dismissed with
costs."). It must NOT be phrased as a request or prayer, must not
repeat the Prayer section, and must be the final numbered paragraph,
immediately after the last reply-point paragraph.

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
11. For paragraph 1, follow the reference format's prescribed
identity/perusal wording closely.

Use the reference's standard identity formulation:
"I say that I am ... and am well acquainted with the facts and
circumstances of the present case."

Adapt only the case-specific portions using information explicitly
supported by MAPPED CASE INFORMATION.

Do not copy factual details from the reference sample that are not
present in the mapped case information.
Do not replace the prescribed identity formulation with a different
opening unless the reference rules require it.

REFERENCE RULES:
{json.dumps(reference_rules, indent=2)}

MAPPED CASE INFORMATION:
{json.dumps(mapped_content, indent=2)}
"""

        response = self.client.generate_content(
            contents=[
                system_prompt
            ],
            config=types.GenerateContentConfig(
                temperature=0
            )
        )

        return clean_json_output(response.text)