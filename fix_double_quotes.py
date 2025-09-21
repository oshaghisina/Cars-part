#!/usr/bin/env python3
"""Fix double quotes in f-strings."""

import re
import os
import glob

def fix_double_quotes(content):
    """Fix double quotes in f-strings."""
    # Fix f-strings with double quotes at the end
    content = re.sub(r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"', content)
    
    # Fix specific patterns
    patterns = [
        (r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"'),
        (r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"'),
        (r'f"([^"]*)"([^"]*)"([^"]*)"', r'f"\1\2\3"'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_file(filepath):
    """Fix double quotes in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Manual fixes for specific patterns
        fixes = [
            ('f"Error getting current user: {e}""', 'f"Error getting current user: {e}"'),
            ('f"Insufficient permissions. Required: {permission}""', 'f"Insufficient permissions. Required: {permission}"'),
            ('f"Insufficient permissions. Required role: {role}""', 'f"Insufficient permissions. Required role: {role}"'),
            ('f"{self.first_name} {self.last_name}"".strip()', 'f"{self.first_name} {self.last_name}".strip()'),
            ('f"Failed to create user {user_data.username}: {e}""', 'f"Failed to create user {user_data.username}: {e}"'),
            ('f"Error creating admin user: {e}""', 'f"Error creating admin user: {e}"'),
            ('f"{part.brand_oem} - {part.oem_code}""', 'f"{part.brand_oem} - {part.oem_code}"'),
            ('f"/parts/{part.id}""', 'f"/parts/{part.id}"'),
            ('f"/vehicles/brands/{brand.id}""', 'f"/vehicles/brands/{brand.id}"'),
        ]
        
        for old, new in fixes:
            content = content.replace(old, new)
        
        # Apply general fixes
        content = fix_double_quotes(content)
        
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
