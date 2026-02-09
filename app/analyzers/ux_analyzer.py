import httpx
from bs4 import BeautifulSoup
from typing import Dict, List
import re


class UXAnalyzer:
    """Enhanced UX/UI analyzer with comprehensive checks"""
    
    def __init__(self):
        self.weights = {
            'mobile': 20,
            'navigation': 15,
            'accessibility': 25,
            'forms': 15,
            'interactive': 15,
            'visual': 10
        }
    
    async def analyze(self, url: str) -> Dict:
        """Perform comprehensive UX analysis"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                html = response.text
            
            soup = BeautifulSoup(html, 'html.parser')
            
            issues = []
            recommendations = []
            scores = {}
            
            # 1. Mobile Responsiveness (20 points)
            mobile_score, mobile_issues, mobile_recs = self._check_mobile_responsiveness(soup)
            scores['mobile'] = mobile_score
            issues.extend(mobile_issues)
            recommendations.extend(mobile_recs)
            
            # 2. Navigation (15 points)
            nav_score, nav_issues, nav_recs = self._check_navigation(soup)
            scores['navigation'] = nav_score
            issues.extend(nav_issues)
            recommendations.extend(nav_recs)
            
            # 3. Accessibility (25 points)
            a11y_score, a11y_issues, a11y_recs = self._check_accessibility(soup)
            scores['accessibility'] = a11y_score
            issues.extend(a11y_issues)
            recommendations.extend(a11y_recs)
            
            # 4. Forms Usability (15 points)
            form_score, form_issues, form_recs = self._check_forms(soup)
            scores['forms'] = form_score
            issues.extend(form_issues)
            recommendations.extend(form_recs)
            
            # 5. Interactive Elements (15 points)
            interactive_score, int_issues, int_recs = self._check_interactive_elements(soup)
            scores['interactive'] = interactive_score
            issues.extend(int_issues)
            recommendations.extend(int_recs)
            
            # 6. Visual Hierarchy (10 points)
            visual_score, vis_issues, vis_recs = self._check_visual_hierarchy(soup)
            scores['visual'] = visual_score
            issues.extend(vis_issues)
            recommendations.extend(vis_recs)
            
            # Calculate weighted total score
            total_score = sum(scores[key] * self.weights[key] / 100 for key in scores)
            
            return {
                "score": round(max(0, min(100, total_score)), 1),
                "issues": issues[:15],
                "recommendations": recommendations[:15],
                "mobile_friendly": scores['mobile'] >= 80,
                "accessibility_score": round(scores['accessibility'], 1),
                "detailed_scores": scores
            }
            
        except Exception as e:
            return {
                "score": 0,
                "issues": [f"Failed to analyze UX: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"],
                "mobile_friendly": False,
                "accessibility_score": 0,
                "detailed_scores": {}
            }
    
    def _check_mobile_responsiveness(self, soup: BeautifulSoup) -> tuple:
        """Check mobile responsiveness (20 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Viewport meta tag (critical)
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            issues.append("❌ Missing mobile viewport meta tag")
            recommendations.append("Add <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
            score -= 40
        elif viewport.get('content'):
            content = viewport.get('content', '')
            if 'width=device-width' not in content:
                issues.append("⚠️ Viewport not optimized for mobile")
                recommendations.append("Set viewport width to device-width")
                score -= 20
        
        # Responsive images
        images = soup.find_all('img')
        responsive_images = [img for img in images if img.get('srcset') or 'responsive' in img.get('class', [])]
        if images and len(responsive_images) / len(images) < 0.3:
            issues.append("⚠️ Few responsive images detected")
            recommendations.append("Use srcset attribute for responsive images")
            score -= 15
        
        # Media queries check (look for responsive CSS)
        styles = soup.find_all('style')
        has_media_queries = any('@media' in str(style) for style in styles)
        links = soup.find_all('link', rel='stylesheet')
        
        if not has_media_queries and len(links) == 0:
            issues.append("⚠️ No responsive CSS detected")
            recommendations.append("Implement responsive design with CSS media queries")
            score -= 25
        
        return max(0, score), issues, recommendations
    
    def _check_navigation(self, soup: BeautifulSoup) -> tuple:
        """Check navigation structure (15 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Find navigation
        nav = soup.find('nav') or soup.find(attrs={'role': 'navigation'})
        
        if not nav:
            issues.append("❌ No semantic navigation element found")
            recommendations.append("Add <nav> element or role='navigation' for better structure")
            score -= 40
        else:
            # Check for navigation links
            nav_links = nav.find_all('a')
            if len(nav_links) < 3:
                issues.append("⚠️ Very few navigation links")
                recommendations.append("Add more navigation options for better site structure")
                score -= 20
            elif len(nav_links) > 10:
                issues.append("⚠️ Too many navigation links (cognitive overload)")
                recommendations.append("Simplify navigation to 5-7 main items, use dropdowns for sub-items")
                score -= 15
            
            # Check for mobile menu (hamburger)
            mobile_menu = soup.find(class_=re.compile(r'(hamburger|mobile-menu|menu-toggle)', re.I))
            if not mobile_menu and len(nav_links) > 5:
                issues.append("⚠️ No mobile menu detected with many nav items")
                recommendations.append("Implement hamburger menu for mobile devices")
                score -= 20
        
        # Check for breadcrumbs
        breadcrumb = soup.find(attrs={'aria-label': 'breadcrumb'}) or soup.find(class_=re.compile(r'breadcrumb', re.I))
        if not breadcrumb:
            recommendations.append("Consider adding breadcrumb navigation for better UX")
            score -= 10
        
        return max(0, score), issues, recommendations
    
    def _check_accessibility(self, soup: BeautifulSoup) -> tuple:
        """Check accessibility (25 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Images without alt text
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        if images_without_alt:
            percentage = (len(images_without_alt) / len(images) * 100) if images else 0
            issues.append(f"❌ {len(images_without_alt)} images ({percentage:.0f}%) missing alt text")
            recommendations.append("Add descriptive alt text to all images for screen readers")
            score -= min(30, percentage / 2)
        
        # Heading hierarchy
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')
        
        if len(h1_tags) == 0:
            issues.append("❌ No H1 heading found")
            recommendations.append("Add a single H1 heading as the main page title")
            score -= 20
        elif len(h1_tags) > 1:
            issues.append("⚠️ Multiple H1 headings found (confuses screen readers)")
            recommendations.append("Use only one H1 heading per page")
            score -= 15
        
        if len(h2_tags) == 0 and len(h3_tags) > 0:
            issues.append("⚠️ Skipped heading levels (H3 without H2)")
            recommendations.append("Maintain proper heading hierarchy (H1 → H2 → H3)")
            score -= 10
        
        # ARIA labels and roles
        interactive_elements = soup.find_all(['button', 'a', 'input'])
        elements_with_aria = [el for el in interactive_elements if el.get('aria-label') or el.get('role')]
        
        if interactive_elements and len(elements_with_aria) / len(interactive_elements) < 0.2:
            issues.append("⚠️ Few ARIA labels for interactive elements")
            recommendations.append("Add ARIA labels to buttons and links for better accessibility")
            score -= 15
        
        # Color contrast (check for inline styles with colors)
        elements_with_color = soup.find_all(style=re.compile(r'color:', re.I))
        if len(elements_with_color) > 10:
            recommendations.append("Ensure sufficient color contrast (WCAG AA: 4.5:1 for text)")
            score -= 5
        
        # Skip links
        skip_link = soup.find('a', href='#main') or soup.find('a', href='#content')
        if not skip_link:
            recommendations.append("Add skip navigation link for keyboard users")
            score -= 10
        
        return max(0, score), issues, recommendations
    
    def _check_forms(self, soup: BeautifulSoup) -> tuple:
        """Check form usability (15 points)"""
        score = 100
        issues = []
        recommendations = []
        
        forms = soup.find_all('form')
        
        if not forms:
            return 100, [], []  # No forms, no issues
        
        for idx, form in enumerate(forms[:3]):  # Check first 3 forms
            # Labels
            inputs = form.find_all(['input', 'textarea', 'select'])
            labels = form.find_all('label')
            
            if inputs and len(labels) < len(inputs):
                issues.append(f"❌ Form {idx+1}: Missing labels for some inputs")
                recommendations.append("Add <label> tags for all form inputs")
                score -= 25
            
            # Required field indicators
            required_inputs = form.find_all(attrs={'required': True})
            if required_inputs and not form.find(text=re.compile(r'\*|required', re.I)):
                issues.append(f"⚠️ Form {idx+1}: No visual indicator for required fields")
                recommendations.append("Mark required fields with asterisk (*) or 'required' text")
                score -= 15
            
            # Submit button
            submit_btn = form.find(['button', 'input'], type='submit')
            if not submit_btn:
                issues.append(f"❌ Form {idx+1}: No clear submit button")
                recommendations.append("Add a clear submit button to the form")
                score -= 20
            
            # Placeholder vs label
            inputs_with_placeholder = form.find_all(attrs={'placeholder': True})
            if inputs_with_placeholder and len(labels) == 0:
                issues.append(f"⚠️ Form {idx+1}: Using placeholders instead of labels")
                recommendations.append("Use labels instead of placeholders (better accessibility)")
                score -= 15
        
        return max(0, score), issues, recommendations
    
    def _check_interactive_elements(self, soup: BeautifulSoup) -> tuple:
        """Check interactive elements (15 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Buttons
        buttons = soup.find_all('button')
        links_as_buttons = soup.find_all('a', class_=re.compile(r'btn|button', re.I))
        total_buttons = len(buttons) + len(links_as_buttons)
        
        if total_buttons < 2:
            issues.append("⚠️ Very few interactive buttons/CTAs")
            recommendations.append("Add clear call-to-action buttons to guide users")
            score -= 25
        
        # Check for empty buttons
        empty_buttons = [btn for btn in buttons if not btn.get_text().strip() and not btn.find('img')]
        if empty_buttons:
            issues.append(f"❌ {len(empty_buttons)} buttons with no text or icon")
            recommendations.append("Add descriptive text or aria-label to all buttons")
            score -= 20
        
        # Links
        links = soup.find_all('a')
        external_links = [link for link in links if link.get('href', '').startswith('http')]
        
        # Check for "click here" or generic link text
        generic_links = [link for link in links if link.get_text().strip().lower() in ['click here', 'here', 'read more', 'more']]
        if generic_links:
            issues.append(f"⚠️ {len(generic_links)} links with generic text ('click here', 'read more')")
            recommendations.append("Use descriptive link text that explains the destination")
            score -= 15
        
        # External links without target
        external_without_target = [link for link in external_links if not link.get('target')]
        if len(external_without_target) > 3:
            recommendations.append("Consider opening external links in new tab (target='_blank')")
            score -= 10
        
        # Focus indicators (check for :focus styles)
        styles = soup.find_all('style')
        has_focus_styles = any(':focus' in str(style) for style in styles)
        if not has_focus_styles:
            issues.append("⚠️ No custom focus styles detected")
            recommendations.append("Add visible focus indicators for keyboard navigation")
            score -= 15
        
        return max(0, score), issues, recommendations
    
    def _check_visual_hierarchy(self, soup: BeautifulSoup) -> tuple:
        """Check visual hierarchy (10 points)"""
        score = 100
        issues = []
        recommendations = []
        
        # Heading distribution
        all_headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if len(all_headings) < 3:
            issues.append("⚠️ Insufficient heading structure")
            recommendations.append("Use more headings (H2, H3) to organize content")
            score -= 30
        
        # Whitespace (check for excessive inline styles)
        elements_with_margin = soup.find_all(style=re.compile(r'margin|padding', re.I))
        if len(elements_with_margin) > 20:
            recommendations.append("Consider using CSS classes instead of inline styles for consistency")
            score -= 10
        
        # Lists for better scannability
        lists = soup.find_all(['ul', 'ol'])
        paragraphs = soup.find_all('p')
        
        if paragraphs and len(lists) == 0:
            recommendations.append("Use bullet points or numbered lists for better scannability")
            score -= 20
        
        # Visual content
        images = soup.find_all('img')
        videos = soup.find_all(['video', 'iframe'])
        
        if len(images) == 0 and len(videos) == 0:
            issues.append("⚠️ No visual content (images/videos) found")
            recommendations.append("Add relevant images or videos to enhance engagement")
            score -= 25
        
        return max(0, score), issues, recommendations
