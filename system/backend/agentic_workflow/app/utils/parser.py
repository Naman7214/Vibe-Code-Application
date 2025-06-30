import json
import re


def parse_model_OUTPUT(text: str) -> dict:
    """
    Extracts JSON enclosed in <OUTPUT>...</OUTPUT> tags from the given text
    and returns it as a Python dictionary.

    Args:
        text: The complete model OUTPUT string containing <OUTPUT>…</OUTPUT>.

    Returns:
        A dict parsed from the JSON inside the <OUTPUT> tags.

    Raises:
        ValueError: If no <OUTPUT>…</OUTPUT> section is found, or if the JSON is invalid.
    """
    # Find the first <OUTPUT>…</OUTPUT> block (DOTALL so . matches newlines)
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
