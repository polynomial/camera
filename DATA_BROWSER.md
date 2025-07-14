# 📊 Canon MTF Collection - Data Browser & Navigation Hub

*Your comprehensive guide to browsing, exploring, and analyzing the Canon lens optical database*

## 🚀 Quick Start - Interactive Viewers

### 🖥️ **Web Viewers** (Click to Open)
| Viewer | Description | Features |
|--------|-------------|----------|
| **[📊 Enhanced MTF Viewer](canon_enhanced_mtf_viewer.html)** | **Primary Interface** - Advanced lens browser | 🔍 Filter by mount/type, 🖼️ Gallery view, 📱 Mobile-responsive |
| **[📈 Classic MTF Viewer](canon_mtf_viewer.html)** | Original simple viewer | 📋 Basic lens listing, 🖼️ Image display |

### 🎯 **Recommended**: Use the **Enhanced MTF Viewer** for the best browsing experience!

---

## 📂 Browse Lens Data by Mount

### 🔵 **RF Lenses** (Full-Frame Mirrorless) - [Browse Directory](canon_mtf_data/rf_lenses/)
**Coverage**: 47/49 lenses (95.9% complete) | **Examples**:
- [RF24-70mm F2.8L IS USM](canon_mtf_data/rf_lenses/RF24_70mm_F2.8L_IS_USM/)
- [RF50mm F1.2L USM](canon_mtf_data/rf_lenses/RF50mm_F1.2L_USM/)
- [RF100-500mm F4.5-7.1L IS USM](canon_mtf_data/rf_lenses/RF100_500mm_F4.5_7.1L_IS_USM/)

### 🔴 **EF Lenses** (DSLR) - [Browse Directory](canon_mtf_data/ef_lenses/)
**Coverage**: 17 lenses (active lenses) | **Examples**:
- [EF24-70mm F2.8L II USM](canon_mtf_data/ef_lenses/EF24_70mm_F2.8L_II_USM/)
- [EF70-200mm F2.8L IS III USM](canon_mtf_data/ef_lenses/EF70_200mm_F2.8L_IS_III_USM/)
- [EF100mm F2.8L Macro IS USM](canon_mtf_data/ef_lenses/EF100mm_F2.8Lマクロ_IS_USM/)

### 🟡 **Other/Specialty** - [Browse Directory](canon_mtf_data/other_lenses/)
**Coverage**: Adapters, extenders, specialty lenses | **Examples**:
- Mount adapters (EF-RF)
- Teleconverters and extenders
- Tilt-shift lenses

---

## 🔧 Tools & Scripts

### 📊 **Data Collection Tools**
| Tool | Purpose | Usage |
|------|---------|-------|
| **[canon_mtf_scraper.py](canon_mtf_scraper.py)** | Individual lens scraping | `python canon_mtf_scraper.py` |
| **[comprehensive_lens_discovery.py](comprehensive_lens_discovery.py)** | Automated lens discovery | Smart web crawling |
| **[collect_all_discovered_lenses.py](collect_all_discovered_lenses.py)** | Batch collection | Process all discovered lenses |

### 🖥️ **Viewer Generation**
| Tool | Purpose | Output |
|------|---------|--------|
| **[create_enhanced_mtf_viewer.py](create_enhanced_mtf_viewer.py)** | **Primary viewer generator** | `canon_enhanced_mtf_viewer.html` |
| **[create_mtf_viewer.py](create_mtf_viewer.py)** | Classic viewer generator | `canon_mtf_viewer.html` |

### 🔍 **Analysis Tools**
| Tool | Purpose | Features |
|------|---------|----------|
| **[generate_mtf_report.py](generate_mtf_report.py)** | Statistics and reporting | Collection analysis |
| **[test_known_lenses.py](test_known_lenses.py)** | Validation testing | URL testing |

---

## 📚 Documentation & References

### 📖 **Primary Documentation**
- **[📋 Project Summary](CANON_MTF_COLLECTION_SUMMARY.md)** - Complete project overview
- **[🌐 Japanese Translation Guide](JAPANESE_TRANSLATION_REFERENCE.md)** - Bilingual reference
- **[📘 Main README](README.md)** - Repository overview

### 📊 **Data References**
- **[📈 Discovery Results](comprehensive_lens_discovery_results_clean.json)** - All discovered lenses
- **[📊 Collection Statistics](final_collection_stats.json)** - Current stats
- **[📂 Comprehensive Lens CSV](contrib/Lenses_%20all%20Canon%20SLR%20and%20Rangefinder%20Lenses%20-%20Canon.csv)** - Historical lens reference

---

## 🎯 Quick Navigation by Interest

### 🔎 **I want to...**

#### **Browse Lenses Visually**
→ **[📊 Open Enhanced MTF Viewer](canon_enhanced_mtf_viewer.html)**

#### **See All RF Lenses**
→ **[🔵 RF Lenses Directory](canon_mtf_data/rf_lenses/)**

#### **Find a Specific Lens**
→ **[📊 Use Enhanced Viewer](canon_enhanced_mtf_viewer.html)** with search/filter

#### **Understand Japanese Text**
→ **[🌐 Translation Reference](JAPANESE_TRANSLATION_REFERENCE.md)**

#### **See Project Statistics**
→ **[📋 Collection Summary](CANON_MTF_COLLECTION_SUMMARY.md)**

#### **Add New Lenses**
→ **[🔧 Use Collection Scripts](collect_all_discovered_lenses.py)**

#### **Generate New Viewer**
→ **[⚙️ Run Enhanced Generator](create_enhanced_mtf_viewer.py)**

---

## 📁 Data Structure Guide

### 🗂️ **Lens Directory Structure**
```
canon_mtf_data/
├── rf_lenses/          # RF Mount (Mirrorless)
│   ├── RF24_70mm_F2.8L_IS_USM/
│   │   ├── metadata.json           # Lens information
│   │   ├── mtf_*.png               # MTF charts
│   │   ├── construction_*.png      # Lens diagrams
│   │   └── extra_*.jpg             # Additional images
│   └── ...
├── ef_lenses/          # EF Mount (DSLR)
│   └── (same structure)
└── other_lenses/       # Adapters, specialty
    └── (same structure)
```

### 📄 **Metadata Fields**
Each lens includes:
- `lens_name` - Primary name
- `lens_name_english` - English translation (where applicable)
- `lens_name_japanese` - Original Japanese name (where applicable)
- `url` - Source Canon page
- `mtf_image_url` - MTF chart URL
- `construction_image_url` - Construction diagram URL
- `specifications` - Technical details

---

## 🎨 Features by Viewer

### 📊 **Enhanced MTF Viewer** (Recommended)
- ✅ **Filter by Mount**: RF, EF, Other
- ✅ **Filter by Type**: Complete sets, MTF only, Construction only
- ✅ **Search**: By lens name
- ✅ **Gallery Mode**: Visual grid browsing
- ✅ **List Mode**: Detailed information
- ✅ **Mobile Responsive**: Works on all devices
- ✅ **Lazy Loading**: Fast performance
- ✅ **Bilingual Support**: Japanese/English names

### 📈 **Classic MTF Viewer**
- ✅ **Simple Interface**: Basic lens listing
- ✅ **Image Display**: MTF and construction diagrams
- ✅ **Lightweight**: Fast loading

---

## 🔄 Updating Data

### 🚀 **To Add New Lenses**:
1. **Auto-discovery**: `python comprehensive_lens_discovery.py`
2. **Batch collection**: `python collect_all_discovered_lenses.py`
3. **Regenerate viewer**: `python create_enhanced_mtf_viewer.py`

### 🔧 **To Update Viewers**:
1. **Enhanced viewer**: `python create_enhanced_mtf_viewer.py`
2. **Classic viewer**: `python create_mtf_viewer.py`

---

## 📊 Current Collection Status

### 🎯 **Coverage Statistics**
- **RF Lenses**: 47/49 (95.9% complete)
- **EF Lenses**: 17 active lenses
- **Total Collection**: 79 lenses
- **Success Rate**: 100% on unique lenses
- **Growth**: 4x expansion from original 19 lenses

### 🏆 **Achievements**
- ✅ Nearly complete RF lens coverage
- ✅ Comprehensive MTF and construction data
- ✅ Bilingual support (Japanese/English)
- ✅ Interactive browsing tools
- ✅ Automated collection system
- ✅ Professional documentation

---

## 🎉 Quick Start Guide

### **New to this collection?**
1. **Start here**: [📊 Enhanced MTF Viewer](canon_enhanced_mtf_viewer.html)
2. **Browse RF lenses**: Use the "RF" filter
3. **Search for specific lenses**: Use the search box
4. **Switch to gallery mode**: Click the gallery icon
5. **View lens details**: Click on any lens card

### **Want to contribute?**
1. **Check for new lenses**: Run discovery scripts
2. **Add missing data**: Use collection tools
3. **Improve translations**: Update the reference guide
4. **Enhance viewers**: Modify generator scripts

---

*This Canon MTF collection represents the most comprehensive optical database for Canon lenses, providing both technical analysis data and visual construction diagrams for photographers, engineers, and optical enthusiasts.*

**🔗 Bookmark this page for easy access to all collection resources!** 