import httpx
from bs4 import BeautifulSoup
from typing import Dict, List
from urllib.parse import urlparse, urljoin
import ssl
import socket
import re


class SecurityAnalyzer:
    """Analyze website security with comprehensive checks"""
    
    # Security best practices
    SECURITY_HEADERS = {
        'Strict-Transport-Security': {
            'weight': 20,
            'description': 'HSTS - Forces HTTPS connections',
            'recommendation': 'Add: Strict-Transport-Security: max-age=31536000; includeSubDomains'
        },
        'Content-Security-Policy': {
            'weight': 15,
            'description': 'CSP - Prevents XSS attacks',
            'recommendation': 'Add Content-Security-Policy header to prevent XSS'
        },
        'X-Frame-Options': {
            'weight': 15,
            'description': 'Prevents clickjacking attacks',
            'recommendation': 'Add: X-Frame-Options: DENY or SAMEORIGIN'
        },
        'X-Content-Type-Options': {
            'weight': 10,
            'description': 'Prevents MIME-sniffing',
            'recommendation': 'Add: X-Content-Type-Options: nosniff'
        },
        'Referrer-Policy': {
            'weight': 8,
            'description': 'Controls referrer information',
            'recommendation': 'Add: Referrer-Policy: strict-origin-when-cross-origin'
        },
        'Permissions-Policy': {
            'weight': 7,
            'description': 'Controls browser features',
            'recommendation': 'Add Permissions-Policy to control feature access'
        }
    }
    
    async def analyze(self, url: str) -> Dict:
        """Perform comprehensive security analysis"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                html = response.text
                headers = response.headers
                final_url = str(response.url)
            
            soup = BeautifulSoup(html, 'html.parser')
            parsed_url = urlparse(url)
            
            issues = []
            recommendations = []
            
            # Analyze all security components
            https_score, https_data = self._analyze_https(parsed_url, issues, recommendations)
            headers_score, headers_data = self._analyze_security_headers(headers, issues, recommendations)
            ssl_score, ssl_data = await self._analyze_ssl_tls(parsed_url.netloc, issues, recommendations)
            content_score, content_data = self._analyze_content_security(soup, url, issues, recommendations)
            cookies_score, cookies_data = self._analyze_cookies(headers, issues, recommendations)
            
            # Weighted scoring
            weights = {
                'https': 20,
                'headers': 30,
                'ssl_tls': 25,
                'content': 15,
                'cookies': 10
            }
            
            score_components = {
                'https': https_score,
                'headers': headers_score,
                'ssl_tls': ssl_score,
                'content': content_score,
                'cookies': cookies_score
            }
            
            final_score = sum(score_components[k] * (weights[k] / 100) for k in weights)
            
            # Calculate security grade
            grade = self._calculate_grade(final_score)
            
            # Security level
            security_level = self._calculate_security_level(final_score)
            
            return {
                "score": round(final_score, 1),
                "grade": grade,
                "security_level": security_level,
                "uses_https": https_data['uses_https'],
                "ssl_grade": ssl_data.get('grade', 'Unknown'),
                "ssl_valid": ssl_data.get('valid', False),
                "security_headers": headers_data['present'],
                "missing_headers": headers_data['missing'],
                "mixed_content": content_data['mixed_content_count'],
                "insecure_forms": content_data['insecure_forms'],
                "vulnerable_libraries": content_data['vulnerable_libraries'],
                "cookie_security": cookies_data['secure_cookies'],
                "score_breakdown": {k: round(v, 1) for k, v in score_components.items()},
                "issues": issues,
                "recommendations": recommendations,
                "security_summary": self._generate_summary(final_score, issues)
            }
            
        except Exception as e:
            return {
                "score": 0,
                "grade": "F",
                "security_level": "Unknown",
                "uses_https": False,
                "issues": [f"Failed to analyze security: {str(e)}"],
                "recommendations": ["Ensure website is accessible and try again"]
            }
    
    def _analyze_https(self, parsed_url, issues: List, recommendations: List) -> tuple:
        """Analyze HTTPS usage"""
        score = 100
        uses_https = parsed_url.scheme == 'https'
        
        if not uses_https:
            issues.append("Critical: Website not using HTTPS - Data transmitted insecurely")
            recommendations.append("Implement SSL/TLS certificate immediately for secure connections")
            score = 0
        
        return score, {'uses_https': uses_https}
    
    def _analyze_security_headers(self, headers: Dict, issues: List, recommendations: List) -> tuple:
        """Analyze security headers"""
        score = 100
        present_headers = []
        missing_headers = []
        
        for header, config in self.SECURITY_HEADERS.items():
            if header in headers or header.lower() in headers:
                present_headers.append(header)
                
                # Validate header values
                header_value = headers.get(header) or headers.get(header.lower(), '')
                
                if header == 'Strict-Transport-Security':
                    if 'max-age' not in header_value.lower():
                        issues.append("HSTS header present but missing max-age directive")
                        score -= 5
                
                elif header == 'X-Frame-Options':
                    if header_value.upper() not in ['DENY', 'SAMEORIGIN']:
                        issues.append(f"X-Frame-Options has weak value: {header_value}")
                        score -= 3
            else:
                missing_headers.append(header)
                issues.append(f"Missing {header} - {config['description']}")
                recommendations.append(config['recommendation'])
                score -= config['weight']
        
        return max(0, score), {
            'present': present_headers,
            'missing': missing_headers,
            'total_headers': len(self.SECURITY_HEADERS)
        }
    
    async def _analyze_ssl_tls(self, hostname: str, issues: List, recommendations: List) -> tuple:
        """Analyze SSL/TLS configuration"""
        score = 100
        ssl_data = {
            'valid': False,
            'grade': 'Unknown',
            'protocol': None,
            'cipher': None
        }
        
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    ssl_data['valid'] = True
                    ssl_data['protocol'] = ssock.version()
                    ssl_data['cipher'] = ssock.cipher()[0]
                    
                    # Check protocol version
                    if ssl_data['protocol'] in ['TLSv1.3', 'TLSv1.2']:
                        ssl_data['grade'] = 'A'
                    elif ssl_data['protocol'] == 'TLSv1.1':
                        ssl_data['grade'] = 'B'
                        issues.append("Using TLSv1.1 - Upgrade to TLS 1.2 or 1.3")
                        recommendations.append("Upgrade to TLS 1.2 or 1.3 for better security")
                        score = 80
                    else:
                        ssl_data['grade'] = 'C'
                        issues.append(f"Using outdated protocol: {ssl_data['protocol']}")
                        recommendations.append("Upgrade SSL/TLS to version 1.2 or higher")
                        score = 60
                    
                    # Check certificate expiry
                    import datetime
                    from datetime import datetime as dt
                    
                    not_after = cert.get('notAfter')
                    if not_after:
                        expiry_date = dt.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (expiry_date - dt.now()).days
                        
                        if days_until_expiry < 0:
                            issues.append("Critical: SSL certificate has expired!")
                            recommendations.append("Renew SSL certificate immediately")
                            score = 0
                        elif days_until_expiry < 30:
                            issues.append(f"SSL certificate expires in {days_until_expiry} days")
                            recommendations.append("Renew SSL certificate soon")
                            score = min(score, 70)
        
        except ssl.SSLError as e:
            issues.append(f"SSL Error: {str(e)}")
            recommendations.append("Fix SSL/TLS configuration issues")
            score = 30
        except Exception as e:
            # If HTTPS not available, score is 0
            if "443" in str(e):
                score = 0
        
        return score, ssl_data
    
    def _analyze_content_security(self, soup: BeautifulSoup, url: str, issues: List, recommendations: List) -> tuple:
        """Analyze content security issues"""
        score = 100
        
        # Check for mixed content
        mixed_content = []
        if url.startswith('https://'):
            for tag in soup.find_all(['img', 'script', 'link', 'iframe']):
                src = tag.get('src') or tag.get('href')
                if src and src.startswith('http://'):
                    mixed_content.append(src)
            
            if mixed_content:
                issues.append(f"Critical: {len(mixed_content)} insecure resources on HTTPS page (mixed content)")
                recommendations.append("Update all resources to use HTTPS URLs")
                score -= 30
        
        # Check for insecure forms
        insecure_forms = []
        for form in soup.find_all('form'):
            action = form.get('action', '')
            if action.startswith('http://') or (not action.startswith('https://') and url.startswith('https://')):
                insecure_forms.append(action or 'current page')
        
        if insecure_forms:
            issues.append(f"Critical: {len(insecure_forms)} forms submitting over HTTP")
            recommendations.append("Ensure all forms submit over HTTPS")
            score -= 25
        
        # Check for vulnerable JavaScript libraries
        vulnerable_libraries = []
        known_vulnerable = {
            'jquery-1.': 'jQuery < 3.0 has known vulnerabilities',
            'jquery-2.': 'jQuery < 3.0 has known vulnerabilities',
            'angular.js/1.0': 'AngularJS 1.0 has XSS vulnerabilities',
            'angular.js/1.1': 'AngularJS 1.1 has XSS vulnerabilities',
        }
        
        for script in soup.find_all('script', src=True):
            src = script.get('src', '').lower()
            for vuln_pattern, description in known_vulnerable.items():
                if vuln_pattern in src:
                    vulnerable_libraries.append(description)
        
        if vulnerable_libraries:
            issues.append(f"Found {len(vulnerable_libraries)} potentially vulnerable libraries")
            recommendations.append("Update JavaScript libraries to latest secure versions")
            score -= 15
        
        # Check for inline JavaScript (XSS risk)
        inline_scripts = soup.find_all('script', src=False)
        if len(inline_scripts) > 10:
            issues.append(f"High number of inline scripts ({len(inline_scripts)}) - XSS risk")
            recommendations.append("Move inline JavaScript to external files and implement CSP")
            score -= 10
        
        return max(0, score), {
            'mixed_content_count': len(mixed_content),
            'mixed_content_urls': mixed_content[:5],
            'insecure_forms': len(insecure_forms),
            'vulnerable_libraries': vulnerable_libraries,
            'inline_scripts': len(inline_scripts)
        }
    
    def _analyze_cookies(self, headers: Dict, issues: List, recommendations: List) -> tuple:
        """Analyze cookie security"""
        score = 100
        
        set_cookie_headers = []
        for key, value in headers.items():
            if key.lower() == 'set-cookie':
                set_cookie_headers.append(value)
        
        if not set_cookie_headers:
            return 100, {'secure_cookies': True, 'cookie_count': 0}
        
        insecure_cookies = 0
        missing_httponly = 0
        missing_samesite = 0
        
        for cookie in set_cookie_headers:
            cookie_lower = cookie.lower()
            
            if 'secure' not in cookie_lower:
                insecure_cookies += 1
            
            if 'httponly' not in cookie_lower:
                missing_httponly += 1
            
            if 'samesite' not in cookie_lower:
                missing_samesite += 1
        
        if insecure_cookies > 0:
            issues.append(f"{insecure_cookies} cookies without Secure flag")
            recommendations.append("Add Secure flag to all cookies")
            score -= 20
        
        if missing_httponly > 0:
            issues.append(f"{missing_httponly} cookies without HttpOnly flag")
            recommendations.append("Add HttpOnly flag to prevent XSS cookie theft")
            score -= 15
        
        if missing_samesite > 0:
            issues.append(f"{missing_samesite} cookies without SameSite attribute")
            recommendations.append("Add SameSite attribute to prevent CSRF attacks")
            score -= 10
        
        return max(0, score), {
            'secure_cookies': insecure_cookies == 0,
            'cookie_count': len(set_cookie_headers),
            'insecure_count': insecure_cookies
        }
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate security grade"""
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
    
    def _calculate_security_level(self, score: float) -> str:
        """Calculate security level description"""
        if score >= 90:
            return "Excellent - Strong security posture"
        elif score >= 80:
            return "Good - Minor security improvements needed"
        elif score >= 70:
            return "Fair - Several security issues to address"
        elif score >= 50:
            return "Poor - Significant security vulnerabilities"
        else:
            return "Critical - Immediate security action required"
    
    def _generate_summary(self, score: float, issues: List) -> str:
        """Generate security summary"""
        critical_issues = [i for i in issues if 'Critical' in i or 'critical' in i]
        
        if score >= 90:
            return "Website has strong security measures in place with minimal vulnerabilities."
        elif score >= 70:
            return f"Website has basic security but needs improvements. {len(issues)} issues found."
        elif critical_issues:
            return f"Website has {len(critical_issues)} critical security issues requiring immediate attention."
        else:
            return f"Website has significant security vulnerabilities. {len(issues)} issues identified."
