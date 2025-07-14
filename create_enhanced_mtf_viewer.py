#!/usr/bin/env python3
"""
Create an enhanced HTML viewer for Canon MTF charts and construction diagrams
"""

import json
import os
from pathlib import Path
from datetime import datetime

def create_enhanced_mtf_viewer():
    base_dir = Path("canon_mtf_data")
    
    if not base_dir.exists():
        print("❌ No MTF data directory found")
        return
    
    # Collect all lens data with both MTF and construction images
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
                        
                        # Find all images in the directory
                        images = {
                            'mtf_chart': None,
                            'construction': None,
                            'extra_images': []
                        }
                        
                        for file in lens_dir.iterdir():
                            if file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                                rel_path = f"canon_mtf_data/rf_lenses/{lens_dir.name}/{file.name}"
                                
                                if file.name.startswith('mtf_'):
                                    images['mtf_chart'] = rel_path
                                elif file.name.startswith('construction_'):
                                    images['construction'] = rel_path
                                elif file.name.startswith('extra_'):
                                    images['extra_images'].append(rel_path)
                        
                        if images['mtf_chart'] or images['construction']:
                            all_lenses.append({
                                'name': data['lens_name'],
                                'type': 'RF',
                                'images': images,
                                'specifications': data.get('specifications', {}),
                                'url': data.get('url', '')
                            })
    
    # EF lenses
    ef_dir = base_dir / "ef_lenses"
    if ef_dir.exists():
        for lens_dir in ef_dir.iterdir():
            if lens_dir.is_dir():
                metadata_file = lens_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Find all images in the directory
                        images = {
                            'mtf_chart': None,
                            'construction': None,
                            'extra_images': []
                        }
                        
                        for file in lens_dir.iterdir():
                            if file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                                rel_path = f"canon_mtf_data/ef_lenses/{lens_dir.name}/{file.name}"
                                
                                if file.name.startswith('mtf_'):
                                    images['mtf_chart'] = rel_path
                                elif file.name.startswith('construction_'):
                                    images['construction'] = rel_path
                                elif file.name.startswith('extra_'):
                                    images['extra_images'].append(rel_path)
                        
                        if images['mtf_chart'] or images['construction']:
                            all_lenses.append({
                                'name': data['lens_name'],
                                'type': 'EF',
                                'images': images,
                                'specifications': data.get('specifications', {}),
                                'url': data.get('url', '')
                            })
    
    # Sort lenses by name
    all_lenses.sort(key=lambda x: x['name'])
    
    # Count available data
    mtf_count = sum(1 for lens in all_lenses if lens['images']['mtf_chart'])
    construction_count = sum(1 for lens in all_lenses if lens['images']['construction'])
    both_count = sum(1 for lens in all_lenses if lens['images']['mtf_chart'] and lens['images']['construction'])
    
    # Generate enhanced HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Canon MTF Charts & Lens Construction Collection</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
            line-height: 1.6;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #c41e3a;
            margin: 0 0 10px 0;
            font-size: 2.8em;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            color: #666;
            font-size: 1.2em;
            margin: 10px 0;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-top: 25px;
        }}
        
        .stat {{
            text-align: center;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }}
        
        .stat .number {{
            font-size: 2.2em;
            font-weight: bold;
            display: block;
        }}
        
        .stat .label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .controls {{
            margin-bottom: 30px;
            text-align: center;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }}
        
        .control-btn {{
            background: #c41e3a;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .control-btn:hover {{
            background: #a01729;
            transform: translateY(-2px);
        }}
        
        .control-btn.active {{
            background: #333;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        
        .view-toggle {{
            background: #667eea;
            margin-left: 20px;
        }}
        
        .view-toggle:hover {{
            background: #5a6fd8;
        }}
        
        .lens-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
        }}
        
        .lens-grid.compact {{
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        }}
        
        .lens-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            overflow: hidden;
        }}
        
        .lens-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        }}
        
        .lens-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .lens-type {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }}
        
        .lens-type.rf {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }}
        
        .lens-type.ef {{
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: white;
        }}
        
        .lens-name {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
            margin: 0;
        }}
        
        .image-section {{
            margin-bottom: 20px;
        }}
        
        .image-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .image-container {{
            text-align: center;
        }}
        
        .image-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
            font-weight: 500;
        }}
        
        .lens-image {{
            width: 100%;
            height: auto;
            max-height: 200px;
            object-fit: contain;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            background: #f8f9fa;
        }}
        
        .no-image {{
            width: 100%;
            height: 150px;
            border: 2px dashed #ccc;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
            font-size: 0.9em;
        }}
        
        .specs-summary {{
            font-size: 0.85em;
            color: #666;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }}
        
        .spec-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            padding: 3px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .spec-label {{
            font-weight: 500;
            color: #555;
        }}
        
        .compact .lens-image {{
            max-height: 120px;
        }}
        
        .compact .image-row {{
            grid-template-columns: 1fr;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 30px;
            color: #666;
            font-size: 0.9em;
            background: white;
            border-radius: 15px;
        }}
        
        @media (max-width: 768px) {{
            .lens-grid {{
                grid-template-columns: 1fr;
            }}
            
            .image-row {{
                grid-template-columns: 1fr;
            }}
            
            .stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔬 Canon MTF & Construction Collection</h1>
        <p class="subtitle">Complete optical analysis with MTF charts and lens construction diagrams</p>
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        <div class="stats">
            <div class="stat">
                <span class="number">{len(all_lenses)}</span>
                <span class="label">Total Lenses</span>
            </div>
            <div class="stat">
                <span class="number">{mtf_count}</span>
                <span class="label">MTF Charts</span>
            </div>
            <div class="stat">
                <span class="number">{construction_count}</span>
                <span class="label">Construction Diagrams</span>
            </div>
            <div class="stat">
                <span class="number">{both_count}</span>
                <span class="label">Complete Sets</span>
            </div>
            <div class="stat">
                <span class="number">{sum(1 for l in all_lenses if l['type'] == 'RF')}</span>
                <span class="label">RF Lenses</span>
            </div>
            <div class="stat">
                <span class="number">{sum(1 for l in all_lenses if l['type'] == 'EF')}</span>
                <span class="label">EF Lenses</span>
            </div>
        </div>
    </div>
    
    <div class="controls">
        <button class="control-btn active" onclick="filterLenses('all')">All Lenses</button>
        <button class="control-btn" onclick="filterLenses('rf')">RF Only</button>
        <button class="control-btn" onclick="filterLenses('ef')">EF Only</button>
        <button class="control-btn" onclick="filterLenses('complete')">Complete Sets</button>
        <button class="control-btn view-toggle" onclick="toggleView()">🔄 Toggle Compact View</button>
    </div>
    
    <div class="lens-grid" id="lensGrid">
"""
    
    # Add lens cards
    for lens in all_lenses:
        mtf_status = "✅" if lens['images']['mtf_chart'] else "❌"
        construction_status = "✅" if lens['images']['construction'] else "❌"
        
        html_content += f"""
        <div class="lens-card" data-type="{lens['type'].lower()}" data-complete="{str(bool(lens['images']['mtf_chart'] and lens['images']['construction'])).lower()}">
            <div class="lens-header">
                <div>
                    <div class="lens-type {lens['type'].lower()}">{lens['type']}</div>
                    <h3 class="lens-name">{lens['name']}</h3>
                </div>
                <div style="text-align: right; font-size: 1.2em;">
                    {mtf_status} {construction_status}
                </div>
            </div>
            
            <div class="image-section">
                <div class="image-row">
                    <div class="image-container">
                        <div class="image-label">📊 MTF Chart</div>
"""
        
        if lens['images']['mtf_chart']:
            mtf_image = lens['images']['mtf_chart']
            html_content += f'<img src="{mtf_image}" alt="MTF Chart" class="lens-image">'
        else:
            html_content += '<div class="no-image">No MTF Chart</div>'
        
        html_content += """
                    </div>
                    <div class="image-container">
                        <div class="image-label">🔧 Construction</div>
"""
        
        if lens['images']['construction']:
            construction_image = lens['images']['construction']
            html_content += f'<img src="{construction_image}" alt="Construction Diagram" class="lens-image">'
        else:
            html_content += '<div class="no-image">No Construction Diagram</div>'
        
        html_content += """
                    </div>
                </div>
            </div>
            
            <div class="specs-summary">
"""
        
        # Add key specifications
        specs = lens['specifications']
        key_specs = ['画角（水平・垂直・対角線）', '最小絞り', '質量', '最短撮影距離', '最大撮影倍率']
        for key in key_specs:
            if key in specs:
                html_content += f"""
                <div class="spec-item">
                    <span class="spec-label">{key}</span>
                    <span>{specs[key]}</span>
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
        <p><strong>🎯 Super Dense Optical Analysis Collection</strong></p>
        <p>MTF charts show lens sharpness across the frame | Construction diagrams reveal optical element arrangement</p>
        <p>Data © Canon Inc. | Collection for educational and research purposes</p>
    </div>
    
    <script>
        let isCompact = false;
        
        function filterLenses(type) {{
            const cards = document.querySelectorAll('.lens-card');
            const buttons = document.querySelectorAll('.control-btn:not(.view-toggle)');
            
            // Update button states
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Filter cards
            cards.forEach(card => {{
                let show = false;
                
                if (type === 'all') {{
                    show = true;
                }} else if (type === 'complete') {{
                    show = card.dataset.complete === 'true';
                }} else {{
                    show = card.dataset.type === type;
                }}
                
                card.style.display = show ? 'block' : 'none';
            }});
        }}
        
        function toggleView() {{
            const grid = document.getElementById('lensGrid');
            const button = document.querySelector('.view-toggle');
            
            isCompact = !isCompact;
            
            if (isCompact) {{
                grid.classList.add('compact');
                button.textContent = '🔄 Normal View';
            }} else {{
                grid.classList.remove('compact');
                button.textContent = '🔄 Compact View';
            }}
        }}
    </script>
</body>
</html>
"""
    
    # Write HTML file
    output_file = "canon_enhanced_mtf_viewer.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Created enhanced MTF viewer: {output_file}")
    print(f"📊 Included {len(all_lenses)} lenses")
    print(f"📈 MTF Charts: {mtf_count}")
    print(f"🔧 Construction Diagrams: {construction_count}")
    print(f"💎 Complete Sets: {both_count}")
    print(f"🌐 Open {output_file} for super dense optical visualization!")

if __name__ == "__main__":
    create_enhanced_mtf_viewer() 