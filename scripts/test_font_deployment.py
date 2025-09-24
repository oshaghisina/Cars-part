#!/usr/bin/env python3
"""
Test script to verify Persian font deployment
"""
import requests
import sys
import os

def test_font_files():
    """Test if font files are accessible on the server"""
    
    # Test URLs (update with actual server domain)
    base_url = "https://yourdomain.com"  # Update this with actual domain
    font_files = [
        "/assets/PeydaWeb-Regular-3vmtpM3F.woff2",
        "/assets/PeydaWeb-Bold-tmeconga.woff2",
        "/assets/PeydaWeb-Medium-BzhHtizS.woff2"
    ]
    
    print("🔍 Testing Persian font deployment...")
    print(f"Base URL: {base_url}")
    
    for font_file in font_files:
        url = base_url + font_file
        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'unknown')
                print(f"✅ {font_file} - Status: {response.status_code}, Type: {content_type}")
            else:
                print(f"❌ {font_file} - Status: {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ {font_file} - Error: {e}")
    
    # Test CSS file
    css_url = base_url + "/assets/index-BbOF0VFv.css"
    try:
        response = requests.get(css_url, timeout=10)
        if response.status_code == 200:
            css_content = response.text
            if "Peyda" in css_content:
                print("✅ CSS file contains Peyda font references")
            else:
                print("❌ CSS file missing Peyda font references")
        else:
            print(f"❌ CSS file - Status: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ CSS file - Error: {e}")

if __name__ == "__main__":
    test_font_files()
