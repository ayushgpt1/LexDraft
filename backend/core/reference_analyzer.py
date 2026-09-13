import pymupdf


def extract_pdf_text(file_path):
    doc = pymupdf.open(file_path)

    pages = []

    for page in doc:
        pages.append(page.get_text())

    doc.close()

    return "\n".join(pages) 

reference_rules = {
    "document_type": "Affidavit in Reply",

    "court_format": {
        "forum_heading": "IN THE HIGH COURT OF JUDICATURE AT [CITY]",
        "jurisdiction": "[TYPE] JURISDICTION",
        "case_number": "[PROCEEDING TYPE] NO. [NUMBER] OF [YEAR]"
    },

    "sections": [
        "FORUM_HEADING",
        "JURISDICTION",
        "CASE_NUMBER",
        "CAUSE_TITLE",
        "AFFIDAVIT_TITLE",
        "DEPONENT_CLAUSE",
        "NUMBERED_PARAGRAPHS",
        "PRAYER",
        "JURAT",
        "VERIFICATION"
    ],

    "cause_title": {
        "petitioner_tag": "...Petitioner",
        "respondent_tag": "...Respondent",
        "versus": "VERSUS",
        "respondents_are_numbered": True
    },

    "affidavit_title": {
        "template": "AFFIDAVIT IN REPLY ON BEHALF OF RESPONDENT NO. [N]",
        "must_include_respondent_number": True
    },

    "paragraph_rules": {
        "continuous_numbering": True,
        "prayer_is_not_numbered_with_body": True,
        "first": "IDENTITY_AND_PERUSAL",
        "second": "BLANKET_DENIAL",
        "third": "PRELIMINARY_POSITION",
        "middle": "SUBSTANTIVE_ANSWER",
        "last": "CLOSING",
        "closing_form": (
            "In the premises aforesaid, I say that the "
            "[PROCEEDING TYPE] deserves to be dismissed with costs."
        ),
        "closing_is_not_a_request": True
    },

    "prayer": {
        "heading": "PRAYER",
        "numbering_style": "letters",
        "items": ["(a)", "(b)", "(c)"]
    },

    "jurat": {
        "affirmation": "Solemnly affirmed at [PLACE]",
        "date": "On this [Nth] day of [MONTH] [YEAR]",
        "deponent": "DEPONENT",
        "before_me": "Before Me"
    },

    "verification": {
        "heading": "VERIFICATION",
        "paragraph_range_must_match_body_count": True,
        "place_and_date_repeat_jurat": True
    },

    "deponent_rules": {
        "person": "the Respondent No.[N] above named",
        "organisation": "the [DESIGNATION] of the Respondent No.[N] above named",
        "organisation_must_not_say": "I am the Respondent No.[N]"
    },

    "entities": [
        "FORUM_CITY",
        "JURISDICTION_TYPE",
        "CASE_TYPE",
        "CASE_NUMBER",
        "YEAR",
        "PETITIONER",
        "RESPONDENT",
        "RESPONDENT_NUMBER",
        "DEPONENT",
        "CAPACITY",
        "ORGANISATION",
        "ADDRESS",
        "AGE",
        "OCCUPATION",
        "VERIFICATION_VERB",
        "PLACE_OF_ATTESTATION",
        "DATE",
        "PARAGRAPH_COUNT"
    ],

    "reply_moves": [
        "IDENTITY_AND_PERUSAL",
        "BLANKET_DENIAL",
        "PRELIMINARY_POSITION",
        "SUBSTANTIVE_ANSWER",
        "CLOSING",
        "PRAYER_TO_DISMISS"
    ],

    "formatting": {
        "major_headings": "bold_all_caps_centred",
        "cause_title_names": "normal_left",
        "status_tags": "right_aligned",
        "versus": "centred_own_line",
        "paragraph_numbers": "bold",
        "prayer_letters": "bold",
        "paragraph_text": "normal_justified",
        "deponent": "all_caps_right_aligned",
        "before_me": "left_aligned"
    }
}

# Default file paths for the bundled reference documents.
# These are used when no user-uploaded replacements are supplied.
DEFAULT_FORMAT_PATH = 'frontend/public/reference/01 Affidavit Format Explained.pdf'
DEFAULT_SAMPLE_PATH = 'frontend/public/reference/02 Affidavit in Reply Sample.docx.pdf'


def extract_rules_from_format_explained(text: str) -> dict:
    """Extract applicable rules from a Format Explained PDF text."""
    rules = {}
    text_lower = text.lower()
    import re

    # Document type
    if 'affidavit in reply' in text_lower:
        rules['document_type'] = 'Affidavit in Reply'
    elif 'affidavit' in text_lower:
        rules['document_type'] = 'Affidavit'

    # Court format
    forum_match = re.search(
        r'(?:forum\s*[Rr]eading|forum\s*heading|high\s*court\s*of\s*judicature).*?(?:\.|$)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    if forum_match:
        rules.setdefault('court_format', {})['forum_heading'] = forum_match.group(0).strip()

    jurisdiction_match = re.search(
        r'(?:jurisdiction)[:\s]+([^\n.]+)',
        text,
        re.IGNORECASE
    )
    if jurisdiction_match:
        rules.setdefault('court_format', {})['jurisdiction'] = jurisdiction_match.group(1).strip()

    case_number_match = re.search(
        r'(?:case\s*number|proceeding\s*number|no\.[\s]*\d+).*?(?:\.|$)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    if case_number_match:
        rules.setdefault('court_format', {})['case_number'] = case_number_match.group(0).strip()

    # Sections
    sections = []
    for kw in ['forum heading', 'jurisdiction', 'case number', 'cause title', 'affidavit',
               'deponent', 'prayer', 'jurat', 'verification', 'body', 'paragraphs']:
        if kw in text_lower:
            sections.append(kw.upper().replace(' ', '_'))
    if sections:
        rules['sections'] = sections

    # Cause title
    if 'petitioner' in text_lower or 'respondent' in text_lower:
        cause_title = {}
        petitioner_match = re.search(r'petitioner[:\s]+(?:as|represented by|and)[^\n.]+', text, re.IGNORECASE)
        if petitioner_match:
            cause_title['petitioner_tag'] = petitioner_match.group(0).strip()
        respondent_match = re.search(r'respondent[:\s]+(?:no\.|represented by|and)[^\n.]+', text, re.IGNORECASE)
        if respondent_match:
            cause_title['respondent_tag'] = respondent_match.group(0).strip()
        versus_match = re.search(r'versus|vs\.|v\.', text, re.IGNORECASE)
        if versus_match:
            cause_title['versus'] = 'VERSUS'
        if re.search(r'respondent\s*(?:no\.?|number)\s*\d+', text, re.IGNORECASE):
            cause_title['respondents_are_numbered'] = True
        if cause_title:
            rules['cause_title'] = cause_title

    return rules


def analyze_format_explained(text: str) -> dict:
    """Public API to analyze a user-supplied Format Explained document."""
    extracted = extract_rules_from_format_explained(text)
    if not extracted:
        return dict(reference_rules)
    merged = dict(reference_rules)
    for key, value in extracted.items():
        # The uploaded Format Explained is the source of truth for any rule
        # it provides. Replace the corresponding default key entirely
        # (both scalar and dict values) so that old hardcoded rules are not
        # silently retained when the uploaded document defines a different
        # rule for the same key. Defaults are preserved only for top-level
        # keys that the uploaded document does not address at all.
        merged[key] = value
    return merged


def get_selected_sample_text(sample_file_path: str | None = None) -> str | None:
    """Return the text of the selected sample affidavit for the current run."""
    if sample_file_path is None:
        return None
    import pymupdf
    doc = pymupdf.open(sample_file_path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return chr(10).join(pages)
