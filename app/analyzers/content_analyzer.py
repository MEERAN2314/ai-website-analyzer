import httpx
from bs4 import BeautifulSoup
from typing import Dict
import re


class ContentAnalyzer:
    """Analyze website content quality"""
    
    async def analyze(self, url: str) -> Dict:
        """Perform content analysis"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                html = response.text
            
            soup = BeautifulSoup(html, 'html.parser')
            
            issues = []
            recommendations = []
            score = 100
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Word count
            words = text.split()
            word_count = len(words)
            
            if word_count < 300:
                issues.append(f"Low word count: {word_count} words")
                recommendations.append("Add more valuable content (aim for 500+ words)")
                score -= 20
            elif word_count < 500:
                issues.append(f"Content could be more comprehensive: {word_count} words")
                recommendations.append("Expand content to provide more value")
                score -= 10
            
            # Readability (simplified Flesch Reading Ease)
            sentences = text.split('.')
            sentence_count = len([s for s in sentences if s.strip()])
            
            if sentence_count == 0:
                readability_score = 0
            else:
                avg_sentence_length = word_count / sentence_count
                
                # Simplified readability
                if avg_sentence_length > 25:
                    readability_score = 40
                    issues.append("Sentences are too long")
                    recommendations.append("Break up long sentences for better readability")
                    score -= 10
                elif avg_sentence_length > 20:
                    readability_score = 60
                else:
                    readability_score = 80
            
            # Check for CTAs
            cta_keywords = ['buy', 'shop', 'get', 'start', 'try', 'sign up', 'subscribe', 'contact', 'learn more']
            text_lower = text.lower()
            has_cta = any(keyword in text_lower for keyword in cta_keywords)
            
            if not has_cta:
                issues.append("No clear call-to-action found")
                recommendations.append("Add compelling CTAs to guide user actions")
                score -= 15
            
            # Check for headings
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if len(headings) < 3:
                issues.append("Insufficient heading structure")
                recommendations.append("Use more headings to organize content")
                score -= 10
            
            # Check for lists
            lists = soup.find_all(['ul', 'ol'])
            if len(lists) == 0:
                issues.append("No lists found")
                recommendations.append("Use bullet points or numbered lists for better scannability")
                score -= 5
            
            # Check for images
            images = soup.find_all('img')
            if len(images) == 0:
                issues.append("No images found")
                recommendations.append("Add relevant images to enhance content")
                score -= 10
            
            # Analyze tone (simplified)
            positive_words = ['best', 'great', 'excellent', 'amazing', 'quality', 'professional']
            negative_words = ['bad', 'poor', 'worst', 'terrible', 'cheap']
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                tone = "Positive"
            elif negative_count > positive_count:
                tone = "Negative"
                issues.append("Content tone is negative")
                recommendations.append("Use more positive language")
                score -= 5
            else:
                tone = "Neutral"
            
            # Check for contact information
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            
            has_email = bool(re.search(email_pattern, text))
            has_phone = bool(re.search(phone_pattern, text))
            
            if not has_email and not has_phone:
                issues.append("No contact information found")
                recommendations.append("Add contact details for credibility")
                score -= 10
            
            return {
                "score": max(0, score),
                "readability_score": readability_score,
                "word_count": word_count,
                "has_cta": has_cta,
                "tone": tone,
                "issues": issues[:10],
                "recommendations": recommendations[:10]
            }
            
        except Exception as e:
            return {
                "score": 0,
                "readability_score": 0,
                "word_count": 0,
                "has_cta": False,
                "tone": "Unknown",
                "issues": [f"Failed to analyze content: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"]
            }
