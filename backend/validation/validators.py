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
    expected_date = case_data.date

    parts = expected_date.split()

    if len(parts) == 3:
        day = int(parts[0])
        month = parts[1]
        year = parts[2]

        if 10 <= day % 100 <= 20:
            suffix = "th"
        else:
            suffix = {
                1: "st",
                2: "nd",
                3: "rd"
            }.get(day % 10, "th")

        equivalent_date = f"{day}{suffix} day of {month} {year}"
    else:
        equivalent_date = expected_date

    passed = (
        expected_date.lower() in text.lower()
        or equivalent_date.lower() in text.lower()
    )

    found = (
        expected_date
        if expected_date.lower() in text.lower()
        else equivalent_date
        if equivalent_date.lower() in text.lower()
        else None
    )

    return {
        "check": "Date consistency",
        "passed": passed,
        "expected": expected_date,
        "found": found,
        "issues": []
        if passed
        else [f"Expected date '{expected_date}' was not found."]
    }


def normalize_exhibit_text(value):
    """
    Normalize Unicode hyphen and quote characters so that
    equivalent exhibit representations compare equal.

    Different Unicode hyphen and apostrophe characters are
    normalized so that formatting differences do not cause
    a false failure.
    """

    normalized = value

    for hyphen in (
        "\u2010",
        "\u2011",
        "\u2012",
        "\u2013",
        "\u2014",
        "\u2212"
    ):
        normalized = normalized.replace(hyphen, "-")

    for quote in ("\u2018", "\u2019"):
        normalized = normalized.replace(quote, "'")

    return normalized


# Exhibit reference in the supplied documents, e.g.
# EXHIBIT-‘A’ / EXHIBIT-‘B’ / EXHIBIT-‘C’.
#
# The hyphen may be a Unicode hyphen and the quotes may be
# Unicode curly quotes or ASCII quotes. The letter is
# captured so the actual expected exhibit identifier can be
# verified rather than merely the word EXHIBIT.

EXHIBIT_PATTERN = (
    r"EXHIBIT"
    r"\s*"
    r"[-‐-‒–—]"
    r"\s*"
    r"[‘']"
    r"([A-Z0-9]+)"
    r"[’']"
)


def validate_exhibit(text, case_data):
    """
    Check exhibit consistency only when the supplied case
    information explicitly contains an exhibit reference.

    The reference explanation states that exhibit references
    are not a prescribed format requirement, so absence of an
    exhibit in the case information must not fail this check.

    When the case information does supply an exhibit, the
    generated affidavit must contain that exact exhibit
    identifier.
    """

    # Collect exhibit references supplied in the structured
    # case information, primarily the reply_points content.
    supplied_exhibits = []

    for point in case_data.reply_points:
        for content in point.content:
            normalized_content = normalize_exhibit_text(
                content
            )

            for match in re.finditer(
                EXHIBIT_PATTERN,
                normalized_content,
                flags=re.IGNORECASE
            ):
                supplied_exhibits.append(
                    match.group(1).upper()
                )

    # Case information contains NO exhibit reference.
    # Not an error: exhibits are not universally prescribed.
    if not supplied_exhibits:
        return {
            "check": "Exhibit consistency",
            "passed": True,
            "expected": (
                "No exhibit reference supplied in case information."
            ),
            "found": None,
            "issues": []
        }

    # Case information supplies exhibit references. Every one
    # of them must appear in the generated affidavit, with the
    # actual identifier verified (not merely the word EXHIBIT).

    normalized_generated = normalize_exhibit_text(text)

    missing = []

    for identifier in supplied_exhibits:

        expected = f"EXHIBIT-{identifier}"

        expected_pattern = (
            r"EXHIBIT"
            r"\s*"
            r"[-]"
            r"\s*"
            r"[‘']\s*"
            + re.escape(identifier)
            + r"\s*[’']"
        )

        found = re.search(
            expected_pattern,
            normalized_generated,
            flags=re.IGNORECASE
        ) is not None

        if not found:
            missing.append(expected)

    return {
        "check": "Exhibit consistency",
        "passed": len(missing) == 0,
        "expected": (
            missing
            if missing
            else [
                f"EXHIBIT-{identifier}"
                for identifier in supplied_exhibits
            ]
        ),
        "found": (
            []
            if missing
            else [
                f"EXHIBIT-{identifier}"
                for identifier in supplied_exhibits
            ]
        ),
        "issues": [
            f"Required exhibit reference is missing: {identifier}."
            for identifier in missing
        ]
        if missing
        else []
    }


def validate_required_sections(text, case_data):
    """
    Check that the major required sections exist
    and appear in the expected order.

    Expected values are derived from the case data so the
    check is format-generic and not specific to one case.
    """

    expected_case_number = (
        f"{case_data.proceeding_type.upper()} NO. "
        f"{case_data.case_number} OF {case_data.year}"
    )

    expected_affidavit_title = (
        f"AFFIDAVIT IN REPLY ON BEHALF OF RESPONDENT NO. "
        f"{case_data.answering_respondent_number}"
    )

    required_sections = [
        case_data.court.upper(),
        case_data.jurisdiction.upper(),
        expected_case_number,
        expected_affidavit_title,
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
            generated_text,
            case_data
        )
    )

    # 5. Required sections and order
    results.append(
        validate_required_sections(
            generated_text,
            case_data
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