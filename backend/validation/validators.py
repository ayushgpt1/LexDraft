import re


def validate_respondent_consistency(text, case_data):
    """
    Check that references to the answering respondent
    use the correct respondent number.

    The cause title is excluded because it legitimately
    contains all respondent numbers.
    """

    expected_number = case_data.answering_respondent_number

    marker = "AFFIDAVIT IN REPLY ON BEHALF OF"

    parts = text.split(marker, 1)

    if len(parts) < 2:
        return {
            "check": "Respondent consistency",
            "passed": False,
            "expected": f"Respondent No. {expected_number}",
            "found": [],
            "issues": ["Affidavit section could not be located."]
        }

    affidavit_text = parts[1]

    occurrences = re.findall(
        r"Respondent\s+No\.\s*\d+",
        affidavit_text,
        flags=re.IGNORECASE
    )

    expected = f"Respondent No. {expected_number}"

    wrong = [
        item for item in occurrences
        if re.search(
            rf"Respondent\s+No\.\s*{expected_number}\b",
            item,
            flags=re.IGNORECASE
        ) is None
    ]

    return {
        "check": "Respondent consistency",
        "passed": len(wrong) == 0,
        "expected": expected,
        "found": occurrences,
        "issues": wrong
    }


def validate_case_number(text, case_data):
    """
    Check that the generated document contains
    the expected proceeding type, case number and year.
    """

    expected = (
        f"{case_data.proceeding_type} NO. "
        f"{case_data.case_number} OF {case_data.year}"
    )

    passed = expected.lower() in text.lower()

    return {
        "check": "Case number consistency",
        "passed": passed,
        "expected": expected,
        "found": expected if passed else None,
        "issues": []
        if passed
        else [f"Expected case reference: {expected}"]
    }


def validate_date(text, case_data):
    """
    Check that the case date appears in the generated document.
    """

    expected_date = case_data.date

    passed = expected_date in text

    return {
        "check": "Date consistency",
        "passed": passed,
        "expected": expected_date,
        "found": expected_date if passed else None,
        "issues": []
        if passed
        else [f"Expected date '{expected_date}' was not found."]
    }


def validate_exhibit(text):
    """
    Check that the required Exhibit-A reference appears.

    Different Unicode hyphen and apostrophe characters are
    normalized so that formatting differences do not cause
    a false failure.
    """

    normalized_text = (
        text
        .replace("\u2010", "-")
        .replace("\u2011", "-")
        .replace("\u2012", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
    )

    normalized_text = (
        normalized_text
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )

    expected = "EXHIBIT-'A'"

    found = expected.lower() in normalized_text.lower()

    return {
        "check": "Exhibit consistency",
        "passed": found,
        "expected": expected,
        "found": expected if found else None,
        "issues": []
        if found
        else ["Required exhibit reference is missing."]
    }


def validate_required_sections(text):
    """
    Check that the major required sections exist
    and appear in the expected order.
    """

    required_sections = [
        "IN THE HIGH COURT OF JUDICATURE AT BOMBAY",
        "ORDINARY ORIGINAL CIVIL JURISDICTION",
        "WRIT PETITION NO.",
        "AFFIDAVIT IN REPLY ON BEHALF OF RESPONDENT NO.",
        "PRAYER",
        "VERIFICATION"
    ]

    issues = []
    positions = {}

    for section in required_sections:
        position = text.upper().find(section.upper())

        if position == -1:
            issues.append(
                f"Required section missing: {section}"
            )
        else:
            positions[section] = position

    found_sections = [
        section
        for section in required_sections
        if section in positions
    ]

    for i in range(len(found_sections) - 1):
        current = found_sections[i]
        next_section = found_sections[i + 1]

        if positions[current] > positions[next_section]:
            issues.append(
                f"Section order incorrect: "
                f"'{current}' appears after '{next_section}'."
            )

    return {
        "check": "Required sections and order",
        "passed": len(issues) == 0,
        "expected": required_sections,
        "found": found_sections,
        "issues": issues
    }


def validate_paragraph_numbers(generated_paragraphs):
    """
    Check that generated paragraphs are numbered
    continuously starting from 1.
    """

    numbers = [
        paragraph.paragraph_number
        for paragraph in generated_paragraphs.paragraphs
    ]

    expected = list(range(1, len(numbers) + 1))

    passed = numbers == expected

    return {
        "check": "Paragraph numbering",
        "passed": passed,
        "actual": numbers,
        "expected": expected,
        "issues": []
        if passed
        else ["Paragraph numbering is not sequential."]
    }


def validate_verification_range(text, generated_paragraphs):
    """
    Check that the verification clause refers to
    the actual number of generated body paragraphs.
    """

    paragraph_count = len(generated_paragraphs.paragraphs)

    expected_phrase = f"paragraphs 1 to {paragraph_count}"

    passed = expected_phrase.lower() in text.lower()

    return {
        "check": "Verification range",
        "passed": passed,
        "expected": expected_phrase,
        "found": expected_phrase if passed else None,
        "issues": []
        if passed
        else [
            f"Verification should refer to paragraphs "
            f"1 to {paragraph_count}."
        ]
    }


def run_all_validations(
    case_data,
    generated_text,
    generated_paragraphs
):
    """
    Run all deterministic validation checks.
    """

    results = []

    # 1. Respondent consistency
    results.append(
        validate_respondent_consistency(
            generated_text,
            case_data
        )
    )

    # 2. Case number consistency
    results.append(
        validate_case_number(
            generated_text,
            case_data
        )
    )

    # 3. Date consistency
    results.append(
        validate_date(
            generated_text,
            case_data
        )
    )

    # 4. Exhibit consistency
    results.append(
        validate_exhibit(
            generated_text
        )
    )

    # 5. Required sections and order
    results.append(
        validate_required_sections(
            generated_text
        )
    )

    # 6. Paragraph numbering
    results.append(
        validate_paragraph_numbers(
            generated_paragraphs
        )
    )

    # 7. Verification range
    results.append(
        validate_verification_range(
            generated_text,
            generated_paragraphs
        )
    )

    return results


def calculate_deterministic_score(validation_results):
    """
    Calculate the overall deterministic validation score.
    """

    total_checks = len(validation_results)

    passed_checks = sum(
        1
        for result in validation_results
        if result["passed"]
    )

    failed_checks = total_checks - passed_checks

    score = (
        (passed_checks / total_checks) * 100
        if total_checks > 0
        else 0
    )

    return {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "score": score
    }