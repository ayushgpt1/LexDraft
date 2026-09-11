def map_content(case_data):
    """
    Maps structured case information into the content structure
    required by the Affidavit in Reply generation stage.
    """

    mapped_points = []

    for reply_point in case_data.reply_points:
        mapped_points.append({
            "paragraph_number": reply_point.point_number,
            "move_type": reply_point.move_type,
            "content": reply_point.content
        })

    return {
        "document_type": case_data.document_type,
        "court": case_data.court,
        "jurisdiction": case_data.jurisdiction,
        "proceeding_type": case_data.proceeding_type,
        "case_number": case_data.case_number,
        "year": case_data.year,
        "petitioner": case_data.petitioner,
        "respondents": [
            {
                "number": respondent.number,
                "name": respondent.name
            }
            for respondent in case_data.respondents
        ],
        "answering_respondent_number": case_data.answering_respondent_number,
        "deponent": case_data.deponent.model_dump(),
        "reply_points": mapped_points,
        "prayer": case_data.prayer,
        "verification_verb": case_data.verification_verb,
        "place": case_data.place,
        "date": case_data.date,
        "advocate_firm": case_data.advocate_firm,
        "advocate_for": case_data.advocate_for
    }