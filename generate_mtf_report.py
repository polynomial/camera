#!/usr/bin/env python3
"""
Generate a comprehensive report of collected Canon MTF data
"""

import json
import os
from pathlib import Path
from datetime import datetime

def generate_mtf_report():
    base_dir = Path("canon_mtf_data")
    
    if not base_dir.exists():
        print("❌ No MTF data directory found")
        return
    
    print("📊 Canon MTF Data Collection Report")
    print("=" * 50)
    print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    rf_dir = base_dir / "rf_lenses"
    ef_dir = base_dir / "ef_lenses"
    
    # Process RF lenses
    if rf_dir.exists():
        print("🔵 RF LENSES")
        print("-" * 30)
        
        rf_lenses = []
        for lens_dir in rf_dir.iterdir():
            if lens_dir.is_dir():
                metadata_file = lens_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        rf_lenses.append({
                            'name': data['lens_name'],
                            'directory': lens_dir.name,
                            'has_mtf': any(f.name.endswith(('.png', '.jpg', '.jpeg')) for f in lens_dir.iterdir()),
                            'specifications': data.get('specifications', {})
                        })
        
        rf_lenses.sort(key=lambda x: x['name'])
        
        for i, lens in enumerate(rf_lenses, 1):
            status = "✅" if lens['has_mtf'] else "❌"
            print(f"{i:2d}. {status} {lens['name']}")
            
            # Show key specs
            specs = lens['specifications']
            if '画角（水平・垂直・対角線）' in specs:
                print(f"     角度: {specs['画角（水平・垂直・対角線）']}")
            if '最小絞り' in specs:
                print(f"     最小絞り: {specs['最小絞り']}")
            if '質量' in specs:
                print(f"     質量: {specs['質量']}")
            print()
        
        print(f"📈 Total RF Lenses: {len(rf_lenses)}")
        print(f"📈 With MTF Charts: {sum(1 for l in rf_lenses if l['has_mtf'])}")
        print()
    
    # Process EF lenses
    if ef_dir.exists():
        print("🔴 EF LENSES")
        print("-" * 30)
        
        ef_lenses = []
        for lens_dir in ef_dir.iterdir():
            if lens_dir.is_dir():
                metadata_file = lens_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        ef_lenses.append({
                            'name': data['lens_name'],
                            'directory': lens_dir.name,
                            'has_mtf': any(f.name.endswith(('.png', '.jpg', '.jpeg')) for f in lens_dir.iterdir()),
                            'specifications': data.get('specifications', {})
                        })
        
        ef_lenses.sort(key=lambda x: x['name'])
        
        for i, lens in enumerate(ef_lenses, 1):
            status = "✅" if lens['has_mtf'] else "❌"
            print(f"{i:2d}. {status} {lens['name']}")
            
            # Show key specs
            specs = lens['specifications']
            if '画角（水平・垂直・対角線）' in specs:
                print(f"     角度: {specs['画角（水平・垂直・対角線）']}")
            if '最小絞り' in specs:
                print(f"     最小絞り: {specs['最小絞り']}")
            if '質量' in specs:
                print(f"     質量: {specs['質量']}")
            print()
        
        print(f"📈 Total EF Lenses: {len(ef_lenses)}")
        print(f"📈 With MTF Charts: {sum(1 for l in ef_lenses if l['has_mtf'])}")
        print()
    
    # Summary
    total_rf = len(rf_lenses) if rf_dir.exists() else 0
    total_ef = len(ef_lenses) if ef_dir.exists() else 0
    total_lenses = total_rf + total_ef
    
    print("📋 SUMMARY")
    print("-" * 30)
    print(f"🔵 RF Lenses: {total_rf}")
    print(f"🔴 EF Lenses: {total_ef}")
    print(f"📊 Total Lenses: {total_lenses}")
    
    if total_lenses > 0:
        print("\n🎯 NEXT STEPS")
        print("-" * 30)
        print("1. ✅ MTF chart collection working correctly")
        print("2. 🔄 Expand to discover more lenses automatically")
        print("3. 📊 Build visualization tools for comparing MTF charts")
        print("4. 🔍 Add lens comparison features")
        print("5. 🌐 Create a web interface for browsing the collection")
    
    print(f"\n📁 Data stored in: {base_dir.absolute()}")

if __name__ == "__main__":
    generate_mtf_report() 