# p2i - Packaging and Distribution Guide

This document provides detailed instructions for packaging and distributing the p2i application across different platforms.

## Table of Contents
- [Project Structure](#project-structure)
- [Building Requirements](#building-requirements)
- [Windows Distribution](#windows-distribution)
- [macOS Distribution](#macos-distribution)
- [Linux Distribution](#linux-distribution)
- [Setting Up Release Channels](#setting-up-release-channels)
- [Continuous Integration](#continuous-integration)
- [Version Management](#version-management)

## Project Structure

Before packaging, ensure your project structure is properly organized:

```
p2i/
├── main.py                 # Main application entry point
├── pdf_merge_tab.py        # Tab modules
├── pdf_split_tab.py
├── pdf_compress_tab.py
├── pdf_to_image_tab.py
├── image_to_pdf_tab.py
├── pdf_security_tab.py
├── image_batch_tab.py
├── office_convert_tab.py
├── utils.py                # Utility functions
├── settings.py             # Settings management
├── drag_drop.py            # Drag and drop functionality
├── icons/                  # Application icons
│   ├── app_icon.ico        # Windows icon
│   ├── app_icon.icns       # macOS icon
│   └── app_icon.png        # Linux icon
├── LICENSE                 # License file
├── README.md               # User documentation
├── DISTRIBUTION.md         # This file
├── requirements.txt        # Python dependencies
└── setup.py                # Installation script
```

Create a `setup.py` file for proper installation:

```python
from setuptools import setup, find_packages

setup(
    name="p2i",
    version="1.0.0",
    description="Advanced PDF & Image Processing Tool",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/p2i",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pdf2image>=1.16.3",
        "Pillow>=9.0.0",
        "tqdm>=4.64.1",
        "pypdfium2>=3.3.0",
        "reportlab>=3.6.0",
        "PyPDF2>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "p2i=p2i.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Topic :: Multimedia :: Graphics :: Editors",
        "Topic :: Office/Business",
    ],
)
```

## Building Requirements

Install the packaging tools needed for all platforms:

```bash
# Basic tools
pip install pyinstaller setuptools wheel twine

# For more advanced packaging
pip install cx_Freeze py2app
```

## Windows Distribution

### PyInstaller (Simple Executable)

PyInstaller is the easiest way to create standalone Windows executables:

```bash
# Install PyInstaller
pip install pyinstaller

# Basic build
pyinstaller --name=p2i --windowed main.py

# Optimized single-file build
pyinstaller --name=p2i --windowed --onefile --icon=icons/app_icon.ico --add-data="icons;icons" main.py
```

The `--windowed` flag prevents a console window from appearing, and `--onefile` creates a single executable rather than a folder with dependencies.

### NSIS Installer

For a professional installer, use NSIS (Nullsoft Scriptable Install System):

1. Download and install [NSIS](https://nsis.sourceforge.io/Download)
2. Create an NSIS script (`p2i_installer.nsi`):

```nsi
!define APPNAME "p2i"
!define COMPANYNAME "Your Company"
!define DESCRIPTION "PDF & Image Processing Tool"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

# Define installer name
OutFile "p2i-setup-${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}.exe"

# Default installation directory
InstallDir "$PROGRAMFILES\${APPNAME}"

# Set compression
SetCompressor lzma

# Request application privileges
RequestExecutionLevel admin

Name "${APPNAME}"
Icon "icons\app_icon.ico"
Caption "${APPNAME} Installer"

# Default section
Section "Install"
    # Set output path to the installation directory
    SetOutPath $INSTDIR
    
    # Add files
    File /r "dist\p2i\*.*"
    
    # Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    # Create desktop shortcut
    CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\p2i.exe" "" "$INSTDIR\icons\app_icon.ico"
    
    # Create start menu shortcut
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\p2i.exe" "" "$INSTDIR\icons\app_icon.ico"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    
    # Write registry keys for uninstaller
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME} - ${DESCRIPTION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$INSTDIR\icons\app_icon.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
SectionEnd

# Uninstaller section
Section "Uninstall"
    # Remove files
    RMDir /r "$INSTDIR"
    
    # Remove shortcuts
    Delete "$DESKTOP\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    
    # Remove registry keys
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
```

3. Run NSIS compiler to build the installer:
   - Right-click the .nsi file and select "Compile NSIS Script"
   - Or use the command line: `makensis p2i_installer.nsi`

### Advanced: MSI Installer with WiX Toolset

For enterprise environments, MSI installers are preferred:

1. Install the [WiX Toolset](https://wixtoolset.org/releases/)
2. Create a WiX source file (p2i.wxs) for your application
3. Compile the WiX project to create an MSI package

## macOS Distribution

### Creating a macOS App Bundle

1. **Using PyInstaller**:

```bash
# Basic app bundle
pyinstaller --name=p2i --windowed --icon=icons/app_icon.icns main.py

# With specific macOS settings
pyinstaller --name=p2i --windowed --icon=icons/app_icon.icns \
  --add-data="icons:icons" \
  --osx-bundle-identifier=com.yourcompany.p2i \
  main.py
```

2. **Create a proper Info.plist**:

Edit the generated Info.plist file in `dist/p2i.app/Contents/` to add proper metadata.

### Creating a DMG Installer

Use the `create-dmg` tool to package your application:

```bash
# Install create-dmg
brew install create-dmg

# Create the DMG
create-dmg \
  --volname "p2i Installer" \
  --volicon "icons/app_icon.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "p2i.app" 200 190 \
  --hide-extension "p2i.app" \
  --app-drop-link 600 185 \
  "p2i-1.0.0.dmg" \
  "dist/p2i.app"
```

### Code Signing for macOS

For distribution outside the App Store:

```bash
# Sign the app bundle
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name (XXXXXXXXXX)" "dist/p2i.app"

# Verify signature
codesign --verify --deep --strict --verbose=2 "dist/p2i.app"

# Sign the DMG installer
codesign --force --verify --verbose --sign "Developer ID Application: Your Name (XXXXXXXXXX)" "p2i-1.0.0.dmg"
```

For App Store distribution, use the App Store certificate and submit through Xcode.

## Linux Distribution

### AppImage (Universal Linux Package)

AppImage allows you to create a single executable that works across most Linux distributions:

1. Install required tools:
```bash
# Download AppImageKit
wget -O appimagetool "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
chmod +x appimagetool
```

2. Create AppDir structure:
```bash
# Build with PyInstaller first
pyinstaller --name=p2i --windowed main.py

# Create AppDir structure
mkdir -p AppDir/usr/bin
cp -r dist/p2i/* AppDir/usr/bin/

# Add application icon
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps/
cp icons/app_icon.png AppDir/usr/share/icons/hicolor/256x256/apps/p2i.png

# Create .desktop file
cat > AppDir/p2i.desktop << EOF
[Desktop Entry]
Name=p2i
Comment=PDF & Image Processing Tool
Exec=p2i
Icon=p2i
Type=Application
Categories=Office;Graphics;
EOF

# Create AppRun script
cat > AppDir/AppRun << EOF
#!/bin/bash
SELF=\$(readlink -f "\$0")
HERE=\${SELF%/*}
export PATH="\${HERE}/usr/bin:\${PATH}"
"\${HERE}/usr/bin/p2i" "\$@"
EOF

chmod +x AppDir/AppRun
```

3. Build the AppImage:
```bash
./appimagetool AppDir p2i-x86_64.AppImage
```

### Debian/Ubuntu (.deb) Package

1. Install build dependencies:
```bash
sudo apt-get install python3-stdeb dh-python
```

2. Use `stdeb` to build a .deb package:
```bash
python setup.py --command-packages=stdeb.command bdist_deb
```

3. The .deb package will be created in the `deb_dist` directory.

### RPM Package (Fedora/RHEL/CentOS)

1. Install build dependencies:
```bash
sudo dnf install rpm-build
```

2. Build the RPM package:
```bash
python setup.py bdist_rpm
```

3. The .rpm package will be created in the `dist` directory.

### Snap Package (Universal Linux)

1. Create a `snapcraft.yaml` file:
```yaml
name: p2i
version: '1.0.0'
summary: PDF & Image Processing Tool
description: |
  p2i is a comprehensive GUI application for PDF and image operations,
  including conversion, merging, splitting, compression, security, and more.

grade: stable
confinement: strict
base: core18

apps:
  p2i:
    command: bin/p2i
    extensions: [gnome-3-28]
    plugs:
      - home
      - removable-media
      - network
      - desktop
      - desktop-legacy
      - wayland
      - x11

parts:
  p2i:
    plugin: python
    python-version: python3
    source: .
    stage-packages:
      - python3-tk
      - python3-pil
      - ghostscript
      - poppler-utils
```

2. Build the snap package:
```bash
snapcraft
```

## Setting Up Release Channels

### GitHub Releases

1. Create a GitHub repository for your project
2. Go to the repository and click the "Releases" tab
3. Click "Draft a new release"
4. Set a tag version (e.g., "v1.0.0")
5. Write release notes
6. Upload your distribution packages:
   - Windows: .exe installer or .zip with portable executable
   - macOS: .dmg file or .zip with app bundle
   - Linux: .AppImage, .deb, .rpm, and/or .snap files
7. Publish the release

### PyPI Distribution

1. Prepare your package:
```bash
python setup.py sdist bdist_wheel
```

2. Upload to PyPI:
```bash
twine upload dist/*
```

3. Users can then install with:
```bash
pip install p2i
```

### Conda Forge

1. Fork the [conda-forge/staged-recipes](https://github.com/conda-forge/staged-recipes) repository
2. Add a new recipe for your package
3. Submit a pull request to get your package added to conda-forge

## Continuous Integration

Set up automated builds using GitHub Actions:

1. Create `.github/workflows/build.yml`:
```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller
      - name: Build with PyInstaller
        run: |
          pyinstaller --name=p2i --windowed --onefile --icon=icons/app_icon.ico --add-data="icons;icons" main.py
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: p2i-windows
          path: dist/p2i.exe

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller
      - name: Build with PyInstaller
        run: |
          pyinstaller --name=p2i --windowed --icon=icons/app_icon.icns --add-data="icons:icons" main.py
      - name: Create DMG
        run: |
          brew install create-dmg
          create-dmg \
            --volname "p2i Installer" \
            --window-pos 200 120 \
            --window-size 800 400 \
            --icon-size 100 \
            --icon "p2i.app" 200 190 \
            --hide-extension "p2i.app" \
            --app-drop-link 600 185 \
            "p2i-installer.dmg" \
            "dist/p2i.app"
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: p2i-macos
          path: p2i-installer.dmg

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller
      - name: Build with PyInstaller
        run: |
          pyinstaller --name=p2i --windowed --add-data="icons:icons" main.py
      - name: Create AppImage
        run: |
          wget -O appimagetool "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
          chmod +x appimagetool
          mkdir -p AppDir/usr/bin
          cp -r dist/p2i/* AppDir/usr/bin/
          cp icons/app_icon.png AppDir/p2i.png
          cat > AppDir/p2i.desktop << EOF
          [Desktop Entry]
          Name=p2i
          Comment=PDF & Image Processing Tool
          Exec=p2i
          Icon=p2i
          Type=Application
          Categories=Office;Graphics;
          EOF
          cat > AppDir/AppRun << EOF
          #!/bin/bash
          SELF=\$(readlink -f "\$0")
          HERE=\${SELF%/*}
          export PATH="\${HERE}/usr/bin:\${PATH}"
          "\${HERE}/usr/bin/p2i" "\$@"
          EOF
          chmod +x AppDir/AppRun
          ./appimagetool AppDir p2i-x86_64.AppImage
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: p2i-linux
          path: p2i-x86_64.AppImage

  release:
    needs: [build-windows, build-macos, build-linux]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Download all artifacts
        uses: actions/download-artifact@v2
      - name: Create Release
        id: create_release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: p2i ${{ github.ref }}
          draft: false
          prerelease: false
      - name: Upload Windows Build
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: ./p2i-windows/p2i.exe
          asset_name: p2i-windows-x64.exe
          asset_content_type: application/octet-stream
      - name: Upload macOS Build
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: ./p2i-macos/p2i-installer.dmg
          asset_name: p2i-macos.dmg
          asset_content_type: application/octet-stream
      - name: Upload Linux Build
        uses: actions/upload-release-asset@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: ./p2i-linux/p2i-x86_64.AppImage
          asset_name: p2i-linux-x86_64.AppImage
          asset_content_type: application/octet-stream
```

## Version Management

1. **Version Numbering**: Use semantic versioning (MAJOR.MINOR.PATCH)
2. **Update Version in Code**:
   - Update version in setup.py
   - Update version in main.py or a dedicated version.py file
3. **Tag in Git**: Create a git tag for each release
4. **Changelog**: Maintain a CHANGELOG.md file

Example version.py file:
```python
VERSION = '1.0.0'
```

Example integrating version in main.py:
```python
try:
    from version import VERSION
except ImportError:
    VERSION = '1.0.0'

def show_about():
    """Show about dialog"""
    about_text = f"""p2i - PDF & Image Processing Tool
Version {VERSION}

A comprehensive toolkit for PDF and image processing.
...
"""
    messagebox.showinfo("About p2i", about_text)
```

## Advanced Topics

### Auto-Updater

To implement an auto-updater:

1. Create an update server or use GitHub releases API
2. Add code to check for updates on application startup
3. If an update is available, prompt the user to download and install

Example update checker:
```python
import requests
import json
import webbrowser
from version import VERSION

def check_for_updates():
    try:
        response = requests.get("https://api.github.com/repos/yourusername/p2i/releases/latest", timeout=5)
        latest_release = json.loads(response.text)
        latest_version = latest_release["tag_name"].lstrip("v")
        
        if latest_version > VERSION:
            # New version available
            if messagebox.askyesno("Update Available", 
                                   f"A new version ({latest_version}) is available. Would you like to download it?"):
                webbrowser.open(latest_release["html_url"])
    except:
        # Silently fail if update check fails
        pass
```

### Telemetry and Crash Reporting

To collect anonymous usage statistics and crash reports:

1. Add a privacy policy to your application
2. Get user consent before collecting data
3. Use a service like Sentry for crash reporting

```python
def setup_crash_reporting():
    if settings.get('enable_crash_reporting', False):
        try:
            import sentry_sdk
            sentry_sdk.init(
                "YOUR_SENTRY_DSN",
                traces_sample_rate=0.1
            )
        except ImportError:
            pass
```

### Licensing and Activation

For commercial applications, implement a licensing system:

1. Generate license keys with a secure algorithm
2. Store and verify license keys locally
3. Optionally validate licenses against a server

Remember to thoroughly test your packages before distribution, especially with dependencies that include compiled code, as they may behave differently across platforms.