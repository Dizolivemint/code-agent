import re
from typing import Tuple

def contains_with_open(code: str) -> bool:
    """
    Check if code contains any 'with open' statements
    
    Args:
        code: Python code to check
        
    Returns:
        True if code contains 'with open' statements, False otherwise
    """
    # Look for 'with open' followed by parentheses
    pattern = r'with\s+open\s*\('
    return bool(re.search(pattern, code))

def refactor_with_open(code: str) -> str:
    """
    Refactor code to replace 'with open' statements with direct open/close
    
    Args:
        code: Python code to refactor
        
    Returns:
        Refactored code without 'with open' statements
    """
    # Pattern to match 'with open' statements
    pattern = r'with\s+open\s*\((.*?)\)\s+as\s+(\w+):\s*(.*?)(?=\n\S|\Z)'
    
    def replace_with_open(match):
        params = match.group(1)
        var_name = match.group(2)
        body = match.group(3)
        
        # Split body into lines and indent them
        lines = body.split('\n')
        indented_lines = [line for line in lines if line.strip()]
        
        # Create the refactored code
        refactored = f"file_obj = open({params})\n"
        refactored += f"{var_name} = file_obj\n"
        for line in indented_lines:
            refactored += line + "\n"
        refactored += f"{var_name}.close()"
        
        return refactored
    
    # Replace all occurrences
    return re.sub(pattern, replace_with_open, code, flags=re.DOTALL)

def check_and_refactor_code(code: str) -> Tuple[bool, str]:
    """
    Check if code needs refactoring and refactor if necessary
    
    Args:
        code: Python code to check and potentially refactor
        
    Returns:
        Tuple of (needs_refactoring, refactored_code)
    """
    if contains_with_open(code):
        return True, refactor_with_open(code)
    return False, code 