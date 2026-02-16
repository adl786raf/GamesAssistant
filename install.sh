#!/bin/bash

# Define colors for cool output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Games Assistant Installer ===${NC}"

# 1. Check if running as Root (sudo)
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root (use sudo).${NC}"
  exit
fi

# 2. Detect System Architecture
ARCH=$(dpkg --print-architecture)
echo -e "System Architecture: $ARCH"

# 3. If system is 64-bit (amd64), enable 32-bit support
if [ "$ARCH" = "amd64" ]; then
    if dpkg --print-foreign-architectures | grep -q "i386"; then
        echo -e "${GREEN}32-bit support is already active.${NC}"
    else
        echo -e "${RED}64-bit system detected. Enabling 32-bit compatibility...${NC}"
        dpkg --add-architecture i386
        apt update
        echo -e "${GREEN}32-bit support enabled!${NC}"
    fi
fi

# 4. Install the App
echo -e "${GREEN}Installing Games Assistant...${NC}"
apt install -y ./GamesAssistant_1.6_i386.deb

# 5. Success Message
echo -e "${GREEN}Installation Complete! You can now run 'GamesAssistant' from your terminal or menu.${NC}"
