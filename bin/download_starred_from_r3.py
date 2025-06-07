#!/usr/bin/env python3
"""
Canon R3 Image Downloader
Downloads images with star rating 1 or higher from Canon R3 camera
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from requests.auth import HTTPDigestAuth

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Camera configuration from environment
CAMERA_IP = os.getenv('CANON_R3_IP', '192.168.1.2')
CAMERA_PORT = int(os.getenv('CANON_R3_PORT', '8080'))
USERNAME = os.getenv('CANON_R3_USERNAME', 'admin')
PASSWORD = os.getenv('CANON_R3_PASSWORD')

if not PASSWORD:
    print("Error: CANON_R3_PASSWORD not set in environment or .env file")
    sys.exit(1)

BASE_URL = f"http://{CAMERA_IP}:{CAMERA_PORT}"

# Default settings
DEFAULT_DOWNLOAD_DIR = "canon_r3_downloads"
REQUEST_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 300
LOGIN_RETRY_COUNT = 3
LOGIN_RETRY_DELAY = 1

# Create session
session = requests.Session()

def login_to_camera():
    """Login to camera using the /brapi/login endpoint with digest auth and retry logic"""
    login_url = urljoin(BASE_URL, "/brapi/login")
    
    print("Logging in to camera...")
    
    # Try multiple times as the connection often drops after first auth attempt
    for attempt in range(LOGIN_RETRY_COUNT):
        try:
            # Create fresh session for each attempt
            global session
            session = requests.Session()
            
            response = session.get(
                login_url,
                auth=HTTPDigestAuth(USERNAME, PASSWORD),
                allow_redirects=False,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 303:
                # Check if we got the session cookie
                if 'brsessionid' in session.cookies:
                    print(f"✓ Successfully logged in (session: {session.cookies['brsessionid']})")
                    return True
                else:
                    # Got redirect but no cookie - might be already logged in
                    location = response.headers.get('Location', '')
                    if 'already_login' in location:
                        print("✓ Already logged in")
                        return True
                    else:
                        print("✗ Login succeeded but no session cookie received")
                        return False
            elif response.status_code == 401:
                print("✗ Authentication failed - check username/password")
                return False
            else:
                print(f"✗ Unexpected status code: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError as e:
            if attempt < LOGIN_RETRY_COUNT - 1:
                print(f"  Connection dropped (attempt {attempt + 1}/{LOGIN_RETRY_COUNT}), retrying...")
                time.sleep(LOGIN_RETRY_DELAY)
                continue
            else:
                print(f"✗ Connection error after {LOGIN_RETRY_COUNT} attempts: {e}")
                return False
                
        except Exception as e:
            print(f"✗ Error logging in to camera: {e}")
            return False
    
    return False

def logout_from_camera():
    """Logout from camera to clear any existing sessions"""
    try:
        logout_url = urljoin(BASE_URL, "/brapi/logout")
        response = session.get(logout_url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 303:
            print("Logged out from camera")
            return True
    except:
        pass
    return False

def get_storage_info():
    """Get available storage media on camera"""
    url = urljoin(BASE_URL, "/ccapi/ver110/contents")
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return data.get('path', [])
        else:
            print(f"Failed to get storage info: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting storage info: {e}")
        return None

def get_directories(storage_path):
    """Get directories in a storage path"""
    url = BASE_URL + storage_path
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return data.get('path', [])
        else:
            print(f"Failed to get directories: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting directories: {e}")
        return None

def get_image_list(directory_path):
    """Get list of images in a directory"""
    url = BASE_URL + directory_path + "?type=all&kind=list"
    all_images = []
    page = 1
    
    while True:
        try:
            page_url = f"{url}&page={page}"
            response = session.get(page_url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                images = data.get('path', [])
                
                if not images:
                    break
                    
                all_images.extend(images)
                page += 1
            else:
                print(f"Failed to get image list: {response.status_code}")
                break
                
        except Exception as e:
            print(f"Error getting image list: {e}")
            break
    
    return all_images

def get_image_info(image_path):
    """Get metadata info for an image"""
    url = BASE_URL + image_path + "?kind=info"
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get image info for {image_path}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting image info: {e}")
        return None

def download_image(image_path, output_path, filesize=None):
    """Download an image from the camera"""
    url = BASE_URL + image_path
    
    # Check if file already exists with correct size
    if os.path.exists(output_path):
        existing_size = os.path.getsize(output_path)
        if filesize and existing_size == filesize:
            print(f"  → Already downloaded (size matches)")
            return True
        else:
            print(f"  → Partial download detected, resuming...")
    
    try:
        # Download with progress
        response = session.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT)
        
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Show progress
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r  → Downloading: {progress:.1f}%", end='', flush=True)
            
            print(f"\r  → Downloaded successfully")
            return True
        else:
            print(f"  → Failed to download: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  → Error downloading: {e}")
        return False

def parse_rating(rating_value):
    """Parse rating value to numeric"""
    if rating_value == "off" or rating_value is None:
        return 0
    try:
        return int(rating_value)
    except:
        return 0

def find_starred_images(min_rating=1):
    """Find all images with rating >= min_rating"""
    starred_images = []
    
    # Get storage devices
    print("\nScanning for images...")
    storage_paths = get_storage_info()
    
    if not storage_paths:
        print("No storage devices found")
        return starred_images
    
    for storage_path in storage_paths:
        storage_name = os.path.basename(storage_path)
        print(f"\nChecking storage: {storage_name}")
        
        # Get directories
        directories = get_directories(storage_path)
        if not directories:
            continue
            
        for directory_path in directories:
            directory_name = os.path.basename(directory_path)
            print(f"  Scanning directory: {directory_name}")
            
            # Get images
            images = get_image_list(directory_path)
            if not images:
                continue
            
            print(f"    Found {len(images)} images")
            
            # Check each image
            starred_count = 0
            for image_path in images:
                image_name = os.path.basename(image_path)
                
                # Get image info
                info = get_image_info(image_path)
                if info:
                    rating = parse_rating(info.get('rating'))
                    
                    if rating >= min_rating:
                        starred_count += 1
                        starred_images.append({
                            'path': image_path,
                            'name': image_name,
                            'rating': rating,
                            'filesize': info.get('filesize'),
                            'date': info.get('lastmodifieddate'),
                            'storage': storage_name,
                            'directory': directory_name
                        })
            
            if starred_count > 0:
                print(f"    → Found {starred_count} starred images")
    
    return starred_images

def download_starred_images(starred_images, output_dir):
    """Download all starred images"""
    if not starred_images:
        print("\nNo starred images to download")
        return
    
    print(f"\nDownloading {len(starred_images)} starred images to {output_dir}")
    
    success_count = 0
    for i, image in enumerate(starred_images, 1):
        # Create output path maintaining camera directory structure
        relative_path = os.path.join(
            image['storage'],
            image['directory'],
            image['name']
        )
        output_path = os.path.join(output_dir, relative_path)
        
        print(f"\n[{i}/{len(starred_images)}] {image['name']} (★{image['rating']})")
        
        if download_image(image['path'], output_path, image['filesize']):
            success_count += 1
    
    print(f"\n✓ Downloaded {success_count}/{len(starred_images)} images successfully")

def print_statistics(starred_images):
    """Print statistics about starred images"""
    if not starred_images:
        return
    
    print("\n" + "="*50)
    print("STATISTICS")
    print("="*50)
    
    # Count by rating
    rating_counts = {}
    total_size = 0
    
    for image in starred_images:
        rating = image['rating']
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
        total_size += image.get('filesize', 0)
    
    print(f"Total starred images: {len(starred_images)}")
    print(f"Total size: {total_size / (1024*1024*1024):.2f} GB")
    
    print("\nBy rating:")
    for rating in sorted(rating_counts.keys()):
        count = rating_counts[rating]
        print(f"  ★{rating}: {count} images")
    
    # By directory
    dir_counts = {}
    for image in starred_images:
        key = f"{image['storage']}/{image['directory']}"
        dir_counts[key] = dir_counts.get(key, 0) + 1
    
    print("\nBy location:")
    for location, count in sorted(dir_counts.items()):
        print(f"  {location}: {count} images")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Download starred images from Canon R3 camera',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                    # List all starred images
  %(prog)s --download                # Download all starred images
  %(prog)s --download --min-rating 2 # Download only 2+ star images
  %(prog)s --stats                   # Show statistics only
        """
    )
    
    parser.add_argument('--list', '-l', action='store_true',
                        help='List starred images without downloading')
    parser.add_argument('--download', '-d', action='store_true',
                        help='Download starred images')
    parser.add_argument('--output-dir', '-o', default=DEFAULT_DOWNLOAD_DIR,
                        help=f'Output directory (default: {DEFAULT_DOWNLOAD_DIR})')
    parser.add_argument('--min-rating', '-r', type=int, default=1,
                        help='Minimum star rating to download (default: 1)')
    parser.add_argument('--stats', '-s', action='store_true',
                        help='Show statistics about starred images')
    
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()
    
    # Print header
    print("Canon R3 Starred Image Downloader")
    print(f"Camera: {CAMERA_IP}:{CAMERA_PORT}")
    print(f"Minimum rating: ★{args.min_rating}")
    print("-" * 50)
    
    # Login to camera
    if not login_to_camera():
        print("\n✗ Failed to authenticate with camera")
        sys.exit(1)
    
    try:
        # Find starred images
        starred_images = find_starred_images(args.min_rating)
        
        if not starred_images:
            print(f"\n✗ No images found with rating ★{args.min_rating} or higher")
            sys.exit(0)
        
        print(f"\n✓ Found {len(starred_images)} starred images")
        
        # List mode
        if args.list:
            print("\nStarred images:")
            for i, image in enumerate(starred_images, 1):
                size_mb = image.get('filesize', 0) / (1024*1024)
                print(f"{i:3d}. {image['name']} (★{image['rating']}, {size_mb:.1f}MB) - {image['storage']}/{image['directory']}")
        
        # Download mode
        if args.download:
            download_starred_images(starred_images, args.output_dir)
        
        # Statistics
        if args.stats or (not args.list and not args.download):
            print_statistics(starred_images)
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    finally:
        # Always try to logout
        logout_from_camera()
    
    print("\nDone!")

if __name__ == "__main__":
    main() 