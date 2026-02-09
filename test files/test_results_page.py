#!/usr/bin/env python3
"""
Test the results page to ensure it loads and displays analysis correctly
"""
import requests
import json

# Test if we can access an existing analysis
# Using one of the analysis IDs from the PDF files
analysis_id = '698a1e5dc19ecc2b63f31fcc'

print("=" * 60)
print("🧪 Testing Results Page")
print("=" * 60)

# Test 1: Check if results page loads
print("\n1️⃣  Testing Results Page HTML...")
try:
    response = requests.get(f'http://localhost:8000/results/{analysis_id}', timeout=5)
    print(f'   Status: {response.status_code}')
    
    if response.status_code == 200:
        print('   ✅ Results page loads successfully')
        
        # Check for key elements
        checks = [
            ('loadingResults', 'Loading state element'),
            ('resultsContent', 'Results content element'),
            ('setupEventListeners', 'Event listeners setup'),
            ('overallScore', 'Overall score element'),
            ('downloadPdfBtn', 'PDF download button'),
            ('exportBtn', 'Export button'),
            ('shareBtn', 'Share button'),
            ('actionPlanBtn', 'Action plan button'),
        ]
        
        for check_id, description in checks:
            if check_id in response.text:
                print(f'   ✅ {description} present')
            else:
                print(f'   ❌ {description} missing')
    else:
        print(f'   ❌ Page returned status {response.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Test 2: Check if API endpoint returns data
print("\n2️⃣  Testing Analysis API Endpoint...")
try:
    response = requests.get(f'http://localhost:8000/api/v1/analysis/{analysis_id}', timeout=5)
    print(f'   Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print('   ✅ API returns data successfully')
        print(f'   Website: {data.get("website_url", "N/A")}')
        print(f'   Status: {data.get("status", "N/A")}')
        print(f'   Overall Score: {data.get("overall_score", "N/A")}')
        
        # Check for required fields
        required_fields = [
            'website_url', 'status', 'overall_score',
            'ux_analysis', 'seo_analysis', 'performance_analysis', 'content_analysis',
            'ai_summary', 'priority_recommendations'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print(f'   ⚠️  Missing fields: {", ".join(missing_fields)}')
        else:
            print('   ✅ All required fields present')
    else:
        print(f'   ❌ API returned status {response.status_code}')
        print(f'   Response: {response.text[:200]}')
except Exception as e:
    print(f'   ❌ Error: {e}')

# Test 3: Check PDF availability
print("\n3️⃣  Testing PDF Endpoint...")
try:
    response = requests.get(f'http://localhost:8000/api/v1/analysis/{analysis_id}/pdf', timeout=5)
    print(f'   Status: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        if 'pdf_url' in data:
            print(f'   ✅ PDF URL: {data["pdf_url"]}')
            
            # Try to access the PDF
            pdf_response = requests.get(data['pdf_url'], timeout=5)
            if pdf_response.status_code == 200:
                print(f'   ✅ PDF accessible ({len(pdf_response.content)} bytes)')
            else:
                print(f'   ❌ PDF not accessible (status {pdf_response.status_code})')
        else:
            print('   ⚠️  PDF URL not in response')
    else:
        print(f'   ❌ PDF endpoint returned status {response.status_code}')
except Exception as e:
    print(f'   ❌ Error: {e}')

print("\n" + "=" * 60)
print("🌐 OPEN IN BROWSER")
print("=" * 60)
print(f"\nURL: http://localhost:8000/results/{analysis_id}")
print("\nExpected behavior:")
print("  1. Page should load without 'Loading...' stuck")
print("  2. Analysis data should display (scores, summary, recommendations)")
print("  3. All buttons should work (PDF, Export, Share, Action Plan)")
print("  4. No console errors about null references")
print("\n" + "=" * 60)
