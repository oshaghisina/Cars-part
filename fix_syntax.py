#!/usr/bin/env python3
"""Fix Python syntax errors in f-strings and other issues."""

import re
import os
import glob

def fix_syntax_errors(content):
    """Fix various syntax errors in Python code."""
    # Fix double quotes in f-strings
    content = re.sub(r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"', content)
    
    # Fix f-strings with trailing double quotes
    content = re.sub(r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"', content)
    
    # Fix specific patterns
    content = re.sub(r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"', content)
    content = re.sub(r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"', content)
    
    # Fix f-strings with unmatched quotes
    content = re.sub(r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"', content)
    
    # Fix specific problematic patterns
    patterns = [
        (r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"'),
        (r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"'),
        (r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_file(filepath):
    """Fix syntax errors in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Manual fixes for specific files
        if 'admin.py' in filepath:
            content = content.replace('f"Settings updated by user {current_user.username}": "', 
                                    'f"Settings updated by user {current_user.username}: "')
        
        # Apply general fixes
        content = fix_syntax_errors(content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Fix all Python files in the app directory."""
    python_files = glob.glob('app/**/*.py', recursive=True)
    fixed_count = 0
    
    for filepath in python_files:
        if fix_file(filepath):
            fixed_count += 1
    
    print(f"Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
