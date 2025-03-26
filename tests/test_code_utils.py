"""
Tests for code utilities.
"""

import unittest
from code_agent.utils.code_utils import contains_with_open, refactor_with_open, check_and_refactor_code

class TestCodeUtils(unittest.TestCase):
    """Test cases for code utilities"""
    
    def test_contains_with_open(self):
        """Test detection of with open statements"""
        # Test positive cases
        self.assertTrue(contains_with_open('with open("file.txt") as f:'))
        self.assertTrue(contains_with_open('with open("file.txt", "r") as f:'))
        self.assertTrue(contains_with_open('with open(file_path) as f:'))
        
        # Test negative cases
        self.assertFalse(contains_with_open('file_obj = open("file.txt")'))
        self.assertFalse(contains_with_open('f = open("file.txt")\nf.close()'))
        self.assertFalse(contains_with_open('def read_file():'))
    
    def test_refactor_with_open(self):
        """Test refactoring of with open statements"""
        # Test simple case
        code = '''with open("file.txt", "r") as f:
    content = f.read()'''
        
        expected = '''file_obj = open("file.txt", "r")
f = file_obj
content = f.read()
f.close()'''
        
        self.assertEqual(refactor_with_open(code), expected)
        
        # Test multiple lines
        code = '''with open("file.txt", "w") as f:
    f.write("Hello")
    f.write("World")'''
        
        expected = '''file_obj = open("file.txt", "w")
f = file_obj
f.write("Hello")
f.write("World")
f.close()'''
        
        self.assertEqual(refactor_with_open(code), expected)
        
        # Test with nested indentation
        code = '''def read_file():
    with open("file.txt", "r") as f:
        content = f.read()
        return content'''
        
        expected = '''def read_file():
    file_obj = open("file.txt", "r")
    f = file_obj
    content = f.read()
    f.close()
    return content'''
        
        self.assertEqual(refactor_with_open(code), expected)
    
    def test_check_and_refactor_code(self):
        """Test the combined check and refactor functionality"""
        # Test code that needs refactoring
        code = '''with open("file.txt", "r") as f:
    content = f.read()'''
        
        needs_refactoring, refactored = check_and_refactor_code(code)
        self.assertTrue(needs_refactoring)
        self.assertIn('file_obj = open', refactored)
        self.assertIn('f.close()', refactored)
        
        # Test code that doesn't need refactoring
        code = '''file_obj = open("file.txt", "r")
content = file_obj.read()
file_obj.close()'''
        
        needs_refactoring, refactored = check_and_refactor_code(code)
        self.assertFalse(needs_refactoring)
        self.assertEqual(refactored, code) 