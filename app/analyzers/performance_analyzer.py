import httpx
import time
from typing import Dict, List, Tuple
from bs4 import BeautifulSoup
import re


class PerformanceAnalyzer:
    """Analyze website performance with industry-standard metrics"""
    
    # Performance thresholds based on Google's recommendations
    THRESHOLDS = {
        'load_time': {'excellent': 1.5, 'good': 2.5, 'poor': 4.0},
        'page_size': {'excellent': 500, 'good': 1000, 'poor': 2000},  # KB
        'requests': {'excellent': 25, 'good': 50, 'poor': 100},
        'lcp': {'excellent': 2500, 'good': 4000, 'poor': 6000},  # ms
        'fid': {'excellent': 100, 'good': 300, 'poor': 500},  # ms
        'cls': {'excellent': 0.1, 'good': 0.25, 'poor': 0.5}
    }
    
    async def analyze(self, url: str) -> Dict:
        """Perform comprehensive performance analysis"""
        try:
            issues = []
            recommendations = []
            metrics = {}
            
            # Measure initial connection and load time
            start_time = time.time()
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                html = response.text
                headers = response.headers
            load_time = time.time() - start_time
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Calculate page size
            page_size_kb = len(html.encode('utf-8')) / 1024
            
            # Analyze resources
            resources = self._analyze_resources(soup)
            
            # Calculate weighted score
            score_components = {
                'load_time': self._score_load_time(load_time),
                'page_size': self._score_page_size(page_size_kb),
                'requests': self._score_requests(resources['total_requests']),
                'compression': self._score_compression(headers),
                'caching': self._score_caching(headers),
                'render_blocking': self._score_render_blocking(resources['render_blocking']),
                'resource_optimization': self._score_resource_optimization(resources)
            }
            
            # Weighted scoring (total = 100)
            weights = {
                'load_time': 25,
                'page_size': 15,
                'requests': 10,
                'compression': 10,
                'caching': 15,
                'render_blocking': 15,
                'resource_optimization': 10
            }
            
            final_score = sum(score_components[k] * (weights[k] / 100) for k in weights)
            
            # Generate detailed issues and recommendations
            self._analyze_load_time(load_time, issues, recommendations)
            self._analyze_page_size(page_size_kb, issues, recommendations)
            self._analyze_requests(resources, issues, recommendations)
            self._analyze_compression(headers, issues, recommendations)
            self._analyze_caching(headers, issues, recommendations)
            self._analyze_render_blocking(resources, issues, recommendations)
            self._analyze_resource_optimization(soup, resources, issues, recommendations)
            
            # Calculate Core Web Vitals
            core_web_vitals = self._calculate_core_web_vitals(load_time, resources, soup)
            
            # Performance grade
            grade = self._calculate_grade(final_score)
            
            # Estimated improvement potential
            improvement_potential = self._calculate_improvement_potential(score_components)
            
            return {
                "score": round(final_score, 1),
                "grade": grade,
                "load_time": round(load_time, 2),
                "page_size": round(page_size_kb, 2),
                "requests_count": resources['total_requests'],
                "core_web_vitals": core_web_vitals,
                "score_breakdown": {k: round(v, 1) for k, v in score_components.items()},
                "resource_breakdown": resources['breakdown'],
                "improvement_potential": improvement_potential,
                "issues": issues,
                "recommendations": recommendations,
                "metrics": {
                    "ttfb": round(load_time * 0.3, 2),  # Estimated Time to First Byte
                    "compression_enabled": 'gzip' in headers.get('content-encoding', '') or 'br' in headers.get('content-encoding', ''),
                    "caching_enabled": bool(headers.get('cache-control', '')),
                    "https_enabled": url.startswith('https')
                }
            }
            
        except Exception as e:
            return {
                "score": 0,
                "grade": "F",
                "load_time": 0,
                "page_size": 0,
                "requests_count": 0,
                "core_web_vitals": {},
                "score_breakdown": {},
                "resource_breakdown": {},
                "improvement_potential": "Unknown",
                "issues": [f"Failed to analyze performance: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"],
                "metrics": {}
            }
    
    def _analyze_resources(self, soup: BeautifulSoup) -> Dict:
        """Analyze all page resources"""
        images = soup.find_all('img')
        scripts = soup.find_all('script')
        stylesheets = soup.find_all('link', rel='stylesheet')
        fonts = soup.find_all('link', rel='preload', as_='font')
        
        # Check for render-blocking scripts
        render_blocking = len([s for s in scripts if s.get('src') and not s.get('async') and not s.get('defer')])
        
        # Check for lazy loading
        lazy_images = len([img for img in images if img.get('loading') == 'lazy'])
        
        return {
            'total_requests': len(images) + len(scripts) + len(stylesheets) + len(fonts) + 1,
            'images': len(images),
            'scripts': len(scripts),
            'stylesheets': len(stylesheets),
            'fonts': len(fonts),
            'render_blocking': render_blocking,
            'lazy_images': lazy_images,
            'breakdown': {
                'images': len(images),
                'scripts': len(scripts),
                'stylesheets': len(stylesheets),
                'fonts': len(fonts)
            }
        }
    
    def _score_load_time(self, load_time: float) -> float:
        """Score based on load time"""
        if load_time <= self.THRESHOLDS['load_time']['excellent']:
            return 100
        elif load_time <= self.THRESHOLDS['load_time']['good']:
            return 85
        elif load_time <= self.THRESHOLDS['load_time']['poor']:
            return 60
        else:
            return max(30, 100 - (load_time - self.THRESHOLDS['load_time']['poor']) * 10)
    
    def _score_page_size(self, size_kb: float) -> float:
        """Score based on page size"""
        if size_kb <= self.THRESHOLDS['page_size']['excellent']:
            return 100
        elif size_kb <= self.THRESHOLDS['page_size']['good']:
            return 85
        elif size_kb <= self.THRESHOLDS['page_size']['poor']:
            return 60
        else:
            return max(30, 100 - (size_kb - self.THRESHOLDS['page_size']['poor']) / 100)
    
    def _score_requests(self, requests: int) -> float:
        """Score based on number of requests"""
        if requests <= self.THRESHOLDS['requests']['excellent']:
            return 100
        elif requests <= self.THRESHOLDS['requests']['good']:
            return 80
        elif requests <= self.THRESHOLDS['requests']['poor']:
            return 50
        else:
            return max(20, 100 - (requests - self.THRESHOLDS['requests']['poor']))
    
    def _score_compression(self, headers: Dict) -> float:
        """Score based on compression"""
        content_encoding = headers.get('content-encoding', '').lower()
        if 'br' in content_encoding:
            return 100
        elif 'gzip' in content_encoding:
            return 90
        else:
            return 30
    
    def _score_caching(self, headers: Dict) -> float:
        """Score based on caching headers"""
        cache_control = headers.get('cache-control', '').lower()
        if not cache_control:
            return 20
        
        score = 60
        if 'max-age' in cache_control:
            max_age_match = re.search(r'max-age=(\d+)', cache_control)
            if max_age_match:
                max_age = int(max_age_match.group(1))
                if max_age >= 31536000:  # 1 year
                    score = 100
                elif max_age >= 604800:  # 1 week
                    score = 90
                elif max_age >= 86400:  # 1 day
                    score = 75
        
        if 'no-cache' in cache_control or 'no-store' in cache_control:
            score = 30
        
        return score
    
    def _score_render_blocking(self, render_blocking: int) -> float:
        """Score based on render-blocking resources"""
        if render_blocking == 0:
            return 100
        elif render_blocking <= 2:
            return 85
        elif render_blocking <= 5:
            return 60
        else:
            return max(30, 100 - render_blocking * 8)
    
    def _score_resource_optimization(self, resources: Dict) -> float:
        """Score based on resource optimization"""
        score = 100
        
        # Penalize excessive resources
        if resources['images'] > 30:
            score -= 20
        elif resources['images'] > 20:
            score -= 10
        
        if resources['scripts'] > 15:
            score -= 15
        elif resources['scripts'] > 10:
            score -= 8
        
        # Reward lazy loading
        if resources['images'] > 0:
            lazy_ratio = resources['lazy_images'] / resources['images']
            if lazy_ratio > 0.7:
                score += 10
            elif lazy_ratio > 0.3:
                score += 5
        
        return max(0, min(100, score))
    
    def _analyze_load_time(self, load_time: float, issues: List, recommendations: List):
        """Analyze load time and add issues/recommendations"""
        if load_time > self.THRESHOLDS['load_time']['poor']:
            issues.append(f"❌ Critical: Very slow load time ({load_time:.2f}s) - Users expect < 3s")
            recommendations.append("🚀 Priority: Implement CDN, optimize images, enable compression, and minify resources")
        elif load_time > self.THRESHOLDS['load_time']['good']:
            issues.append(f"⚠️ Slow load time ({load_time:.2f}s) - Target < 2.5s for good UX")
            recommendations.append("⚡ Optimize server response time, enable browser caching, and compress assets")
        elif load_time > self.THRESHOLDS['load_time']['excellent']:
            recommendations.append(f"✨ Good load time ({load_time:.2f}s) - Consider optimizing to < 1.5s for excellent performance")
    
    def _analyze_page_size(self, size_kb: float, issues: List, recommendations: List):
        """Analyze page size"""
        if size_kb > self.THRESHOLDS['page_size']['poor']:
            issues.append(f"❌ Very large page size ({size_kb:.0f}KB) - Target < 1MB")
            recommendations.append("📦 Minify HTML/CSS/JS, compress images to WebP/AVIF, remove unused code")
        elif size_kb > self.THRESHOLDS['page_size']['good']:
            issues.append(f"⚠️ Large page size ({size_kb:.0f}KB) - Optimize to < 1MB")
            recommendations.append("🗜️ Enable text compression (Gzip/Brotli) and optimize images")
    
    def _analyze_requests(self, resources: Dict, issues: List, recommendations: List):
        """Analyze HTTP requests"""
        total = resources['total_requests']
        if total > self.THRESHOLDS['requests']['poor']:
            issues.append(f"❌ Too many HTTP requests ({total}) - Target < 50")
            recommendations.append("🔗 Combine CSS/JS files, use CSS sprites, implement lazy loading for images")
        elif total > self.THRESHOLDS['requests']['good']:
            issues.append(f"⚠️ High number of requests ({total}) - Reduce to < 50")
            recommendations.append("📊 Audit and remove unnecessary resources, combine files where possible")
    
    def _analyze_compression(self, headers: Dict, issues: List, recommendations: List):
        """Analyze compression"""
        content_encoding = headers.get('content-encoding', '').lower()
        if 'br' not in content_encoding and 'gzip' not in content_encoding:
            issues.append("❌ No text compression enabled")
            recommendations.append("🗜️ Enable Gzip or Brotli compression on server (can reduce size by 70%)")
        elif 'gzip' in content_encoding and 'br' not in content_encoding:
            recommendations.append("💡 Consider upgrading from Gzip to Brotli for better compression")
    
    def _analyze_caching(self, headers: Dict, issues: List, recommendations: List):
        """Analyze caching headers"""
        cache_control = headers.get('cache-control', '')
        if not cache_control:
            issues.append("❌ No caching headers found")
            recommendations.append("⏰ Implement Cache-Control headers (e.g., max-age=31536000 for static assets)")
        elif 'no-cache' in cache_control or 'no-store' in cache_control:
            issues.append("⚠️ Caching disabled - impacts repeat visit performance")
            recommendations.append("💾 Enable caching for static resources to improve repeat visit speed")
    
    def _analyze_render_blocking(self, resources: Dict, issues: List, recommendations: List):
        """Analyze render-blocking resources"""
        if resources['render_blocking'] > 5:
            issues.append(f"❌ {resources['render_blocking']} render-blocking scripts delay page rendering")
            recommendations.append("⚡ Add 'async' or 'defer' attributes to non-critical scripts")
        elif resources['render_blocking'] > 2:
            issues.append(f"⚠️ {resources['render_blocking']} render-blocking scripts found")
            recommendations.append("🎯 Defer non-critical JavaScript to improve initial render time")
    
    def _analyze_resource_optimization(self, soup: BeautifulSoup, resources: Dict, issues: List, recommendations: List):
        """Analyze resource optimization"""
        # Check for lazy loading
        if resources['images'] > 5 and resources['lazy_images'] == 0:
            issues.append(f"⚠️ {resources['images']} images without lazy loading")
            recommendations.append("🖼️ Implement lazy loading for below-the-fold images (loading='lazy')")
        
        # Check for modern image formats
        images = soup.find_all('img')
        modern_formats = sum(1 for img in images if any(fmt in img.get('src', '').lower() for fmt in ['.webp', '.avif']))
        if len(images) > 0 and modern_formats == 0:
            recommendations.append("🎨 Use modern image formats (WebP/AVIF) for 25-35% better compression")
        
        # Check for inline styles
        inline_styles = soup.find_all(style=True)
        if len(inline_styles) > 15:
            issues.append(f"⚠️ {len(inline_styles)} elements with inline styles")
            recommendations.append("🎨 Move inline styles to external CSS for better caching")
    
    def _calculate_core_web_vitals(self, load_time: float, resources: Dict, soup: BeautifulSoup) -> Dict:
        """Calculate estimated Core Web Vitals"""
        # LCP (Largest Contentful Paint) - estimated
        lcp = load_time * 1000 * 0.75  # Typically 75% of load time
        if resources['images'] > 20:
            lcp *= 1.2
        
        # FID (First Input Delay) - estimated
        fid = 50 if load_time < 2 else min(300, 50 + (load_time - 2) * 50)
        if resources['render_blocking'] > 3:
            fid *= 1.5
        
        # CLS (Cumulative Layout Shift) - estimated
        inline_styles = len(soup.find_all(style=True))
        images_without_dimensions = len([img for img in soup.find_all('img') if not img.get('width') or not img.get('height')])
        cls = 0.05 + (inline_styles * 0.01) + (images_without_dimensions * 0.02)
        cls = min(0.5, cls)
        
        return {
            "LCP": round(lcp, 0),
            "LCP_rating": "good" if lcp <= 2500 else "needs-improvement" if lcp <= 4000 else "poor",
            "FID": round(fid, 0),
            "FID_rating": "good" if fid <= 100 else "needs-improvement" if fid <= 300 else "poor",
            "CLS": round(cls, 3),
            "CLS_rating": "good" if cls <= 0.1 else "needs-improvement" if cls <= 0.25 else "poor"
        }
    
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
    
    def _calculate_improvement_potential(self, score_components: Dict) -> str:
        """Calculate improvement potential"""
        avg_score = sum(score_components.values()) / len(score_components)
        if avg_score >= 85:
            return "Low - Already well optimized"
        elif avg_score >= 70:
            return "Medium - Several optimization opportunities"
        else:
            return "High - Significant performance gains possible"
