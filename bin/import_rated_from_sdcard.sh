#!/usr/bin/env nix-shell
#!nix-shell -i bash -p exiftool coreutils findutils

# Simple Rated Photo Import - No Fancy Features
set -e

echo "Canon R3 Rated Photo Import"
echo "============================"

# Get the first rated file's date to create directory name
first_rated_file=""
first_rated_date=""

echo "Scanning for first rated photo to get date..."
for file in /Volumes/EOS_DIGITAL/DCIM/*/023A*.CR3; do
    if [ -f "$file" ]; then
        rating=$(exiftool -Rating -s3 "$file" 2>/dev/null || echo "0")
        if [ "$rating" -gt 0 ] 2>/dev/null; then
            first_rated_file="$file"
            first_rated_date=$(exiftool -CreateDate -s3 "$file" 2>/dev/null || echo "")
            echo "Found first rated photo: $(basename "$file") (★$rating)"
            echo "Date: $first_rated_date"
            break
        fi
    fi
done

if [ -z "$first_rated_file" ]; then
    echo "No rated photos found!"
    exit 1
fi

# Create output directory
date_clean=$(echo "$first_rated_date" | sed 's/[:-]/ /g' | sed 's/+.*$//' | sed 's/-.*$//')
timestamp_ms=$(date -j -f "%Y %m %d %H %M %S" "$date_clean" "+%s000" 2>/dev/null || echo "$(date +%s)000")
output_dir="$HOME/camera/$timestamp_ms"

echo "Output directory: $output_dir"
mkdir -p "$output_dir"

echo ""
echo "Copying all rated photos..."

# Simple loop through all CR3 files
copied=0
skipped=0

for file in /Volumes/EOS_DIGITAL/DCIM/*/023A*.CR3; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        rating=$(exiftool -Rating -s3 "$file" 2>/dev/null || echo "0")
        
        if [ "$rating" -gt 0 ] 2>/dev/null; then
            dest_path="$output_dir/$filename"
            
            if [ -f "$dest_path" ]; then
                echo "EXISTS: $filename (★$rating)"
                skipped=$((skipped + 1))
            else
                echo "COPY: $filename (★$rating)"
                cp "$file" "$dest_path"
                copied=$((copied + 1))
            fi
        fi
    fi
done

echo ""
echo "DONE!"
echo "Copied: $copied files"
echo "Skipped: $skipped files"
echo "Location: $output_dir"

ls -la "$output_dir" | head -10 