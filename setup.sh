#!/bin/bash

# AI Website Analyzer - Quick Setup Script
# This script helps you set up the application for the first time

set -e

echo "🚀 AI Website Analyzer - Quick Setup"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11 or higher.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found: $(python3 --version)${NC}"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 is not installed. Please install pip3.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ pip3 found${NC}"
echo ""

# Ask user for setup method
echo "Choose setup method:"
echo "1) Local development (Python virtual environment)"
echo "2) Docker (recommended for testing)"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "📦 Setting up local development environment..."
        echo ""
        
        # Create virtual environment
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
            echo -e "${GREEN}✅ Virtual environment created${NC}"
        else
            echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
        fi
        
        # Activate virtual environment
        echo "Activating virtual environment..."
        source venv/bin/activate
        
        # Upgrade pip
        echo "Upgrading pip..."
        pip install --upgrade pip
        
        # Install dependencies
        echo "Installing dependencies..."
        pip install -r requirements.txt
        
        # Install Playwright
        echo "Installing Playwright browsers..."
        playwright install chromium
        
        # Setup environment file
        if [ ! -f ".env" ]; then
            echo "Creating .env file..."
            cp .env.example .env
            echo -e "${GREEN}✅ .env file created${NC}"
            echo -e "${YELLOW}⚠️  Please edit .env file with your credentials${NC}"
        else
            echo -e "${YELLOW}⚠️  .env file already exists${NC}"
        fi
        
        echo ""
        echo -e "${GREEN}✅ Setup complete!${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Edit .env file with your credentials:"
        echo "   - MongoDB connection string"
        echo "   - Google Gemini API key"
        echo "   - Redis configuration (or install Redis locally)"
        echo ""
        echo "2. Start Redis (if not using Docker):"
        echo "   - macOS: brew install redis && brew services start redis"
        echo "   - Ubuntu: sudo apt install redis-server && sudo systemctl start redis"
        echo ""
        echo "3. Run the application:"
        echo "   source venv/bin/activate"
        echo "   make dev"
        echo ""
        echo "4. Access the application at http://localhost:8000"
        ;;
        
    2)
        echo ""
        echo "🐳 Setting up Docker environment..."
        echo ""
        
        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
            echo "Visit: https://docs.docker.com/get-docker/"
            exit 1
        fi
        
        echo -e "${GREEN}✅ Docker found: $(docker --version)${NC}"
        
        # Check if Docker Compose is installed
        if ! command -v docker-compose &> /dev/null; then
            echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✅ Docker Compose found: $(docker-compose --version)${NC}"
        
        # Setup environment file
        if [ ! -f ".env" ]; then
            echo "Creating .env file..."
            cp .env.example .env
            echo -e "${GREEN}✅ .env file created${NC}"
            echo -e "${YELLOW}⚠️  Please edit .env file with your credentials${NC}"
        else
            echo -e "${YELLOW}⚠️  .env file already exists${NC}"
        fi
        
        echo ""
        echo -e "${GREEN}✅ Setup complete!${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Edit .env file with your credentials:"
        echo "   - MongoDB connection string"
        echo "   - Google Gemini API key"
        echo "   - Set REDIS_HOST=redis (for Docker)"
        echo ""
        echo "2. Start the application:"
        echo "   make docker-up"
        echo ""
        echo "3. Access the application at http://localhost:8000"
        echo ""
        echo "Useful Docker commands:"
        echo "   make docker-logs    - View logs"
        echo "   make docker-down    - Stop containers"
        echo "   make docker-clean   - Clean up everything"
        ;;
        
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "📚 Documentation:"
echo "   - README.md - Project overview and features"
echo "   - DEPLOYMENT.md - Detailed deployment guide"
echo "   - docs/ - Additional documentation"
echo ""
echo "🎉 Happy coding!"
