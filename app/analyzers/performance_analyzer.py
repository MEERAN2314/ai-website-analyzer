import httpx
import time
from typing import Dict
from bs4 import BeautifulSoup


class PerformanceAnalyzer:
    """Analyze website performance"""
    
    async def analyze(self, url: str) -> Dict:
        """Perform performance analysis"""
        try:
            issues = []
            recommendations = []
            score = 100
            
            # Measure load time
            start_time = time.time()
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                html = response.text
            load_time = time.time() - start_time
            
            # Analyze load time
            if load_time > 3:
                issues.append(f"Slow page load time: {load_time:.2f}s")
                recommendations.append("Optimize server response time and enable caching")
                score -= 20
            elif load_time > 2:
                issues.append(f"Page load time could be improved: {load_time:.2f}s")
                recommendations.append("Consider CDN and image optimization")
                score -= 10
            
            # Page size
            page_size = len(html.encode('utf-8')) / 1024  # KB
            if page_size > 1000:
                issues.append(f"Large page size: {page_size:.2f}KB")
                recommendations.append("Minify HTML, CSS, and JavaScript")
                score -= 15
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Count resources
            images = soup.find_all('img')
            scripts = soup.find_all('script')
            stylesheets = soup.find_all('link', rel='stylesheet')
            
            requests_count = len(images) + len(scripts) + len(stylesheets) + 1
            
            if requests_count > 50:
                issues.append(f"Too many HTTP requests: {requests_count}")
                recommendations.append("Combine files and use sprite sheets")
                score -= 15
            
            # Check for large images
            large_images = 0
            for img in images[:20]:  # Check first 20 images
                src = img.get('src', '')
                if src and not src.startswith('data:'):
                    # Simplified check - in production, fetch and check actual size
                    if 'original' in src.lower() or 'full' in src.lower():
                        large_images += 1
            
            if large_images > 0:
                issues.append(f"{large_images} potentially unoptimized images")
                recommendations.append("Compress and resize images, use WebP format")
                score -= 10
            
            # Check for inline styles
            inline_styles = soup.find_all(style=True)
            if len(inline_styles) > 10:
                issues.append("Excessive inline styles detected")
                recommendations.append("Move inline styles to external CSS files")
                score -= 5
            
            # Check for render-blocking resources
            render_blocking = len([s for s in scripts if not s.get('async') and not s.get('defer')])
            if render_blocking > 3:
                issues.append(f"{render_blocking} render-blocking scripts")
                recommendations.append("Add async or defer attributes to scripts")
                score -= 10
            
            # Simulated Core Web Vitals (in production, use Lighthouse)
            core_web_vitals = {
                "LCP": load_time * 1000,  # Largest Contentful Paint (ms)
                "FID": 50 if load_time < 2 else 100,  # First Input Delay (ms)
                "CLS": 0.1 if len(inline_styles) < 10 else 0.25  # Cumulative Layout Shift
            }
            
            # Check compression
            content_encoding = response.headers.get('content-encoding', '')
            if 'gzip' not in content_encoding and 'br' not in content_encoding:
                issues.append("No compression detected")
                recommendations.append("Enable Gzip or Brotli compression")
                score -= 10
            
            # Check caching
            cache_control = response.headers.get('cache-control', '')
            if not cache_control:
                issues.append("No caching headers found")
                recommendations.append("Implement browser caching with Cache-Control headers")
                score -= 10
            
            return {
                "score": max(0, score),
                "load_time": round(load_time, 2),
                "page_size": round(page_size, 2),
                "requests_count": requests_count,
                "core_web_vitals": core_web_vitals,
                "issues": issues[:10],
                "recommendations": recommendations[:10]
            }
            
        except Exception as e:
            return {
                "score": 0,
                "load_time": 0,
                "page_size": 0,
                "requests_count": 0,
                "core_web_vitals": {},
                "issues": [f"Failed to analyze performance: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"]
            }
