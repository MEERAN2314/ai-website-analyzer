# Testing Advanced Features

This guide helps you test all the newly implemented advanced features.

## Prerequisites

1. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Open browser:**
   ```
   http://localhost:8000
   ```

## Automated Testing

Run the integration test script:

```bash
python test_features_integration.py
```

This will:
- Create a test user and analysis
- Wait for analysis to complete
- Test all advanced features via API
- Provide a summary of results

## Manual Testing

### 1. Create an Analysis

1. Go to http://localhost:8000
2. Click "Get Started" or "Try Free"
3. Register/Login with credentials
4. Enter a website URL (e.g., `https://example.com`)
5. Click "Analyze Website"
6. Wait for analysis to complete

### 2. Test Action Plan (30/60/90 Day Plan)

**Location:** Results page

**Steps:**
1. Click the **"30/60/90 Day Plan"** button (purple gradient button)
2. A modal should appear with:
   - Title: "📋 30/60/90 Day Action Plan"
   - Formatted roadmap with markdown rendering
   - Sections for 30, 60, and 90 day plans
   - Close button (X)

**Expected Result:**
- Modal displays with well-formatted action plan
- Markdown is properly rendered (headers, bullets, bold text)
- Plan includes specific tasks for each timeframe

### 3. Test PDF Download

**Location:** Results page

**Steps:**
1. Click the **"Download PDF"** button (blue button)
2. PDF should open in a new browser tab

**Expected Result:**
- PDF opens successfully
- Contains all analysis data:
  - Website URL and date
  - Overall score with color coding
  - Individual scores (UX, SEO, Performance, Content)
  - AI summary
  - Priority recommendations with color-coded boxes
  - Detailed analysis for each category
- Professional styling with high contrast colors

### 4. Test Export Formats

**Location:** Results page

#### JSON Export

**Steps:**
1. Click the **"Export"** dropdown button (gray button)
2. Click **"Export as JSON"** from the dropdown
3. File should download automatically

**Expected Result:**
- File downloads: `analysis_[id].json`
- Contains complete analysis data in JSON format
- Includes:
  - website_url
  - analysis_date
  - overall_score
  - scores breakdown
  - ai_summary
  - priority_recommendations
  - action_plan
  - detailed_analysis

#### CSV Export

**Steps:**
1. Click the **"Export"** dropdown button
2. Click **"Export as CSV"** from the dropdown
3. File should download automatically

**Expected Result:**
- File downloads: `analysis_[id].csv`
- Contains analysis data in CSV format
- Includes:
  - Header with website and date
  - Scores table
  - Priority recommendations
  - Issues and recommendations by category

### 5. Test Share Link

**Location:** Results page

**Steps:**
1. Click the **"Share Analysis"** button (green button)
2. Modal appears with expiry days input (default: 7)
3. Click **"Generate Share Link"**
4. Share link appears with copy button
5. Click **"Copy"** to copy link to clipboard
6. Open the share link in a new incognito/private window

**Expected Result:**
- Share link is generated successfully
- Link format: `http://localhost:8000/api/v1/share/[token]`
- Expiry date is displayed
- Copy button works (shows notification)
- Share link is accessible without login
- Shared analysis displays all data correctly

## API Endpoint Testing

You can also test endpoints directly using curl or Postman:

### Get Action Plan
```bash
curl -X GET "http://localhost:8000/api/v1/export/{analysis_id}/action-plan" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Export JSON
```bash
curl -X GET "http://localhost:8000/api/v1/export/{analysis_id}/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o analysis.json
```

### Export CSV
```bash
curl -X GET "http://localhost:8000/api/v1/export/{analysis_id}/csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o analysis.csv
```

### Create Share Link
```bash
curl -X POST "http://localhost:8000/api/v1/share/{analysis_id}/share?expires_in_days=7" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Access Shared Analysis
```bash
curl -X GET "http://localhost:8000/api/v1/share/{share_token}"
```

## Troubleshooting

### Action Plan Not Generated
- Check server logs for AI service errors
- Verify Gemini API key is valid
- Check if quota is exceeded (429 error)

### PDF Not Available
- Check `app/static/pdfs/` directory exists
- Verify PDF service has write permissions
- Check server logs for PDF generation errors

### Export Buttons Not Working
- Open browser console (F12) for JavaScript errors
- Verify API endpoints are responding
- Check network tab for failed requests

### Share Link Not Working
- Verify MongoDB `shares` collection exists
- Check share link hasn't expired
- Ensure share link is active (not revoked)

## Success Criteria

All features should work as follows:

✅ **Action Plan:**
- Generates during analysis
- Displays in modal with markdown formatting
- Contains 30/60/90 day roadmap

✅ **PDF Download:**
- Generates automatically during analysis
- Opens in new tab
- Contains all analysis data with professional styling

✅ **JSON Export:**
- Downloads complete analysis data
- Valid JSON format
- Includes action plan

✅ **CSV Export:**
- Downloads analysis in CSV format
- Properly formatted with headers
- Includes all key metrics

✅ **Share Link:**
- Creates unique shareable URL
- Works without authentication
- Respects expiry date
- Tracks view count

## Next Steps

After testing, you can:

1. **Customize action plans** - Edit `app/services/ai_service.py` to adjust prompts
2. **Modify PDF styling** - Edit `app/services/pdf_service.py` for layout changes
3. **Add more export formats** - Extend `app/api/v1/endpoints/export.py`
4. **Enhance share features** - Add password protection, custom expiry, etc.

## Support

If you encounter issues:
1. Check server logs: `tail -f logs/app.log`
2. Check MongoDB connection: `python check_mongodb.py`
3. Verify environment variables in `.env`
4. Review `docs/TROUBLESHOOTING.md`
