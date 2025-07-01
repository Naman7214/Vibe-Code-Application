import re
from typing import Any, Dict, List


def parse_xml_to_dict(xml_str: str) -> List[Dict[str, Any]]:
    """
    Parse LLM response using regex to extract file data
    Much more robust than XML parsing for our specific format
    """
    file_data = []

    file_pattern = r"<FILE>\s*<FILE_PATH>(.*?)</FILE_PATH>\s*<CODE_SNIPPET>(.*?)</CODE_SNIPPET>\s*</FILE>"

    matches = re.findall(file_pattern, xml_str, re.DOTALL)

    for match in matches:
        file_path = match[0].strip()
        code_snippet = match[1].strip()

        if file_path and code_snippet:
            file_data.append(
                {"file_path": file_path, "code_snippet": code_snippet}
            )

    return file_data
