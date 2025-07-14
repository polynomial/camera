#!/usr/bin/env python3
"""
Canon MTF Chart Scraper
Collects MTF charts for all Canon lenses from the Japanese Canon website.
"""

import requests
from bs4 import BeautifulSoup
import os
import json
import re
import time
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path

class CanonMTFScraper:
    def __init__(self, base_dir="canon_mtf_data"):
        self.base_url = "https://personal.canon.jp"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.rf_dir = self.base_dir / "rf_lenses"
        self.ef_dir = self.base_dir / "ef_lenses"
        self.rf_dir.mkdir(exist_ok=True)
        self.ef_dir.mkdir(exist_ok=True)
        
        # Headers to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Session for connection reuse
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def get_page(self, url):
        """Get a page with error handling and rate limiting."""
        try:
            time.sleep(1)  # Rate limiting
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def clean_filename(self, filename):
        """Clean filename by removing query parameters and invalid characters."""
        # Remove query parameters
        if '?' in filename:
            filename = filename.split('?')[0]
        
        # Remove invalid characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        filename = re.sub(r'[-\s]+', '_', filename)
        return filename
    
    def extract_lens_name(self, title):
        """Extract clean lens name from page title."""
        # Remove "仕様" prefix and clean up
        lens_name = re.sub(r'^仕様\s*', '', title)
        lens_name = re.sub(r'：.*$', '', lens_name)  # Remove anything after colon
        return lens_name.strip()
    
    def discover_rf_lenses(self):
        """Discover all RF lens URLs from the main RF lens page."""
        rf_main_url = f"{self.base_url}/product/camera/rf/"
        response = self.get_page(rf_main_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        lens_urls = []
        
        # Look for links to individual lens pages
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Match RF lens URLs (e.g., /product/camera/rf/rf16-f28/)
            if re.match(r'/product/camera/rf/rf\d+.*/$', href):
                lens_url = urljoin(rf_main_url, href)
                spec_url = urljoin(lens_url, 'spec')
                lens_urls.append(spec_url)
        
        return list(set(lens_urls))  # Remove duplicates
    
    def discover_ef_lenses(self):
        """Discover all EF lens URLs from the main EF lens page."""
        ef_main_url = f"{self.base_url}/product/camera/ef/"
        response = self.get_page(ef_main_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        lens_urls = []
        
        # Look for links to individual lens pages
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Match EF lens URLs (e.g., /product/camera/ef/ef16-35-f28l/)
            if re.match(r'/product/camera/ef/ef\d+.*/$', href):
                lens_url = urljoin(ef_main_url, href)
                spec_url = urljoin(lens_url, 'spec')
                lens_urls.append(spec_url)
        
        return list(set(lens_urls))  # Remove duplicates
    
    def parse_lens_spec_page(self, url):
        """Parse a lens specification page to extract MTF chart and metadata."""
        response = self.get_page(url)
        if not response:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract lens name from the page
        lens_name = None
        h1_tag = soup.find('h1')
        if h1_tag:
            raw_title = h1_tag.get_text().strip()
            lens_name = self.extract_lens_name(raw_title)
        
        # Find MTF chart image
        mtf_image_url = None
        
        # Look for images with 'mtf' in the src
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and 'mtf' in src.lower():
                mtf_image_url = urljoin(url, src)
                break
        
        # Extract specifications table
        specs = {}
        spec_table = soup.find('table')
        if spec_table:
            for row in spec_table.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    specs[key] = value
        
        return {
            'lens_name': lens_name,
            'url': url,
            'mtf_image_url': mtf_image_url,
            'specifications': specs
        }
    
    def download_image(self, url, filepath):
        """Download an image from URL to filepath."""
        try:
            response = self.get_page(url)
            if response:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"Error downloading image {url}: {e}")
        return False
    
    def save_lens_data(self, lens_data, lens_dir):
        """Save lens data and download MTF chart."""
        if not lens_data or not lens_data['lens_name']:
            return False
        
        # Create directory for this lens
        lens_name = self.clean_filename(lens_data['lens_name'])
        lens_path = lens_dir / lens_name
        lens_path.mkdir(exist_ok=True)
        
        # Save metadata
        metadata_file = lens_path / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(lens_data, f, indent=2, ensure_ascii=False)
        
        # Download MTF chart
        if lens_data['mtf_image_url']:
            # Extract original filename and extension
            url_path = urlparse(lens_data['mtf_image_url']).path
            original_filename = os.path.basename(url_path)
            
            # Clean the filename
            clean_name = self.clean_filename(original_filename)
            if not clean_name:
                clean_name = "mtf_chart.png"
            
            mtf_image_path = lens_path / clean_name
            if self.download_image(lens_data['mtf_image_url'], mtf_image_path):
                print(f"✅ Downloaded MTF chart for {lens_data['lens_name']}")
                return True
            else:
                print(f"❌ Failed to download MTF chart for {lens_data['lens_name']}")
        
        return False
    
    def test_single_lens(self, lens_url):
        """Test the scraper with a single lens."""
        print(f"Testing with lens: {lens_url}")
        
        lens_data = self.parse_lens_spec_page(lens_url)
        if lens_data:
            print(f"Found lens: {lens_data['lens_name']}")
            print(f"MTF image URL: {lens_data['mtf_image_url']}")
            print(f"Specifications: {len(lens_data['specifications'])} items")
            
            # Determine if it's RF or EF lens
            lens_dir = self.rf_dir if '/rf/' in lens_url else self.ef_dir
            
            success = self.save_lens_data(lens_data, lens_dir)
            return success
        else:
            print("Failed to parse lens data")
            return False
    
    def scrape_all_lenses(self, lens_type=None):
        """Scrape all lenses. lens_type can be 'rf', 'ef', or None for both."""
        lens_urls = []
        
        if lens_type is None or lens_type == 'rf':
            print("🔍 Discovering RF lenses...")
            rf_urls = self.discover_rf_lenses()
            lens_urls.extend(rf_urls)
            print(f"Found {len(rf_urls)} RF lenses")
        
        if lens_type is None or lens_type == 'ef':
            print("🔍 Discovering EF lenses...")
            ef_urls = self.discover_ef_lenses()
            lens_urls.extend(ef_urls)
            print(f"Found {len(ef_urls)} EF lenses")
        
        print(f"📋 Total lenses to process: {len(lens_urls)}")
        
        success_count = 0
        for i, url in enumerate(lens_urls, 1):
            print(f"\n[{i}/{len(lens_urls)}] Processing: {url}")
            lens_data = self.parse_lens_spec_page(url)
            
            if lens_data and lens_data['lens_name']:
                lens_dir = self.rf_dir if '/rf/' in url else self.ef_dir
                if self.save_lens_data(lens_data, lens_dir):
                    success_count += 1
                else:
                    print(f"⚠️  Failed to save data for {lens_data['lens_name']}")
            else:
                print(f"⚠️  Failed to parse data from {url}")
        
        print(f"\n🎉 Completed! Successfully processed {success_count}/{len(lens_urls)} lenses")
        return success_count

def main():
    scraper = CanonMTFScraper()
    
    # Test with a single lens first
    print("=== Testing Single Lens ===")
    test_url = "https://personal.canon.jp/product/camera/rf/rf16-f28/spec"
    success = scraper.test_single_lens(test_url)
    
    if success:
        print("\n✅ Single lens test successful!")
        
        # Ask if user wants to continue with full scraping
        print("\n=== Full Scraping ===")
        print("This will discover and download MTF charts for all Canon lenses.")
        print("It may take several minutes...")
        
        # For now, let's just test with a few RF lenses
        print("\n🚀 Starting RF lens discovery and scraping...")
        rf_count = scraper.scrape_all_lenses('rf')
        
        print(f"\n📁 Data saved to: {scraper.base_dir}")
        print(f"📊 Total lenses processed: {rf_count}")
        
    else:
        print("❌ Single lens test failed")

if __name__ == "__main__":
    main() 