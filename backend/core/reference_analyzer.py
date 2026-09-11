import re


class ReferenceAnalyzer:
    """
    Analyzes the supplied Affidavit in Reply reference document
    and extracts its expected structural sections and rules.
    """

    def run(self, reference_text):
        sections = [
            "FORUM_HEADING",
            "JURISDICTION",
            "CASE_NUMBER",
            "CAUSE_TITLE",
            "AFFIDAVIT_TITLE",
            "DEPONENT_CLAUSE",
            "NUMBERED_PARAGRAPHS",
            "PRAYER",
            "JURAT",
            "VERIFICATION",
            "ADVOCATE_BLOCK",
        ]

        section_positions = {}

        section_patterns = {
            "FORUM_HEADING": r"IN THE HIGH COURT OF JUDICATURE",
            "JURISDICTION": r"JURISDICTION",
            "CASE_NUMBER": r"(?:WRIT PETITION|PETITION)\s+NO\.",
            "CAUSE_TITLE": r"VERSUS",
            "AFFIDAVIT_TITLE": r"AFFIDAVIT IN REPLY",
            "PRAYER": r"PRAYER",
            "JURAT": r"SOLEMNLY AFFIRMED",
            "VERIFICATION": r"VERIFICATION",
            "ADVOCATE_BLOCK": r"ADVOCATE",
        }

        for section, pattern in section_patterns.items():
            match = re.search(pattern, reference_text, re.IGNORECASE)
            if match:
                section_positions[section] = match.start()

        ordered_sections = sorted(
            section_positions,
            key=section_positions.get
        )

        return {
            "document_type": "Affidavit in Reply",
            "sections": sections,
            "detected_sections": ordered_sections,
            "section_positions": section_positions,
            "formatting_rules": {
                "major_headings": "Bold, uppercase and centered",
                "cause_title": "Left aligned",
                "party_labels": "Right aligned",
                "versus": "Centered",
                "paragraph_numbers": "Bold",
                "body": "Justified",
                "prayer_items": "Lettered",
                "deponent": "Uppercase and right aligned",
                "verification": "Appears after jurat",
            },
            "fixed_phrases": {
                "deponent_clause": "do hereby solemnly affirm and state as under",
                "verification": "true and correct to my knowledge and belief",
                "verification_closing": "nothing material has been concealed therefrom",
            }
        }