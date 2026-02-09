import httpx
from bs4 import BeautifulSoup
from typing import Dict, List
from urllib.parse import urljoin
import asyncio


class ImageAnalyzer:
    """Analyze images for optimization opportunities"""
    
    # Image optimization thresholds
    THRESHOLDS = {
        'max_size_kb': 200,  # Images should be under 200KB
        'ideal_size_kb': 100,  # Ideal size is under 100KB
        'max_dimensions': 2000,  # Max width/height
        'min_images': 1,
        'max_images': 50
    }
    
    # Modern image formats
    MODERN_FORMATS = ['webp', 'avif']
    LEGACY_FORMATS = ['jpg', 'jpeg', 'png', 'gif']
    
    async def analyze(self, url: str, soup: BeautifulSoup = None) -> Dict:
        """Perform comprehensive image analysis"""
        try:
            if not soup:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(url)
                    html = response.text
                soup = BeautifulSoup(html, 'html.parser')
            
            issues = []
            recommendations = []
            
            # Find all images
            images = soup.find_all('img')
            
            if len(images) == 0:
                return {
                    "score": 100,
                    "total_images": 0,
                    "issues": ["No images found on page"],
                    "recommendations": ["Consider adding relevant images to enhance content"]
                }
            
            # Analyze images
            image_data = await self._analyze_images(images, url, issues, recommendations)
            
            # Calculate scores
            size_score = self._score_image_sizes(image_data, issues, recommendations)
            format_score = self._score_image_formats(image_data, issues, recommendations)
            optimization_score = self._score_optimization(image_data, issues, recommendations)
            responsive_score = self._score_responsive_images(image_data, issues, recommendations)
            lazy_score = self._score_lazy_loading(image_data, issues, recommendations)
            alt_score = self._score_alt_text(image_data, issues, recommendations)
            
            # Weighted scoring
            weights = {
                'size': 25,
                'format': 20,
                'optimization': 15,
                'responsive': 15,
                'lazy_loading': 15,
                'alt_text': 10
            }
            
            score_components = {
                'size': size_score,
                'format': format_score,
                'optimization': optimization_score,
                'responsive': responsive_score,
                'lazy_loading': lazy_score,
                'alt_text': alt_score
            }
            
            final_score = sum(score_components[k] * (weights[k] / 100) for k in weights)
            
            # Calculate potential savings
            potential_savings = self._calculate_savings(image_data)
            
            return {
                "score": round(final_score, 1),
                "grade": self._calculate_grade(final_score),
                "total_images": len(images),
                "total_size_kb": image_data['total_size_kb'],
                "average_size_kb": image_data['avg_size_kb'],
                "large_images": image_data['large_images_count'],
                "modern_format_usage": image_data['modern_format_percentage'],
                "responsive_images": image_data['responsive_count'],
                "lazy_loaded_images": image_data['lazy_loaded_count'],
                "images_without_alt": image_data['missing_alt_count'],
                "potential_savings_kb": potential_savings['total_kb'],
                "potential_savings_percentage": potential_savings['percentage'],
                "score_breakdown": {k: round(v, 1) for k, v in score_components.items()},
                "issues": issues,
                "recommendations": recommendations,
                "optimization_summary": self._generate_summary(image_data, potential_savings)
            }
            
        except Exception as e:
            return {
                "score": 0,
                "grade": "F",
                "total_images": 0,
                "issues": [f"Failed to analyze images: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"]
            }
    
    async def _analyze_images(self, images: List, base_url: str, issues: List, recommendations: List) -> Dict:
        """Analyze individual images"""
        image_details = []
        total_size = 0
        large_images = 0
        modern_format_count = 0
        responsive_count = 0
        lazy_loaded_count = 0
        missing_alt_count = 0
        
        # Limit to first 20 images for performance
        images_to_check = images[:20]
        
        # Analyze images concurrently
        tasks = []
        for img in images_to_check:
            tasks.append(self._get_image_info(img, base_url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for img, result in zip(images_to_check, results):
            if isinstance(result, Exception):
                continue
            
            if result:
                image_details.append(result)
                total_size += result['size_kb']
                
                if result['size_kb'] > self.THRESHOLDS['max_size_kb']:
                    large_images += 1
                
                if result['format'] in self.MODERN_FORMATS:
                    modern_format_count += 1
                
                if result['is_responsive']:
                    responsive_count += 1
                
                if result['is_lazy_loaded']:
                    lazy_loaded_count += 1
            
            # Check alt text
            if not img.get('alt'):
                missing_alt_count += 1
        
        return {
            'images': image_details,
            'total_size_kb': round(total_size, 2),
            'avg_size_kb': round(total_size / len(image_details), 2) if image_details else 0,
            'large_images_count': large_images,
            'modern_format_count': modern_format_count,
            'modern_format_percentage': round((modern_format_count / len(images)) * 100, 1) if images else 0,
            'responsive_count': responsive_count,
            'lazy_loaded_count': lazy_loaded_count,
            'missing_alt_count': missing_alt_count,
            'total_analyzed': len(image_details)
        }
    
    async def _get_image_info(self, img, base_url: str) -> Dict:
        """Get information about a single image"""
        try:
            src = img.get('src')
            if not src:
                return None
            
            # Skip data URLs and SVGs
            if src.startswith('data:') or src.endswith('.svg'):
                return None
            
            # Build full URL
            img_url = urljoin(base_url, src)
            
            # Get image size
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.head(img_url, follow_redirects=True)
                size_bytes = int(response.headers.get('content-length', 0))
                size_kb = size_bytes / 1024
                
                # Detect format from URL or content-type
                content_type = response.headers.get('content-type', '').lower()
                format_from_url = src.split('.')[-1].lower().split('?')[0]
                
                if 'webp' in content_type or format_from_url == 'webp':
                    img_format = 'webp'
                elif 'avif' in content_type or format_from_url == 'avif':
                    img_format = 'avif'
                elif 'jpeg' in content_type or 'jpg' in content_type or format_from_url in ['jpg', 'jpeg']:
                    img_format = 'jpeg'
                elif 'png' in content_type or format_from_url == 'png':
                    img_format = 'png'
                elif 'gif' in content_type or format_from_url == 'gif':
                    img_format = 'gif'
                else:
                    img_format = 'unknown'
                
                return {
                    'url': img_url,
                    'size_kb': round(size_kb, 2),
                    'format': img_format,
                    'is_responsive': bool(img.get('srcset') or img.get('sizes')),
                    'is_lazy_loaded': img.get('loading') == 'lazy',
                    'has_alt': bool(img.get('alt')),
                    'width': img.get('width'),
                    'height': img.get('height')
                }
        except:
            return None
    
    def _score_image_sizes(self, image_data: Dict, issues: List, recommendations: List) -> float:
        """Score based on image sizes"""
        score = 100
        large_count = image_data['large_images_count']
        total = image_data['total_analyzed']
        
        if total == 0:
            return 100
        
        large_percentage = (large_count / total) * 100
        
        if large_percentage > 50:
            issues.append(f"Critical: {large_count} images over 200KB ({large_percentage:.0f}% of images)")
            recommendations.append(f"Compress large images - potential savings of {image_data['total_size_kb'] * 0.6:.0f}KB")
            score = 40
        elif large_percentage > 25:
            issues.append(f"{large_count} images over 200KB")
            recommendations.append("Compress images to reduce page load time")
            score = 70
        elif large_count > 0:
            recommendations.append(f"Optimize {large_count} large images for better performance")
            score = 85
        
        return score
    
    def _score_image_formats(self, image_data: Dict, issues: List, recommendations: List) -> float:
        """Score based on modern image format usage"""
        score = 100
        modern_percentage = image_data['modern_format_percentage']
        
        if modern_percentage == 0:
            issues.append("No modern image formats (WebP/AVIF) detected")
            recommendations.append("Convert images to WebP format for 25-35% better compression")
            score = 50
        elif modern_percentage < 50:
            recommendations.append(f"Only {modern_percentage:.0f}% of images use modern formats - convert more to WebP/AVIF")
            score = 75
        elif modern_percentage < 100:
            recommendations.append("Consider converting remaining images to WebP/AVIF")
            score = 90
        
        return score
    
    def _score_optimization(self, image_data: Dict, issues: List, recommendations: List) -> float:
        """Score overall optimization"""
        score = 100
        avg_size = image_data['avg_size_kb']
        
        if avg_size > 150:
            issues.append(f"High average image size: {avg_size:.0f}KB")
            recommendations.append("Implement image compression and optimization pipeline")
            score = 60
        elif avg_size > 100:
            recommendations.append(f"Average image size ({avg_size:.0f}KB) could be reduced")
            score = 80
        
        return score
    
    def _score_responsive_images(self, image_data: Dict, issues: List, recommendations: List) -> float:
        """Score responsive image implementation"""
        score = 100
        responsive_count = image_data['responsive_count']
        total = image_data['total_analyzed']
        
        if total == 0:
            return 100
        
        responsive_percentage = (responsive_count / total) * 100
        
        if responsive_percentage == 0:
            issues.append("No responsive images (srcset/sizes) detected")
            recommendations.append("Implement responsive images with srcset for different screen sizes")
            score = 50
        elif responsive_percentage < 50:
            recommendations.append(f"Only {responsive_percentage:.0f}% of images are responsive")
            score = 75
        elif responsive_percentage < 100:
            recommendations.append("Add srcset to remaining images for better mobile performance")
            score = 90
        
        return score
    
    def _score_lazy_loading(self, image_data: Dict, issues: List, recommendations: List) -> float:
        """Score lazy loading implementation"""
        score = 100
        lazy_count = image_data['lazy_loaded_count']
        total = image_data['total_analyzed']
        
        if total == 0:
            return 100
        
        lazy_percentage = (lazy_count / total) * 100
        
        if lazy_percentage == 0 and total > 5:
            issues.append("No lazy loading detected for images")
            recommendations.append("Add loading='lazy' to below-the-fold images")
            score = 60
        elif lazy_percentage < 50 and total > 10:
            recommendations.append(f"Only {lazy_percentage:.0f}% of images use lazy loading")
            score = 80
        
        return score
    
    def _score_alt_text(self, image_data: Dict, issues: List, recommendations: List) -> float:
        """Score alt text coverage"""
        score = 100
        missing_count = image_data['missing_alt_count']
        
        if missing_count > 0:
            issues.append(f"{missing_count} images missing alt text")
            recommendations.append("Add descriptive alt text to all images for accessibility and SEO")
            score = max(0, 100 - (missing_count * 10))
        
        return score
    
    def _calculate_savings(self, image_data: Dict) -> Dict:
        """Calculate potential file size savings"""
        total_size = image_data['total_size_kb']
        
        # Estimate savings from:
        # - WebP conversion: 25-30% savings
        # - Compression: 20-40% savings
        # - Responsive images: 30-50% savings on mobile
        
        webp_savings = total_size * 0.25 if image_data['modern_format_percentage'] < 50 else 0
        compression_savings = total_size * 0.30 if image_data['large_images_count'] > 0 else 0
        
        total_savings = webp_savings + compression_savings
        savings_percentage = (total_savings / total_size * 100) if total_size > 0 else 0
        
        return {
            'total_kb': round(total_savings, 2),
            'percentage': round(savings_percentage, 1),
            'webp_savings_kb': round(webp_savings, 2),
            'compression_savings_kb': round(compression_savings, 2)
        }
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate grade"""
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
    
    def _generate_summary(self, image_data: Dict, savings: Dict) -> str:
        """Generate optimization summary"""
        total = image_data['total_analyzed']
        
        if savings['percentage'] > 50:
            return f"Significant optimization opportunity: {savings['total_kb']:.0f}KB ({savings['percentage']:.0f}%) can be saved"
        elif savings['percentage'] > 25:
            return f"Moderate optimization needed: {savings['total_kb']:.0f}KB potential savings"
        elif savings['percentage'] > 10:
            return f"Minor optimizations possible: {savings['total_kb']:.0f}KB can be saved"
        else:
            return "Images are well optimized with minimal improvement opportunities"
