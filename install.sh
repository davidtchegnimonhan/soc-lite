#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════╗"
echo "║     SOC-Lite Installation Script     ║"
echo "║   Lightweight SIEM for SMEs          ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Detect if running as root (common on fresh VPS, just warn)
if [ "$EUID" -eq 0 ]; then
   echo -e "${YELLOW}⚠️  Running as root. This is common on fresh VPS instances.${NC}"
   echo -e "${YELLOW}   Continuing installation...${NC}"
fi

# Detect OS
OS="unknown"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

echo -e "${YELLOW}Detected OS: $OS${NC}"

# Use sudo only if not already root (sudo may not exist on minimal/root systems)
if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"

if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    $SUDO apt-get update
    $SUDO apt-get install -y python3 python3-pip python3-venv git
elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    $SUDO yum install -y python3 python3-pip git
elif [ "$OS" = "darwin" ]; then
    # macOS
    if ! command -v brew &> /dev/null; then
        echo -e "${RED}Homebrew not found. Installing...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python3 git
else
    echo -e "${RED}Unsupported OS. Please install Python 3.8+ and git manually.${NC}"
    exit 1
fi

# Clone repository (skip if already running from inside an existing clone)
if [ -f "main.py" ] && [ -d "dashboard" ] && [ -d "parser" ]; then
    echo -e "${YELLOW}Already inside a SOC-Lite directory. Skipping clone.${NC}"
elif [ -d "soc-lite" ]; then
    echo -e "${YELLOW}Cloning SOC-Lite...${NC}"
    echo -e "${YELLOW}Directory exists. Updating...${NC}"
    cd soc-lite
    git pull
else
    echo -e "${YELLOW}Cloning SOC-Lite...${NC}"
    git clone https://github.com/davidtchegnimonhan/soc-lite.git
    cd soc-lite
fi

# Create virtual environment
echo -e "${YELLOW}Setting up Python environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo -e "${YELLOW}Installing Python packages...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest

# Create data directories
mkdir -p data logs

# Generate sample data if needed
if [ ! -f "data/attack_dataset.log" ]; then
    echo -e "${YELLOW}Generating sample data...${NC}"
    python utils/attack_injector.py
fi

# Run tests (use 'python -m pytest' to guarantee the venv's interpreter
# and installed packages are used, not a global system pytest)
echo -e "${YELLOW}Running tests...${NC}"
python -m pytest tests/ -v || echo -e "${RED}Some tests failed, but installation continues...${NC}"

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════╗"
echo "║   ✅ Installation Complete!           ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${GREEN}To start SOC-Lite:${NC}"
echo -e "  cd soc-lite"
echo -e "  source venv/bin/activate"
echo -e "  python dashboard/app.py"
echo ""
echo -e "${GREEN}Then open:${NC} http://localhost:5000"
echo ""
echo -e "${YELLOW}For more details, see:${NC} docs/INSTALLATION.md"
echo ""
echo -e "${GREEN}Need help? for.help.it.s@gmail.com${NC}"
