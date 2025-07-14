#!/usr/bin/env python3
"""
Test script for Canon MTF scraper with known lens URLs
"""

from canon_mtf_scraper import CanonMTFScraper

# Known Canon RF lens URLs for testing
KNOWN_RF_LENSES = [
    "https://personal.canon.jp/product/camera/rf/rf16-f28/spec",
    "https://personal.canon.jp/product/camera/rf/rf35-f18/spec",
    "https://personal.canon.jp/product/camera/rf/rf50-f12l/spec",
    "https://personal.canon.jp/product/camera/rf/rf85-f12l/spec",
    "https://personal.canon.jp/product/camera/rf/rf28-70-f2l/spec",
    "https://personal.canon.jp/product/camera/rf/rf70-200-f28l/spec",
    "https://personal.canon.jp/product/camera/rf/rf100-500-f45-71l/spec",
    "https://personal.canon.jp/product/camera/rf/rf24-105-f4l/spec",
    "https://personal.canon.jp/product/camera/rf/rf15-35-f28l/spec",
    "https://personal.canon.jp/product/camera/rf/rf24-70-f28l/spec",
]

# Known Canon EF lens URLs with corrected pattern
KNOWN_EF_LENSES = [
    "https://personal.canon.jp/product/camera/ef/ef70-200-f28l-iii/spec",
    "https://personal.canon.jp/product/camera/ef/ef24-70-f28l-ii/spec",
    "https://personal.canon.jp/product/camera/ef/ef16-35-f28liii/spec",
    "https://personal.canon.jp/product/camera/ef/ef16-35-f4l-is-usm/spec",
    "https://personal.canon.jp/product/camera/ef/ef24-105-f4lii/spec",
    "https://personal.canon.jp/product/camera/ef/ef70-300-f4-56ii/spec",
    "https://personal.canon.jp/product/camera/ef/ef100-400-f45-56l-ii-usm/spec",
    "https://personal.canon.jp/product/camera/ef/ef50-f18stm/spec",
    "https://personal.canon.jp/product/camera/ef/ef100-f28l/spec",
]

def test_known_lenses():
    scraper = CanonMTFScraper()
    
    print("=== Testing Known RF Lenses ===")
    rf_success = 0
    rf_total = len(KNOWN_RF_LENSES)
    
    for i, lens_url in enumerate(KNOWN_RF_LENSES, 1):
        print(f"\n[{i}/{rf_total}] Testing: {lens_url}")
        
        lens_data = scraper.parse_lens_spec_page(lens_url)
        if lens_data and lens_data['lens_name'] and lens_data['mtf_image_url']:
            print(f"✅ Found: {lens_data['lens_name']}")
            success = scraper.save_lens_data(lens_data, scraper.rf_dir)
            if success:
                rf_success += 1
        else:
            print("❌ Failed to parse lens data")
    
    print(f"\n=== RF Results: {rf_success}/{rf_total} successful ===")
    
    print("\n=== Testing Known EF Lenses ===")
    ef_success = 0
    ef_total = len(KNOWN_EF_LENSES)
    
    for i, lens_url in enumerate(KNOWN_EF_LENSES, 1):
        print(f"\n[{i}/{ef_total}] Testing: {lens_url}")
        
        lens_data = scraper.parse_lens_spec_page(lens_url)
        if lens_data and lens_data['lens_name'] and lens_data['mtf_image_url']:
            print(f"✅ Found: {lens_data['lens_name']}")
            success = scraper.save_lens_data(lens_data, scraper.ef_dir)
            if success:
                ef_success += 1
        else:
            print("❌ Failed to parse lens data")
    
    print(f"\n=== EF Results: {ef_success}/{ef_total} successful ===")
    
    print(f"\n=== Overall Results ===")
    print(f"RF Lenses: {rf_success}/{rf_total}")
    print(f"EF Lenses: {ef_success}/{ef_total}")
    print(f"Total: {rf_success + ef_success}/{rf_total + ef_total}")
    print(f"📁 Data saved to: {scraper.base_dir}")

if __name__ == "__main__":
    test_known_lenses() 