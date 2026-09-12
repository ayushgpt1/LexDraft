import json


def clean_json_output(raw_output):
    """
    Strip Markdown code fences and surrounding prose that a model
    may place around a JSON response, so the existing Pydantic
    JSON parsing does not fail.

    Returns the original text unchanged when no JSON object can be
    recovered, preserving the existing error behaviour.
    """

    if raw_output is None:
        return raw_output

    cleaned = raw_output.strip()

    # Remove ```json ... ``` code fences
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    # Remove any prose before or after the JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:
        candidate = cleaned[start:end + 1]

        try:
            json.loads(candidate)
            cleaned = candidate
        except json.JSONDecodeError:
            pass

    return cleaned