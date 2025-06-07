{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    imagemagick
    libheif
    
    # Python for R3 download
    python3
    python3Packages.requests
    python3Packages.python-dotenv
  ];
  
  shellHook = ''
    echo "Photography automation environment loaded"
    echo "ImageMagick with HEIF support is available"
    echo "Python with requests and dotenv is available"
  '';
} 