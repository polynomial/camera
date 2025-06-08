{ pkgs ? import <nixpkgs> { config.allowUnfree = true; } }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    imagemagick
    libheif
    
    # Python for R3 download and FTP server
    python3
    python3Packages.requests
    python3Packages.python-dotenv
    python3Packages.pyftpdlib
    python3Packages.watchdog
    
    # Metadata extraction
    exiftool
    
    # Networking tools
    ngrok
    curl
  ];
  
  shellHook = ''
    echo "Photography automation environment loaded"
    echo "ImageMagick with HEIF support is available"
    echo "Python with requests, pyftpdlib, and watchdog is available"
    echo "ngrok is available for tunneling"
  '';
} 