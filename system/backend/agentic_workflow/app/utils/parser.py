import json
import re


def parse_model_output(text: str) -> dict:
    """
    Extracts JSON enclosed in <output>...</output> tags from the given text
    and returns it as a Python dictionary.
    Args:
        text: The complete model output string containing <output>…</output>.
    Returns:
        A dict parsed from the JSON inside the <output> tags.
    Raises:
        ValueError: If no <output>…</output> section is found, or if the JSON is invalid.
    """
    # Find the first <output>…</output> block (DOTALL so . matches newlines)
    match = re.search(r"<OUTPUT>(.*?)</OUTPUT>", text, re.DOTALL)
    if not match:
        raise ValueError("No <OUTPUT>...</OUTPUT> section found in the input.")
    # Extract and clean up the JSON string
    json_str = match.group(1).strip()
    # Parse and return
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON inside <OUTPUT> tags: {e}")
