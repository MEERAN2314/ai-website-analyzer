#!/usr/bin/env python3
"""
Test script to verify PDF generation fix
"""
import asyncio
import sys
from app.services.pdf_service import PDFService

async def test_pdf_generation():
    """Test PDF generation with sample data"""
    print("🧪 Testing PDF Generation Fix...")
    print("-" * 60)
    
    # Sample analysis data
    test_data = {
        'id': 'test_123',
        'website_url': 'https://example.com',
        'overall_score': 75.5,
        'ux_analysis': {
            'score': 80,
            'issues': ['Missing viewport meta tag', 'No skip navigation link'],
            'recommendations': ['Add viewport meta tag', 'Add skip link for accessibility']
        },
        'seo_analysis': {
            'score': 70,
            'issues': ['Meta description too short', 'Missing canonical URL'],
            'recommendations': ['Expand meta description to 150-160 characters', 'Add canonical tag']
        },
        'performance_analysis': {
            'score': 75,
            'issues': ['Slow load time (2.3s)', 'No compression enabled'],
            'recommendations': ['Enable Gzip compression', 'Optimize images']
        },
        'content_analysis': {
            'score': 78,
            'issues': ['Content could be more comprehensive (450 words)'],
            'recommendations': ['Expand content to 500+ words']
        },
        'ai_summary': '''
## Overall Assessment
The website shows good potential with a score of 75.5/100. The analysis reveals several areas for improvement, particularly in SEO and performance optimization.

## Key Findings
- UX design is solid with an 80/100 score
- SEO needs attention with a 70/100 score
- Performance is acceptable at 75/100
- Content quality is good at 78/100

## Next Steps
Focus on improving meta descriptions, enabling compression, and expanding content for better search engine visibility.
        ''',
        'priority_recommendations': [
            {
                'title': 'Enable Gzip Compression',
                'description': 'Implement server-side compression to reduce page size by 70%',
                'priority': 'High',
                'impact': 'High',
                'effort': 'Low',
                'category': 'Performance'
            },
            {
                'title': 'Optimize Meta Description',
                'description': 'Expand meta description to 150-160 characters for better CTR',
                'priority': 'High',
                'impact': 'Medium',
                'effort': 'Low',
                'category': 'SEO'
            },
            {
                'title': 'Add Viewport Meta Tag',
                'description': 'Ensure mobile responsiveness with proper viewport configuration',
                'priority': 'Medium',
                'impact': 'High',
                'effort': 'Low',
                'category': 'UX'
            }
        ]
    }
    
    try:
        print("📄 Initializing PDF Service...")
        pdf_service = PDFService()
        
        print("📝 Generating PDF report...")
        pdf_path = await pdf_service.generate_report(test_data)
        
        print(f"\n✅ SUCCESS!")
        print(f"📁 PDF generated at: {pdf_path}")
        print(f"🌐 Access URL: /static/pdfs/analysis_test_123.pdf")
        print("\n" + "=" * 60)
        print("✅ PDF generation is working correctly!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
        print("❌ PDF generation has issues that need fixing")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = asyncio.run(test_pdf_generation())
    sys.exit(0 if success else 1)
