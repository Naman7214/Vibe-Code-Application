import re
from typing import Union, Dict, Any
from system.backend.tools.app.utils.logger import loggers

class JsonResponseError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)

def extract_text_content(response: Union[Dict[str, Any], str]) -> str:
        """
        Extract markdown content from API response, specifically looking for content
        wrapped in ```markdown code blocks
        
        :param response: API response dictionary
        :return: Extracted markdown content (without the code block wrapper)
        """
        try:
            # Get the raw text content from the response
            if isinstance(response, str):
                raw_text = response
            else:
                raw_text = response["content"][0]["text"]
            
            # Use regex to find content between ```markdown and ```
            markdown_pattern = r'```markdown\s*(.*?)\s*```'
            match = re.search(markdown_pattern, raw_text, re.DOTALL)
            
            if match:
                # Return the content inside the markdown code block
                return match.group(1).strip()
            else:
                # If no markdown code block found, try to find any code block
                general_pattern = r'```.*?\s*(.*?)\s*```'
                general_match = re.search(general_pattern, raw_text, re.DOTALL)
                
                if general_match:
                    return general_match.group(1).strip()
                else:
                    # If no code blocks found, return the raw text
                    return raw_text.strip()
                    
        except (KeyError, IndexError, TypeError) as e:
            raise JsonResponseError(
                status_code=500,
                detail=f"Unexpected response format from Anthropic API: {str(e)}"
            )
            
def extract_json_content(response: Union[Dict[str, Any], str]) -> str:
    """
    Extract json content from API response, specifically looking for content
    wrapped in ```json code blocks
    
    :param response: API response dictionary
    :return: Extracted json content (without the code block wrapper)
    """
    try:
        # Get the raw text content from the response
        if isinstance(response, str):
            raw_text = response
        else:
            raw_text = response["content"][0]["text"]
        
        # Use regex to find content between ```json and ```
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, raw_text, re.DOTALL)
        
        if match:
            # Return the content inside the json code block
            return match.group(1).strip()
        else:
            # If no json code block found, try to find any code block
            general_pattern = r'```.*?\s*(.*?)\s*```'
            general_match = re.search(general_pattern, raw_text, re.DOTALL)
            
            if general_match:
                return general_match.group(1).strip()
            else:
                # If no code blocks found, return the raw text
                return raw_text.strip()
                
    except (KeyError, IndexError, TypeError) as e:
        raise JsonResponseError(
            status_code=500,
            detail=f"Unexpected response format from Anthropic API: {str(e)}"
        )