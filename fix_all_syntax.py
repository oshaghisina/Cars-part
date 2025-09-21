#!/usr/bin/env python3
"""
Comprehensive syntax error fixer for the entire codebase.
This script will fix all common syntax errors in one pass.
"""

import os
import re
import glob
from typing import List, Tuple

def fix_f_strings(content: str) -> str:
    """Fix all f-string syntax errors."""
    # Fix unterminated f-strings
    content = re.sub(r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"', content)
    content = re.sub(r'f"([^"]*){([^}]*)}([^"]*)"([^"]*)"', r'f"\1{\2}\3\4"', content)
    
    # Fix missing quotes in f-strings
    content = re.sub(r'f"([^"]*){([^}]*)}([^"]*)"([^"]*)"', r'f"\1{\2}\3"', content)
    content = re.sub(r'f([^"]{[^}]*}[^"]*)', r'f"\1"', content)
    
    # Fix specific patterns
    patterns = [
        (r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"'),
        (r'f"([^"]*){([^}]*)}([^"]*)"([^"]*)"', r'f"\1{\2}\3"'),
        (r'detail=f"([^"]*){([^}]*)}([^"]*)")', r'detail=f"\1{\2}\3")'),
        (r'f"([^"]*){([^}]*)}([^"]*)")', r'f"\1{\2}\3")'),
        (r'f([A-Za-z][^"]*{[^}]*}[^"]*)', r'f"\1"'),
        (r'fRow {([^}]*)} already exists', r'f"Row {\1} already exists"'),
        (r'fItem {([^}]*)}: {([^}]*)}', r'f"Item {\1}: {\2}"'),
        (r'f"([^"]*)"([^"]*)"', r'f"\1\2"'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_docstrings(content: str) -> str:
    """Fix all docstring syntax errors."""
    # Fix unterminated docstrings
    content = re.sub(r'"""([^"]*)"([^"]*)"([^"]*)"([^"]*)"([^"]*)"([^"]*)"', r'"""\1\2\3\4\5\6"""', content)
    content = re.sub(r'""([^"]*)"', r'"""\1"""', content)
    content = re.sub(r'"([^"]*)"([^"]*)"([^"]*)"([^"]*)"([^"]*)"([^"]*)"', r'"""\1\2\3\4\5\6"""', content)
    
    # Fix specific patterns
    patterns = [
        (r'^(\s+)([A-Z][^"]*)\."$', r'\1"""\2."""'),
        (r'^(\s+)([A-Z][^"]*)"$', r'\1"""\2"""'),
        (r'^(\s+)"([A-Z][^"]*)"$', r'\1"""\2"""'),
        (r'^(\s+)([A-Z][^"]*)\."""$', r'\1"""\2."""'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    return content

def fix_route_decorators(content: str) -> str:
    """Fix route decorator syntax errors."""
    patterns = [
        (r'@router\.get\(([^"]/[^"]*), ', r'@router.get("\1", '),
        (r'@router\.post\(([^"]/[^"]*), ', r'@router.post("\1", '),
        (r'@router\.put\(([^"]/[^"]*), ', r'@router.put("\1", '),
        (r'@router\.delete\(([^"]/[^"]*), ', r'@router.delete("\1", '),
        (r'@router\.patch\(([^"]/[^"]*), ', r'@router.patch("\1", '),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_query_params(content: str) -> str:
    """Fix Query parameter syntax errors."""
    patterns = [
        (r'Query\(([^"]\w+), ', r'Query("\1", '),
        (r'regex=\^([^"]*)\$\)', r'regex="^\1$")'),
        (r'description=([^"][^,]*),', r'description="\1",'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_string_literals(content: str) -> str:
    """Fix string literal syntax errors."""
    patterns = [
        (r'detail=([^"][^)]*)\)', r'detail="\1")'),
        (r'raise ValueError\(([^"][^)]*)\)', r'raise ValueError("\1")'),
        (r'message=([^"][^,]*),', r'message="\1",'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_file(filepath: str) -> bool:
    """Fix all syntax errors in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all fixes
        content = fix_f_strings(content)
        content = fix_docstrings(content)
        content = fix_route_decorators(content)
        content = fix_query_params(content)
        content = fix_string_literals(content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def main():
    """Fix all Python files in the app directory."""
    python_files = glob.glob('app/**/*.py', recursive=True)
    fixed_count = 0
    
    print(f"🔧 Processing {len(python_files)} Python files...")
    
    for filepath in python_files:
        if fix_file(filepath):
            fixed_count += 1
    
    print(f"\n✅ Fixed {fixed_count} files")
    print("🚀 Running syntax check...")
    
    # Test syntax of all files
    failed_files = []
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                compile(f.read(), filepath, 'exec')
        except SyntaxError as e:
            failed_files.append((filepath, str(e)))
    
    if failed_files:
        print(f"\n❌ {len(failed_files)} files still have syntax errors:")
        for filepath, error in failed_files:
            print(f"  - {filepath}: {error}")
    else:
        print("\n🎉 All files pass syntax check!")

if __name__ == "__main__":
    main()
