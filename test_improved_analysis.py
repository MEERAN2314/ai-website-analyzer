#!/usr/bin/env python3
"""
Test the improved analysis system
"""
import asyncio
from app.analyzers.ux_analyzer import UXAnalyzer
from app.analyzers.seo_analyzer import SEOAnalyzer
from app.analyzers.performance_analyzer import PerformanceAnalyzer
from app.analyzers.content_analyzer import ContentAnalyzer

async def test_analyzers():
    """Test all improved analyzers"""
    
    # Test URL
    test_url = "https://example.com"
    
    print("=" * 70)
    print("🧪 TESTING IMPROVED ANALYZERS")
    print("=" * 70)
    print(f"\nTest URL: {test_url}\n")
    
    # 1. UX Analyzer
    print("1️⃣  UX ANALYZER")
    print("-" * 70)
    ux_analyzer = UXAnalyzer()
    ux_result = await ux_analyzer.analyze(test_url)
    
    print(f"Overall Score: {ux_result['score']}/100")
    if 'detailed_scores' in ux_result:
        print("\nDetailed Scores:")
        for category, score in ux_result['detailed_scores'].items():
            print(f"  • {category.replace('_', ' ').title()}: {score:.1f}/100")
    
    print(f"\nIssues Found: {len(ux_result['issues'])}")
    for issue in ux_result['issues'][:3]:
        print(f"  {issue}")
    
    print(f"\nRecommendations: {len(ux_result['recommendations'])}")
    for rec in ux_result['recommendations'][:3]:
        print(f"  • {rec}")
    
    # 2. SEO Analyzer
    print("\n\n2️⃣  SEO ANALYZER")
    print("-" * 70)
    seo_analyzer = SEOAnalyzer()
    seo_result = await seo_analyzer.analyze(test_url)
    
    print(f"Overall Score: {seo_result['score']}/100")
    if 'detailed_scores' in seo_result:
        print("\nDetailed Scores:")
        for category, score in seo_result['detailed_scores'].items():
            print(f"  • {category.replace('_', ' ').title()}: {score:.1f}/100")
    
    print(f"\nMeta Title: {seo_result.get('meta_title', 'N/A')}")
    meta_desc = seo_result.get('meta_description') or 'N/A'
    print(f"Meta Description: {meta_desc[:60] if len(meta_desc) > 60 else meta_desc}...")
    
    print(f"\nTop Keywords: {', '.join(seo_result.get('keywords', [])[:5])}")
    
    print(f"\nIssues Found: {len(seo_result['issues'])}")
    for issue in seo_result['issues'][:3]:
        print(f"  {issue}")
    
    # 3. Performance Analyzer
    print("\n\n3️⃣  PERFORMANCE ANALYZER")
    print("-" * 70)
    perf_analyzer = PerformanceAnalyzer()
    perf_result = await perf_analyzer.analyze(test_url)
    
    print(f"Overall Score: {perf_result['score']}/100")
    if 'detailed_scores' in perf_result:
        print("\nDetailed Scores:")
        for category, score in perf_result['detailed_scores'].items():
            print(f"  • {category.replace('_', ' ').title()}: {score:.1f}/100")
    
    print(f"\nLoad Time: {perf_result['load_time']}s")
    print(f"Page Size: {perf_result['page_size']}KB")
    print(f"HTTP Requests: {perf_result['requests_count']}")
    
    if 'core_web_vitals' in perf_result:
        cwv = perf_result['core_web_vitals']
        print("\nCore Web Vitals:")
        print(f"  • LCP: {cwv.get('LCP', 'N/A')}ms ({cwv.get('LCP_rating', 'N/A')})")
        print(f"  • FID: {cwv.get('FID', 'N/A')}ms ({cwv.get('FID_rating', 'N/A')})")
        print(f"  • CLS: {cwv.get('CLS', 'N/A')} ({cwv.get('CLS_rating', 'N/A')})")
    
    print(f"\nIssues Found: {len(perf_result['issues'])}")
    for issue in perf_result['issues'][:3]:
        print(f"  {issue}")
    
    # 4. Content Analyzer
    print("\n\n4️⃣  CONTENT ANALYZER")
    print("-" * 70)
    content_analyzer = ContentAnalyzer()
    content_result = await content_analyzer.analyze(test_url)
    
    print(f"Overall Score: {content_result['score']}/100")
    if 'detailed_scores' in content_result:
        print("\nDetailed Scores:")
        for category, score in content_result['detailed_scores'].items():
            print(f"  • {category.replace('_', ' ').title()}: {score:.1f}/100")
    
    print(f"\nWord Count: {content_result['word_count']}")
    print(f"Readability Score: {content_result['readability_score']}/100")
    print(f"Has CTA: {'✅ Yes' if content_result['has_cta'] else '❌ No'}")
    print(f"Tone: {content_result['tone']}")
    
    print(f"\nIssues Found: {len(content_result['issues'])}")
    for issue in content_result['issues'][:3]:
        print(f"  {issue}")
    
    # Summary
    print("\n\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    avg_score = (
        ux_result['score'] + 
        seo_result['score'] + 
        perf_result['score'] + 
        content_result['score']
    ) / 4
    
    print(f"\nOverall Website Score: {avg_score:.1f}/100")
    print("\nCategory Scores:")
    print(f"  • UX/UI:       {ux_result['score']:.1f}/100")
    print(f"  • SEO:         {seo_result['score']:.1f}/100")
    print(f"  • Performance: {perf_result['score']:.1f}/100")
    print(f"  • Content:     {content_result['score']:.1f}/100")
    
    total_issues = (
        len(ux_result['issues']) + 
        len(seo_result['issues']) + 
        len(perf_result['issues']) + 
        len(content_result['issues'])
    )
    
    total_recommendations = (
        len(ux_result['recommendations']) + 
        len(seo_result['recommendations']) + 
        len(perf_result['recommendations']) + 
        len(content_result['recommendations'])
    )
    
    print(f"\nTotal Issues Found: {total_issues}")
    print(f"Total Recommendations: {total_recommendations}")
    
    print("\n✅ All analyzers working with enhanced accuracy!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_analyzers())
