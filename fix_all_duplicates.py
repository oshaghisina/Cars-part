#!/usr/bin/env python3
"""
Fix all duplicate class attributes in Vue files
"""

import os
import re
import glob

def fix_duplicate_classes_in_file(file_path):
    """Fix duplicate class attributes in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix duplicate font-persian classes
        content = re.sub(r'font-persian font-persian', 'font-persian', content)
        
        # Fix duplicate font-persian-bold classes
        content = re.sub(r'font-persian-bold font-persian-bold', 'font-persian-bold', content)
        
        # Fix duplicate text-rtl classes
        content = re.sub(r'text-rtl text-rtl', 'text-rtl', content)
        
        # Fix duplicate text-ltr classes
        content = re.sub(r'text-ltr text-ltr', 'text-ltr', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed duplicates in {file_path}")
            return True
        else:
            print(f"ℹ️  No duplicates found in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Fix all Vue files in the project"""
    vue_files = glob.glob('app/frontend/web/src/**/*.vue', recursive=True)
    
    print(f"🔍 Found {len(vue_files)} Vue files to check...")
    
    fixed_count = 0
    for file_path in vue_files:
        if fix_duplicate_classes_in_file(file_path):
            fixed_count += 1
    
    print(f"\n🎯 Summary: Fixed duplicates in {fixed_count} files")

if __name__ == "__main__":
    main()
