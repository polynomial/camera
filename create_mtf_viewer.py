#!/usr/bin/env python3
"""
Create a simple HTML viewer for Canon MTF charts
"""

import json
import os
from pathlib import Path
from datetime import datetime

def create_mtf_viewer():
    base_dir = Path("canon_mtf_data")
    
    if not base_dir.exists():
        print("❌ No MTF data directory found")
        return
    
    # Collect all lens data
    all_lenses = []
    
    # RF lenses
    rf_dir = base_dir / "rf_lenses"
    if rf_dir.exists():
        for lens_dir in rf_dir.iterdir():
            if lens_dir.is_dir():
                metadata_file = lens_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Find MTF image
                        mtf_image = None
                        for file in lens_dir.iterdir():
                            if file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                                mtf_image = f"canon_mtf_data/rf_lenses/{lens_dir.name}/{file.name}"
                                break
                        
                        if mtf_image:
                            all_lenses.append({
                                'name': data['lens_name'],
                                'type': 'RF',
                                'image_path': mtf_image,
                                'specifications': data.get('specifications', {}),
                                'url': data.get('url', '')
                            })
    
    # EF lenses (for when we add them later)
    ef_dir = base_dir / "ef_lenses"
    if ef_dir.exists():
        for lens_dir in ef_dir.iterdir():
            if lens_dir.is_dir():
                metadata_file = lens_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Find MTF image
                        mtf_image = None
                        for file in lens_dir.iterdir():
                            if file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                                mtf_image = f"canon_mtf_data/ef_lenses/{lens_dir.name}/{file.name}"
                                break
                        
                        if mtf_image:
                            all_lenses.append({
                                'name': data['lens_name'],
                                'type': 'EF',
                                'image_path': mtf_image,
                                'specifications': data.get('specifications', {}),
                                'url': data.get('url', '')
                            })
    
    # Sort lenses by name
    all_lenses.sort(key=lambda x: x['name'])
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Canon MTF Chart Collection</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #c41e3a;
            margin: 0;
            font-size: 2.5em;
        }}
        
        .header p {{
            color: #666;
            margin: 10px 0 0 0;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat .number {{
            font-size: 2em;
            font-weight: bold;
            color: #c41e3a;
        }}
        
        .stat .label {{
            font-size: 0.9em;
            color: #666;
        }}
        
        .filter-controls {{
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .filter-btn {{
            background: #c41e3a;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            margin: 0 5px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .filter-btn:hover {{
            background: #a01729;
        }}
        
        .filter-btn.active {{
            background: #333;
        }}
        
        .lens-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        
        .lens-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .lens-card:hover {{
            transform: translateY(-5px);
        }}
        
        .lens-type {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .lens-type.rf {{
            background: #007bff;
            color: white;
        }}
        
        .lens-type.ef {{
            background: #28a745;
            color: white;
        }}
        
        .lens-name {{
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }}
        
        .mtf-image {{
            width: 100%;
            height: auto;
            border-radius: 5px;
            margin-bottom: 15px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
        }}
        
        .specifications {{
            font-size: 0.9em;
            color: #666;
        }}
        
        .spec-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            padding: 2px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .spec-label {{
            font-weight: bold;
            min-width: 120px;
        }}
        
        .spec-value {{
            text-align: right;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .lens-grid {{
                grid-template-columns: 1fr;
            }}
            
            .stats {{
                flex-direction: column;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Canon MTF Chart Collection</h1>
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        <div class="stats">
            <div class="stat">
                <div class="number">{len(all_lenses)}</div>
                <div class="label">Total Lenses</div>
            </div>
            <div class="stat">
                <div class="number">{sum(1 for l in all_lenses if l['type'] == 'RF')}</div>
                <div class="label">RF Lenses</div>
            </div>
            <div class="stat">
                <div class="number">{sum(1 for l in all_lenses if l['type'] == 'EF')}</div>
                <div class="label">EF Lenses</div>
            </div>
        </div>
    </div>
    
    <div class="filter-controls">
        <button class="filter-btn active" onclick="filterLenses('all')">All Lenses</button>
        <button class="filter-btn" onclick="filterLenses('rf')">RF Lenses</button>
        <button class="filter-btn" onclick="filterLenses('ef')">EF Lenses</button>
    </div>
    
    <div class="lens-grid" id="lensGrid">
"""
    
    # Add lens cards
    for lens in all_lenses:
        html_content += f"""
        <div class="lens-card" data-type="{lens['type'].lower()}">
            <div class="lens-type {lens['type'].lower()}">{lens['type']}</div>
            <div class="lens-name">{lens['name']}</div>
            <img src="{lens['image_path']}" alt="MTF Chart for {lens['name']}" class="mtf-image">
            <div class="specifications">
"""
        
        # Add key specifications
        specs = lens['specifications']
        for key, value in specs.items():
            if key in ['画角（水平・垂直・対角線）', '最小絞り', '質量', '最短撮影距離', '最大撮影倍率']:
                html_content += f"""
                <div class="spec-row">
                    <span class="spec-label">{key}</span>
                    <span class="spec-value">{value}</span>
                </div>
"""
        
        html_content += """
            </div>
        </div>
"""
    
    # Close HTML
    html_content += f"""
    </div>
    
    <div class="footer">
        <p>MTF charts and lens data © Canon Inc. | Collection generated by Canon MTF Scraper</p>
        <p>For educational and research purposes only</p>
    </div>
    
    <script>
        function filterLenses(type) {{
            const cards = document.querySelectorAll('.lens-card');
            const buttons = document.querySelectorAll('.filter-btn');
            
            // Update button states
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Filter cards
            cards.forEach(card => {{
                if (type === 'all' || card.dataset.type === type) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""
    
    # Write HTML file
    output_file = "canon_mtf_viewer.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Created MTF viewer: {output_file}")
    print(f"📊 Included {len(all_lenses)} lenses")
    print(f"🌐 Open {output_file} in your browser to view the collection")

if __name__ == "__main__":
    create_mtf_viewer() 