#!/usr/bin/env python3
"""
Comprehensive Canon Lens Discovery System
Automatically discovers all Canon lenses from official Canon Japan pages
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
from urllib.parse import urljoin, urlparse
from pathlib import Path
from canon_mtf_scraper import CanonMTFScraper

class ComprehensiveLensDiscovery:
    def __init__(self):
        self.base_url = "https://personal.canon.jp"
        self.scraper = CanonMTFScraper()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Canon lens discovery URLs
        self.discovery_urls = [
            "https://personal.canon.jp/product/camera/rf",  # RF lenses
            "https://personal.canon.jp/product/camera/ef",  # EF lenses
            "https://personal.canon.jp/product/camera/ef-s", # EF-S lenses  
        ]
        
        # Also try to discover from the camera museum
        self.museum_urls = [
            "https://global.canon/en/c-museum/lens.html?s=rf",
            "https://global.canon/en/c-museum/lens.html?s=ef",
        ]
        
        self.discovered_lenses = []
        
    def get_page(self, url):
        """Get a page with error handling and rate limiting."""
        try:
            time.sleep(1)  # Rate limiting
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def discover_from_main_pages(self):
        """Discover lenses from main Canon lens pages."""
        print("🔍 Discovering lenses from Canon Japan main pages...")
        
        for base_url in self.discovery_urls:
            print(f"\n📍 Checking: {base_url}")
            
            response = self.get_page(base_url)
            if not response:
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for lens links in various patterns
            lens_links = set()
            
            # Pattern 1: Links with "商品詳細" (product details)
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text().strip()
                
                if href and ('商品詳細' in text or 'spec' in href):
                    full_url = urljoin(base_url, href)
                    if '/product/camera/' in full_url:
                        lens_links.add(full_url)
            
            # Pattern 2: Direct spec page links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and href.endswith('/spec'):
                    full_url = urljoin(base_url, href)
                    lens_links.add(full_url)
            
            # Pattern 3: Links containing lens model names
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and re.search(r'(rf|ef|ef-s)\d+', href, re.IGNORECASE):
                    full_url = urljoin(base_url, href)
                    if '/product/camera/' in full_url:
                        # Try to construct spec URL
                        if not full_url.endswith('/spec'):
                            spec_url = full_url.rstrip('/') + '/spec'
                            lens_links.add(spec_url)
                        else:
                            lens_links.add(full_url)
            
            print(f"✅ Found {len(lens_links)} potential lens URLs from {base_url}")
            for url in sorted(lens_links):
                print(f"   🔗 {url}")
            
            # Test each discovered URL
            for url in lens_links:
                self.test_and_add_lens(url)
    
    def discover_from_museum(self):
        """Discover lens names from Canon Museum to build comprehensive list."""
        print("\n🏛️ Discovering lenses from Canon Camera Museum...")
        
        for museum_url in self.museum_urls:
            print(f"\n📍 Checking: {museum_url}")
            
            response = self.get_page(museum_url)
            if not response:
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract lens names from museum
            lens_names = []
            for element in soup.find_all(['h3', 'h4', 'p', 'div']):
                text = element.get_text().strip()
                # Look for lens patterns like "RF24-70mm F2.8 L IS USM" or "EF50mm F1.8 STM"
                if re.search(r'(RF|EF|EF-S)[0-9-]+mm\s+F[0-9.-]+', text):
                    lens_names.append(text)
            
            print(f"✅ Found {len(lens_names)} lens names from museum")
            
            # Try to construct Canon Japan URLs for these lenses
            for lens_name in lens_names:
                self.construct_spec_url_from_name(lens_name)
    
    def construct_spec_url_from_name(self, lens_name):
        """Try to construct Canon Japan spec URL from lens name."""
        # Clean up the lens name
        clean_name = lens_name.strip()
        
        # Extract key parts
        mount_match = re.search(r'(RF|EF|EF-S)', clean_name)
        if not mount_match:
            return
            
        mount = mount_match.group(1).lower()
        
        # Try various URL patterns based on the lens name
        patterns = [
            lambda name: self.name_to_url_pattern(name, mount),
        ]
        
        for pattern in patterns:
            url = pattern(clean_name)
            if url:
                print(f"🔍 Testing constructed URL: {url}")
                self.test_and_add_lens(url)
    
    def name_to_url_pattern(self, lens_name, mount):
        """Convert lens name to Canon Japan URL pattern."""
        # Extract focal length and aperture
        focal_match = re.search(r'([0-9-]+)mm', lens_name)
        aperture_match = re.search(r'F([0-9.-]+)', lens_name)
        
        if not focal_match or not aperture_match:
            return None
            
        focal = focal_match.group(1)
        aperture = aperture_match.group(1)
        
        # Convert to URL format
        # Examples:
        # RF24-70mm F2.8 L IS USM -> rf24-70-f28l-is-usm
        # EF50mm F1.8 STM -> ef50-f18-stm
        
        url_focal = focal.replace('-', '-')
        url_aperture = aperture.replace('.', '')
        
        # Build URL components
        url_parts = [mount, url_focal, f'f{url_aperture}']
        
        # Add L designation if present
        if ' L ' in lens_name:
            url_parts.append('l')
        
        # Add IS if present
        if ' IS ' in lens_name:
            url_parts.append('is')
        
        # Add motor type
        if ' USM' in lens_name:
            url_parts.append('usm')
        elif ' STM' in lens_name:
            url_parts.append('stm')
        
        # Add macro if present
        if 'MACRO' in lens_name.upper():
            url_parts.append('macro')
        
        url_name = '-'.join(url_parts)
        
        # Construct full URL
        if mount == 'rf':
            base_path = '/product/camera/rf'
        elif mount == 'ef-s':
            base_path = '/product/camera/ef-s'
        else:
            base_path = '/product/camera/ef'
            
        return f"{self.base_url}{base_path}/{url_name}/spec"
    
    def discover_by_brute_force_patterns(self):
        """Discover lenses by trying common URL patterns."""
        print("\n🔍 Discovering lenses by testing common patterns...")
        
        # Common Canon lens patterns
        patterns = [
            # RF lenses
            ("rf", [
                "rf14-35-f4l-is-usm",
                "rf24-50-f45-63-is-stm", 
                "rf24-105-f28l-is-usm-z",
                "rf28-f28-stm",
                "rf100-300-f28-l-is-usm",
                "rf135-f18-l-is-usm",
                "rf200-800-f63-9-is-usm",
                "rf24-f18-macro-is-stm",
                "rf15-30-f45-63-is-stm",
                "rf-s10-18-f45-63-is-stm",
                "rf-s18-45-f45-63-is-stm",
                "rf-s18-150-f35-63-is-stm",
                "rf-s55-210-f5-71-is-stm",
                "rf10-20-f4-l-is-stm",
                "rf100-400-f56-8-is-usm",
                "rf600-f11-is-stm",
                "rf800-f11-is-stm",
                "rf400-f28-l-is-usm",
                "rf600-f4-l-is-usm",
                "rf800-f56-l-is-usm",
                "rf1200-f8-l-is-usm",
                "rf50-f18-stm",
                "rf85-f2-macro-is-stm",
                "rf70-200-f4-l-is-usm",
                "rf24-105-f4-71-is-stm",
                "rf24-240-f4-63-is-usm",
            ]),
            # EF lenses
            ("ef", [
                "ef11-24-f4l-usm",
                "ef24-70-f4l-is-usm",
                "ef35-f14l-ii-usm",
                "ef35-f2-is-usm",
                "ef40-f28-stm",
                "ef85-f14l-is-usm",
                "ef200-f2l-is-usm",
                "ef300-f28l-is-ii-usm",
                "ef400-f28l-is-ii-usm",
                "ef500-f4l-is-ii-usm",
                "ef600-f4l-is-ii-usm",
                "ef800-f56l-is-usm",
                "ef200-400-f4l-is-usm-extender-14x",
                "ef8-15-f4l-fisheye-usm",
                "ef24-f28-is-usm",
                "ef28-f28-is-usm",
                "ef24-f14l-ii-usm",
                "ef14-f28l-ii-usm",
                "ef70-200-f4l-is-ii-usm",
                "ts-e135-f4l-macro",
                "ts-e90-f28l-macro",
                "ts-e50-f28l-macro",
                "ef85-f12l-ii-usm",
                "ef50-f12l-usm",
                "ef16-35-f4l-is-usm",
                "ef24-105-f35-56-is-stm",
                "ef400-f4-do-is-ii-usm",
                "ef70-300-f4-56l-is-usm",
            ]),
            # EF-S lenses
            ("ef-s", [
                "ef-s10-18-f45-56-is-stm",
                "ef-s15-85-f35-56-is-usm",
                "ef-s17-55-f28-is-usm",
                "ef-s18-55-f35-56-is-stm",
                "ef-s18-55-f4-56-is-stm", 
                "ef-s18-135-f35-56-is-stm",
                "ef-s18-135-f35-56-is-usm",
                "ef-s18-200-f35-56-is",
                "ef-s55-250-f4-56-is-stm",
                "ef-s55-250-f4-56-is-ii",
                "ef-s60-f28-macro-usm",
                "ef-s35-f28-macro-is-stm",
                "ef-s24-f28-stm",
            ]),
        ]
        
        for mount, lens_patterns in patterns:
            print(f"\n📍 Testing {mount.upper()} lens patterns...")
            base_path = f"/product/camera/{mount}"
            
            for pattern in lens_patterns:
                url = f"{self.base_url}{base_path}/{pattern}/spec"
                print(f"🔍 Testing: {url}")
                self.test_and_add_lens(url)
    
    def test_and_add_lens(self, url):
        """Test if a URL is a valid lens spec page and add to collection."""
        response = self.get_page(url)
        if not response:
            return False
            
        # Check if it's a valid lens spec page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for lens indicators
        has_lens_content = (
            soup.find('h1') and 
            ('mm' in soup.get_text() or 'F' in soup.get_text()) and
            ('仕様' in soup.get_text() or 'spec' in url)
        )
        
        if has_lens_content:
            if url not in [lens['url'] for lens in self.discovered_lenses]:
                lens_data = self.scraper.parse_lens_spec_page(url)
                if lens_data and lens_data['lens_name']:
                    self.discovered_lenses.append({
                        'url': url,
                        'name': lens_data['lens_name'],
                        'mount': self.get_mount_from_url(url),
                        'mtf_available': bool(lens_data.get('mtf_image_url')),
                        'construction_available': bool(lens_data.get('construction_image_url')),
                        'spec_images': len(lens_data.get('all_spec_images', [])),
                        'data': lens_data
                    })
                    print(f"✅ Added: {lens_data['lens_name']}")
                    return True
        
        return False
    
    def get_mount_from_url(self, url):
        """Extract mount type from URL."""
        if '/rf/' in url:
            return 'RF'
        elif '/ef-s/' in url:
            return 'EF-S'
        elif '/ef/' in url:
            return 'EF'
        return 'Unknown'
    
    def run_comprehensive_discovery(self):
        """Run complete lens discovery process."""
        print("🚀 Starting comprehensive Canon lens discovery...")
        
        # Method 1: Main Canon Japan lens pages
        self.discover_from_main_pages()
        
        # Method 2: Canon Museum discovery
        self.discover_from_museum()
        
        # Method 3: Brute force common patterns
        self.discover_by_brute_force_patterns()
        
        # Summary
        print(f"\n📊 DISCOVERY COMPLETE!")
        print(f"🎯 Total lenses discovered: {len(self.discovered_lenses)}")
        
        # Group by mount
        by_mount = {}
        for lens in self.discovered_lenses:
            mount = lens['mount']
            if mount not in by_mount:
                by_mount[mount] = []
            by_mount[mount].append(lens)
        
        for mount, lenses in by_mount.items():
            print(f"📍 {mount}: {len(lenses)} lenses")
        
        # Count with MTF and construction
        with_mtf = sum(1 for lens in self.discovered_lenses if lens['mtf_available'])
        with_construction = sum(1 for lens in self.discovered_lenses if lens['construction_available'])
        
        print(f"📈 MTF charts available: {with_mtf}")
        print(f"🔧 Construction diagrams available: {with_construction}")
        
        # Save discovery results
        self.save_discovery_results()
        
        return self.discovered_lenses
    
    def save_discovery_results(self):
        """Save discovery results to file."""
        results = {
            'total_discovered': len(self.discovered_lenses),
            'by_mount': {},
            'lenses': []
        }
        
        # Group by mount for summary
        for lens in self.discovered_lenses:
            mount = lens['mount']
            if mount not in results['by_mount']:
                results['by_mount'][mount] = 0
            results['by_mount'][mount] += 1
            
            # Add lens info (without full data to keep file size manageable)
            results['lenses'].append({
                'name': lens['name'],
                'mount': lens['mount'],
                'url': lens['url'],
                'mtf_available': lens['mtf_available'],
                'construction_available': lens['construction_available'],
                'spec_images': lens['spec_images']
            })
        
        # Save to file
        with open('comprehensive_lens_discovery_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Discovery results saved to: comprehensive_lens_discovery_results.json")

if __name__ == "__main__":
    discovery = ComprehensiveLensDiscovery()
    discovered_lenses = discovery.run_comprehensive_discovery()
    
    print(f"\n🎉 Ready to collect {len(discovered_lenses)} lenses!")
    print("Run the collection with the discovered URLs to build complete database.") 