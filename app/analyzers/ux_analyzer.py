import httpx
from bs4 import BeautifulSoup
from typing import Dict, List
import re


class UXAnalyzer:
    """Analyze website UX/UI with comprehensive accessibility and usability checks"""
    
    # UX best practice thresholds
    THRESHOLDS = {
        'navigation_items': {'min': 3, 'max': 7},
        'form_fields': {'max': 10},
        'button_count': {'min': 2, 'max': 15},
        'color_contrast': {'min': 4.5},  # WCAG AA standard
        'touch_target': {'min': 44}  # pixels
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
            
            # Analyze different UX aspects
            mobile_score, mobile_data = self._analyze_mobile_friendliness(soup, issues, recommendations)
            navigation_score, navigation_data = self._analyze_navigation(soup, issues, recommendations)
            accessibility_score, accessibility_data = self._analyze_accessibility(soup, issues, recommendations)
            forms_score, forms_data = self._analyze_forms(soup, issues, recommendations)
            interactive_score, interactive_data = self._analyze_interactive_elements(soup, issues, recommendations)
            visual_score, visual_data = self._analyze_visual_design(soup, issues, recommendations)
            
            # Weighted scoring
            weights = {
                'mobile': 20,
                'navigation': 18,
                'accessibility': 22,
                'forms': 15,
                'interactive': 15,
                'visual': 10
            }
            
            score_components = {
                'mobile': mobile_score,
                'navigation': navigation_score,
                'accessibility': accessibility_score,
                'forms': forms_score,
                'interactive': interactive_score,
                'visual': visual_score
            }
            
            final_score = sum(score_components[k] * (weights[k] / 100) for k in weights)
            
            # Calculate UX grade
            grade = self._calculate_grade(final_score)
            
            # Calculate overall accessibility score
            accessibility_overall = self._calculate_accessibility_score(accessibility_data, mobile_data, forms_data)
            
            return {
                "score": round(final_score, 1),
                "grade": grade,
                "mobile_friendly": mobile_data['is_mobile_friendly'],
                "has_viewport": mobile_data['has_viewport'],
                "responsive_images": mobile_data['responsive_images'],
                "accessibility_score": accessibility_overall,
                "wcag_compliance": accessibility_data['wcag_level'],
                "navigation_quality": navigation_data['quality'],
                "navigation_items": navigation_data['item_count'],
                "form_accessibility": forms_data['accessibility_score'],
                "interactive_elements": interactive_data['total_interactive'],
                "has_skip_link": accessibility_data['has_skip_link'],
                "aria_usage": accessibility_data['aria_usage'],
                "score_breakdown": {k: round(v, 1) for k, v in score_components.items()},
                "issues": issues,
                "recommendations": recommendations,
                "ux_health": self._calculate_ux_health(score_components)
            }
            
        except Exception as e:
            return {
                "score": 0,
                "grade": "F",
                "mobile_friendly": False,
                "accessibility_score": 0,
                "issues": [f"Failed to analyze UX: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"]
            }
    
    def _analyze_mobile_friendliness(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze mobile responsiveness"""
        score = 100
        
        # Check viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        has_viewport = bool(viewport)
        
        if not has_viewport:
            issues.append("❌ Critical: Missing viewport meta tag - Not mobile-friendly")
            recommendations.append("📱 Add <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
            score = 30
        else:
            viewport_content = viewport.get('content', '').lower()
            if 'width=device-width' not in viewport_content:
                issues.append("⚠️ Viewport not properly configured")
                recommendations.append("📱 Set viewport width to device-width")
                score = 60
        
        # Check for responsive images
        images = soup.find_all('img')
        responsive_images = 0
        
        for img in images:
            if img.get('srcset') or img.get('sizes'):
                responsive_images += 1
        
        if len(images) > 0:
            responsive_ratio = responsive_images / len(images)
            if responsive_ratio == 0:
                issues.append("⚠️ No responsive images found")
                recommendations.append("🖼️ Use srcset and sizes attributes for responsive images")
                score = min(score, 75)
            elif responsive_ratio < 0.5:
                recommendations.append("💡 Consider making more images responsive")
                score = min(score, 85)
        
        # Check for mobile-specific meta tags
        apple_mobile = soup.find('meta', attrs={'name': 'apple-mobile-web-app-capable'})
        theme_color = soup.find('meta', attrs={'name': 'theme-color'})
        
        if not theme_color:
            recommendations.append("🎨 Add theme-color meta tag for better mobile browser integration")
        
        # Check for fixed-width elements (potential mobile issues)
        style_tags = soup.find_all('style')
        inline_styles = soup.find_all(style=True)
        
        fixed_width_count = 0
        for element in inline_styles:
            style = element.get('style', '')
            if re.search(r'width:\s*\d+px', style):
                fixed_width_count += 1
        
        if fixed_width_count > 5:
            issues.append(f"⚠️ {fixed_width_count} elements with fixed pixel widths")
            recommendations.append("📐 Use relative units (%, em, rem) instead of fixed pixels")
            score = min(score, 80)
        
        return score, {
            'is_mobile_friendly': has_viewport,
            'has_viewport': has_viewport,
            'responsive_images': responsive_images,
            'total_images': len(images),
            'has_theme_color': bool(theme_color)
        }
    
    def _analyze_navigation(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze navigation structure and usability"""
        score = 100
        
        # Find navigation elements
        nav = soup.find('nav') or soup.find(attrs={'role': 'navigation'})
        
        if not nav:
            issues.append("❌ Critical: No navigation structure found")
            recommendations.append("🧭 Add a clear <nav> element with site navigation")
            score = 30
            return score, {'quality': 'Poor', 'item_count': 0, 'has_nav': False}
        
        # Count navigation items
        nav_links = nav.find_all('a')
        nav_item_count = len(nav_links)
        
        if nav_item_count == 0:
            issues.append("❌ Navigation has no links")
            recommendations.append("🔗 Add navigation links to main site sections")
            score = 40
        elif nav_item_count < self.THRESHOLDS['navigation_items']['min']:
            issues.append(f"⚠️ Very few navigation items ({nav_item_count})")
            recommendations.append("📊 Add more navigation links for better site structure")
            score = 70
        elif nav_item_count > self.THRESHOLDS['navigation_items']['max']:
            issues.append(f"⚠️ Too many top-level navigation items ({nav_item_count})")
            recommendations.append("📉 Simplify navigation - use dropdowns for secondary items")
            score = 75
        
        # Check for navigation labels
        empty_nav_links = [link for link in nav_links if not link.get_text().strip()]
        if empty_nav_links:
            issues.append(f"⚠️ {len(empty_nav_links)} navigation links without text")
            recommendations.append("📝 Add descriptive text to all navigation links")
            score = min(score, 70)
        
        # Check for aria-label or aria-labelledby on nav
        if not nav.get('aria-label') and not nav.get('aria-labelledby'):
            recommendations.append("♿ Add aria-label to <nav> for better accessibility")
            score = min(score, 90)
        
        # Check for breadcrumbs
        breadcrumbs = soup.find(attrs={'aria-label': 'breadcrumb'}) or soup.find('ol', class_=re.compile('breadcrumb', re.I))
        if not breadcrumbs:
            recommendations.append("💡 Consider adding breadcrumb navigation for better UX")
        
        # Determine navigation quality
        if score >= 85:
            quality = "Excellent"
        elif score >= 70:
            quality = "Good"
        elif score >= 50:
            quality = "Fair"
        else:
            quality = "Poor"
        
        return score, {
            'quality': quality,
            'item_count': nav_item_count,
            'has_nav': True,
            'has_breadcrumbs': bool(breadcrumbs)
        }
    
    def _analyze_accessibility(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze accessibility compliance (WCAG)"""
        score = 100
        accessibility_issues = []
        
        # Check for skip link
        skip_link = soup.find('a', href='#main') or soup.find('a', href='#content')
        has_skip_link = bool(skip_link)
        
        if not has_skip_link:
            issues.append("⚠️ Missing skip navigation link")
            recommendations.append("♿ Add skip link for keyboard navigation (e.g., <a href='#main'>Skip to content</a>)")
            score -= 10
            accessibility_issues.append('skip_link')
        
        # Check images for alt text
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt') and img.get('alt') != '']
        
        if images_without_alt:
            issues.append(f"❌ Critical: {len(images_without_alt)} images missing alt text")
            recommendations.append("♿ Add descriptive alt text to all images for screen readers")
            score -= 20
            accessibility_issues.append('alt_text')
        
        # Check for proper heading hierarchy
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')
        
        if len(h1_tags) == 0:
            issues.append("❌ No H1 heading - Poor document structure")
            recommendations.append("🏷️ Add a single H1 heading for page title")
            score -= 15
            accessibility_issues.append('heading_structure')
        elif len(h1_tags) > 1:
            issues.append("⚠️ Multiple H1 headings - Confusing for screen readers")
            recommendations.append("🎯 Use only one H1 per page")
            score -= 10
            accessibility_issues.append('heading_structure')
        
        # Check for ARIA landmarks
        landmarks = soup.find_all(attrs={'role': re.compile('main|navigation|banner|contentinfo|complementary|search')})
        aria_usage = len(landmarks)
        
        if aria_usage == 0:
            issues.append("⚠️ No ARIA landmarks found")
            recommendations.append("♿ Add ARIA landmarks (role='main', 'navigation', etc.) for better accessibility")
            score -= 15
            accessibility_issues.append('aria_landmarks')
        elif aria_usage < 3:
            recommendations.append("💡 Add more ARIA landmarks for better screen reader navigation")
            score -= 5
        
        # Check for language attribute
        html_tag = soup.find('html')
        if not html_tag or not html_tag.get('lang'):
            issues.append("⚠️ Missing language declaration")
            recommendations.append("🌐 Add lang attribute to <html> tag")
            score -= 10
            accessibility_issues.append('language')
        
        # Check for focus indicators (simplified check)
        style_tags = soup.find_all('style')
        has_focus_styles = False
        for style in style_tags:
            if ':focus' in style.get_text():
                has_focus_styles = True
                break
        
        if not has_focus_styles:
            recommendations.append("⌨️ Ensure visible focus indicators for keyboard navigation")
            score -= 5
        
        # Check for color contrast issues (simplified - would need actual color analysis)
        # This is a placeholder for more advanced color contrast checking
        recommendations.append("🎨 Verify color contrast meets WCAG AA standards (4.5:1 for text)")
        
        # Determine WCAG compliance level
        if len(accessibility_issues) == 0:
            wcag_level = "AAA"
        elif len(accessibility_issues) <= 2:
            wcag_level = "AA"
        elif len(accessibility_issues) <= 4:
            wcag_level = "A"
        else:
            wcag_level = "Non-compliant"
        
        return max(0, score), {
            'wcag_level': wcag_level,
            'has_skip_link': has_skip_link,
            'images_without_alt': len(images_without_alt),
            'aria_usage': aria_usage,
            'accessibility_issues': accessibility_issues
        }
    
    def _analyze_forms(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze form usability and accessibility"""
        forms = soup.find_all('form')
        
        if len(forms) == 0:
            return 100, {'accessibility_score': 100, 'form_count': 0}
        
        score = 100
        total_inputs = 0
        inputs_with_labels = 0
        
        for form in forms:
            inputs = form.find_all(['input', 'textarea', 'select'])
            total_inputs += len(inputs)
            
            for input_elem in inputs:
                input_id = input_elem.get('id')
                input_type = input_elem.get('type', 'text')
                
                # Skip hidden and submit inputs
                if input_type in ['hidden', 'submit', 'button']:
                    continue
                
                # Check for associated label
                if input_id:
                    label = form.find('label', attrs={'for': input_id})
                    if label:
                        inputs_with_labels += 1
                    else:
                        # Check if input is wrapped in label
                        parent_label = input_elem.find_parent('label')
                        if parent_label:
                            inputs_with_labels += 1
                
                # Check for placeholder (not a replacement for label)
                if not input_elem.get('placeholder') and input_type not in ['checkbox', 'radio']:
                    recommendations.append("💡 Add placeholder text to form inputs for better UX")
                    score = min(score, 90)
                
                # Check for required attribute
                if input_elem.get('required') and not input_elem.get('aria-required'):
                    recommendations.append("♿ Add aria-required='true' to required fields")
                    score = min(score, 85)
        
        # Calculate label coverage
        visible_inputs = total_inputs
        if visible_inputs > 0:
            label_coverage = inputs_with_labels / visible_inputs
            
            if label_coverage < 0.5:
                issues.append(f"❌ Critical: Most form inputs missing labels ({inputs_with_labels}/{visible_inputs})")
                recommendations.append("♿ Add <label> tags to all form inputs for accessibility")
                score = 40
            elif label_coverage < 1.0:
                issues.append(f"⚠️ Some form inputs missing labels ({inputs_with_labels}/{visible_inputs})")
                recommendations.append("📝 Ensure all form fields have associated labels")
                score = 70
        
        # Check for form validation
        has_validation = any(form.get('novalidate') is None for form in forms)
        if not has_validation:
            recommendations.append("✅ Implement client-side form validation for better UX")
        
        # Check for autocomplete
        inputs_with_autocomplete = soup.find_all(['input'], attrs={'autocomplete': True})
        if len(inputs_with_autocomplete) == 0 and total_inputs > 0:
            recommendations.append("⚡ Add autocomplete attributes to form fields for faster completion")
            score = min(score, 85)
        
        accessibility_score = score
        
        return score, {
            'accessibility_score': accessibility_score,
            'form_count': len(forms),
            'total_inputs': total_inputs,
            'inputs_with_labels': inputs_with_labels
        }
    
    def _analyze_interactive_elements(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze buttons, links, and other interactive elements"""
        score = 100
        
        # Find all interactive elements
        buttons = soup.find_all('button')
        links = soup.find_all('a', href=True)
        inputs = soup.find_all('input', type=['button', 'submit'])
        
        total_interactive = len(buttons) + len(links) + len(inputs)
        
        # Check buttons
        if len(buttons) < self.THRESHOLDS['button_count']['min']:
            issues.append("⚠️ Very few interactive buttons")
            recommendations.append("🔘 Add clear call-to-action buttons")
            score -= 15
        elif len(buttons) > self.THRESHOLDS['button_count']['max']:
            issues.append("⚠️ Too many buttons may overwhelm users")
            recommendations.append("🎯 Prioritize primary actions and reduce button clutter")
            score -= 10
        
        # Check for empty buttons
        empty_buttons = [btn for btn in buttons if not btn.get_text().strip() and not btn.get('aria-label')]
        if empty_buttons:
            issues.append(f"❌ {len(empty_buttons)} buttons without text or aria-label")
            recommendations.append("📝 Add descriptive text or aria-label to all buttons")
            score -= 15
        
        # Check links
        empty_links = [link for link in links if not link.get_text().strip() and not link.get('aria-label')]
        if empty_links:
            issues.append(f"⚠️ {len(empty_links)} links without text")
            recommendations.append("🔗 Add descriptive text to all links")
            score -= 10
        
        # Check for generic link text
        generic_texts = ['click here', 'read more', 'here', 'more', 'link']
        generic_links = [link for link in links if link.get_text().strip().lower() in generic_texts]
        if len(generic_links) > 3:
            issues.append(f"⚠️ {len(generic_links)} links with generic text")
            recommendations.append("📝 Use descriptive link text instead of 'click here' or 'read more'")
            score -= 10
        
        # Check for external links without indication
        external_links = [link for link in links if link.get('href', '').startswith('http')]
        external_with_indicator = [link for link in external_links if link.get('target') == '_blank']
        
        if len(external_with_indicator) > 0:
            # Check if they have aria-label or visual indicator
            external_without_warning = [link for link in external_with_indicator if not link.get('aria-label')]
            if len(external_without_warning) > 0:
                recommendations.append("🔗 Add aria-label to external links that open in new tab")
                score = min(score, 85)
        
        return score, {
            'total_interactive': total_interactive,
            'buttons': len(buttons),
            'links': len(links),
            'empty_buttons': len(empty_buttons),
            'empty_links': len(empty_links)
        }
    
    def _analyze_visual_design(self, soup: BeautifulSoup, issues: List, recommendations: List) -> tuple:
        """Analyze visual design elements"""
        score = 100
        
        # Check for consistent heading sizes (simplified)
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if len(headings) == 0:
            score -= 20
        
        # Check for whitespace (paragraph spacing)
        paragraphs = soup.find_all('p')
        if len(paragraphs) > 10:
            # Good content structure
            pass
        elif len(paragraphs) < 3:
            recommendations.append("📐 Use more paragraphs to improve content spacing")
            score -= 10
        
        # Check for favicon
        favicon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
        if not favicon:
            recommendations.append("🎨 Add a favicon for better brand recognition")
            score -= 5
        
        # Check for custom fonts
        font_links = soup.find_all('link', href=re.compile('fonts'))
        if len(font_links) == 0:
            recommendations.append("💡 Consider using custom fonts for better typography")
        
        return score, {
            'has_favicon': bool(favicon),
            'heading_count': len(headings),
            'paragraph_count': len(paragraphs)
        }
    
    def _calculate_accessibility_score(self, accessibility_data: Dict, mobile_data: Dict, forms_data: Dict) -> int:
        """Calculate overall accessibility score"""
        score = 100
        
        # Deduct for accessibility issues
        score -= len(accessibility_data.get('accessibility_issues', [])) * 10
        
        # Deduct for images without alt
        score -= min(20, accessibility_data.get('images_without_alt', 0) * 2)
        
        # Deduct if not mobile friendly
        if not mobile_data.get('is_mobile_friendly', False):
            score -= 15
        
        # Deduct for form accessibility
        form_score = forms_data.get('accessibility_score', 100)
        score = min(score, form_score)
        
        return max(0, round(score))
    
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
    
    def _calculate_ux_health(self, score_components: Dict) -> str:
        """Calculate overall UX health"""
        avg_score = sum(score_components.values()) / len(score_components)
        
        if avg_score >= 85:
            return "Excellent - User-friendly and accessible"
        elif avg_score >= 70:
            return "Good - Solid UX with minor improvements needed"
        elif avg_score >= 50:
            return "Fair - Several UX issues to address"
        else:
            return "Poor - Significant UX improvements required"
