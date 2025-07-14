#!/usr/bin/env python3
"""
Collect all discovered Canon lenses with MTF charts and construction diagrams
"""

import json
import time
from canon_mtf_scraper import CanonMTFScraper
from pathlib import Path

def collect_all_discovered_lenses():
    """Collect all lenses found by the comprehensive discovery."""
    
    # Load discovery results
    results_file = "comprehensive_lens_discovery_results.json"
    if not Path(results_file).exists():
        print(f"❌ Discovery results file not found: {results_file}")
        print("Run comprehensive_lens_discovery.py first!")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        discovery_results = json.load(f)
    
    print(f"🚀 Starting collection of {discovery_results['total_discovered']} discovered lenses")
    print(f"📊 RF: {discovery_results['by_mount'].get('RF', 0)}")
    print(f"📊 EF: {discovery_results['by_mount'].get('EF', 0)}")
    print(f"📊 Unknown: {discovery_results['by_mount'].get('Unknown', 0)}")
    
    # Initialize scraper
    scraper = CanonMTFScraper()
    
    # Collect statistics
    stats = {
        'total_attempted': 0,
        'successful_collections': 0,
        'mtf_charts_collected': 0,
        'construction_diagrams_collected': 0,
        'failed_collections': 0,
        'by_mount': {'RF': 0, 'EF': 0, 'EF-S': 0, 'Unknown': 0}
    }
    
    # Process each discovered lens
    for i, lens_info in enumerate(discovery_results['lenses'], 1):
        print(f"\n📍 [{i}/{len(discovery_results['lenses'])}] Processing: {lens_info['name']}")
        print(f"   🔗 URL: {lens_info['url']}")
        
        stats['total_attempted'] += 1
        
        # Parse the lens spec page
        lens_data = scraper.parse_lens_spec_page(lens_info['url'])
        
        if lens_data and lens_data['lens_name']:
            # Determine lens mount and directory
            mount = lens_info['mount']
            if mount == 'RF':
                lens_dir = scraper.rf_dir
            elif mount in ['EF', 'EF-S']:
                lens_dir = scraper.ef_dir
            else:
                # Create a directory for unknown mounts
                lens_dir = scraper.base_dir / "other_lenses"
                lens_dir.mkdir(exist_ok=True)
            
            # Save lens data and download images
            success = scraper.save_lens_data(lens_data, lens_dir)
            
            if success:
                stats['successful_collections'] += 1
                stats['by_mount'][mount] = stats['by_mount'].get(mount, 0) + 1
                
                # Count image types collected
                if lens_data.get('mtf_image_url'):
                    stats['mtf_charts_collected'] += 1
                if lens_data.get('construction_image_url'):
                    stats['construction_diagrams_collected'] += 1
                
                print(f"   ✅ Success! Collected {lens_data['lens_name']}")
                
                # Show what was collected
                mtf_status = "✅" if lens_data.get('mtf_image_url') else "❌"
                construction_status = "✅" if lens_data.get('construction_image_url') else "❌"
                extra_count = len(lens_data.get('all_spec_images', [])) - 2  # Subtract MTF and construction
                
                print(f"      📊 MTF Chart: {mtf_status}")
                print(f"      🔧 Construction: {construction_status}")
                print(f"      📷 Extra Images: {max(0, extra_count)}")
            else:
                stats['failed_collections'] += 1
                print(f"   ❌ Failed to collect lens data")
        else:
            stats['failed_collections'] += 1
            print(f"   ❌ Failed to parse lens spec page")
        
        # Rate limiting - be respectful to Canon's servers
        time.sleep(2)
        
        # Progress update every 10 lenses
        if i % 10 == 0:
            success_rate = (stats['successful_collections'] / stats['total_attempted']) * 100
            print(f"\n📊 Progress Update:")
            print(f"   🎯 {i}/{len(discovery_results['lenses'])} processed ({i/len(discovery_results['lenses'])*100:.1f}%)")
            print(f"   ✅ {stats['successful_collections']} successful ({success_rate:.1f}%)")
            print(f"   📊 {stats['mtf_charts_collected']} MTF charts")
            print(f"   🔧 {stats['construction_diagrams_collected']} construction diagrams")
    
    # Final statistics
    print(f"\n🎉 COLLECTION COMPLETE!")
    print(f"{'='*50}")
    print(f"📊 Final Statistics:")
    print(f"   🎯 Total Attempted: {stats['total_attempted']}")
    print(f"   ✅ Successful: {stats['successful_collections']}")
    print(f"   ❌ Failed: {stats['failed_collections']}")
    print(f"   📈 Success Rate: {(stats['successful_collections']/stats['total_attempted'])*100:.1f}%")
    print(f"\n📊 Images Collected:")
    print(f"   📊 MTF Charts: {stats['mtf_charts_collected']}")
    print(f"   🔧 Construction Diagrams: {stats['construction_diagrams_collected']}")
    print(f"\n📍 By Mount:")
    for mount, count in stats['by_mount'].items():
        if count > 0:
            print(f"   {mount}: {count} lenses")
    
    # Save collection statistics
    stats_file = "final_collection_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Collection statistics saved to: {stats_file}")
    print(f"🌐 Generate updated HTML viewer with: python3 create_enhanced_mtf_viewer.py")
    
    return stats

if __name__ == "__main__":
    stats = collect_all_discovered_lenses()
    print(f"\n🚀 Ready to view your comprehensive Canon lens collection!")
    print(f"✨ Total unique lenses collected: {stats['successful_collections']}")
    print(f"🎯 This is a {stats['successful_collections']//19 if stats['successful_collections'] > 19 else 1}x increase from the original 19 lenses!") 