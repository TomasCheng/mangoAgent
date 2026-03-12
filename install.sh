#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🥭 Installing Mango Agent...${NC}"

# Ensure we are in the project root
cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

echo -e "${BLUE}Project Root: ${PROJECT_ROOT}${NC}"

# Check for python3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate venv and install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -e .

# Create symlink
TARGET_BIN="$HOME/.local/bin"
mkdir -p "$TARGET_BIN"

echo -e "${BLUE}Linking executable to $TARGET_BIN/mango...${NC}"
ln -sf "$PROJECT_ROOT/venv/bin/mango" "$TARGET_BIN/mango"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "\n${GREEN}Warning: $HOME/.local/bin is not in your PATH.${NC}"
    echo "Please add the following line to your shell configuration (.zshrc, .bashrc, etc.):"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo -e "\n${GREEN}✅ Installation Complete!${NC}"
echo -e "You can now run '${GREEN}mango${NC}' from any terminal."
