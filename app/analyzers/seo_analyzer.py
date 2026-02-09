import httpx
from bs4 import BeautifulSoup
from typing import Dict, List
from urllib.parse import urlparse, urljoin
import re
from collections import Counter


class SEOAnalyzer:
    """Analyze website SEO with comprehensive checks"""
    
    # SEO best practice thresholds
    THRESHOLDS = {
        'title': {'min': 30, 'ideal_min': 50, 'ideal_max': 60, 'max': 70},
        'description': {'min': 120, 'ideal_min': 150, 'ideal_max': 160, 'max': 200},
        'h1_length': {'min': 20, 'max': 70},
        'keyword_density': {'min': 0.5, 'max': 3.0},  # percentage
        'internal_links': {'min': 3, 'ideal': 10},
        'external_links': {'max': 50}
    }
    
    async def analyze(self, url: str) -> Dict:
        """Perform comprehensive SEO analysis"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                html = response.text
                final_url = str(response.url)
            
            soup = BeautifulSoup(html, 'html.parser')
            
            issues = []
            recommendations = []
            
            # Analyze all SEO components
            title_score, title_data = self._analyze_title(soup, issues, recommendations)
            description_score, description_data = self._analyze_description(soup, issues, recommendations)
            headings_score, headings_data = self._analyze_headings(soup, issues, recommendations)
            content_score, content_data = self._analyze_content(soup, issues, recommendations)
            technical_score, technical_data = self._analyze_technical_seo(soup, url, final_url, issues, recommendations)
            links_score, links_data = self._analyze_links(soup, url, issues, recommendations)
            social_score, social_data = self._analyze_social_meta(soup, issues, recommendations)
            structured_score, structured_data = self._analyze_structured_data(soup, issues, recommendations)
            
            # Weighted scoring
            weights = {
                'title': 15,
                'description': 12,
                'headings': 12,
                'content': 15,
                'technical': 20,
                'links': 10,
                'social': 8,
                'structured': 8
            }
            
            score_components = {
                'title': title_score,
                'description': description_score,
                'headings': headings_score,
                'content': content_score,
                'technical': technical_score,
                'links': links_score,
                'social': social_score,
                'structured': structured_score
            }
            
            final_score = sum(score_components[k] * (weights[k] / 100) for k in weights)
            
            # Calculate SEO grade
            grade = self._calculate_grade(final_score)
            
            # Keyword analysis
            keywords = self._extract_keywords(soup, title_data.get('text', ''))
            
            return {
                "score": round(final_score, 1),
                "grade": grade,
                "meta_title": title_data.get('text'),
                "meta_title_length": title_data.get('length', 0),
                "meta_description": description_data.get('text'),
                "meta_description_length": description_data.get('length', 0),
                "headings_structure": headings_data.get('structure', {}),
                "h1_text": headings_data.get('h1_text'),
                "keywords": keywords,
                "keyword_density": content_data.get('keyword_density', {}),
                "word_count": content_data.get('word_count', 0),
                "internal_links": links_data.get('internal', 0),
                "external_links": links_data.get('external', 0),
                "broken_links": links_data.get('broken', []),
                "has_sitemap": technical_data.get('has_sitemap', False),
                "has_robots_txt": technical_data.get('has_robots_txt', False),
                "is_mobile_friendly": technical_data.get('mobile_friendly', False),
                "uses_https": technical_data.get('https', False),
                "canonical_url": technical_data.get('canonical'),
                "score_breakdown": {k: round(v, 1) for k, v in score_components.items()},
                "issues": issues,
                "recommendations": recommendations,
                "seo_health": self._calculate_seo_health(score_components)
            }
            
        except Exception as e:
            return {
                "score": 0,
                "grade": "F",
                "meta_title": None,
                "meta_description": None,
                "headings_structure": {},
                "keywords": [],
                "issues": [f"Failed to analyze SEO: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"]
            }
    
    def _analyze_title(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze page title"""
        title = soup.find('title')
        title_text = title.get_text().strip() if title else None
        title_length = len(title_text) if title_text else 0
        
        score = 100
        
        if not title_text:
            issues.append("❌ Critical: Missing page title tag")
            recommendations.append("🎯 Add a unique, descriptive title tag (50-60 characters)")
            score = 0
        else:
            if title_length < self.THRESHOLDS['title']['min']:
                issues.append(f"⚠️ Title too short ({title_length} chars) - May not be descriptive enough")
                recommendations.append(f"📝 Expand title to {self.THRESHOLDS['title']['ideal_min']}-{self.THRESHOLDS['title']['ideal_max']} characters")
                score = 60
            elif title_length > self.THRESHOLDS['title']['max']:
                issues.append(f"⚠️ Title too long ({title_length} chars) - May be truncated in search results")
                recommendations.append(f"✂️ Shorten title to {self.THRESHOLDS['title']['ideal_min']}-{self.THRESHOLDS['title']['ideal_max']} characters")
                score = 70
            elif title_length < self.THRESHOLDS['title']['ideal_min'] or title_length > self.THRESHOLDS['title']['ideal_max']:
                recommendations.append(f"💡 Title length ({title_length} chars) is acceptable but could be optimized to {self.THRESHOLDS['title']['ideal_min']}-{self.THRESHOLDS['title']['ideal_max']} chars")
                score = 85
            
            # Check for keyword placement
            if title_text and len(title_text.split()) < 3:
                issues.append("⚠️ Title may be too generic")
                recommendations.append("🎯 Include primary keywords in title for better relevance")
                score = min(score, 75)
        
        return score, {'text': title_text, 'length': title_length}
    
    def _analyze_description(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        desc_text = meta_desc.get('content').strip() if meta_desc and meta_desc.get('content') else None
        desc_length = len(desc_text) if desc_text else 0
        
        score = 100
        
        if not desc_text:
            issues.append("❌ Critical: Missing meta description")
            recommendations.append("📄 Add compelling meta description (150-160 characters) to improve CTR")
            score = 0
        else:
            if desc_length < self.THRESHOLDS['description']['min']:
                issues.append(f"⚠️ Meta description too short ({desc_length} chars)")
                recommendations.append(f"📝 Expand description to {self.THRESHOLDS['description']['ideal_min']}-{self.THRESHOLDS['description']['ideal_max']} characters")
                score = 60
            elif desc_length > self.THRESHOLDS['description']['max']:
                issues.append(f"⚠️ Meta description too long ({desc_length} chars) - Will be truncated")
                recommendations.append(f"✂️ Shorten description to {self.THRESHOLDS['description']['ideal_min']}-{self.THRESHOLDS['description']['ideal_max']} characters")
                score = 70
            elif desc_length < self.THRESHOLDS['description']['ideal_min'] or desc_length > self.THRESHOLDS['description']['ideal_max']:
                recommendations.append(f"💡 Description length ({desc_length} chars) is acceptable but could be optimized")
                score = 85
        
        return score, {'text': desc_text, 'length': desc_length}
    
    def _analyze_headings(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze heading structure"""
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')
        h4_tags = soup.find_all('h4')
        
        score = 100
        h1_text = None
        
        if len(h1_tags) == 0:
            issues.append("❌ Critical: No H1 heading found")
            recommendations.append("🏷️ Add a single H1 tag with primary keyword")
            score = 30
        elif len(h1_tags) > 1:
            issues.append(f"⚠️ Multiple H1 tags found ({len(h1_tags)}) - Use only one per page")
            recommendations.append("🎯 Consolidate to single H1 tag for better SEO")
            score = 60
            h1_text = h1_tags[0].get_text().strip()
        else:
            h1_text = h1_tags[0].get_text().strip()
            h1_length = len(h1_text)
            
            if h1_length < self.THRESHOLDS['h1_length']['min']:
                issues.append(f"⚠️ H1 too short ({h1_length} chars)")
                recommendations.append("📝 Make H1 more descriptive (20-70 characters)")
                score = 75
            elif h1_length > self.THRESHOLDS['h1_length']['max']:
                issues.append(f"⚠️ H1 too long ({h1_length} chars)")
                recommendations.append("✂️ Shorten H1 to 20-70 characters")
                score = 80
        
        # Check heading hierarchy
        if len(h2_tags) == 0 and len(h3_tags) > 0:
            issues.append("⚠️ Poor heading hierarchy - H3 without H2")
            recommendations.append("📊 Use proper heading hierarchy (H1 → H2 → H3)")
            score = min(score, 70)
        
        if len(h2_tags) < 2:
            recommendations.append("💡 Add more H2 headings to improve content structure")
            score = min(score, 85)
        
        structure = {
            "h1": len(h1_tags),
            "h2": len(h2_tags),
            "h3": len(h3_tags),
            "h4": len(h4_tags)
        }
        
        return score, {'structure': structure, 'h1_text': h1_text}
    
    def _analyze_content(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze content quality and keyword usage"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        words = text.lower().split()
        word_count = len(words)
        
        score = 100
        
        # Analyze word count
        if word_count < 300:
            issues.append(f"❌ Thin content ({word_count} words) - Search engines prefer 500+ words")
            recommendations.append("📝 Add comprehensive, valuable content (target 500-1000+ words)")
            score = 40
        elif word_count < 500:
            issues.append(f"⚠️ Content could be more comprehensive ({word_count} words)")
            recommendations.append("📄 Expand content to 500+ words for better rankings")
            score = 70
        elif word_count < 800:
            recommendations.append(f"💡 Good content length ({word_count} words) - Consider expanding to 1000+ for competitive topics")
            score = 90
        
        # Keyword density analysis
        word_freq = Counter(word for word in words if len(word) > 3)
        total_words = len(words)
        keyword_density = {}
        
        if total_words > 0:
            top_words = word_freq.most_common(5)
            for word, count in top_words:
                density = (count / total_words) * 100
                keyword_density[word] = round(density, 2)
                
                if density > self.THRESHOLDS['keyword_density']['max']:
                    issues.append(f"⚠️ Keyword '{word}' may be over-optimized ({density:.1f}% density)")
                    recommendations.append("⚖️ Reduce keyword density to avoid keyword stuffing (aim for 1-2%)")
                    score = min(score, 75)
        
        return score, {'word_count': word_count, 'keyword_density': keyword_density}
    
    def _analyze_technical_seo(self, soup: BeautifulSoup, url: str, final_url: str, issues: List, recommendations: List) -> tuple:
        """Analyze technical SEO elements"""
        score = 100
        
        # Check HTTPS
        parsed_url = urlparse(url)
        uses_https = parsed_url.scheme == 'https'
        
        if not uses_https:
            issues.append("❌ Critical: Website not using HTTPS")
            recommendations.append("🔒 Implement SSL certificate for security and SEO boost")
            score -= 25
        
        # Check canonical URL
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        canonical_url = canonical.get('href') if canonical else None
        
        if not canonical_url:
            issues.append("⚠️ Missing canonical URL")
            recommendations.append("🔗 Add canonical tag to prevent duplicate content issues")
            score -= 10
        
        # Check robots meta
        robots = soup.find('meta', attrs={'name': 'robots'})
        if robots:
            content = robots.get('content', '').lower()
            if 'noindex' in content:
                issues.append("❌ Critical: Page set to noindex - Won't appear in search results")
                recommendations.append("🚫 Remove noindex directive if you want page indexed")
                score -= 30
            if 'nofollow' in content:
                issues.append("⚠️ Page set to nofollow - Links won't pass authority")
                recommendations.append("🔗 Consider removing nofollow if appropriate")
                score -= 10
        
        # Check mobile viewport
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        mobile_friendly = bool(viewport)
        
        if not mobile_friendly:
            issues.append("❌ Critical: Missing viewport meta tag - Not mobile-friendly")
            recommendations.append("📱 Add viewport meta tag for mobile optimization")
            score -= 20
        
        # Check for language declaration
        html_tag = soup.find('html')
        if not html_tag or not html_tag.get('lang'):
            issues.append("⚠️ Missing language declaration")
            recommendations.append("🌐 Add lang attribute to <html> tag (e.g., lang='en')")
            score -= 5
        
        # Check for favicon
        favicon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
        if not favicon:
            recommendations.append("💡 Add favicon for better brand recognition")
            score -= 3
        
        return max(0, score), {
            'https': uses_https,
            'canonical': canonical_url,
            'mobile_friendly': mobile_friendly,
            'has_sitemap': False,  # Would need to check /sitemap.xml
            'has_robots_txt': False  # Would need to check /robots.txt
        }
    
    def _analyze_links(self, soup: BeautifulSoup, url: str, issues: List, recommendations: List) -> tuple:
        """Analyze internal and external links"""
        all_links = soup.find_all('a', href=True)
        parsed_base = urlparse(url)
        
        internal_links = []
        external_links = []
        broken_links = []
        
        for link in all_links:
            href = link.get('href', '')
            if not href or href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                continue
            
            parsed_href = urlparse(href)
            
            # Determine if internal or external
            if not parsed_href.netloc or parsed_href.netloc == parsed_base.netloc:
                internal_links.append(href)
            else:
                external_links.append(href)
        
        score = 100
        
        # Analyze internal linking
        if len(internal_links) < self.THRESHOLDS['internal_links']['min']:
            issues.append(f"⚠️ Few internal links ({len(internal_links)}) - Hurts site navigation")
            recommendations.append("🔗 Add more internal links to improve site structure and SEO")
            score -= 15
        elif len(internal_links) < self.THRESHOLDS['internal_links']['ideal']:
            recommendations.append(f"💡 Good internal linking ({len(internal_links)}) - Consider adding more for better navigation")
            score -= 5
        
        # Analyze external links
        if len(external_links) > self.THRESHOLDS['external_links']['max']:
            issues.append(f"⚠️ Too many external links ({len(external_links)})")
            recommendations.append("🔗 Reduce external links or ensure they're valuable")
            score -= 10
        
        # Check for links without anchor text
        empty_links = [link for link in all_links if not link.get_text().strip()]
        if empty_links:
            issues.append(f"⚠️ {len(empty_links)} links without anchor text")
            recommendations.append("📝 Add descriptive anchor text to all links")
            score -= 10
        
        return max(0, score), {
            'internal': len(internal_links),
            'external': len(external_links),
            'broken': broken_links
        }
    
    def _analyze_social_meta(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze social media meta tags"""
        score = 100
        
        # Check Open Graph tags
        og_tags = {
            'og:title': soup.find('meta', property='og:title'),
            'og:description': soup.find('meta', property='og:description'),
            'og:image': soup.find('meta', property='og:image'),
            'og:url': soup.find('meta', property='og:url'),
            'og:type': soup.find('meta', property='og:type')
        }
        
        missing_og = [tag for tag, element in og_tags.items() if not element]
        
        if len(missing_og) >= 4:
            issues.append("⚠️ Missing Open Graph tags - Poor social media sharing")
            recommendations.append("📱 Add Open Graph tags for better social media appearance")
            score = 40
        elif len(missing_og) > 0:
            recommendations.append(f"💡 Add missing Open Graph tags: {', '.join(missing_og)}")
            score = 70
        
        # Check Twitter Card tags
        twitter_card = soup.find('meta', attrs={'name': 'twitter:card'})
        if not twitter_card:
            recommendations.append("🐦 Add Twitter Card tags for better Twitter sharing")
            score = min(score, 80)
        
        return score, {'og_tags': len([t for t in og_tags.values() if t])}
    
    def _analyze_structured_data(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze structured data (Schema.org)"""
        score = 100
        
        # Check for JSON-LD structured data
        json_ld = soup.find_all('script', type='application/ld+json')
        
        # Check for microdata
        microdata = soup.find_all(attrs={'itemtype': True})
        
        if not json_ld and not microdata:
            issues.append("⚠️ No structured data found")
            recommendations.append("📊 Add Schema.org structured data for rich snippets")
            score = 50
        elif len(json_ld) == 0 and len(microdata) > 0:
            recommendations.append("💡 Consider using JSON-LD format for structured data")
            score = 75
        
        return score, {'json_ld': len(json_ld), 'microdata': len(microdata)}
    
    def _extract_keywords(self, soup: BeautifulSoup, title: str) -> List[str]:
        """Extract primary keywords"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        text = soup.get_text().lower()
        title_lower = title.lower() if title else ""
        
        # Common stop words
        stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'will', 'your', 'are', 'can', 'our', 'more', 'about', 'what', 'when', 'where', 'which', 'their', 'there', 'been', 'were', 'they', 'than', 'into', 'also', 'other', 'some', 'such', 'only', 'over', 'just', 'like', 'these', 'those', 'then', 'them', 'here', 'very', 'much', 'many', 'most', 'both', 'each', 'does', 'done', 'being', 'would', 'could', 'should'}
        
        words = re.findall(r'\b[a-z]{4,}\b', text)
        word_freq = Counter(word for word in words if word not in stop_words)
        
        # Boost words in title
        title_words = re.findall(r'\b[a-z]{4,}\b', title_lower)
        for word in title_words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 10
        
        return [word for word, _ in word_freq.most_common(10)]
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _calculate_seo_health(self, score_components: Dict) -> str:
        """Calculate overall SEO health status"""
        avg_score = sum(score_components.values()) / len(score_components)
        
        if avg_score >= 85:
            return "Excellent - Well optimized for search engines"
        elif avg_score >= 70:
            return "Good - Some optimization opportunities remain"
        elif avg_score >= 50:
            return "Fair - Significant improvements needed"
        else:
            return "Poor - Critical SEO issues require immediate attention"
