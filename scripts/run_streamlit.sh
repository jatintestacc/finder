#!/usr/bin/env bash
#
# Job Hunter - Streamlit UI Launcher
# Starts the Streamlit web interface for Job Hunter
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎯 Job Hunter - Streamlit UI${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 not found${NC}"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate venv
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update requirements
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "Please copy .env.example to .env and add your API key"
    cp .env.example .env
    echo "Created .env file. Please edit it with your API key."
fi

# Launch Streamlit
echo ""
echo -e "${GREEN}🚀 Launching Streamlit UI...${NC}"
echo -e "${BLUE}📱 Open your browser to: http://localhost:8501${NC}"
echo ""

streamlit run streamlit_app.py
