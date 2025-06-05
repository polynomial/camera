# Photography Automation Tools

A collection of scripts and utilities for automating photography workflows with Canon R3 and Google Photos upload via Android.

## Quick Start

```bash
# Import photos from SD card
./photo-upload --import

# Upload HIF files to Google Photos
./photo-upload ~/Pictures/canon_photos

# Upload pre-existing JPEG files
./photo-upload --jpeg ~/Pictures/prepared_jpgs

# Get help
./photo-upload --help

# Check setup
./photo-upload --check
```

## Overview

This repository contains tools to:
- Process HIF (HEIF) files from Canon R3 camera
- Convert HIF files to Android-compatible formats
- Automatically upload processed images to Google Photos via ADB and Android device
- Handle all dependencies automatically via nix-shell

## Main Features

### Simple Command-Line Interface

The `photo-upload` script handles everything automatically:

```bash
# Basic usage
./photo-upload <directory>

# Convert with custom quality
./photo-upload --quality 95 <directory>

# Convert single file
./photo-upload --single input.HIF output.jpg

# Dry run to preview actions
./photo-upload --dry-run <directory>
```

### Automatic Dependency Management

All dependencies are handled automatically through nix-shell:
- ImageMagick with HEIF support
- No manual installation required
- Consistent environment across systems

## Prerequisites

- macOS (tested on Darwin 24.5.0)
- Nix package manager
- Android device with USB debugging enabled
- Local ADB binary (included in bin/)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd camera
```

2. Ensure scripts are executable:
```bash
chmod +x photo-upload
chmod +x bin/*.sh
```

3. Connect your Android device:
   - Enable Developer Options (tap Build Number 7 times)
   - Enable USB Debugging
   - Connect via USB and authorize the connection

4. Test the setup:
```bash
./photo-upload --check
```

## Usage Examples

### Upload Directory of HIF Files
```bash
./photo-upload ~/Pictures/processed_hif
```

### Convert with Custom Quality
```bash
# Use 95% quality instead of default 100%
./photo-upload --quality 95 ~/Pictures/photos
```

### Convert Single File
```bash
./photo-upload --single DSC_0001.HIF vacation.jpg
```

### Preview Without Processing
```bash
./photo-upload --dry-run ~/Pictures/test
```

### Upload Pre-existing JPEG Files
```bash
# For testing with other cameras or pre-processed JPEGs
./photo-upload --jpeg ~/Pictures/camera_jpgs
```

This is useful when:
- Testing with cameras that output JPEG directly
- You've already processed images elsewhere
- You have a batch of JPEGs ready for Google Photos

### Import Photos from SD Card
```bash
# Automatically find and import photos from SD card
./photo-upload --import
```

This feature:
- Automatically detects SD cards in /Volumes
- Finds all photo files (JPG, HEIC, HIF, CR3, RAW, DNG)
- Organizes by date range (first_date_last_date)
- Shows progress and summary (size, count, date range)
- Optionally unmounts SD card when done

## Workflow

1. **Process RAW files in Darktable** → Export as HIF
2. **Run photo-upload** → Automatically converts and uploads
3. **Google Photos syncs** → Files appear in your photo library

The tool will:
1. Create a temporary upload directory on the Android device
2. Convert HIF files to JPEG format (100% quality by default)
3. Copy converted files to the Android device
4. Move files to DCIM/Camera for Google Photos sync
5. Clean up temporary files

## Command-Line Options

```
Options:
  -h, --help         Show help message
  -v, --version      Show version information
  -c, --check        Run setup check only
  -i, --import       Import photos from SD card
  -r, --resume       Resume interrupted upload
  -j, --jpeg         Upload pre-existing JPEG files (no conversion)
  -s, --single       Convert a single HIF file to JPEG
  -q, --quality      JPEG quality 1-100 (default: 100)
  -k, --keep-temp    Keep temporary files
  -d, --dry-run      Preview actions without executing
```

## Directory Structure

```
.
├── photo-upload      # Main wrapper script (use this!)
├── shell.nix        # Nix environment configuration
├── README.md        # This file
├── docs/            # Documentation
│   └── workflow.md  # Detailed workflow documentation
├── bin/             # Implementation scripts
│   ├── adb                  # Android Debug Bridge binary
│   ├── upload_to_android.sh # Main upload script
│   ├── upload_jpgs.sh       # JPEG-only upload script
│   ├── import_from_sdcard.sh   # SD card import script
│   ├── convert_hif.sh       # HIF conversion utility
│   ├── resume_upload.sh     # Resume interrupted uploads
│   └── check_setup.sh       # Setup verification
└── temp/            # Temporary files (gitignored)
```

## Troubleshooting

### No Android Device Connected
- Ensure USB debugging is enabled
- Try different USB cables/ports
- Run: `./bin/adb kill-server && ./bin/adb start-server`

### Conversion Issues
- The tool automatically handles ImageMagick via nix-shell
- Check disk space for temporary files

### Permission Denied
- Ensure scripts are executable: `chmod +x photo-upload`
- Check Android storage permissions

## Advanced Usage

For detailed workflow documentation and advanced configurations, see:
- [docs/workflow.md](docs/workflow.md) - Complete workflow guide
- Run `./photo-upload --help` for all options

## Contributing

Feel free to submit issues or pull requests for improvements.

## License

MIT License - See LICENSE file for details