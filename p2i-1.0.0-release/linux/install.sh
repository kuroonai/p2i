#!/bin/bash
set -e

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or using sudo"
  exit 1
fi

# Create application directory
mkdir -p /opt/p2i

# Copy files
cp -r ./* /opt/p2i/

# Create desktop entry
mkdir -p /usr/share/applications
cp p2i.desktop /usr/share/applications/

# Create symlink in PATH
ln -sf /opt/p2i/p2i /usr/local/bin/p2i

echo "p2i has been installed successfully. You can run it by typing 'p2i' or from your application menu."

