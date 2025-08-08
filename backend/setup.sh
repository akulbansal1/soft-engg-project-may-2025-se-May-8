#!/bin/bash

# Backend Development Script
# This script helps with common development tasks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}FastAPI Backend Development Helper${NC}"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${RED}Please update .env file with your actual database and Redis URLs${NC}"
fi

echo ""
echo -e "${GREEN}Setup complete! Available commands:${NC}"
echo ""
echo "1. Start FastAPI server:"
echo "   python main.py"
echo ""
echo ""
echo "2. Run tests:"
echo "   pytest"
echo ""
echo "3. Create database migration:"
echo "   alembic revision --autogenerate -m 'Description'"
echo ""
echo "4. Apply migrations:"
echo "   alembic upgrade head"
echo ""
echo -e "${YELLOW}API Documentation will be available at: http://localhost:8000/docs${NC}"
