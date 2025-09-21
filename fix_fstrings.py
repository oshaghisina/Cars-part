#!/usr/bin/env python3
"""Fix f-string syntax errors in Python files."""

import re
import os
import glob

def fix_fstring_syntax(content):
    """Fix malformed f-strings with unmatched braces."""
    # Pattern to match f-strings with unmatched braces across lines
    pattern = r'f"([^"]*)\{\s*\n\s*([^}]+)\s*\}"'
    
    def replacement(match):
        prefix = match.group(1)
        content = match.group(2).strip()
        return f'f"{prefix}{{{content}}}"'
    
    return re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

def fix_file(filepath):
    """Fix f-string syntax in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        content = fix_fstring_syntax(content)
        
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
