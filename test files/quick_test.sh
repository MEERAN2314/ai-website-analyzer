#!/bin/bash

echo "🧪 AI Website Analyzer - Quick Test Suite"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: MongoDB Connection
echo "1️⃣  Testing MongoDB Connection..."
python check_mongodb.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ MongoDB connection successful${NC}"
else
    echo -e "${RED}❌ MongoDB connection failed${NC}"
    echo "   Fix: Check MONGODB_URL in .env file"
    exit 1
fi
echo ""

# Test 2: Local Storage
echo "2️⃣  Testing Local Storage..."
python test_local_storage.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Local storage working${NC}"
else
    echo -e "${RED}❌ Local storage failed${NC}"
    exit 1
fi
echo ""

# Test 3: Analysis Flow
echo "3️⃣  Testing Analysis Flow..."
python test_analysis_flow.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Analysis flow working${NC}"
else
    echo -e "${RED}❌ Analysis flow failed${NC}"
    echo "   Check server logs for details"
    exit 1
fi
echo ""

echo -e "${GREEN}=========================================="
echo "✨ All tests passed! You're ready to go!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Start the server: uvicorn app.main:app --reload"
echo "2. Open browser: http://localhost:8000"
echo "3. Register a new account"
echo "4. Try analyzing a website (e.g., https://example.com)"
echo ""
echo "Need help? Check TROUBLESHOOTING.md"
