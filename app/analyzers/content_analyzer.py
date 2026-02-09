import httpx
from bs4 import BeautifulSoup
from typing import Dict, List
import re
from collections import Counter
import math


class ContentAnalyzer:
    """Analyze website content quality with advanced metrics"""
    
    # Content quality thresholds
    THRESHOLDS = {
        'word_count': {'min': 300, 'good': 500, 'excellent': 1000},
        'sentence_length': {'min': 10, 'max': 25, 'ideal': 18},
        'paragraph_length': {'min': 40, 'max': 150},
        'readability': {'easy': 80, 'standard': 60, 'difficult': 40},
        'heading_ratio': {'min': 0.02, 'max': 0.10},  # headings per 100 words
        'media_ratio': {'min': 0.001, 'max': 0.01}  # images per word
    }
    
    async def analyze(self, url: str) -> Dict:
        """Perform comprehensive content analysis"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                html = response.text
            
            soup = BeautifulSoup(html, 'html.parser')
            
            issues = []
            recommendations = []
            
            # Remove non-content elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Analyze different content aspects
            text_score, text_data = self._analyze_text_content(soup, issues, recommendations)
            readability_score, readability_data = self._analyze_readability(soup, text_data, issues, recommendations)
            structure_score, structure_data = self._analyze_content_structure(soup, text_data, issues, recommendations)
            engagement_score, engagement_data = self._analyze_engagement_elements(soup, issues, recommendations)
            media_score, media_data = self._analyze_media_content(soup, text_data, issues, recommendations)
            quality_score, quality_data = self._analyze_content_quality(soup, text_data, issues, recommendations)
            
            # Weighted scoring
            weights = {
                'text': 20,
                'readability': 20,
                'structure': 15,
                'engagement': 15,
                'media': 15,
                'quality': 15
            }
            
            score_components = {
                'text': text_score,
                'readability': readability_score,
                'structure': structure_score,
                'engagement': engagement_score,
                'media': media_score,
                'quality': quality_score
            }
            
            final_score = sum(score_components[k] * (weights[k] / 100) for k in weights)
            
            # Calculate content grade
            grade = self._calculate_grade(final_score)
            
            return {
                "score": round(final_score, 1),
                "grade": grade,
                "word_count": text_data['word_count'],
                "sentence_count": text_data['sentence_count'],
                "paragraph_count": text_data['paragraph_count'],
                "readability_score": readability_data['flesch_score'],
                "readability_level": readability_data['level'],
                "avg_sentence_length": readability_data['avg_sentence_length'],
                "avg_word_length": readability_data['avg_word_length'],
                "has_cta": engagement_data['has_cta'],
                "cta_count": engagement_data['cta_count'],
                "tone": quality_data['tone'],
                "sentiment_score": quality_data['sentiment_score'],
                "keyword_usage": quality_data['top_keywords'],
                "content_depth": self._calculate_content_depth(text_data, structure_data),
                "media_count": media_data['total_media'],
                "images_with_alt": media_data['images_with_alt'],
                "score_breakdown": {k: round(v, 1) for k, v in score_components.items()},
                "issues": issues,
                "recommendations": recommendations,
                "content_health": self._calculate_content_health(score_components)
            }
            
        except Exception as e:
            return {
                "score": 0,
                "grade": "F",
                "word_count": 0,
                "readability_score": 0,
                "has_cta": False,
                "tone": "Unknown",
                "issues": [f"Failed to analyze content: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"]
            }
    
    def _analyze_text_content(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze basic text content metrics"""
        # Get main content text
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Count words
        words = text.split()
        word_count = len(words)
        
        # Count sentences
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Count paragraphs
        paragraphs = soup.find_all('p')
        paragraph_count = len([p for p in paragraphs if p.get_text().strip()])
        
        score = 100
        
        # Analyze word count
        if word_count < self.THRESHOLDS['word_count']['min']:
            issues.append(f"❌ Insufficient content ({word_count} words) - Minimum 300 words recommended")
            recommendations.append("📝 Add comprehensive, valuable content (target 500-1000+ words)")
            score = 30
        elif word_count < self.THRESHOLDS['word_count']['good']:
            issues.append(f"⚠️ Content could be more comprehensive ({word_count} words)")
            recommendations.append("📄 Expand content to 500+ words for better engagement and SEO")
            score = 65
        elif word_count < self.THRESHOLDS['word_count']['excellent']:
            recommendations.append(f"💡 Good content length ({word_count} words) - Consider expanding for competitive topics")
            score = 85
        
        # Check paragraph count
        if paragraph_count < 3:
            issues.append("⚠️ Very few paragraphs - Content may lack structure")
            recommendations.append("📐 Break content into multiple paragraphs for better readability")
            score = min(score, 70)
        
        return score, {
            'text': text,
            'words': words,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count
        }
    
    def _analyze_readability(self, soup: BeautifulSoup, text_data: Dict, issues: List, recommendations: List) -> tuple:
        """Analyze content readability using Flesch Reading Ease"""
        words = text_data['words']
        word_count = text_data['word_count']
        sentence_count = text_data['sentence_count']
        
        if word_count == 0 or sentence_count == 0:
            return 0, {'flesch_score': 0, 'level': 'Unknown', 'avg_sentence_length': 0, 'avg_word_length': 0}
        
        # Calculate average sentence length
        avg_sentence_length = word_count / sentence_count
        
        # Calculate average syllables per word (simplified)
        total_syllables = sum(self._count_syllables(word) for word in words)
        avg_syllables_per_word = total_syllables / word_count if word_count > 0 else 0
        
        # Calculate average word length
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        
        # Flesch Reading Ease Score
        flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        flesch_score = max(0, min(100, flesch_score))
        
        # Determine readability level
        if flesch_score >= 80:
            level = "Very Easy"
            score = 100
        elif flesch_score >= 60:
            level = "Easy"
            score = 90
        elif flesch_score >= 50:
            level = "Fairly Easy"
            score = 80
        elif flesch_score >= 30:
            level = "Difficult"
            score = 60
            issues.append(f"⚠️ Content is difficult to read (Flesch score: {flesch_score:.0f})")
            recommendations.append("📖 Simplify language and shorten sentences for better readability")
        else:
            level = "Very Difficult"
            score = 40
            issues.append(f"❌ Content is very difficult to read (Flesch score: {flesch_score:.0f})")
            recommendations.append("📖 Significantly simplify content - use shorter sentences and simpler words")
        
        # Check sentence length
        if avg_sentence_length > self.THRESHOLDS['sentence_length']['max']:
            issues.append(f"⚠️ Sentences too long (avg {avg_sentence_length:.1f} words)")
            recommendations.append("✂️ Break up long sentences - aim for 15-20 words per sentence")
            score = min(score, 70)
        elif avg_sentence_length < self.THRESHOLDS['sentence_length']['min']:
            issues.append(f"⚠️ Sentences too short (avg {avg_sentence_length:.1f} words)")
            recommendations.append("📝 Vary sentence length for better flow")
            score = min(score, 75)
        
        return score, {
            'flesch_score': round(flesch_score, 1),
            'level': level,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'avg_word_length': round(avg_word_length, 1),
            'avg_syllables_per_word': round(avg_syllables_per_word, 2)
        }
    
    def _analyze_content_structure(self, soup: BeautifulSoup, text_data: Dict, issues: List, recommendations: List) -> tuple:
        """Analyze content structure and organization"""
        word_count = text_data['word_count']
        
        # Count structural elements
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        lists = soup.find_all(['ul', 'ol'])
        list_items = soup.find_all('li')
        blockquotes = soup.find_all('blockquote')
        tables = soup.find_all('table')
        
        score = 100
        
        # Analyze heading usage
        if word_count > 0:
            heading_ratio = len(headings) / (word_count / 100)
            
            if len(headings) < 2:
                issues.append("❌ Insufficient headings - Content lacks structure")
                recommendations.append("🏷️ Add headings (H2, H3) to organize content into sections")
                score -= 25
            elif heading_ratio < self.THRESHOLDS['heading_ratio']['min']:
                issues.append("⚠️ Too few headings for content length")
                recommendations.append("📊 Add more subheadings to break up content")
                score -= 15
            elif heading_ratio > self.THRESHOLDS['heading_ratio']['max']:
                issues.append("⚠️ Too many headings - May fragment content")
                recommendations.append("🎯 Consolidate some headings for better flow")
                score -= 10
        
        # Analyze lists
        if len(lists) == 0 and word_count > 300:
            issues.append("⚠️ No lists found - Reduces scannability")
            recommendations.append("📋 Use bullet points or numbered lists for key information")
            score -= 15
        elif len(list_items) > 20:
            recommendations.append("💡 Consider breaking up very long lists")
            score -= 5
        
        # Check for other structural elements
        if len(blockquotes) == 0 and word_count > 500:
            recommendations.append("💡 Consider adding quotes or testimonials for credibility")
        
        return score, {
            'headings': len(headings),
            'lists': len(lists),
            'list_items': len(list_items),
            'blockquotes': len(blockquotes),
            'tables': len(tables)
        }
    
    def _analyze_engagement_elements(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze engagement elements like CTAs, links, etc."""
        text = soup.get_text().lower()
        
        # Check for CTAs
        cta_keywords = [
            'buy now', 'shop now', 'get started', 'start free', 'try free', 'sign up',
            'subscribe', 'contact us', 'learn more', 'download', 'register', 'join',
            'book now', 'order now', 'get quote', 'request demo'
        ]
        
        cta_count = sum(text.count(keyword) for keyword in cta_keywords)
        has_cta = cta_count > 0
        
        # Find CTA buttons
        buttons = soup.find_all(['button', 'a'])
        cta_buttons = [b for b in buttons if any(keyword in b.get_text().lower() for keyword in cta_keywords)]
        
        score = 100
        
        if not has_cta and len(cta_buttons) == 0:
            issues.append("❌ No clear call-to-action found")
            recommendations.append("🎯 Add compelling CTAs to guide user actions and increase conversions")
            score = 40
        elif cta_count < 2:
            issues.append("⚠️ Limited CTAs - May miss conversion opportunities")
            recommendations.append("💡 Add more strategic CTAs throughout content")
            score = 70
        
        # Check for contact information
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        has_email = bool(re.search(email_pattern, text))
        has_phone = bool(re.search(phone_pattern, text))
        
        if not has_email and not has_phone:
            issues.append("⚠️ No contact information found")
            recommendations.append("📞 Add contact details (email/phone) for credibility and trust")
            score = min(score, 75)
        
        # Check for social proof
        social_keywords = ['review', 'testimonial', 'customer', 'rating', 'stars', 'trusted']
        has_social_proof = any(keyword in text for keyword in social_keywords)
        
        if not has_social_proof:
            recommendations.append("⭐ Add testimonials or reviews for social proof")
            score = min(score, 85)
        
        return score, {
            'has_cta': has_cta,
            'cta_count': cta_count,
            'cta_buttons': len(cta_buttons),
            'has_contact': has_email or has_phone,
            'has_social_proof': has_social_proof
        }
    
    def _analyze_media_content(self, soup: BeautifulSoup, text_data: Dict, issues: List, recommendations: List) -> tuple:
        """Analyze media content (images, videos)"""
        word_count = text_data['word_count']
        
        images = soup.find_all('img')
        videos = soup.find_all(['video', 'iframe'])
        
        # Check image alt text
        images_with_alt = len([img for img in images if img.get('alt')])
        images_without_alt = len(images) - images_with_alt
        
        score = 100
        
        # Analyze image usage
        if len(images) == 0 and word_count > 300:
            issues.append("❌ No images found - Visual content improves engagement")
            recommendations.append("🖼️ Add relevant images to enhance content and break up text")
            score = 50
        elif len(images) < 2 and word_count > 500:
            issues.append("⚠️ Limited visual content")
            recommendations.append("📸 Add more images to improve visual appeal")
            score = 70
        
        # Check alt text
        if images_without_alt > 0:
            issues.append(f"⚠️ {images_without_alt} images missing alt text")
            recommendations.append("♿ Add descriptive alt text to all images for accessibility and SEO")
            score = min(score, 75)
        
        # Check media ratio
        if word_count > 0:
            media_ratio = len(images) / word_count
            if media_ratio > self.THRESHOLDS['media_ratio']['max']:
                issues.append("⚠️ Too many images relative to text")
                recommendations.append("⚖️ Balance image-to-text ratio for better user experience")
                score = min(score, 80)
        
        # Check for videos
        if len(videos) > 0:
            recommendations.append("✨ Great! Video content increases engagement")
        elif word_count > 800:
            recommendations.append("🎥 Consider adding video content for better engagement")
        
        return score, {
            'total_media': len(images) + len(videos),
            'images': len(images),
            'videos': len(videos),
            'images_with_alt': images_with_alt,
            'images_without_alt': images_without_alt
        }
    
    def _analyze_content_quality(self, soup: BeautifulSoup, text_data: Dict, issues: List, recommendations: List) -> tuple:
        """Analyze content quality, tone, and keyword usage"""
        text = text_data['text'].lower()
        words = text_data['words']
        
        # Sentiment analysis (simplified)
        positive_words = [
            'best', 'great', 'excellent', 'amazing', 'quality', 'professional',
            'innovative', 'reliable', 'trusted', 'premium', 'superior', 'outstanding'
        ]
        negative_words = [
            'bad', 'poor', 'worst', 'terrible', 'cheap', 'inferior',
            'disappointing', 'unreliable', 'subpar'
        ]
        
        positive_count = sum(text.count(word) for word in positive_words)
        negative_count = sum(text.count(word) for word in negative_words)
        
        # Calculate sentiment score (-100 to 100)
        total_sentiment = positive_count + negative_count
        if total_sentiment > 0:
            sentiment_score = ((positive_count - negative_count) / total_sentiment) * 100
        else:
            sentiment_score = 0
        
        # Determine tone
        if sentiment_score > 30:
            tone = "Positive"
            score = 100
        elif sentiment_score > 0:
            tone = "Slightly Positive"
            score = 90
        elif sentiment_score > -30:
            tone = "Neutral"
            score = 80
        else:
            tone = "Negative"
            score = 60
            issues.append("⚠️ Content tone is negative")
            recommendations.append("😊 Use more positive, encouraging language")
        
        # Keyword analysis
        stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'will', 'your', 'are', 'can', 'our', 'more', 'about', 'what', 'when', 'where', 'which', 'their', 'there', 'been', 'were', 'they', 'than', 'into', 'also', 'other', 'some', 'such', 'only', 'over', 'just', 'like', 'these', 'those', 'then', 'them', 'here', 'very', 'much', 'many', 'most', 'both', 'each', 'does', 'done', 'being', 'would', 'could', 'should'}
        
        filtered_words = [word for word in words if word.lower() not in stop_words and len(word) > 3]
        word_freq = Counter(filtered_words)
        top_keywords = [word for word, _ in word_freq.most_common(10)]
        
        # Check for keyword stuffing
        if len(filtered_words) > 0:
            max_freq = word_freq.most_common(1)[0][1] if word_freq else 0
            keyword_density = (max_freq / len(filtered_words)) * 100
            
            if keyword_density > 5:
                issues.append(f"⚠️ Possible keyword stuffing detected ({keyword_density:.1f}% density)")
                recommendations.append("⚖️ Reduce keyword repetition for more natural content")
                score = min(score, 70)
        
        return score, {
            'tone': tone,
            'sentiment_score': round(sentiment_score, 1),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'top_keywords': top_keywords[:5]
        }
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        # Every word has at least one syllable
        if syllable_count == 0:
            syllable_count = 1
        
        return syllable_count
    
    def _calculate_content_depth(self, text_data: Dict, structure_data: Dict) -> str:
        """Calculate content depth rating"""
        word_count = text_data['word_count']
        headings = structure_data['headings']
        lists = structure_data['lists']
        
        depth_score = 0
        
        if word_count >= 1000:
            depth_score += 40
        elif word_count >= 500:
            depth_score += 25
        elif word_count >= 300:
            depth_score += 15
        
        if headings >= 5:
            depth_score += 30
        elif headings >= 3:
            depth_score += 20
        
        if lists >= 2:
            depth_score += 30
        elif lists >= 1:
            depth_score += 15
        
        if depth_score >= 80:
            return "Comprehensive"
        elif depth_score >= 60:
            return "Detailed"
        elif depth_score >= 40:
            return "Moderate"
        else:
            return "Basic"
    
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
    
    def _calculate_content_health(self, score_components: Dict) -> str:
        """Calculate overall content health"""
        avg_score = sum(score_components.values()) / len(score_components)
        
        if avg_score >= 85:
            return "Excellent - High-quality, engaging content"
        elif avg_score >= 70:
            return "Good - Content is solid with room for improvement"
        elif avg_score >= 50:
            return "Fair - Content needs significant enhancement"
        else:
            return "Poor - Content requires major improvements"
