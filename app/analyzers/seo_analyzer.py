import httpx
from bs4 import BeautifulSoup
from typing import Dict, List
from urllib.parse import urlparse


class SEOAnalyzer:
    """Analyze website SEO"""
    
    async def analyze(self, url: str) -> Dict:
        """Perform SEO analysis"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                html = response.text
            
            soup = BeautifulSoup(html, 'html.parser')
            
            issues = []
            recommendations = []
            score = 100
            
            # Meta title
            title = soup.find('title')
            meta_title = title.get_text() if title else None
            if not meta_title:
                issues.append("Missing page title")
                recommendations.append("Add a descriptive page title (50-60 characters)")
                score -= 15
            elif len(meta_title) < 30 or len(meta_title) > 60:
                issues.append("Page title length not optimal")
                recommendations.append("Optimize title length to 50-60 characters")
                score -= 5
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_description = meta_desc.get('content') if meta_desc else None
            if not meta_description:
                issues.append("Missing meta description")
                recommendations.append("Add a compelling meta description (150-160 characters)")
                score -= 15
            elif len(meta_description) < 120 or len(meta_description) > 160:
                issues.append("Meta description length not optimal")
                recommendations.append("Optimize meta description to 150-160 characters")
                score -= 5
            
            # Headings structure
            h1_tags = soup.find_all('h1')
            h2_tags = soup.find_all('h2')
            h3_tags = soup.find_all('h3')
            
            headings_structure = {
                "h1": len(h1_tags),
                "h2": len(h2_tags),
                "h3": len(h3_tags)
            }
            
            if len(h1_tags) == 0:
                issues.append("No H1 tag found")
                recommendations.append("Add a single H1 tag with primary keyword")
                score -= 10
            elif len(h1_tags) > 1:
                issues.append("Multiple H1 tags found")
                recommendations.append("Use only one H1 tag per page")
                score -= 5
            
            # Extract keywords (simplified)
            text_content = soup.get_text()
            words = text_content.lower().split()
            word_freq = {}
            for word in words:
                if len(word) > 4:  # Only words longer than 4 chars
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            keywords = [k[0] for k in keywords]
            
            # Check for canonical URL
            canonical = soup.find('link', attrs={'rel': 'canonical'})
            if not canonical:
                issues.append("Missing canonical URL")
                recommendations.append("Add canonical URL to avoid duplicate content issues")
                score -= 5
            
            # Check for Open Graph tags
            og_tags = soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')})
            if len(og_tags) < 3:
                issues.append("Incomplete Open Graph tags")
                recommendations.append("Add Open Graph tags for better social media sharing")
                score -= 5
            
            # Check for robots meta
            robots = soup.find('meta', attrs={'name': 'robots'})
            if robots and 'noindex' in robots.get('content', '').lower():
                issues.append("Page is set to noindex")
                recommendations.append("Remove noindex if you want the page indexed")
                score -= 20
            
            # Check for SSL (from URL)
            parsed_url = urlparse(url)
            if parsed_url.scheme != 'https':
                issues.append("Website not using HTTPS")
                recommendations.append("Implement SSL certificate for security and SEO")
                score -= 15
            
            return {
                "score": max(0, score),
                "meta_title": meta_title,
                "meta_description": meta_description,
                "headings_structure": headings_structure,
                "keywords": keywords,
                "issues": issues[:10],
                "recommendations": recommendations[:10]
            }
            
        except Exception as e:
            return {
                "score": 0,
                "meta_title": None,
                "meta_description": None,
                "headings_structure": {},
                "keywords": [],
                "issues": [f"Failed to analyze SEO: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"]
            }
