# Canon R3 FTP Upload Setup

This guide helps you set up real-time photo uploads from your Canon R3 to Google Photos via FTP.

## Overview

The FTP server feature allows your Canon R3 to upload photos directly to your Mac over the internet. Photos are automatically:
- Converted from CR3 to JPEG (95% quality)
- Uploaded to your Android device
- Synced to Google Photos
- Saved locally in `~/camera/ftp_uploads/`

## Prerequisites

1. **ngrok account** (free tier works fine)
   - Sign up at https://ngrok.com
   - Get your auth token from the dashboard

2. **Android device** connected via USB with debugging enabled

## Setup Steps

### 1. Install ngrok

ngrok is automatically provided through nix-shell when you run the FTP server.

If you want to install it separately:
```bash
# On macOS with Homebrew
brew install ngrok

# Or download from https://ngrok.com/download
```

### 2. Configure ngrok

```bash
# Add your auth token to .env file:
echo "NGROK_API_TOKEN=your_token_here" >> .env

# Or configure ngrok globally:
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

### 3. Start the FTP Server

```bash
./photo-upload --ftp-server
```

You'll see output like:
```
Canon R3 FTP Upload Service
================================
Starting FTP server on port 2121...
Starting ngrok tunnel...
Waiting for tunnel... ✓

✅ FTP Server is ready!

Configure your Canon R3 with these settings:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FTP Server: 2.tcp.ngrok.io
Port:       12345
Username:   admin
Password:   [Your password from .env]
Directory:  /
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4. Configure Canon R3

On your Canon R3:

1. **Menu → Network Settings → FTP Transfer Settings**
2. **Select SET1 (or any empty slot)**
3. **Configure:**
   - Transfer Type: FTP transfer
   - Auto transfer: Enable
   - Server: `[ngrok host from above]`
   - Port: `[ngrok port from above]`
   - Username: `admin` (or your username)
   - Password: `[your password from .env]`
   - Directory: `/`
   - Passive mode: Enable

4. **Test Connection**
5. **Enable FTP Transfer**

### 5. Take Photos!

Now when you take photos:
1. They automatically upload to the FTP server
2. Convert to JPEG (95% quality)
3. Upload to your Android device
4. Appear in Google Photos

## Features

- **Automatic conversion**: CR3 → JPEG at 95% quality
- **Instant Android upload**: Files go straight to DCIM/Camera
- **Media scanning**: Photos appear immediately in gallery
- **Local backup**: All files saved to ~/camera/ftp_uploads/
- **Progress tracking**: See each upload in real-time

## Troubleshooting

### ngrok not starting
- Check your auth token is correct
- Ensure you're not hitting free tier limits

### FTP connection fails
- Verify ngrok URL is correct in camera
- Check username/password match .env
- Try passive mode on/off

### Android upload fails
- Ensure device is connected: `adb devices`
- Check USB debugging is enabled
- Try reconnecting USB cable

### Conversion fails
- Ensure ImageMagick is installed (handled by nix-shell)
- Check disk space for temp files

## Security Notes

- The ngrok URL changes each time you restart
- Use strong passwords in .env
- Free ngrok URLs are public (anyone with URL can connect)
- Consider ngrok paid tier for reserved domains

## Advanced Configuration

Edit `.env` to customize:
```bash
FTP_PORT=2121          # Local FTP port
JPEG_QUALITY=95        # JPEG quality (1-100)
CANON_R3_USERNAME=admin
CANON_R3_PASSWORD=your_secure_password
``` 