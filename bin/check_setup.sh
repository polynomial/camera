#!/bin/bash

# check_setup.sh - Verify photography automation setup
# Usage: ./check_setup.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_info() {
    echo -e "  $1"
}

# Track if setup is complete
SETUP_COMPLETE=true

print_header "Photography Automation Setup Check"
echo "Checking all dependencies and configuration..."

# Check ImageMagick
print_header "ImageMagick"
if command -v magick &> /dev/null; then
    VERSION=$(magick -version | head -n 1)
    print_success "ImageMagick installed: $VERSION"
    
    # Check HEIF support
    if magick -list format | grep -q "HEIF\|HEIC"; then
        print_success "HEIF/HEIC support detected"
    else
        print_error "HEIF/HEIC support not found"
        print_info "Reinstall ImageMagick with: brew reinstall imagemagick"
        SETUP_COMPLETE=false
    fi
else
    print_error "ImageMagick not installed"
    print_info "Install with: brew install imagemagick"
    SETUP_COMPLETE=false
fi

# Check ADB
print_header "Android Debug Bridge (ADB)"
if command -v adb &> /dev/null; then
    VERSION=$(adb version | head -n 1)
    print_success "ADB installed: $VERSION"
    
    # Check for connected devices
    DEVICES=$(adb devices | grep -v "List of devices" | grep "device$" | wc -l | tr -d ' ')
    if [ "$DEVICES" -gt 0 ]; then
        print_success "Android device connected"
        DEVICE_INFO=$(adb shell getprop ro.product.model 2>/dev/null || echo "Unknown")
        print_info "Device: $DEVICE_INFO"
    else
        print_warning "No Android device connected"
        print_info "Connect your device and enable USB debugging"
    fi
else
    print_error "ADB not installed"
    print_info "Install with: brew install android-platform-tools"
    SETUP_COMPLETE=false
    DEVICES=0  # Set DEVICES to 0 when ADB is not installed
fi

# Check Darktable (optional)
print_header "Darktable (Optional)"
if command -v darktable &> /dev/null; then
    VERSION=$(darktable --version 2>&1 | grep -o "darktable [0-9.]*" || echo "Unknown version")
    print_success "Darktable installed: $VERSION"
else
    print_warning "Darktable not installed"
    print_info "Install from: https://www.darktable.org/install/"
    print_info "Or with: brew install --cask darktable"
fi

# Check directory structure
print_header "Directory Structure"
if [ -d "bin" ]; then
    print_success "bin/ directory exists"
else
    print_error "bin/ directory missing"
    SETUP_COMPLETE=false
fi

if [ -d "docs" ]; then
    print_success "docs/ directory exists"
else
    print_error "docs/ directory missing"
    SETUP_COMPLETE=false
fi

# Check scripts
print_header "Scripts"
if [ -x "bin/upload_to_android.sh" ]; then
    print_success "upload_to_android.sh is executable"
else
    print_error "upload_to_android.sh is not executable or missing"
    SETUP_COMPLETE=false
fi

if [ -x "bin/convert_hif.sh" ]; then
    print_success "convert_hif.sh is executable"
else
    print_error "convert_hif.sh is not executable or missing"
    SETUP_COMPLETE=false
fi

# Test Android storage access (if device connected)
if [ "$DEVICES" -gt 0 ] 2>/dev/null; then
    print_header "Android Storage Access"
    if adb shell "ls /storage/self/primary/" &> /dev/null; then
        print_success "Can access Android storage"
        
        # Check if DCIM/Camera exists
        if adb shell "ls /storage/self/primary/DCIM/Camera" &> /dev/null; then
            print_success "DCIM/Camera directory exists"
        else
            print_warning "DCIM/Camera directory not found"
            print_info "It will be created when needed"
        fi
    else
        print_error "Cannot access Android storage"
        print_info "Check device permissions"
        SETUP_COMPLETE=false
    fi
fi

# Summary
print_header "Setup Summary"
if [ "$SETUP_COMPLETE" = true ]; then
    echo -e "${GREEN}✅ All required dependencies are installed!${NC}"
    echo -e "\nYou're ready to start using the photography automation tools."
    echo -e "Try: ${BLUE}./bin/upload_to_android.sh /path/to/hif/files${NC}"
else
    echo -e "${RED}❌ Some dependencies are missing.${NC}"
    echo -e "Please install the missing components listed above."
fi

echo -e "\nFor more information, see:"
echo -e "  - ${BLUE}README.md${NC} for general information"
echo -e "  - ${BLUE}docs/workflow.md${NC} for detailed workflow guide" 