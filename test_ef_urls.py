#!/usr/bin/env python3
"""
Test EF lens URL patterns to find the correct format
"""

import requests
from urllib.parse import urljoin

def test_ef_url_patterns():
    base_url = "https://personal.canon.jp/product/camera/ef/"
    
    # Test different URL patterns based on the EF lens listing
    test_patterns = [
        # Current EF lenses from the listing
        "ef16-35-f28l-3/spec",
        "ef16-35-f4l/spec", 
        "ef24-70-f28l-2/spec",
        "ef24-105-f4l-2/spec",
        "ef70-200-f28l-3/spec",
        "ef70-300-f4-56-2/spec",
        "ef100-400-f45-56l-2/spec",
        "ef50-f18-stm/spec",
        "ef100-f28l-macro/spec",
        
        # Try different variations
        "ef50mm-f18-stm/spec",
        "ef50mm-f1.8-stm/spec",
        "ef-50mm-f1.8-stm/spec",
        "ef50-f1.8-stm/spec",
        
        # Try the current available lenses with different formats
        "ef16-35mm-f28l-iii-usm/spec",
        "ef16-35mm-f4l-is-usm/spec",
        "ef24-70mm-f28l-ii-usm/spec",
        "ef24-105mm-f4l-is-ii-usm/spec",
        "ef70-200mm-f28l-is-iii-usm/spec",
        "ef70-300mm-f4-56-is-ii-usm/spec",
        "ef100-400mm-f45-56l-is-ii-usm/spec",
        "ef50mm-f18-stm/spec",
        "ef100mm-f28l-macro-is-usm/spec",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    working_urls = []
    
    for pattern in test_patterns:
        url = urljoin(base_url, pattern)
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ WORKING: {url}")
                working_urls.append(url)
            else:
                print(f"❌ {response.status_code}: {url}")
        except Exception as e:
            print(f"❌ ERROR: {url} - {e}")
    
    print(f"\n📊 Found {len(working_urls)} working URLs:")
    for url in working_urls:
        print(f"  - {url}")
    
    return working_urls

if __name__ == "__main__":
    test_ef_url_patterns() 