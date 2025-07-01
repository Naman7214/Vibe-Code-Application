import re

def parse_xml_to_dict(xml_str):
    """
    Parse LLM response using regex to extract file data
    Much more robust than XML parsing for our specific format
    """
    
    file_data = []
    
    # Regex pattern to match FILE blocks
    file_pattern = r'<FILE>\s*<FILE_PATH>(.*?)</FILE_PATH>\s*<CODE_SNIPPET>(.*?)</CODE_SNIPPET>\s*</FILE>'
    
    # Find all matches with DOTALL flag to handle multiline code
    matches = re.findall(file_pattern, xml_str, re.DOTALL)
    
    for match in matches:
        file_path = match[0].strip()
        code_snippet = match[1].strip()
        
        if file_path and code_snippet:
            file_data.append({
                'file_path': file_path,
                'code_snippet': code_snippet
            })
    
    return file_data






