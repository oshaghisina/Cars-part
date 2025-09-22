#!/usr/bin/env python3
"""
Fix duplicate class attributes in Track.vue
"""

import re

def fix_duplicate_classes():
    file_path = 'app/frontend/web/src/views/Track.vue'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix duplicate font-persian classes
    content = re.sub(r'font-persian font-persian', 'font-persian', content)
    
    # Fix duplicate font-persian-bold classes
    content = re.sub(r'font-persian-bold font-persian-bold', 'font-persian-bold', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed duplicate class attributes in Track.vue")

if __name__ == "__main__":
    fix_duplicate_classes()
