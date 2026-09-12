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