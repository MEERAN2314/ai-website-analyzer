import httpx
import time
from typing import Dict
from bs4 import BeautifulSoup
import re


class PerformanceAnalyzer:
    """Enhanced performance analyzer with comprehensive metrics"""
    
    def __init__(self):
        self.weights = {
            'load_time': 30,
            'page_size': 20,
            'resources': 20,
            'optimization': 20,
            'caching': 10
        }
    
    async def analyze(self, url: str) -> Dict:
        """Perform comprehensive performance analysis"""
        try:
            issues = []
            recommendations = []
            scores = {}
            
            # Measure load time and get response
            start_time = time.time()
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                html = response.text
                headers = response.headers
            load_time = time.time() - start_time
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 1. Load Time Analysis (30 points)
            load_score, load_issues, load_recs = self._analyze_load_time(load_time)
            scores['load_time'] = load_score
            issues.extend(load_issues)
            recommendations.extend(load_recs)
            
            # 2. Page Size Analysis (20 points)
            page_size = len(html.encode('utf-8')) / 1024  # KB
            size_score, size_issues, size_recs = self._analyze_page_size(page_size, html)
            scores['page_size'] = size_score
            issues.extend(size_issues)
            recommendations.extend(size_recs)
            
            # 3. Resources Analysis (20 points)
            resource_score, resource_issues, resource_recs, requests_count = self._analyze_resources(soup)
            scores['resources'] = resource_score
            issues.extend(resource_issues)
            recommendations.extend(resource_recs)
            
            # 4. Optimization Analysis (20 points)
            opt_score, opt_issues, opt_recs = self._analyze_optimization(soup, html)
            scores['optimization'] = opt_score
            issues.extend(opt_issues)
            recommendations.extend(opt_recs)
            
            # 5. Caching & Compression (10 points)
            cache_score, cache_issues, cache_recs = self._analyze_caching_compression(headers)
            scores['caching'] = cache_score
            issues.extend(cache_issues)
            recommendations.extend(cache_recs)
            
            # Simulate Core Web Vitals
            core_web_vitals = self._calculate_core_web_vitals(load_time, page_size, soup)
            
            # Calculate weighted total score
            total_score = sum(scores[key] * self.weights[key] / 100 for key in scores)
            
            return {
                "score": round(max(0, min(100, total_score)), 1),
                "load_time": round(load_time, 2),
                "page_size": round(page_size, 2),
                "requests_count": requests_count,
                "core_web_vitals": core_web_vitals,
                "issues": issues[:15],
                "recommendations": recommendations[:15],
                "detailed_scores": scores
            }
            
        except Exception as e:
            return {
                "score": 0,
                "load_time": 0,
                "page_size": 0,
                "requests_count": 0,
                "core_web_vitals": {},
                "issues": [f"Failed to analyze performance: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"],
                "detailed_scores": {}
            }
    
    def _analyze_load_time(self, load_time: float) -> tuple:
        """Analyze load time (30 points)"""
        score = 100
        issues = []
        recommendations = []
        
        if load_time < 1.0:
            # Excellent
            pass
        elif load_time < 2.0:
            # Good
            recommendations.append("Good load time, consider CDN for further improvement")
            score -= 10
        elif load_time < 3.0:
            # Fair
            issues.append(f"⚠️ Moderate load time: {load_time:.2f}s (target: <2s)")
            recommendations.append("Optimize images and enable browser caching")
            score -= 30
        elif load_time < 5.0:
            # Poor
            issues.append(f"❌ Slow load time: {load_time:.2f}s (target: <2s)")
            recommendations.append("Critical: Optimize server response, compress assets, use CDN")
            score -= 50
        else:
            # Very Poor
            issues.append(f"❌ Very slow load time: {load_time:.2f}s (target: <2s)")
            recommendations.append("Urgent: Review server configuration, database queries, and asset sizes")
            score -= 70
        
        return max(0, score), issues, recommendations
    
    def _analyze_page_size(self, page_size: float, html: str) -> tuple:
        """Analyze page size (20 points)"""
        score = 100
        issues = []
        recommendations = []
        
        if page_size < 500:
            # Excellent
            pass
        elif page_size < 1000:
            # Good
            recommendations.append("Page size is acceptable, consider minification")
            score -= 10
        elif page_size < 2000:
            # Fair
            issues.append(f"⚠️ Large page size: {page_size:.0f}KB (target: <1MB)")
            recommendations.append("Minify HTML, CSS, and JavaScript")
            score -= 30
        else:
            # Poor
            issues.append(f"❌ Very large page size: {page_size:.0f}KB (target: <1MB)")
            recommendations.append("Critical: Reduce page size through minification and compression")
            score -= 50
        
        # Check for minification
        if '  ' in html or '\n\n' in html:
            issues.append("⚠️ HTML not minified")
            recommendations.append("Minify HTML to reduce page size by 20-30%")
            score -= 20
        
        return max(0, score), issues, recommendations
    
    def _analyze_resources(self, soup: BeautifulSoup) -> tuple:
        """Analyze resources (20 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Count resources
        images = soup.find_all('img')
        scripts = soup.find_all('script', src=True)
        stylesheets = soup.find_all('link', rel='stylesheet')
        fonts = soup.find_all('link', href=re.compile(r'\.(woff|woff2|ttf|otf)'))
        
        requests_count = len(images) + len(scripts) + len(stylesheets) + len(fonts) + 1
        
        # Analyze request count
        if requests_count < 30:
            # Excellent
            pass
        elif requests_count < 50:
            # Good
            recommendations.append("Good resource count, consider combining files")
            score -= 10
        elif requests_count < 80:
            # Fair
            issues.append(f"⚠️ Many HTTP requests: {requests_count} (target: <50)")
            recommendations.append("Combine CSS/JS files, use image sprites")
            score -= 30
        else:
            # Poor
            issues.append(f"❌ Too many HTTP requests: {requests_count} (target: <50)")
            recommendations.append("Critical: Reduce requests through bundling and lazy loading")
            score -= 50
        
        # Image optimization
        if images:
            # Check for modern image formats
            webp_images = [img for img in images if img.get('src', '').endswith('.webp')]
            if len(webp_images) / len(images) < 0.3:
                issues.append("⚠️ Few images using modern formats (WebP/AVIF)")
                recommendations.append("Convert images to WebP format for 25-35% size reduction")
                score -= 20
            
            # Check for lazy loading
            lazy_images = [img for img in images if img.get('loading') == 'lazy']
            if len(images) > 5 and len(lazy_images) == 0:
                issues.append("⚠️ No lazy loading detected for images")
                recommendations.append("Implement lazy loading for below-fold images")
                score -= 15
            
            # Check for responsive images
            responsive_images = [img for img in images if img.get('srcset')]
            if len(images) > 3 and len(responsive_images) / len(images) < 0.3:
                recommendations.append("Use srcset for responsive images")
                score -= 10
        
        # Script optimization
        if scripts:
            async_scripts = [s for s in scripts if s.get('async')]
            defer_scripts = [s for s in scripts if s.get('defer')]
            optimized_scripts = len(async_scripts) + len(defer_scripts)
            
            if len(scripts) > 3 and optimized_scripts / len(scripts) < 0.5:
                issues.append(f"⚠️ {len(scripts) - optimized_scripts} render-blocking scripts")
                recommendations.append("Add async or defer attributes to non-critical scripts")
                score -= 20
        
        return max(0, score), issues, recommendations, requests_count
    
    def _analyze_optimization(self, soup: BeautifulSoup, html: str) -> tuple:
        """Analyze optimization techniques (20 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Inline styles
        inline_styles = soup.find_all(style=True)
        if len(inline_styles) > 15:
            issues.append(f"⚠️ Excessive inline styles: {len(inline_styles)}")
            recommendations.append("Move inline styles to external CSS files")
            score -= 20
        
        # CSS in head
        style_tags = soup.find_all('style')
        if len(style_tags) > 3:
            issues.append(f"⚠️ Multiple <style> tags: {len(style_tags)}")
            recommendations.append("Combine CSS into fewer files")
            score -= 15
        
        # Critical CSS
        head = soup.find('head')
        if head:
            head_styles = head.find_all('style')
            if len(head_styles) == 0:
                recommendations.append("Consider inlining critical CSS in <head>")
                score -= 10
        
        # Font optimization
        font_links = soup.find_all('link', href=re.compile(r'fonts\.(googleapis|gstatic)'))
        if len(font_links) > 2:
            issues.append("⚠️ Multiple font files loaded")
            recommendations.append("Limit to 2-3 font families, use font-display: swap")
            score -= 15
        
        # Preload/Prefetch
        preload_links = soup.find_all('link', rel='preload')
        prefetch_links = soup.find_all('link', rel='prefetch')
        
        if len(preload_links) == 0:
            recommendations.append("Use <link rel='preload'> for critical resources")
            score -= 10
        
        # DNS prefetch for external resources
        dns_prefetch = soup.find_all('link', rel='dns-prefetch')
        external_domains = set()
        
        for script in soup.find_all('script', src=True):
            src = script.get('src', '')
            if src.startswith('http') and 'googleapis' not in src:
                external_domains.add(src.split('/')[2])
        
        if external_domains and len(dns_prefetch) == 0:
            recommendations.append("Add DNS prefetch for external domains")
            score -= 10
        
        # Check for unused CSS/JS (simplified check)
        if len(style_tags) > 5 or len(soup.find_all('script')) > 10:
            recommendations.append("Audit and remove unused CSS/JavaScript")
            score -= 10
        
        return max(0, score), issues, recommendations
    
    def _analyze_caching_compression(self, headers: dict) -> tuple:
        """Analyze caching and compression (10 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Compression
        content_encoding = headers.get('content-encoding', '').lower()
        if 'gzip' not in content_encoding and 'br' not in content_encoding:
            issues.append("❌ No compression detected")
            recommendations.append("Enable Gzip or Brotli compression (30-70% size reduction)")
            score -= 50
        elif 'gzip' in content_encoding:
            recommendations.append("Good: Gzip enabled. Consider Brotli for better compression")
            score -= 10
        
        # Caching
        cache_control = headers.get('cache-control', '').lower()
        if not cache_control:
            issues.append("❌ No caching headers found")
            recommendations.append("Implement Cache-Control headers for static assets")
            score -= 40
        elif 'no-cache' in cache_control or 'no-store' in cache_control:
            issues.append("⚠️ Caching disabled")
            recommendations.append("Enable caching for static resources")
            score -= 30
        elif 'max-age' in cache_control:
            # Check max-age value
            max_age_match = re.search(r'max-age=(\d+)', cache_control)
            if max_age_match:
                max_age = int(max_age_match.group(1))
                if max_age < 3600:  # Less than 1 hour
                    recommendations.append("Increase cache duration for static assets")
                    score -= 15
        
        # ETag
        etag = headers.get('etag')
        if not etag:
            recommendations.append("Consider adding ETag headers for cache validation")
            score -= 10
        
        return max(0, score), issues, recommendations
    
    def _calculate_core_web_vitals(self, load_time: float, page_size: float, soup: BeautifulSoup) -> dict:
        """Calculate simulated Core Web Vitals"""
        
        # LCP (Largest Contentful Paint) - simulated
        # Good: <2.5s, Needs Improvement: 2.5-4s, Poor: >4s
        lcp = load_time * 1000  # Convert to ms
        if page_size > 1000:
            lcp *= 1.3  # Larger pages take longer
        
        # FID (First Input Delay) - simulated
        # Good: <100ms, Needs Improvement: 100-300ms, Poor: >300ms
        scripts = soup.find_all('script')
        fid = 50 + (len(scripts) * 10)  # More scripts = higher FID
        
        # CLS (Cumulative Layout Shift) - simulated
        # Good: <0.1, Needs Improvement: 0.1-0.25, Poor: >0.25
        inline_styles = soup.find_all(style=True)
        images_without_dimensions = [img for img in soup.find_all('img') 
                                     if not img.get('width') or not img.get('height')]
        
        cls = 0.05  # Base
        if len(inline_styles) > 10:
            cls += 0.1
        if len(images_without_dimensions) > 5:
            cls += 0.15
        
        return {
            "LCP": round(lcp, 0),  # ms
            "FID": round(fid, 0),  # ms
            "CLS": round(cls, 2),  # score
            "LCP_rating": "Good" if lcp < 2500 else "Needs Improvement" if lcp < 4000 else "Poor",
            "FID_rating": "Good" if fid < 100 else "Needs Improvement" if fid < 300 else "Poor",
            "CLS_rating": "Good" if cls < 0.1 else "Needs Improvement" if cls < 0.25 else "Poor"
        }
