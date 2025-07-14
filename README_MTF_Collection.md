# Canon MTF Chart Collection

A comprehensive collection of Canon lens MTF (Modulation Transfer Function) charts scraped from Canon's Japanese website, organized for easy browsing and comparison.

## 🎯 Project Overview

This project systematically collects MTF charts and specifications for Canon lenses, providing a centralized repository for lens performance analysis. MTF charts are crucial for understanding lens sharpness, contrast, and optical performance across the image frame.

## 📊 Current Collection

- **Total Lenses**: 10 Canon RF lenses
- **Data Sources**: Canon Japan Official Website
- **Chart Format**: PNG images with metadata
- **Organization**: Hierarchical directory structure

### Collected RF Lenses

1. ✅ RF15-35mm F2.8 L IS USM
2. ✅ RF16mm F2.8 STM
3. ✅ RF24-70mm F2.8 L IS USM
4. ✅ RF24-105mm F4 L IS USM
5. ✅ RF28-70mm F2 L USM
6. ✅ RF35mm F1.8 MACRO IS STM
7. ✅ RF50mm F1.2 L USM
8. ✅ RF70-200mm F2.8 L IS USM
9. ✅ RF85mm F1.2 L USM
10. ✅ RF100-500mm F4.5-7.1 L IS USM

## 🗂️ Directory Structure

```
canon_mtf_data/
├── rf_lenses/
│   ├── RF16mm_F2.8_STM/
│   │   ├── spec_mtf.png
│   │   └── metadata.json
│   ├── RF35mm_F1.8_MACRO_IS_STM/
│   │   ├── spec_mtf.png
│   │   └── metadata.json
│   └── [other RF lenses...]
└── ef_lenses/
    └── [future EF lens collection]
```

## 🔧 Tools and Scripts

### Core Scripts

1. **`canon_mtf_scraper.py`** - Main scraping engine
   - Extracts MTF charts from Canon Japan website
   - Saves lens specifications and metadata
   - Handles rate limiting and error recovery

2. **`test_known_lenses.py`** - Validation script
   - Tests scraper with known lens URLs
   - Validates data collection accuracy

3. **`generate_mtf_report.py`** - Analysis tool
   - Generates comprehensive collection reports
   - Shows statistics and missing data

4. **`create_mtf_viewer.py`** - Web interface generator
   - Creates HTML viewer for the collection
   - Enables filtering and comparison

### Generated Files

- **`canon_mtf_viewer.html`** - Interactive web viewer
- **`README_MTF_Collection.md`** - This documentation

## 🚀 Usage Instructions

### 1. View the Collection

Open `canon_mtf_viewer.html` in your browser to browse the MTF charts interactively.

### 2. Run the Scraper

```bash
python3 canon_mtf_scraper.py
```

### 3. Generate Reports

```bash
python3 generate_mtf_report.py
```

### 4. Test with Known Lenses

```bash
python3 test_known_lenses.py
```

### 5. Create Web Viewer

```bash
python3 create_mtf_viewer.py
```

## 📈 Data Format

### Metadata Structure (JSON)

```json
{
  "lens_name": "RF50mm F1.2 L USM",
  "url": "https://personal.canon.jp/product/camera/rf/rf50-f12l/spec",
  "mtf_image_url": "https://personal.canon.jp/.../spec-mtf.png",
  "specifications": {
    "画角（水平・垂直・対角線）": "40° ・ 27° ・ 46°",
    "レンズ構成": "9群13枚",
    "絞り羽根枚数": "9枚（円形絞り）",
    "最小絞り": "16",
    "最短撮影距離": "0.4m",
    "最大撮影倍率": "0.19倍",
    "フィルター径": "77mm",
    "最大径×長さ": "約φ89.8×108.2mm",
    "質量": "950g"
  }
}
```

## 🔍 Understanding MTF Charts

MTF charts show lens performance characteristics:

- **Horizontal Axis**: Distance from image center (mm)
- **Vertical Axis**: Contrast/Sharpness (0-1 scale)
- **Solid Lines**: Sagittal (radial) detail
- **Dashed Lines**: Meridional (tangential) detail
- **Thick Lines**: 10 line pairs/mm (coarse detail)
- **Thin Lines**: 30 line pairs/mm (fine detail)

### Reading the Charts

- **Higher values** = Better performance
- **Close solid/dashed lines** = Minimal astigmatism
- **Flat curves** = Consistent performance across frame
- **Wide open vs stopped down** = Aperture impact

## 🎯 Next Steps

### Phase 1: Expansion ✅
- [x] RF lens collection (10 lenses)
- [x] Data validation and cleaning
- [x] Web viewer creation

### Phase 2: Enhancement
- [ ] EF lens collection
- [ ] Automatic lens discovery
- [ ] Advanced comparison tools
- [ ] MTF chart analysis algorithms

### Phase 3: Analysis
- [ ] Performance benchmarking
- [ ] Lens recommendation system
- [ ] Statistical analysis tools
- [ ] Export formats (CSV, JSON)

## 🛠️ Technical Details

### Dependencies

```bash
pip install requests beautifulsoup4
```

### Rate Limiting

- 1-second delays between requests
- Respectful scraping practices
- Error handling and retry logic

### Image Processing

- PNG format preservation
- Metadata extraction
- Filename normalization

## 📚 Educational Purpose

This collection is created for:
- Lens research and analysis
- Photography education
- Optical performance study
- Comparison and evaluation

**Note**: All MTF charts and lens data are © Canon Inc. This collection is for educational and research purposes only.

## 🤝 Contributing

To extend this collection:

1. Add new lens URLs to the scraper
2. Implement EF lens discovery
3. Enhance the web viewer
4. Add analytical tools

## 📝 License

This project is for educational use. All Canon lens data and MTF charts remain property of Canon Inc.

---

*Generated on July 13, 2025*
*Canon MTF Collection - Building Better Lens Analysis Tools* 