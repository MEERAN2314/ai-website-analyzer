import httpx
from bs4 import BeautifulSoup
from typing import Dict


class UXAnalyzer:
    """Analyze website UX/UI"""
    
    async def analyze(self, url: str) -> Dict:
        """Perform UX analysis"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                html = response.text
            
            soup = BeautifulSoup(html, 'html.parser')
            
            issues = []
            recommendations = []
            score = 100
            
            # Check for mobile viewport
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            mobile_friendly = bool(viewport)
            if not mobile_friendly:
                issues.append("Missing mobile viewport meta tag")
                recommendations.append("Add viewport meta tag for mobile responsiveness")
                score -= 15
            
            # Check navigation
            nav = soup.find('nav') or soup.find(attrs={'role': 'navigation'})
            if not nav:
                issues.append("No clear navigation structure found")
                recommendations.append("Add a clear navigation menu")
                score -= 10
            
            # Check for forms
            forms = soup.find_all('form')
            for form in forms:
                if not form.find('label'):
                    issues.append("Forms missing labels for accessibility")
                    recommendations.append("Add labels to all form inputs")
                    score -= 10
                    break
            
            # Check for images without alt text
            images = soup.find_all('img')
            images_without_alt = [img for img in images if not img.get('alt')]
            if images_without_alt:
                issues.append(f"{len(images_without_alt)} images missing alt text")
                recommendations.append("Add descriptive alt text to all images")
                score -= 10
            
            # Check for heading structure
            h1_tags = soup.find_all('h1')
            if len(h1_tags) == 0:
                issues.append("No H1 heading found")
                recommendations.append("Add a clear H1 heading to the page")
                score -= 10
            elif len(h1_tags) > 1:
                issues.append("Multiple H1 headings found")
                recommendations.append("Use only one H1 heading per page")
                score -= 5
            
            # Check for buttons/CTAs
            buttons = soup.find_all(['button', 'a'])
            cta_count = len([b for b in buttons if b.get_text().strip()])
            if cta_count < 2:
                issues.append("Limited call-to-action elements")
                recommendations.append("Add clear call-to-action buttons")
                score -= 10
            
            # Accessibility score (simplified)
            accessibility_score = max(0, 100 - len(issues) * 10)
            
            return {
                "score": max(0, score),
                "issues": issues[:10],  # Limit to top 10
                "recommendations": recommendations[:10],
                "mobile_friendly": mobile_friendly,
                "accessibility_score": accessibility_score
            }
            
        except Exception as e:
            return {
                "score": 0,
                "issues": [f"Failed to analyze UX: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"],
                "mobile_friendly": False,
                "accessibility_score": 0
            }
