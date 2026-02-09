import httpx
from bs4 import BeautifulSoup
from typing import Dict, List
import re


class ContentAnalyzer:
    """Enhanced content quality analyzer"""
    
    def __init__(self):
        self.weights = {
            'quality': 30,
            'readability': 25,
            'structure': 20,
            'engagement': 15,
            'credibility': 10
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
            scores = {}
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get clean text content
            text = self._get_clean_text(soup)
            
            # 1. Content Quality (30 points)
            quality_score, quality_issues, quality_recs, word_count = self._analyze_content_quality(text, soup)
            scores['quality'] = quality_score
            issues.extend(quality_issues)
            recommendations.extend(quality_recs)
            
            # 2. Readability (25 points)
            read_score, read_issues, read_recs, readability_score = self._analyze_readability(text)
            scores['readability'] = read_score
            issues.extend(read_issues)
            recommendations.extend(read_recs)
            
            # 3. Content Structure (20 points)
            struct_score, struct_issues, struct_recs = self._analyze_structure(soup)
            scores['structure'] = struct_score
            issues.extend(struct_issues)
            recommendations.extend(struct_recs)
            
            # 4. Engagement Elements (15 points)
            engage_score, engage_issues, engage_recs, has_cta = self._analyze_engagement(soup, text)
            scores['engagement'] = engage_score
            issues.extend(engage_issues)
            recommendations.extend(engage_recs)
            
            # 5. Credibility Signals (10 points)
            cred_score, cred_issues, cred_recs = self._analyze_credibility(soup, text)
            scores['credibility'] = cred_score
            issues.extend(cred_issues)
            recommendations.extend(cred_recs)
            
            # Analyze tone
            tone = self._analyze_tone(text)
            
            # Calculate weighted total score
            total_score = sum(scores[key] * self.weights[key] / 100 for key in scores)
            
            return {
                "score": round(max(0, min(100, total_score)), 1),
                "readability_score": round(readability_score, 1),
                "word_count": word_count,
                "has_cta": has_cta,
                "tone": tone,
                "issues": issues[:15],
                "recommendations": recommendations[:15],
                "detailed_scores": scores
            }
            
        except Exception as e:
            return {
                "score": 0,
                "readability_score": 0,
                "word_count": 0,
                "has_cta": False,
                "tone": "Unknown",
                "issues": [f"Failed to analyze content: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"],
                "detailed_scores": {}
            }
    
    def _get_clean_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text content"""
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text
    
    def _analyze_content_quality(self, text: str, soup: BeautifulSoup) -> tuple:
        """Analyze content quality (30 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Word count
        words = text.split()
        word_count = len(words)
        
        if word_count < 200:
            issues.append(f"❌ Very low word count: {word_count} words")
            recommendations.append("Add substantial content (aim for 500+ words minimum)")
            score -= 60
        elif word_count < 300:
            issues.append(f"⚠️ Low word count: {word_count} words")
            recommendations.append("Expand content to at least 500 words for better SEO")
            score -= 40
        elif word_count < 500:
            issues.append(f"⚠️ Content could be more comprehensive: {word_count} words")
            recommendations.append("Add more valuable content (aim for 800-1500 words)")
            score -= 25
        elif word_count > 3000:
            recommendations.append("Consider breaking long content into multiple pages")
            score -= 5
        
        # Content uniqueness (check for repeated phrases)
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        if len(sentences) > 5:
            unique_sentences = len(set(sentences))
            if unique_sentences / len(sentences) < 0.8:
                issues.append("⚠️ Repetitive content detected")
                recommendations.append("Reduce repetition, provide unique value")
                score -= 20
        
        # Keyword density (check for over-optimization)
        word_freq = {}
        for word in words:
            word_lower = word.lower().strip('.,!?;:')
            if len(word_lower) > 4:
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        if word_freq:
            max_freq = max(word_freq.values())
            if max_freq / word_count > 0.03:  # More than 3% is suspicious
                issues.append("⚠️ Possible keyword stuffing detected")
                recommendations.append("Use natural language, avoid keyword over-optimization")
                score -= 25
        
        # Paragraph length
        paragraphs = soup.find_all('p')
        if paragraphs:
            long_paragraphs = [p for p in paragraphs if len(p.get_text().split()) > 150]
            if long_paragraphs:
                issues.append(f"⚠️ {len(long_paragraphs)} very long paragraphs")
                recommendations.append("Break long paragraphs into smaller chunks (50-100 words)")
                score -= 15
        
        return max(0, score), issues, recommendations, word_count
    
    def _analyze_readability(self, text: str) -> tuple:
        """Analyze readability (25 points)"""
        score = 100
        issues = []
        recommendations = []
        
        words = text.split()
        word_count = len(words)
        
        # Sentence analysis
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        sentence_count = len(sentences)
        
        if sentence_count == 0:
            return 0, ["❌ No readable sentences found"], ["Add proper sentence structure"], 0
        
        avg_sentence_length = word_count / sentence_count
        
        # Flesch Reading Ease (simplified)
        # Score: 90-100 (Very Easy), 60-70 (Standard), 0-30 (Very Difficult)
        
        # Count syllables (simplified - count vowel groups)
        total_syllables = 0
        for word in words:
            syllables = len(re.findall(r'[aeiou]+', word.lower()))
            total_syllables += max(1, syllables)
        
        avg_syllables_per_word = total_syllables / word_count if word_count > 0 else 0
        
        # Flesch Reading Ease formula (simplified)
        readability_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        readability_score = max(0, min(100, readability_score))
        
        # Analyze sentence length
        if avg_sentence_length > 25:
            issues.append(f"⚠️ Sentences too long (avg: {avg_sentence_length:.1f} words)")
            recommendations.append("Break up long sentences (aim for 15-20 words per sentence)")
            score -= 30
        elif avg_sentence_length > 20:
            issues.append(f"⚠️ Sentences could be shorter (avg: {avg_sentence_length:.1f} words)")
            recommendations.append("Simplify sentence structure for better readability")
            score -= 15
        
        # Analyze readability score
        if readability_score < 30:
            issues.append("⚠️ Content is very difficult to read")
            recommendations.append("Simplify language, use shorter words and sentences")
            score -= 35
        elif readability_score < 50:
            issues.append("⚠️ Content readability could be improved")
            recommendations.append("Use simpler language for broader audience")
            score -= 20
        elif readability_score < 60:
            recommendations.append("Good readability, consider simplifying complex terms")
            score -= 10
        
        # Check for transition words
        transition_words = ['however', 'therefore', 'moreover', 'furthermore', 'additionally', 
                          'consequently', 'meanwhile', 'nevertheless', 'thus', 'hence']
        transition_count = sum(1 for word in transition_words if word in text.lower())
        
        if sentence_count > 10 and transition_count < 2:
            recommendations.append("Use more transition words to improve flow")
            score -= 10
        
        return max(0, score), issues, recommendations, readability_score
    
    def _analyze_structure(self, soup: BeautifulSoup) -> tuple:
        """Analyze content structure (20 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Headings
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if len(headings) < 3:
            issues.append("❌ Insufficient heading structure")
            recommendations.append("Add more headings (H2, H3) to organize content")
            score -= 35
        elif len(headings) < 5:
            recommendations.append("Add more subheadings for better content organization")
            score -= 15
        
        # Lists
        lists = soup.find_all(['ul', 'ol'])
        paragraphs = soup.find_all('p')
        
        if len(paragraphs) > 5 and len(lists) == 0:
            issues.append("⚠️ No lists found")
            recommendations.append("Use bullet points or numbered lists for better scannability")
            score -= 25
        elif len(paragraphs) > 10 and len(lists) < 2:
            recommendations.append("Add more lists to break up text")
            score -= 15
        
        # Tables
        tables = soup.find_all('table')
        if tables:
            tables_without_headers = [t for t in tables if not t.find('th')]
            if tables_without_headers:
                issues.append("⚠️ Tables missing header rows")
                recommendations.append("Add <th> headers to tables for accessibility")
                score -= 15
        
        # Blockquotes
        blockquotes = soup.find_all('blockquote')
        if len(paragraphs) > 15 and len(blockquotes) == 0:
            recommendations.append("Consider using blockquotes for emphasis")
            score -= 5
        
        # Content sections
        sections = soup.find_all(['section', 'article', 'div'])
        semantic_sections = [s for s in sections if s.get('id') or s.get('class')]
        
        if len(semantic_sections) < 3 and len(paragraphs) > 10:
            recommendations.append("Organize content into semantic sections")
            score -= 10
        
        return max(0, score), issues, recommendations
    
    def _analyze_engagement(self, soup: BeautifulSoup, text: str) -> tuple:
        """Analyze engagement elements (15 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Call-to-Action
        cta_keywords = ['buy', 'shop', 'get', 'start', 'try', 'sign up', 'subscribe', 
                       'contact', 'learn more', 'download', 'register', 'join', 'book']
        text_lower = text.lower()
        cta_matches = [kw for kw in cta_keywords if kw in text_lower]
        has_cta = len(cta_matches) > 0
        
        if not has_cta:
            issues.append("❌ No clear call-to-action found")
            recommendations.append("Add compelling CTAs to guide user actions")
            score -= 40
        elif len(cta_matches) < 2:
            recommendations.append("Add more CTAs throughout the content")
            score -= 20
        
        # Buttons
        buttons = soup.find_all('button')
        cta_links = soup.find_all('a', class_=re.compile(r'btn|button|cta', re.I))
        total_ctas = len(buttons) + len(cta_links)
        
        if total_ctas == 0:
            issues.append("❌ No CTA buttons found")
            recommendations.append("Add prominent CTA buttons")
            score -= 30
        elif total_ctas < 2:
            recommendations.append("Add more CTA buttons for better conversion")
            score -= 15
        
        # Visual content
        images = soup.find_all('img')
        videos = soup.find_all(['video', 'iframe'])
        
        if len(images) == 0 and len(videos) == 0:
            issues.append("❌ No visual content (images/videos)")
            recommendations.append("Add relevant images or videos to enhance engagement")
            score -= 30
        elif len(images) < 2:
            recommendations.append("Add more images to break up text")
            score -= 15
        
        # Interactive elements
        forms = soup.find_all('form')
        if len(forms) == 0:
            recommendations.append("Consider adding a form for user interaction")
            score -= 10
        
        return max(0, score), issues, recommendations, has_cta
    
    def _analyze_credibility(self, soup: BeautifulSoup, text: str) -> tuple:
        """Analyze credibility signals (10 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Contact information
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b'
        
        has_email = bool(re.search(email_pattern, text))
        has_phone = bool(re.search(phone_pattern, text))
        
        if not has_email and not has_phone:
            issues.append("⚠️ No contact information found")
            recommendations.append("Add contact details (email/phone) for credibility")
            score -= 30
        elif not has_email or not has_phone:
            recommendations.append("Add both email and phone for better credibility")
            score -= 15
        
        # Social proof
        social_keywords = ['customer', 'client', 'testimonial', 'review', 'rating', 'trusted']
        social_proof = any(kw in text.lower() for kw in social_keywords)
        
        if not social_proof:
            recommendations.append("Add testimonials or social proof")
            score -= 20
        
        # Trust signals
        trust_keywords = ['secure', 'guarantee', 'certified', 'verified', 'privacy', 'terms']
        trust_signals = sum(1 for kw in trust_keywords if kw in text.lower())
        
        if trust_signals == 0:
            recommendations.append("Add trust signals (security, guarantees, certifications)")
            score -= 20
        
        # Author/Date information
        author = soup.find(attrs={'class': re.compile(r'author', re.I)})
        date = soup.find('time') or soup.find(attrs={'class': re.compile(r'date|published', re.I)})
        
        if not author and not date:
            recommendations.append("Add author and publication date for credibility")
            score -= 15
        
        return max(0, score), issues, recommendations
    
    def _analyze_tone(self, text: str) -> str:
        """Analyze content tone"""
        text_lower = text.lower()
        
        positive_words = ['best', 'great', 'excellent', 'amazing', 'quality', 'professional',
                         'innovative', 'outstanding', 'superior', 'premium', 'exceptional']
        negative_words = ['bad', 'poor', 'worst', 'terrible', 'cheap', 'inferior',
                         'disappointing', 'awful', 'horrible', 'mediocre']
        formal_words = ['therefore', 'furthermore', 'consequently', 'nevertheless', 'moreover']
        casual_words = ['hey', 'yeah', 'cool', 'awesome', 'stuff', 'things', 'gonna']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        formal_count = sum(1 for word in formal_words if word in text_lower)
        casual_count = sum(1 for word in casual_words if word in text_lower)
        
        # Determine tone
        if positive_count > negative_count * 2:
            sentiment = "Positive"
        elif negative_count > positive_count * 2:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        if formal_count > casual_count:
            style = "Formal"
        elif casual_count > formal_count:
            style = "Casual"
        else:
            style = "Balanced"
        
        return f"{sentiment} & {style}"
