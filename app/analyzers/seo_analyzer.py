import httpx
from bs4 import BeautifulSoup
from typing import Dict, List
from urllib.parse import urlparse, urljoin
import re


class SEOAnalyzer:
    """Enhanced SEO analyzer with comprehensive checks"""
    
    def __init__(self):
        self.weights = {
            'meta_tags': 25,
            'content_structure': 20,
            'technical': 25,
            'links': 15,
            'social': 15
        }
    
    async def analyze(self, url: str) -> Dict:
        """Perform comprehensive SEO analysis"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                html = response.text
                headers = response.headers
            
            soup = BeautifulSoup(html, 'html.parser')
            
            issues = []
            recommendations = []
            scores = {}
            
            # 1. Meta Tags (25 points)
            meta_score, meta_issues, meta_recs, meta_data = self._check_meta_tags(soup)
            scores['meta_tags'] = meta_score
            issues.extend(meta_issues)
            recommendations.extend(meta_recs)
            
            # 2. Content Structure (20 points)
            content_score, content_issues, content_recs, headings = self._check_content_structure(soup)
            scores['content_structure'] = content_score
            issues.extend(content_issues)
            recommendations.extend(content_recs)
            
            # 3. Technical SEO (25 points)
            tech_score, tech_issues, tech_recs = self._check_technical_seo(soup, url, headers)
            scores['technical'] = tech_score
            issues.extend(tech_issues)
            recommendations.extend(tech_recs)
            
            # 4. Links (15 points)
            links_score, links_issues, links_recs = self._check_links(soup, url)
            scores['links'] = links_score
            issues.extend(links_issues)
            recommendations.extend(links_recs)
            
            # 5. Social & Rich Snippets (15 points)
            social_score, social_issues, social_recs = self._check_social_and_rich_snippets(soup)
            scores['social'] = social_score
            issues.extend(social_issues)
            recommendations.extend(social_recs)
            
            # Extract keywords
            keywords = self._extract_keywords(soup)
            
            # Calculate weighted total score
            total_score = sum(scores[key] * self.weights[key] / 100 for key in scores)
            
            return {
                "score": round(max(0, min(100, total_score)), 1),
                "meta_title": meta_data['title'],
                "meta_description": meta_data['description'],
                "headings_structure": headings,
                "keywords": keywords,
                "issues": issues[:15],
                "recommendations": recommendations[:15],
                "detailed_scores": scores
            }
            
        except Exception as e:
            return {
                "score": 0,
                "meta_title": None,
                "meta_description": None,
                "headings_structure": {},
                "keywords": [],
                "issues": [f"Failed to analyze SEO: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"],
                "detailed_scores": {}
            }
    
    def _check_meta_tags(self, soup: BeautifulSoup) -> tuple:
        """Check meta tags (25 points)"""
        score = 100
        issues = []
        recommendations = []
        meta_data = {'title': None, 'description': None}
        
        # Title tag
        title = soup.find('title')
        meta_data['title'] = title.get_text().strip() if title else None
        
        if not meta_data['title']:
            issues.append("❌ Missing page title tag")
            recommendations.append("Add a descriptive title tag (50-60 characters)")
            score -= 40
        else:
            title_len = len(meta_data['title'])
            if title_len < 30:
                issues.append(f"⚠️ Title too short ({title_len} chars)")
                recommendations.append("Expand title to 50-60 characters for better SEO")
                score -= 20
            elif title_len > 60:
                issues.append(f"⚠️ Title too long ({title_len} chars, may be truncated)")
                recommendations.append("Shorten title to 50-60 characters")
                score -= 15
            
            # Check for keyword stuffing
            words = meta_data['title'].lower().split()
            if len(words) != len(set(words)):
                issues.append("⚠️ Possible keyword stuffing in title")
                recommendations.append("Use natural language in title, avoid repetition")
                score -= 10
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_data['description'] = meta_desc.get('content').strip() if meta_desc and meta_desc.get('content') else None
        
        if not meta_data['description']:
            issues.append("❌ Missing meta description")
            recommendations.append("Add compelling meta description (150-160 characters)")
            score -= 35
        else:
            desc_len = len(meta_data['description'])
            if desc_len < 120:
                issues.append(f"⚠️ Meta description too short ({desc_len} chars)")
                recommendations.append("Expand description to 150-160 characters")
                score -= 20
            elif desc_len > 160:
                issues.append(f"⚠️ Meta description too long ({desc_len} chars)")
                recommendations.append("Shorten description to 150-160 characters")
                score -= 15
        
        # Meta keywords (deprecated but check)
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            recommendations.append("Meta keywords tag is deprecated, focus on content quality")
        
        return max(0, score), issues, recommendations, meta_data
    
    def _check_content_structure(self, soup: BeautifulSoup) -> tuple:
        """Check content structure (20 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Heading analysis
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')
        h4_tags = soup.find_all('h4')
        
        headings_structure = {
            "h1": len(h1_tags),
            "h2": len(h2_tags),
            "h3": len(h3_tags),
            "h4": len(h4_tags)
        }
        
        # H1 check
        if len(h1_tags) == 0:
            issues.append("❌ No H1 tag found")
            recommendations.append("Add a single H1 tag with primary keyword")
            score -= 35
        elif len(h1_tags) > 1:
            issues.append(f"⚠️ Multiple H1 tags found ({len(h1_tags)})")
            recommendations.append("Use only one H1 tag per page for SEO")
            score -= 25
        else:
            h1_text = h1_tags[0].get_text().strip()
            if len(h1_text) < 20:
                issues.append("⚠️ H1 tag is very short")
                recommendations.append("Make H1 more descriptive (20-70 characters)")
                score -= 15
            elif len(h1_text) > 70:
                issues.append("⚠️ H1 tag is too long")
                recommendations.append("Keep H1 concise (20-70 characters)")
                score -= 10
        
        # H2 structure
        if len(h2_tags) == 0:
            issues.append("⚠️ No H2 tags found")
            recommendations.append("Add H2 tags to structure content with keywords")
            score -= 20
        elif len(h2_tags) < 2:
            recommendations.append("Add more H2 tags to better organize content")
            score -= 10
        
        # Heading hierarchy
        if len(h3_tags) > 0 and len(h2_tags) == 0:
            issues.append("⚠️ Broken heading hierarchy (H3 without H2)")
            recommendations.append("Maintain proper heading hierarchy (H1 → H2 → H3)")
            score -= 15
        
        # Content length check
        text_content = soup.get_text()
        words = text_content.split()
        word_count = len(words)
        
        if word_count < 300:
            issues.append(f"⚠️ Low content volume ({word_count} words)")
            recommendations.append("Add more quality content (aim for 500+ words)")
            score -= 20
        
        return max(0, score), issues, recommendations, headings_structure
    
    def _check_technical_seo(self, soup: BeautifulSoup, url: str, headers: dict) -> tuple:
        """Check technical SEO (25 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # HTTPS check
        parsed_url = urlparse(url)
        if parsed_url.scheme != 'https':
            issues.append("❌ Website not using HTTPS")
            recommendations.append("Implement SSL certificate for security and SEO boost")
            score -= 30
        
        # Canonical URL
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if not canonical:
            issues.append("⚠️ Missing canonical URL")
            recommendations.append("Add canonical URL to prevent duplicate content issues")
            score -= 15
        elif canonical.get('href'):
            canonical_url = canonical.get('href')
            if not canonical_url.startswith('http'):
                issues.append("⚠️ Canonical URL is relative, should be absolute")
                recommendations.append("Use absolute URLs for canonical tags")
                score -= 10
        
        # Robots meta tag
        robots = soup.find('meta', attrs={'name': 'robots'})
        if robots:
            content = robots.get('content', '').lower()
            if 'noindex' in content:
                issues.append("❌ Page is set to noindex (won't appear in search)")
                recommendations.append("Remove noindex if you want the page indexed")
                score -= 40
            if 'nofollow' in content:
                issues.append("⚠️ Page is set to nofollow (links won't be followed)")
                recommendations.append("Remove nofollow unless intentional")
                score -= 20
        
        # Structured data (Schema.org)
        structured_data = soup.find_all('script', type='application/ld+json')
        if len(structured_data) == 0:
            issues.append("⚠️ No structured data (Schema.org) found")
            recommendations.append("Add JSON-LD structured data for rich snippets")
            score -= 15
        
        # XML Sitemap reference
        sitemap_link = soup.find('link', attrs={'rel': 'sitemap'})
        if not sitemap_link:
            recommendations.append("Consider adding sitemap reference in HTML")
            score -= 5
        
        # Language declaration
        html_tag = soup.find('html')
        if html_tag and not html_tag.get('lang'):
            issues.append("⚠️ Missing language declaration")
            recommendations.append("Add lang attribute to <html> tag (e.g., lang='en')")
            score -= 10
        
        # Mobile-friendly
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            issues.append("❌ Missing viewport meta tag (not mobile-friendly)")
            recommendations.append("Add viewport meta tag for mobile SEO")
            score -= 20
        
        return max(0, score), issues, recommendations
    
    def _check_links(self, soup: BeautifulSoup, base_url: str) -> tuple:
        """Check links (15 points)"""
        score = 100
        issues = []
        recommendations = []
        
        all_links = soup.find_all('a', href=True)
        
        if len(all_links) == 0:
            issues.append("❌ No links found on page")
            recommendations.append("Add internal and external links for better SEO")
            return 0, issues, recommendations
        
        # Categorize links
        internal_links = []
        external_links = []
        broken_links = []
        
        for link in all_links:
            href = link.get('href', '')
            
            if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
            
            if href.startswith('http'):
                if urlparse(base_url).netloc in href:
                    internal_links.append(link)
                else:
                    external_links.append(link)
            else:
                internal_links.append(link)
        
        # Internal linking
        if len(internal_links) < 3:
            issues.append("⚠️ Very few internal links")
            recommendations.append("Add more internal links to improve site structure")
            score -= 25
        
        # External links
        if len(external_links) == 0:
            recommendations.append("Consider adding relevant external links for credibility")
            score -= 10
        
        # Check for nofollow on external links
        external_with_nofollow = [link for link in external_links if 'nofollow' in link.get('rel', [])]
        if external_links and len(external_with_nofollow) == 0:
            recommendations.append("Consider adding rel='nofollow' to external links")
            score -= 5
        
        # Check for descriptive anchor text
        generic_anchors = [link for link in all_links if link.get_text().strip().lower() in ['click here', 'here', 'read more', 'more', 'link']]
        if generic_anchors:
            issues.append(f"⚠️ {len(generic_anchors)} links with generic anchor text")
            recommendations.append("Use descriptive anchor text with keywords")
            score -= 20
        
        # Check for broken links (empty href)
        empty_links = [link for link in all_links if not link.get('href').strip()]
        if empty_links:
            issues.append(f"❌ {len(empty_links)} links with empty href")
            recommendations.append("Fix or remove broken links")
            score -= 25
        
        return max(0, score), issues, recommendations
    
    def _check_social_and_rich_snippets(self, soup: BeautifulSoup) -> tuple:
        """Check social media and rich snippets (15 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Open Graph tags
        og_tags = soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')})
        og_properties = [tag.get('property') for tag in og_tags]
        
        required_og = ['og:title', 'og:description', 'og:image', 'og:url']
        missing_og = [prop for prop in required_og if prop not in og_properties]
        
        if len(missing_og) == len(required_og):
            issues.append("❌ No Open Graph tags found")
            recommendations.append("Add Open Graph tags for better social media sharing")
            score -= 40
        elif missing_og:
            issues.append(f"⚠️ Missing Open Graph tags: {', '.join(missing_og)}")
            recommendations.append(f"Add missing OG tags: {', '.join(missing_og)}")
            score -= 20
        
        # Twitter Card tags
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        
        if len(twitter_tags) == 0:
            issues.append("⚠️ No Twitter Card tags found")
            recommendations.append("Add Twitter Card tags for better Twitter sharing")
            score -= 25
        elif len(twitter_tags) < 3:
            recommendations.append("Add more Twitter Card tags (card, title, description, image)")
            score -= 15
        
        # Favicon
        favicon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
        if not favicon:
            recommendations.append("Add favicon for better brand recognition")
            score -= 10
        
        # Schema.org structured data
        structured_data = soup.find_all('script', type='application/ld+json')
        if len(structured_data) == 0:
            recommendations.append("Add Schema.org structured data for rich snippets")
            score -= 15
        
        return max(0, score), issues, recommendations
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract potential keywords from content"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        text_content = soup.get_text().lower()
        
        # Remove special characters and split
        words = re.findall(r'\b[a-z]{4,}\b', text_content)
        
        # Common stop words to exclude
        stop_words = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'will', 
                     'your', 'their', 'what', 'when', 'where', 'which', 'about', 'would',
                     'there', 'could', 'other', 'than', 'then', 'them', 'these', 'those'}
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        return [k[0] for k in keywords]
