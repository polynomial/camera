#!/usr/bin/env python3
"""
Canon R3 FTP Server with Auto-Upload to Android
Receives CR3 files via FTP, converts to JPEG, and uploads to Android device
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment
FTP_USER = os.getenv('CANON_R3_USERNAME', 'admin')
FTP_PASS = os.getenv('CANON_R3_PASSWORD', '')
FTP_PORT = int(os.getenv('FTP_PORT', '2121'))
FTP_UPLOAD_DIR = os.path.expanduser('~/camera/ftp_uploads')
JPEG_QUALITY = int(os.getenv('JPEG_QUALITY', '95'))

# Ensure upload directory exists
os.makedirs(FTP_UPLOAD_DIR, exist_ok=True)

class CanonUploadHandler(FileSystemEventHandler):
    """Handles new file uploads from Canon R3"""
    
    def __init__(self):
        self.processing = set()
        
    def on_created(self, event):
        if event.is_directory:
            return
            
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        # Only process CR3 files
        if not filename.lower().endswith('.cr3'):
            return
            
        # Avoid processing the same file multiple times
        if filepath in self.processing:
            return
            
        self.processing.add(filepath)
        
        # Wait for file to be fully written
        print(f"\n📸 New upload detected: {filename}")
        self.wait_for_file_complete(filepath)
        
        # Process the file in a separate thread
        thread = threading.Thread(target=self.process_upload, args=(filepath,))
        thread.start()
    
    def wait_for_file_complete(self, filepath, timeout=30):
        """Wait for file to be fully written"""
        last_size = -1
        stable_count = 0
        
        for _ in range(timeout):
            try:
                current_size = os.path.getsize(filepath)
                if current_size == last_size:
                    stable_count += 1
                    if stable_count >= 2:  # File size stable for 2 seconds
                        return True
                else:
                    stable_count = 0
                last_size = current_size
                time.sleep(1)
            except:
                time.sleep(1)
        
        return False
    
    def process_upload(self, cr3_path):
        """Convert CR3 to JPEG and upload to Android"""
        try:
            filename = os.path.basename(cr3_path)
            name_base = os.path.splitext(filename)[0]
            jpeg_filename = f"{name_base}.jpg"
            jpeg_path = os.path.join(os.path.dirname(cr3_path), jpeg_filename)
            
            print(f"  Converting to JPEG ({JPEG_QUALITY}% quality)...")
            
            # Convert CR3 to JPEG using ImageMagick
            cmd = [
                'magick', cr3_path,
                '-quality', str(JPEG_QUALITY),
                jpeg_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"  ❌ Conversion failed: {result.stderr}")
                return
            
            print(f"  ✅ Converted to {jpeg_filename}")
            
            # Upload to Android
            self.upload_to_android(jpeg_path, jpeg_filename)
            
        except Exception as e:
            print(f"  ❌ Error processing {filename}: {e}")
        finally:
            self.processing.discard(cr3_path)
    
    def upload_to_android(self, jpeg_path, filename):
        """Upload JPEG to Android device"""
        try:
            print(f"  📱 Uploading to Android...")
            
            # Check if device is connected
            check_cmd = ['adb', 'devices']
            result = subprocess.run(check_cmd, capture_output=True, text=True)
            
            if 'device' not in result.stdout:
                print(f"  ❌ No Android device connected")
                return
            
            # Create temp directory on Android
            temp_dir = f"/sdcard/Download/camera_upload_{int(time.time())}"
            subprocess.run(['adb', 'shell', 'mkdir', '-p', temp_dir], check=True)
            
            # Push file
            remote_path = f"{temp_dir}/{filename}"
            subprocess.run(['adb', 'push', jpeg_path, remote_path], check=True)
            
            # Move to DCIM/Camera
            final_path = f"/storage/self/primary/DCIM/Camera/{filename}"
            subprocess.run(['adb', 'shell', 'mv', remote_path, final_path], check=True)
            
            # Trigger media scan
            subprocess.run([
                'adb', 'shell', 'am', 'broadcast',
                '-a', 'android.intent.action.MEDIA_SCANNER_SCAN_FILE',
                '-d', f'file://{final_path}'
            ], check=True)
            
            # Clean up temp directory
            subprocess.run(['adb', 'shell', 'rmdir', temp_dir])
            
            print(f"  ✅ Uploaded to Android: {filename}")
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Android upload failed: {e}")
        except Exception as e:
            print(f"  ❌ Upload error: {e}")

def start_ftp_server():
    """Start the FTP server"""
    # Create authorizer and add user
    authorizer = DummyAuthorizer()
    authorizer.add_user(FTP_USER, FTP_PASS, FTP_UPLOAD_DIR, perm='elradfmw')
    
    # Create handler
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "Canon R3 FTP Server Ready"
    
    # Create server
    server = FTPServer(('0.0.0.0', FTP_PORT), handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5
    
    print(f"🚀 FTP Server starting on port {FTP_PORT}")
    print(f"📁 Upload directory: {FTP_UPLOAD_DIR}")
    print(f"👤 Username: {FTP_USER}")
    print(f"🔑 Password: {'*' * len(FTP_PASS)}")
    print(f"📸 JPEG Quality: {JPEG_QUALITY}%")
    print("\nWaiting for Canon R3 uploads...")
    
    # Start file watcher in separate thread
    event_handler = CanonUploadHandler()
    observer = Observer()
    observer.schedule(event_handler, FTP_UPLOAD_DIR, recursive=False)
    observer.start()
    
    try:
        # Start FTP server
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down FTP server...")
        observer.stop()
        observer.join()
        server.close_all()

if __name__ == '__main__':
    if not FTP_PASS:
        print("Error: CANON_R3_PASSWORD not set in .env file")
        sys.exit(1)
    
    start_ftp_server() 