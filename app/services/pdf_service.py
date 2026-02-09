from weasyprint import HTML, CSS
from jinja2 import Template
from datetime import datetime
from typing import Dict
import os


class PDFService:
    """Service for generating PDF reports"""
    
    def __init__(self):
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_report(self, analysis_data: Dict) -> str:
        """
        Generate PDF report from analysis data
        
        Args:
            analysis_data: Complete analysis data
            
        Returns:
            Path to generated PDF file
        """
        # Create HTML content
        html_content = self._create_html_report(analysis_data)
        
        # Generate PDF
        filename = f"analysis_{analysis_data['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[CSS(string=self._get_pdf_styles())]
        )
        
        return output_path
    
    def _create_html_report(self, data: Dict) -> str:
        """Create HTML content for PDF report"""
        
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Website Analysis Report</title>
        </head>
        <body>
            <div class="header">
                <h1>Website Analysis Report</h1>
                <p class="subtitle">{{ website_url }}</p>
                <p class="date">Generated on {{ date }}</p>
            </div>
            
            <div class="summary-box">
                <h2>Overall Score</h2>
                <div class="score-circle">{{ overall_score }}</div>
            </div>
            
            <div class="scores-grid">
                <div class="score-card">
                    <h3>UX Score</h3>
                    <div class="score">{{ ux_score }}</div>
                </div>
                <div class="score-card">
                    <h3>SEO Score</h3>
                    <div class="score">{{ seo_score }}</div>
                </div>
                <div class="score-card">
                    <h3>Performance</h3>
                    <div class="score">{{ perf_score }}</div>
                </div>
                <div class="score-card">
                    <h3>Content</h3>
                    <div class="score">{{ content_score }}</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <p>{{ ai_summary }}</p>
            </div>
            
            <div class="section">
                <h2>Priority Recommendations</h2>
                {% for rec in recommendations %}
                <div class="recommendation">
                    <h3>{{ rec.title }}</h3>
                    <p><strong>Priority:</strong> {{ rec.priority }} | 
                       <strong>Impact:</strong> {{ rec.impact }} | 
                       <strong>Effort:</strong> {{ rec.effort }}</p>
                    <p>{{ rec.description }}</p>
                </div>
                {% endfor %}
            </div>
            
            <div class="section">
                <h2>UX Analysis</h2>
                <h3>Issues</h3>
                <ul>
                    {% for issue in ux_issues %}
                    <li>{{ issue }}</li>
                    {% endfor %}
                </ul>
                <h3>Recommendations</h3>
                <ul>
                    {% for rec in ux_recommendations %}
                    <li>{{ rec }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="section">
                <h2>SEO Analysis</h2>
                <h3>Issues</h3>
                <ul>
                    {% for issue in seo_issues %}
                    <li>{{ issue }}</li>
                    {% endfor %}
                </ul>
                <h3>Recommendations</h3>
                <ul>
                    {% for rec in seo_recommendations %}
                    <li>{{ rec }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="section">
                <h2>Performance Analysis</h2>
                <h3>Issues</h3>
                <ul>
                    {% for issue in perf_issues %}
                    <li>{{ issue }}</li>
                    {% endfor %}
                </ul>
                <h3>Recommendations</h3>
                <ul>
                    {% for rec in perf_recommendations %}
                    <li>{{ rec }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="section">
                <h2>Content Analysis</h2>
                <h3>Issues</h3>
                <ul>
                    {% for issue in content_issues %}
                    <li>{{ issue }}</li>
                    {% endfor %}
                </ul>
                <h3>Recommendations</h3>
                <ul>
                    {% for rec in content_recommendations %}
                    <li>{{ rec }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="footer">
                <p>Generated by AI Website Analyzer</p>
                <p>© 2026 WebAnalyzer AI. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_str)
        
        return template.render(
            website_url=data.get('website_url', ''),
            date=datetime.now().strftime('%B %d, %Y'),
            overall_score=f"{data.get('overall_score', 0):.0f}",
            ux_score=f"{data.get('ux_analysis', {}).get('score', 0):.0f}",
            seo_score=f"{data.get('seo_analysis', {}).get('score', 0):.0f}",
            perf_score=f"{data.get('performance_analysis', {}).get('score', 0):.0f}",
            content_score=f"{data.get('content_analysis', {}).get('score', 0):.0f}",
            ai_summary=data.get('ai_summary', ''),
            recommendations=data.get('priority_recommendations', []),
            ux_issues=data.get('ux_analysis', {}).get('issues', []),
            ux_recommendations=data.get('ux_analysis', {}).get('recommendations', []),
            seo_issues=data.get('seo_analysis', {}).get('issues', []),
            seo_recommendations=data.get('seo_analysis', {}).get('recommendations', []),
            perf_issues=data.get('performance_analysis', {}).get('issues', []),
            perf_recommendations=data.get('performance_analysis', {}).get('recommendations', []),
            content_issues=data.get('content_analysis', {}).get('issues', []),
            content_recommendations=data.get('content_analysis', {}).get('recommendations', [])
        )
    
    def _get_pdf_styles(self) -> str:
        """Get CSS styles for PDF"""
        return """
        @page {
            size: A4;
            margin: 2cm;
        }
        
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            color: #333;
            line-height: 1.6;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #2563EB;
        }
        
        .header h1 {
            color: #2563EB;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .subtitle {
            font-size: 18px;
            color: #666;
            margin: 5px 0;
        }
        
        .date {
            font-size: 14px;
            color: #999;
        }
        
        .summary-box {
            background: linear-gradient(135deg, #2563EB, #3B82F6);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin: 30px 0;
        }
        
        .score-circle {
            font-size: 72px;
            font-weight: bold;
            margin: 20px 0;
        }
        
        .scores-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 30px 0;
        }
        
        .score-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 2px solid #e5e7eb;
        }
        
        .score-card h3 {
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }
        
        .score-card .score {
            font-size: 36px;
            font-weight: bold;
            color: #2563EB;
        }
        
        .section {
            margin: 30px 0;
            page-break-inside: avoid;
        }
        
        .section h2 {
            color: #2563EB;
            font-size: 24px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }
        
        .section h3 {
            color: #333;
            font-size: 18px;
            margin: 15px 0 10px 0;
        }
        
        .recommendation {
            background: #f8f9fa;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #2563EB;
            border-radius: 4px;
        }
        
        .recommendation h3 {
            color: #2563EB;
            margin-top: 0;
        }
        
        ul {
            margin: 10px 0;
            padding-left: 25px;
        }
        
        li {
            margin: 8px 0;
        }
        
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            color: #999;
            font-size: 12px;
        }
        """
