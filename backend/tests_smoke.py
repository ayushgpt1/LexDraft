# -*- coding: utf-8 -*-
"""Deterministic smoke test for the document generator and validators.

Builds a CaseInformation matching the supplied case PDF, generates the
DOCX with a mock paragraph list, and runs every deterministic validator.
No LLM is involved.
"""

from backend.models.schemas import (
    CaseInformation,
    Respondent,
    Deponent,
    ReplyPoint,
)
from backend.core.orchestrator import GeneratedParagraph, GeneratedParagraphs
from backend.core.document_generator import (
    build_affidavit_docx,
    extract_docx_text,
)
from backend.validation.validators import (
    run_all_validations,
    calculate_deterministic_score,
)


def main():

    case_data = CaseInformation(
        document_type="Affidavit in Reply",
        court="IN THE HIGH COURT OF JUDICATURE AT BOMBAY",
        jurisdiction="ORDINARY ORIGINAL CIVIL JURISDICTION",
        proceeding_type="WRIT PETITION",
        case_number="1847",
        year=2026,
        petitioner="Sunrise Housing Private Limited",
        respondents=[
            Respondent(number=1, name="State of Maharashtra"),
            Respondent(
                number=2,
                name="Mumbai Metropolitan Region Development Authority",
            ),
        ],
        answering_respondent_number=2,
        deponent=Deponent(
            name="Arvind Rajan",
            designation="Deputy Metropolitan Commissioner",
            organisation="Mumbai Metropolitan Region Development Authority",
            address="Bandra East, Mumbai, Maharashtra",
        ),
        reply_points=[
            ReplyPoint(
                point_number=1,
                move_type="identity_and_perusal",
                content=["Point 1 content"],
            ),
            ReplyPoint(
                point_number=2,
                move_type="blanket_denial",
                content=["Point 2 content"],
            ),
            ReplyPoint(
                point_number=3,
                move_type="preliminary_position",
                content=["Point 3 content"],
            ),
            ReplyPoint(
                point_number=4,
                move_type="substantive_answer",
                content=["Point 4 content"],
            ),
            ReplyPoint(
                point_number=5,
                move_type="substantive_answer",
                content=["Point 5 content"],
            ),
            ReplyPoint(
                point_number=6,
                move_type="substantive_answer",
                content=[
                    "Point 6 content with EXHIBIT-\u2018A\u2019 reference",
                ],
            ),
        ],
        prayer=["Respondent No. 2 prays that the Writ Petition be dismissed with costs."],
        verification_verb="solemnly affirm",
        place="Mumbai",
        date="5 September 2026",
        advocate_firm="Rajan & Associates",
        advocate_for="Respondent No. 2",
    )

    generated_paragraphs = GeneratedParagraphs(
        paragraphs=[
            GeneratedParagraph(
                paragraph_number=i,
                content=(
                    f"Mock body paragraph {i}."
                    if i != 6
                    else "Mock body paragraph 6 with EXHIBIT-\u2018A\u2019."
                ),
            )
            for i in range(1, 7)
        ]
        + [
            GeneratedParagraph(
                paragraph_number=7,
                content=(
                    "In the premises aforesaid, I say that the "
                    "Writ Petition deserves to be dismissed with costs."
                ),
            )
        ]
    )

    output_path = "outputs/smoke_test_affidavit.docx"

    build_affidavit_docx(
        case_data,
        generated_paragraphs,
        output_path,
    )

    text = extract_docx_text(output_path)

    print("=" * 70)
    print(text)
    print("=" * 70)

    results = run_all_validations(
        case_data,
        text,
        generated_paragraphs,
    )

    score = calculate_deterministic_score(results)

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] {result['check']}")
        if not result["passed"]:
            print(f"        issues: {result['issues']}")

    print(f"Deterministic score: {score['score']} ({score['passed_checks']}/{score['total_checks']})")

    # Key content assertions
    assert "the Deputy Metropolitan Commissioner of the Respondent No.2 above named" in text
    assert "do hereby solemnly affirm and state as under:" in text
    assert "Solemnly affirmed at Mumbai" in text
    assert "On this 5th day of September 2026" in text
    assert "paragraphs 1 to 7" in text
    assert "(a) dismiss the present Writ Petition with costs;" in text
    assert "WRIT PETITION NO. 1847 OF 2026" in text
    print("All content assertions passed.")


if __name__ == "__main__":
    main()
