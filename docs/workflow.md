# Photography Workflow Documentation

## Overview

This document describes the complete workflow for processing Canon R3 HIF files and uploading them to Google Photos via an Android device.

## Understanding HIF Files

HIF (HEIF) files are Canon's implementation of the High Efficiency Image Format:
- Smaller file sizes compared to JPEG with similar or better quality
- 10-bit color depth support
- Advanced compression using HEVC codec
- Not universally supported across all platforms

## Complete Workflow

### 1. Initial RAW Processing in Darktable

1. Import RAW files from Canon R3 into Darktable
2. Apply your preferred edits (exposure, color grading, etc.)
3. Export as HIF files to maintain quality while reducing file size

### 2. Prepare Files for Upload

```bash
# Create a directory for processed files
mkdir ~/Pictures/processed_hif

# Move or copy your exported HIF files here
cp /path/to/darktable/exports/*.HIF ~/Pictures/processed_hif/
```

### 3. Connect Android Device

1. Connect your Android phone via USB
2. Select "File Transfer" or "MTP" mode on the phone
3. Verify connection:
   ```bash
   adb devices
   ```
   You should see your device listed

### 4. Run the Upload Script

```bash
cd /Users/bsmith/src/camera
./bin/upload_to_android.sh ~/Pictures/processed_hif
```

The script will:
1. Check all prerequisites
2. Count HIF files to process
3. Create temporary directories
4. Convert HIF → JPEG (quality 100%)
5. Push files to Android temp directory
6. Move files to DCIM/Camera
7. Clean up temporary files

### 5. Google Photos Sync

Once files are in `/storage/self/primary/DCIM/Camera/`:
- Google Photos will automatically detect new images
- Sync will begin based on your settings
- Files will be backed up to your Google Photos library

## Advanced Usage

### Custom Conversion Settings

Edit `bin/upload_to_android.sh` to modify:
```bash
JPEG_QUALITY=100  # Default is 100% for maximum quality
```

### Batch Processing Multiple Directories

```bash
# Process multiple directories
for dir in ~/Pictures/batch1 ~/Pictures/batch2; do
    ./bin/upload_to_android.sh "$dir"
done
```

### Converting Individual Files

```bash
# Convert single HIF file
./bin/convert_hif.sh DSC_0001.HIF
# Output: DSC_0001.jpg

# Specify custom output
./bin/convert_hif.sh DSC_0001.HIF vacation_photo.jpg
```

### Handling Interrupted Uploads

The upload script now includes robust resume capabilities:

1. **Automatic Detection**: The script checks file sizes to detect partial uploads
2. **State Tracking**: Progress is saved in `.upload_state` files
3. **Resume Command**: Use `./photo-upload --resume` to continue
4. **No Duplicate Uploads**: Already uploaded files are skipped

Example workflow for interrupted upload:
```bash
# Start upload
./photo-upload ~/Pictures/photos

# If interrupted, simply resume
./photo-upload --resume

# Check what's in the temp directory
ls -la temp/upload_*/

# Manually specify temp directory if needed
./photo-upload --resume temp/upload_20240115_143022
```

## Troubleshooting

### Common Issues

#### Upload Interrupted

If your upload is interrupted (network issues, device disconnection, etc.), the script now handles resuming:

```bash
# Resume the most recent interrupted upload
./photo-upload --resume

# Or resume a specific temp directory
./photo-upload --resume temp/upload_20240115_143022
```

The resume feature:
- Detects already uploaded files by comparing file sizes
- Removes and re-uploads partial files
- Skips files that are already fully uploaded
- Continues where it left off

#### "No Android device connected"
- Ensure USB debugging is enabled
- Try a different USB cable
- Restart ADB: `adb kill-server && adb start-server`

#### "Failed to convert"
- Check ImageMagick HEIF support: `magick -list format | grep HEIF`
- Reinstall ImageMagick: `brew reinstall imagemagick`

#### "Permission denied on Android"
- Grant file access permissions to ADB
- Check Android storage permissions

### Performance Tips

1. **Process in batches**: Don't process thousands of files at once
2. **Check storage**: Ensure sufficient space on both Mac and Android
3. **Use USB 3.0**: Faster transfer speeds for large batches

## File Organization Tips

### Recommended Directory Structure
```
~/Pictures/
├── canon_raw/          # Original CR3 files
├── darktable_export/   # Processed HIF files
├── ready_to_upload/    # Files ready for Android upload
└── uploaded/           # Archive of uploaded files
```

### Naming Convention
Consider renaming files before upload:
```bash
# Example: YYYY-MM-DD_description_####.jpg
2024-01-15_sunset_beach_0001.jpg
```

## Automation Ideas

### Create a Watch Folder
```bash
# Use fswatch to monitor a directory
fswatch -o ~/Pictures/ready_to_upload | xargs -n1 -I{} ./bin/upload_to_android.sh ~/Pictures/ready_to_upload
```

### Schedule Regular Uploads
Add to crontab:
```bash
# Upload every day at 9 PM
0 21 * * * /Users/bsmith/src/camera/bin/upload_to_android.sh ~/Pictures/ready_to_upload
```

## Best Practices

1. **Always backup originals**: Keep CR3 files safe
2. **Test with small batches**: Verify workflow before processing hundreds of files
3. **Monitor Google Photos storage**: Check your quota regularly
4. **Clean up after uploads**: Move processed files to archive

## Additional Resources

- [Canon R3 User Manual](https://www.usa.canon.com/support/p/eos-r3)
- [Darktable Documentation](https://www.darktable.org/usermanual/)
- [ADB Documentation](https://developer.android.com/studio/command-line/adb)
- [ImageMagick HEIF Support](https://imagemagick.org/script/formats.php#supported) 