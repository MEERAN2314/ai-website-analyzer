# Testing the Improved Analyzers

## 🧪 Quick Test Guide

### Test 1: Basic Functionality Test

Run a quick analysis to verify all analyzers work:

```bash
# Start your application
python app/main.py

# Or with Docker
docker-compose up
```

Then analyze a website through the UI or API.

---

### Test 2: Individual Analyzer Testing

Create a test script to verify each analyzer:

```python
# test_analyzers.py
import asyncio
from app.analyzers.performance_analyzer import PerformanceAnalyzer
from app.analyzers.seo_analyzer import SEOAnalyzer
from app.analyzers.content_analyzer import ContentAnalyzer
from app.analyzers.ux_analyzer import UXAnalyzer

async def test_analyzers():
    test_url = "https://example.com"
    
    print("🧪 Testing Performance Analyzer...")
    perf = PerformanceAnalyzer()
    perf_result = await perf.analyze(test_url)
    print(f"✅ Performance Score: {perf_result['score']} ({perf_result['grade']})")
    print(f"   Load Time: {perf_result['load_time']}s")
    print(f"   Issues: {len(perf_result['issues'])}")
    print()
    
    print("🧪 Testing SEO Analyzer...")
    seo = SEOAnalyzer()
    seo_result = await seo.analyze(test_url)
    print(f"✅ SEO Score: {seo_result['score']} ({seo_result['grade']})")
    print(f"   Title: {seo_result['meta_title']}")
    print(f"   Keywords: {len(seo_result['keywords'])}")
    print()
    
    print("🧪 Testing Content Analyzer...")
    content = ContentAnalyzer()
    content_result = await content.analyze(test_url)
    print(f"✅ Content Score: {content_result['score']} ({content_result['grade']})")
    print(f"   Word Count: {content_result['word_count']}")
    print(f"   Readability: {content_result['readability_level']}")
    print()
    
    print("🧪 Testing UX Analyzer...")
    ux = UXAnalyzer()
    ux_result = await ux.analyze(test_url)
    print(f"✅ UX Score: {ux_result['score']} ({ux_result['grade']})")
    print(f"   Mobile Friendly: {ux_result['mobile_friendly']}")
    print(f"   WCAG: {ux_result['wcag_compliance']}")
    print()
    
    print("🎉 All analyzers working correctly!")

if __name__ == "__main__":
    asyncio.run(test_analyzers())
```

Run the test:
```bash
python test_analyzers.py
```

---

### Test 3: Score Breakdown Verification

Verify that score breakdowns are working:

```python
# test_score_breakdown.py
import asyncio
from app.analyzers.performance_analyzer import PerformanceAnalyzer

async def test_score_breakdown():
    analyzer = PerformanceAnalyzer()
    result = await analyzer.analyze("https://example.com")
    
    print("📊 Score Breakdown:")
    for component, score in result['score_breakdown'].items():
        print(f"   {component}: {score:.1f}")
    
    print(f"\n🎯 Final Score: {result['score']:.1f}")
    print(f"📈 Grade: {result['grade']}")
    print(f"💡 Improvement Potential: {result['improvement_potential']}")

if __name__ == "__main__":
    asyncio.run(test_score_breakdown())
```

---

### Test 4: Different Website Types

Test with various website types to ensure accuracy:

```python
# test_website_types.py
import asyncio
from app.analyzers.performance_analyzer import PerformanceAnalyzer

async def test_multiple_sites():
    analyzer = PerformanceAnalyzer()
    
    test_sites = [
        ("https://example.com", "Simple Site"),
        ("https://google.com", "Fast Site"),
        ("https://amazon.com", "Complex Site"),
        ("https://wikipedia.org", "Content-Heavy Site")
    ]
    
    for url, description in test_sites:
        try:
            result = await analyzer.analyze(url)
            print(f"\n{description} ({url}):")
            print(f"  Score: {result['score']:.1f} ({result['grade']})")
            print(f"  Load Time: {result['load_time']}s")
            print(f"  Page Size: {result['page_size']:.1f}KB")
            print(f"  Requests: {result['requests_count']}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_multiple_sites())
```

---

### Test 5: Error Handling

Test error handling with invalid URLs:

```python
# test_error_handling.py
import asyncio
from app.analyzers.performance_analyzer import PerformanceAnalyzer

async def test_error_handling():
    analyzer = PerformanceAnalyzer()
    
    invalid_urls = [
        "not-a-url",
        "http://this-domain-does-not-exist-12345.com",
        "https://localhost:99999"
    ]
    
    for url in invalid_urls:
        print(f"\n🧪 Testing: {url}")
        result = await analyzer.analyze(url)
        print(f"   Score: {result['score']}")
        print(f"   Grade: {result['grade']}")
        print(f"   Issues: {result['issues'][0] if result['issues'] else 'None'}")

if __name__ == "__main__":
    asyncio.run(test_error_handling())
```

---

### Test 6: Compare Before/After

Compare old vs new analyzer results:

```python
# test_comparison.py
import asyncio
from app.analyzers.performance_analyzer import PerformanceAnalyzer

async def compare_results():
    analyzer = PerformanceAnalyzer()
    result = await analyzer.analyze("https://example.com")
    
    print("🆕 NEW ANALYZER RESULTS:")
    print(f"   Score: {result['score']:.1f} ({result['grade']})")
    print(f"   Components: {len(result['score_breakdown'])}")
    print(f"   Metrics: {len(result.get('metrics', {}))}")
    print(f"   Issues: {len(result['issues'])}")
    print(f"   Recommendations: {len(result['recommendations'])}")
    print(f"   Core Web Vitals: {len(result['core_web_vitals'])}")
    
    print("\n📊 SCORE BREAKDOWN:")
    for component, score in result['score_breakdown'].items():
        print(f"   {component}: {score:.1f}")
    
    print("\n🎯 CORE WEB VITALS:")
    cwv = result['core_web_vitals']
    print(f"   LCP: {cwv['LCP']}ms ({cwv['LCP_rating']})")
    print(f"   FID: {cwv['FID']}ms ({cwv['FID_rating']})")
    print(f"   CLS: {cwv['CLS']} ({cwv['CLS_rating']})")

if __name__ == "__main__":
    asyncio.run(compare_results())
```

---

### Test 7: Full Integration Test

Test the complete analysis flow:

```python
# test_full_analysis.py
import asyncio
from app.services.analysis_service import perform_website_analysis
from app.core.database import get_database
from bson import ObjectId

async def test_full_analysis():
    db = get_database()
    
    # Create test analysis
    analysis = {
        "website_url": "https://example.com",
        "status": "pending",
        "user_id": ObjectId()
    }
    
    result = await db.analyses.insert_one(analysis)
    analysis_id = str(result.inserted_id)
    
    print(f"🧪 Created test analysis: {analysis_id}")
    print("⏳ Running analysis...")
    
    # Run analysis
    await perform_website_analysis(analysis_id, "https://example.com")
    
    # Fetch results
    completed = await db.analyses.find_one({"_id": ObjectId(analysis_id)})
    
    print("\n✅ ANALYSIS COMPLETE!")
    print(f"   Status: {completed['status']}")
    print(f"   Overall Score: {completed['overall_score']}")
    print(f"   UX Score: {completed['ux_analysis']['score']}")
    print(f"   SEO Score: {completed['seo_analysis']['score']}")
    print(f"   Performance Score: {completed['performance_analysis']['score']}")
    print(f"   Content Score: {completed['content_analysis']['score']}")
    
    # Check for new fields
    print("\n🆕 NEW FIELDS:")
    if 'grade' in completed['performance_analysis']:
        print(f"   Performance Grade: {completed['performance_analysis']['grade']}")
    if 'score_breakdown' in completed['performance_analysis']:
        print(f"   Score Breakdown: ✅")
    if 'improvement_potential' in completed['performance_analysis']:
        print(f"   Improvement Potential: {completed['performance_analysis']['improvement_potential']}")
    
    # Cleanup
    await db.analyses.delete_one({"_id": ObjectId(analysis_id)})
    print("\n🧹 Cleaned up test data")

if __name__ == "__main__":
    asyncio.run(test_full_analysis())
```

---

## 🎯 Expected Results

### Performance Analyzer
- ✅ Score between 0-100 with decimal precision
- ✅ Grade (A-F)
- ✅ 7 score breakdown components
- ✅ Core Web Vitals with ratings
- ✅ Resource breakdown
- ✅ Improvement potential
- ✅ Priority-based issues (❌⚠️💡)

### SEO Analyzer
- ✅ Score between 0-100 with decimal precision
- ✅ Grade (A-F)
- ✅ 8 score breakdown components
- ✅ Character counts for title/description
- ✅ Keyword density analysis
- ✅ Link analysis (internal/external)
- ✅ Technical SEO checks
- ✅ SEO health status

### Content Analyzer
- ✅ Score between 0-100 with decimal precision
- ✅ Grade (A-F)
- ✅ 6 score breakdown components
- ✅ Flesch Reading Ease score
- ✅ Readability level
- ✅ Sentiment score
- ✅ Content depth rating
- ✅ Media analysis

### UX Analyzer
- ✅ Score between 0-100 with decimal precision
- ✅ Grade (A-F)
- ✅ 6 score breakdown components
- ✅ WCAG compliance level
- ✅ Navigation quality
- ✅ Accessibility score
- ✅ Form accessibility
- ✅ UX health status

---

## 🐛 Common Issues & Solutions

### Issue 1: Import Errors
**Problem**: `ModuleNotFoundError: No module named 'collections'`

**Solution**: Ensure you're using Python 3.7+
```bash
python3 --version
```

### Issue 2: Timeout Errors
**Problem**: Analysis times out for slow websites

**Solution**: Increase timeout in analyzer:
```python
async with httpx.AsyncClient(timeout=60.0) as client:  # Increase from 30
```

### Issue 3: Memory Issues
**Problem**: Large websites cause memory issues

**Solution**: Limit content parsing:
```python
html = response.text[:1000000]  # Limit to 1MB
```

### Issue 4: Missing Dependencies
**Problem**: `ModuleNotFoundError: No module named 'httpx'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📊 Performance Benchmarks

Expected analysis times:
- **Small website** (< 100KB): 1-2 seconds
- **Medium website** (100KB-1MB): 2-4 seconds
- **Large website** (> 1MB): 4-8 seconds

Memory usage:
- **Per analyzer**: ~10-20MB
- **All analyzers**: ~50-80MB
- **With AI service**: ~100-150MB

---

## ✅ Validation Checklist

Before deploying, verify:

- [ ] All 4 analyzers return valid JSON
- [ ] Scores are between 0-100
- [ ] Grades are A, B, C, D, or F
- [ ] Score breakdowns sum correctly (weighted)
- [ ] Issues have priority indicators
- [ ] Recommendations are actionable
- [ ] Error handling works for invalid URLs
- [ ] Timeout handling works for slow sites
- [ ] All new fields are present
- [ ] Backward compatibility maintained

---

## 🚀 Load Testing

Test with multiple concurrent analyses:

```python
# test_load.py
import asyncio
from app.analyzers.performance_analyzer import PerformanceAnalyzer

async def analyze_concurrent(url: str, id: int):
    analyzer = PerformanceAnalyzer()
    result = await analyzer.analyze(url)
    print(f"✅ Analysis {id} complete: {result['score']:.1f}")

async def load_test():
    tasks = [
        analyze_concurrent("https://example.com", i)
        for i in range(10)  # 10 concurrent analyses
    ]
    
    start = asyncio.get_event_loop().time()
    await asyncio.gather(*tasks)
    duration = asyncio.get_event_loop().time() - start
    
    print(f"\n⏱️  Total time: {duration:.2f}s")
    print(f"📊 Average per analysis: {duration/10:.2f}s")

if __name__ == "__main__":
    asyncio.run(load_test())
```

---

## 📝 Manual Testing Checklist

Test with these website types:

- [ ] **Simple static site** (e.g., example.com)
- [ ] **Blog/content site** (e.g., medium.com)
- [ ] **E-commerce site** (e.g., amazon.com)
- [ ] **News site** (e.g., bbc.com)
- [ ] **SPA/React site** (e.g., airbnb.com)
- [ ] **Slow loading site**
- [ ] **Mobile-optimized site**
- [ ] **Accessibility-focused site**
- [ ] **SEO-optimized site**
- [ ] **Your own website**

---

## 🎉 Success Criteria

Your improved analyzers are working correctly if:

1. ✅ All scores are more granular (not just 0, 10, 20, etc.)
2. ✅ Grades accurately reflect score ranges
3. ✅ Score breakdowns provide insight into weak areas
4. ✅ Issues are prioritized (❌⚠️💡)
5. ✅ Recommendations are specific and actionable
6. ✅ New metrics (Core Web Vitals, WCAG, etc.) are present
7. ✅ Error handling is graceful
8. ✅ Performance is acceptable (< 10s per site)
9. ✅ Results are consistent across multiple runs
10. ✅ All documentation matches actual output

---

## 📞 Need Help?

If you encounter issues:

1. Check the error message in analyzer output
2. Verify the website is accessible
3. Check Python version (3.7+ required)
4. Verify all dependencies are installed
5. Review the API reference documentation
6. Test with a simple website first (example.com)

Happy testing! 🚀
