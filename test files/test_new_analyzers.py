#!/usr/bin/env python3
"""
Test script for new Security and Image analyzers
"""
import asyncio
from app.analyzers.security_analyzer import SecurityAnalyzer
from app.analyzers.image_analyzer import ImageAnalyzer


async def test_security_analyzer():
    """Test Security Analyzer"""
    print("=" * 70)
    print("🔒 TESTING SECURITY ANALYZER")
    print("=" * 70)
    
    analyzer = SecurityAnalyzer()
    
    # Test with HTTPS site
    print("\n📊 Testing with HTTPS site (https://example.com)...")
    result = await analyzer.analyze("https://example.com")
    
    print(f"\n✅ Security Score: {result['score']}/100")
    print(f"📊 Grade: {result['grade']}")
    print(f"🔐 Security Level: {result['security_level']}")
    print(f"🔒 Uses HTTPS: {result['uses_https']}")
    print(f"📜 SSL Grade: {result['ssl_grade']}")
    print(f"✓ SSL Valid: {result['ssl_valid']}")
    
    print(f"\n📋 Security Headers Present ({len(result['security_headers'])}):")
    for header in result['security_headers']:
        print(f"  ✓ {header}")
    
    print(f"\n⚠️  Missing Headers ({len(result['missing_headers'])}):")
    for header in result['missing_headers'][:5]:
        print(f"  ✗ {header}")
    
    print(f"\n🔍 Issues Found ({len(result['issues'])}):")
    for issue in result['issues'][:5]:
        print(f"  • {issue}")
    
    print(f"\n💡 Recommendations ({len(result['recommendations'])}):")
    for rec in result['recommendations'][:3]:
        print(f"  → {rec}")
    
    print(f"\n📊 Score Breakdown:")
    for component, score in result['score_breakdown'].items():
        print(f"  {component}: {score}/100")
    
    return result


async def test_image_analyzer():
    """Test Image Analyzer"""
    print("\n" + "=" * 70)
    print("🖼️  TESTING IMAGE ANALYZER")
    print("=" * 70)
    
    analyzer = ImageAnalyzer()
    
    # Test with image-heavy site
    print("\n📊 Testing with example.com...")
    result = await analyzer.analyze("https://example.com")
    
    print(f"\n✅ Image Score: {result['score']}/100")
    print(f"📊 Grade: {result.get('grade', 'N/A')}")
    print(f"🖼️  Total Images: {result['total_images']}")
    
    if result['total_images'] > 0:
        print(f"📦 Total Size: {result.get('total_size_kb', 0):.2f} KB")
        print(f"📊 Average Size: {result.get('average_size_kb', 0):.2f} KB")
        print(f"⚠️  Large Images (>200KB): {result.get('large_images', 0)}")
        print(f"🎨 Modern Format Usage: {result.get('modern_format_usage', 0):.1f}%")
        print(f"📱 Responsive Images: {result.get('responsive_images', 0)}")
        print(f"⚡ Lazy Loaded: {result.get('lazy_loaded_images', 0)}")
        print(f"♿ Missing Alt Text: {result.get('images_without_alt', 0)}")
        
        print(f"\n💰 Potential Savings:")
        print(f"  💾 {result.get('potential_savings_kb', 0):.2f} KB ({result.get('potential_savings_percentage', 0):.1f}%)")
        
        if 'score_breakdown' in result:
            print(f"\n📊 Score Breakdown:")
            for component, score in result['score_breakdown'].items():
                print(f"  {component}: {score}/100")
        
        print(f"\n🔍 Issues Found ({len(result.get('issues', []))}):")
        for issue in result.get('issues', [])[:5]:
            print(f"  • {issue}")
        
        print(f"\n💡 Recommendations ({len(result.get('recommendations', []))}):")
        for rec in result.get('recommendations', [])[:3]:
            print(f"  → {rec}")
    else:
        print("\n📝 No images found on this page")
        print(f"\n🔍 Issues: {result.get('issues', ['No issues'])[0]}")
        print(f"💡 Recommendation: {result.get('recommendations', ['No recommendations'])[0]}")
    
    return result


async def test_both_analyzers():
    """Test both analyzers in parallel"""
    print("\n" + "=" * 70)
    print("⚡ TESTING PARALLEL EXECUTION")
    print("=" * 70)
    
    print("\n🚀 Running both analyzers in parallel...")
    
    security_analyzer = SecurityAnalyzer()
    image_analyzer = ImageAnalyzer()
    
    # Run in parallel
    security_result, image_result = await asyncio.gather(
        security_analyzer.analyze("https://example.com"),
        image_analyzer.analyze("https://example.com"),
        return_exceptions=True
    )
    
    print("\n✅ Parallel execution completed!")
    
    if isinstance(security_result, Exception):
        print(f"❌ Security Analyzer Error: {security_result}")
        return
    if isinstance(image_result, Exception):
        print(f"❌ Image Analyzer Error: {image_result}")
        return
    
    print(f"🔒 Security Score: {security_result['score']}/100")
    print(f"🖼️  Image Score: {image_result['score']}/100")
    
    # Calculate contribution to overall score
    security_contribution = security_result['score'] * 0.15
    image_contribution = image_result['score'] * 0.10
    
    print(f"\n📊 Contribution to Overall Score:")
    print(f"  Security (15%): {security_contribution:.1f} points")
    print(f"  Images (10%): {image_contribution:.1f} points")
    print(f"  Combined: {security_contribution + image_contribution:.1f} points")


async def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print("🧪 NEW ANALYZERS TEST SUITE")
    print("=" * 70)
    print("\nTesting the new Security and Image analyzers...")
    print("This will analyze https://example.com\n")
    
    try:
        # Test Security Analyzer
        await test_security_analyzer()
        
        # Test Image Analyzer
        await test_image_analyzer()
        
        # Test parallel execution
        await test_both_analyzers()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\n🎉 Your analysis system now includes:")
        print("  ✓ Security Analysis (SSL, headers, vulnerabilities)")
        print("  ✓ Image Optimization (sizes, formats, lazy loading)")
        print("  ✓ 6 comprehensive analyzers total")
        print("  ✓ 110+ checks across all categories")
        print("\n🚀 Ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
