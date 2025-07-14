#!/usr/bin/env python3
"""
Investigate the actual HTML structure of EF lens pages to find individual lens links
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def investigate_ef_structure():
    ef_main_url = "https://personal.canon.jp/product/camera/ef"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("🔍 Investigating EF lens main page structure...")
    
    try:
        response = requests.get(ef_main_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look specifically for "商品詳細" (product details) links
        print("🔍 Looking for 商品詳細 (product details) links...")
        product_detail_links = []
        
        for link in soup.find_all('a', href=True):
            text = link.get_text().strip()
            if '商品詳細' in text:
                full_url = urljoin(ef_main_url, link['href'])
                product_detail_links.append({
                    'href': link['href'],
                    'full_url': full_url,
                    'text': text
                })
        
        print(f"📊 Found {len(product_detail_links)} 商品詳細 links:")
        for link in product_detail_links:
            print(f"  - {link['text']} -> {link['full_url']}")
        
        # Look for lens names and their associated links
        print("\n🔍 Looking for lens names and their links...")
        
        # Find all headings that contain EF lens names
        lens_headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        ef_lens_sections = []
        
        for heading in lens_headings:
            text = heading.get_text().strip()
            if text.startswith('EF'):
                # Look for links near this heading
                parent = heading.parent
                if parent:
                    nearby_links = parent.find_all('a', href=True)
                    for link in nearby_links:
                        if '商品詳細' in link.get_text():
                            full_url = urljoin(ef_main_url, link['href'])
                            ef_lens_sections.append({
                                'lens_name': text,
                                'detail_url': full_url
                            })
        
        print(f"📊 Found {len(ef_lens_sections)} EF lens sections with detail links:")
        for section in ef_lens_sections:
            print(f"  - {section['lens_name']} -> {section['detail_url']}")
        
        # Test these URLs to see if they lead to spec pages
        print("\n🧪 Testing found URLs...")
        working_urls = []
        
        for section in ef_lens_sections[:5]:  # Test first 5
            try:
                test_response = requests.get(section['detail_url'], headers=headers, timeout=10)
                if test_response.status_code == 200:
                    print(f"✅ WORKING: {section['lens_name']} -> {section['detail_url']}")
                    working_urls.append(section['detail_url'])
                    
                    # Check if there's a /spec URL
                    spec_url = section['detail_url'].rstrip('/') + '/spec'
                    try:
                        spec_response = requests.get(spec_url, headers=headers, timeout=10)
                        if spec_response.status_code == 200:
                            print(f"  ✅ SPEC PAGE: {spec_url}")
                            working_urls.append(spec_url)
                    except:
                        pass
                else:
                    print(f"❌ {test_response.status_code}: {section['lens_name']} -> {section['detail_url']}")
            except Exception as e:
                print(f"❌ ERROR: {section['lens_name']} -> {section['detail_url']}: {e}")
        
        return working_urls
        
    except Exception as e:
        print(f"❌ Error investigating EF structure: {e}")
        return []

if __name__ == "__main__":
    working_urls = investigate_ef_structure()
    if working_urls:
        print(f"\n🎉 Found {len(working_urls)} working URLs to test with the scraper!")
        for url in working_urls:
            print(f"  - {url}") 