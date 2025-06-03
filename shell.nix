{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    imagemagick
    libheif
  ];
  
  shellHook = ''
    echo "Photography automation environment loaded"
    echo "ImageMagick with HEIF support is available"
  '';
} 