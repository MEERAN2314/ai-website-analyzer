#!/bin/bash

echo "🧪 Testing Share Page Feature"
echo "=============================="
echo ""

# Check if server is running
if ! curl -s http://localhost:8000 > /dev/null; then
    echo "❌ Server is not running!"
    echo "Please start the server: uvicorn app.main:app --reload"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Get an existing share token from database
echo "📋 Instructions:"
echo "1. Go to http://localhost:8000"
echo "2. Login with: basic@example.com / Basic@123"
echo "3. Analyze a website (or use existing analysis)"
echo "4. Click 'Share Analysis' button"
echo "5. Generate share link"
echo "6. Copy the link and open in new incognito/private window"
echo ""
echo "Expected Result:"
echo "✅ Beautiful HTML page with analysis results"
echo "✅ No login required"
echo "✅ All scores and recommendations visible"
echo "✅ Professional layout with branding"
echo "✅ CTA button to try own analysis"
echo ""
echo "Previous Issue:"
echo "❌ Black screen with JSON data"
echo ""
echo "Fixed:"
echo "✅ Created dedicated share page template"
echo "✅ Added /share/{token} route"
echo "✅ Renders analysis in beautiful HTML"
echo ""
