# Analyzer API Reference

## Quick Reference for Improved Analyzers

---

## 📊 Performance Analyzer

### Method
```python
async def analyze(url: str) -> Dict
```

### Returns
```python
{
    # Core Metrics
    "score": float,              # 0-100 weighted score
    "grade": str,                # A, B, C, D, or F
    "load_time": float,          # Seconds
    "page_size": float,          # Kilobytes
    "requests_count": int,       # Total HTTP requests
    
    # Core Web Vitals
    "core_web_vitals": {
        "LCP": float,            # Largest Contentful Paint (ms)
        "LCP_rating": str,       # good/needs-improvement/poor
        "FID": float,            # First Input Delay (ms)
        "FID_rating": str,       # good/needs-improvement/poor
        "CLS": float,            # Cumulative Layout Shift
        "CLS_rating": str        # good/needs-improvement/poor
    },
    
    # Detailed Breakdown
    "score_breakdown": {
        "load_time": float,
        "page_size": float,
        "requests": float,
        "compression": float,
        "caching": float,
        "render_blocking": float,
        "resource_optimization": float
    },
    
    "resource_breakdown": {
        "images": int,
        "scripts": int,
        "stylesheets": int,
        "fonts": int
    },
    
    # Analysis Results
    "improvement_potential": str,  # Low/Medium/High
    "issues": List[str],
    "recommendations": List[str],
    
    # Additional Metrics
    "metrics": {
        "ttfb": float,              # Time to First Byte
        "compression_enabled": bool,
        "caching_enabled": bool,
        "https_enabled": bool
    }
}
```

### Thresholds
```python
THRESHOLDS = {
    'load_time': {'excellent': 1.5, 'good': 2.5, 'poor': 4.0},
    'page_size': {'excellent': 500, 'good': 1000, 'poor': 2000},  # KB
    'requests': {'excellent': 25, 'good': 50, 'poor': 100},
    'lcp': {'excellent': 2500, 'good': 4000, 'poor': 6000},  # ms
    'fid': {'excellent': 100, 'good': 300, 'poor': 500},  # ms
    'cls': {'excellent': 0.1, 'good': 0.25, 'poor': 0.5}
}
```

---

## 🔍 SEO Analyzer

### Method
```python
async def analyze(url: str) -> Dict
```

### Returns
```python
{
    # Core Metrics
    "score": float,                    # 0-100 weighted score
    "grade": str,                      # A, B, C, D, or F
    
    # Meta Information
    "meta_title": str,
    "meta_title_length": int,
    "meta_description": str,
    "meta_description_length": int,
    
    # Heading Structure
    "headings_structure": {
        "h1": int,
        "h2": int,
        "h3": int,
        "h4": int
    },
    "h1_text": str,
    
    # Keywords
    "keywords": List[str],             # Top 10 keywords
    "keyword_density": Dict[str, float],  # Top 5 with percentages
    "word_count": int,
    
    # Links
    "internal_links": int,
    "external_links": int,
    "broken_links": List[str],
    
    # Technical SEO
    "has_sitemap": bool,
    "has_robots_txt": bool,
    "is_mobile_friendly": bool,
    "uses_https": bool,
    "canonical_url": str,
    
    # Detailed Breakdown
    "score_breakdown": {
        "title": float,
        "description": float,
        "headings": float,
        "content": float,
        "technical": float,
        "links": float,
        "social": float,
        "structured": float
    },
    
    # Analysis Results
    "issues": List[str],
    "recommendations": List[str],
    "seo_health": str
}
```

### Thresholds
```python
THRESHOLDS = {
    'title': {'min': 30, 'ideal_min': 50, 'ideal_max': 60, 'max': 70},
    'description': {'min': 120, 'ideal_min': 150, 'ideal_max': 160, 'max': 200},
    'h1_length': {'min': 20, 'max': 70},
    'keyword_density': {'min': 0.5, 'max': 3.0},  # percentage
    'internal_links': {'min': 3, 'ideal': 10},
    'external_links': {'max': 50}
}
```

---

## 📝 Content Analyzer

### Method
```python
async def analyze(url: str) -> Dict
```

### Returns
```python
{
    # Core Metrics
    "score": float,                    # 0-100 weighted score
    "grade": str,                      # A, B, C, D, or F
    
    # Text Metrics
    "word_count": int,
    "sentence_count": int,
    "paragraph_count": int,
    
    # Readability
    "readability_score": float,        # Flesch Reading Ease (0-100)
    "readability_level": str,          # Very Easy to Very Difficult
    "avg_sentence_length": float,      # Words per sentence
    "avg_word_length": float,          # Characters per word
    
    # Engagement
    "has_cta": bool,
    "cta_count": int,
    
    # Quality
    "tone": str,                       # Positive/Neutral/Negative
    "sentiment_score": float,          # -100 to 100
    "keyword_usage": List[str],        # Top 5 keywords
    "content_depth": str,              # Comprehensive/Detailed/Moderate/Basic
    
    # Media
    "media_count": int,
    "images_with_alt": int,
    
    # Detailed Breakdown
    "score_breakdown": {
        "text": float,
        "readability": float,
        "structure": float,
        "engagement": float,
        "media": float,
        "quality": float
    },
    
    # Analysis Results
    "issues": List[str],
    "recommendations": List[str],
    "content_health": str
}
```

### Thresholds
```python
THRESHOLDS = {
    'word_count': {'min': 300, 'good': 500, 'excellent': 1000},
    'sentence_length': {'min': 10, 'max': 25, 'ideal': 18},
    'paragraph_length': {'min': 40, 'max': 150},
    'readability': {'easy': 80, 'standard': 60, 'difficult': 40},
    'heading_ratio': {'min': 0.02, 'max': 0.10},  # per 100 words
    'media_ratio': {'min': 0.001, 'max': 0.01}    # images per word
}
```

---

## 🎨 UX Analyzer

### Method
```python
async def analyze(url: str) -> Dict
```

### Returns
```python
{
    # Core Metrics
    "score": float,                    # 0-100 weighted score
    "grade": str,                      # A, B, C, D, or F
    
    # Mobile Friendliness
    "mobile_friendly": bool,
    "has_viewport": bool,
    "responsive_images": int,
    
    # Accessibility
    "accessibility_score": int,        # 0-100
    "wcag_compliance": str,            # AAA/AA/A/Non-compliant
    "has_skip_link": bool,
    "aria_usage": int,                 # Number of ARIA landmarks
    
    # Navigation
    "navigation_quality": str,         # Excellent/Good/Fair/Poor
    "navigation_items": int,
    
    # Forms
    "form_accessibility": int,         # 0-100
    
    # Interactive Elements
    "interactive_elements": int,
    
    # Detailed Breakdown
    "score_breakdown": {
        "mobile": float,
        "navigation": float,
        "accessibility": float,
        "forms": float,
        "interactive": float,
        "visual": float
    },
    
    # Analysis Results
    "issues": List[str],
    "recommendations": List[str],
    "ux_health": str
}
```

### Thresholds
```python
THRESHOLDS = {
    'navigation_items': {'min': 3, 'max': 7},
    'form_fields': {'max': 10},
    'button_count': {'min': 2, 'max': 15},
    'color_contrast': {'min': 4.5},    # WCAG AA standard
    'touch_target': {'min': 44}        # pixels
}
```

---

## 🎯 Common Patterns

### Error Handling
All analyzers return a fallback response on error:
```python
{
    "score": 0,
    "grade": "F",
    "issues": ["Failed to analyze: {error_message}"],
    "recommendations": ["Ensure website is accessible and try again"]
}
```

### Priority Indicators
Issues and recommendations use emojis for priority:
- ❌ **Critical**: Immediate action required
- ⚠️ **Warning**: Should be addressed soon
- 💡 **Suggestion**: Nice to have
- ✨ **Positive**: What's working well

### Grade Calculation
```python
def _calculate_grade(score: float) -> str:
    if score >= 90: return "A"
    elif score >= 80: return "B"
    elif score >= 70: return "C"
    elif score >= 60: return "D"
    else: return "F"
```

### Health Status
Each analyzer provides a health status:
- **Excellent**: 85+ score
- **Good**: 70-84 score
- **Fair**: 50-69 score
- **Poor**: < 50 score

---

## 📚 Usage Examples

### Basic Usage
```python
from app.analyzers.performance_analyzer import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()
result = await analyzer.analyze("https://example.com")

print(f"Score: {result['score']}")
print(f"Grade: {result['grade']}")
print(f"Load Time: {result['load_time']}s")
```

### Parallel Analysis
```python
import asyncio
from app.analyzers import *

async def analyze_website(url: str):
    ux = UXAnalyzer()
    seo = SEOAnalyzer()
    perf = PerformanceAnalyzer()
    content = ContentAnalyzer()
    
    results = await asyncio.gather(
        ux.analyze(url),
        seo.analyze(url),
        perf.analyze(url),
        content.analyze(url)
    )
    
    return {
        'ux': results[0],
        'seo': results[1],
        'performance': results[2],
        'content': results[3]
    }
```

### Score Breakdown Analysis
```python
result = await analyzer.analyze(url)

# Find weakest component
breakdown = result['score_breakdown']
weakest = min(breakdown.items(), key=lambda x: x[1])
print(f"Focus on improving: {weakest[0]} (score: {weakest[1]})")

# Calculate improvement potential
avg_score = sum(breakdown.values()) / len(breakdown)
if avg_score < 70:
    print("High improvement potential!")
```

---

## 🔧 Customization

### Adjusting Thresholds
```python
class CustomPerformanceAnalyzer(PerformanceAnalyzer):
    THRESHOLDS = {
        'load_time': {'excellent': 1.0, 'good': 2.0, 'poor': 3.0},
        # ... customize other thresholds
    }
```

### Adjusting Weights
```python
# In analyzer's analyze() method
weights = {
    'load_time': 30,      # Increase from 25
    'page_size': 10,      # Decrease from 15
    'requests': 10,
    'compression': 10,
    'caching': 20,        # Increase from 15
    'render_blocking': 15,
    'resource_optimization': 5  # Decrease from 10
}
```

---

## 📊 Integration with Analysis Service

The analyzers are used in `app/services/analysis_service.py`:

```python
async def perform_website_analysis(analysis_id: str, website_url: str):
    # Initialize analyzers
    ux_analyzer = UXAnalyzer()
    seo_analyzer = SEOAnalyzer()
    performance_analyzer = PerformanceAnalyzer()
    content_analyzer = ContentAnalyzer()
    
    # Run in parallel
    ux_result, seo_result, perf_result, content_result = await asyncio.gather(
        ux_analyzer.analyze(website_url),
        seo_analyzer.analyze(website_url),
        performance_analyzer.analyze(website_url),
        content_analyzer.analyze(website_url)
    )
    
    # Calculate overall score (equal weights)
    overall_score = (
        ux_result.get("score", 0) * 0.25 +
        seo_result.get("score", 0) * 0.25 +
        perf_result.get("score", 0) * 0.25 +
        content_result.get("score", 0) * 0.25
    )
```

---

## 🚀 Performance Tips

1. **Timeout**: All analyzers use 30s timeout for HTTP requests
2. **Parallel Execution**: Use `asyncio.gather()` for concurrent analysis
3. **Error Handling**: Each analyzer handles exceptions gracefully
4. **Caching**: Consider caching results for frequently analyzed URLs
5. **Rate Limiting**: Implement rate limiting for external URL analysis

---

## 📖 Further Reading

- [ANALYSIS_IMPROVEMENTS.md](./ANALYSIS_IMPROVEMENTS.md) - Detailed improvement documentation
- [BEFORE_AFTER_COMPARISON.md](./BEFORE_AFTER_COMPARISON.md) - Real-world examples
- [Google Core Web Vitals](https://web.dev/vitals/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Flesch Reading Ease](https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests)
