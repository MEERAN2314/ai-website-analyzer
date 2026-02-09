from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from typing import Dict
import os


class PDFService:
    """Service for generating PDF reports"""
    
    def __init__(self):
        self.output_dir = "app/static/pdfs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_report(self, analysis_data: Dict) -> str:
        """
        Generate PDF report from analysis data
        
        Args:
            analysis_data: Complete analysis data
            
        Returns:
            Path to generated PDF file
        """
        try:
            # Generate PDF filename
            filename = f"analysis_{analysis_data['id']}.pdf"
            output_path = os.path.join(self.output_dir, filename)
            
            print(f"📄 Creating PDF at: {output_path}")
            
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=30
            )
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Define styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2563EB'),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#2563EB'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )
            
            subheading_style = ParagraphStyle(
                'CustomSubHeading',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.HexColor('#374151'),
                spaceAfter=8,
                spaceBefore=8,
                fontName='Helvetica-Bold'
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                alignment=TA_LEFT
            )
            
            # Title
            elements.append(Paragraph("Website Analysis Report", title_style))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(analysis_data.get('website_url', ''), styles['Normal']))
            elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            # Overall Score Box
            score_data = [
                ['Overall Score', 'UX', 'SEO', 'Performance', 'Content'],
                [
                    f"{analysis_data.get('overall_score', 0):.0f}/100",
                    f"{analysis_data.get('ux_analysis', {}).get('score', 0):.0f}/100",
                    f"{analysis_data.get('seo_analysis', {}).get('score', 0):.0f}/100",
                    f"{analysis_data.get('performance_analysis', {}).get('score', 0):.0f}/100",
                    f"{analysis_data.get('content_analysis', {}).get('score', 0):.0f}/100"
                ]
            ]
            
            score_table = Table(score_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1.2*inch, 1*inch])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F3F4F6')),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
                ('TOPPADDING', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.white)
            ]))
            
            elements.append(score_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # AI Summary
            elements.append(Paragraph("Executive Summary", heading_style))
            summary_text = analysis_data.get('ai_summary', 'No summary available')
            
            # Clean markdown formatting for PDF - remove markdown syntax
            summary_text = summary_text.replace('**', '').replace('##', '').replace('###', '').replace('*', '')
            
            # Split into paragraphs
            paragraphs = summary_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    elements.append(Paragraph(para.strip(), normal_style))
                    elements.append(Spacer(1, 0.1*inch))
            
            elements.append(Spacer(1, 0.2*inch))
            
            # Priority Recommendations
            elements.append(Paragraph("Priority Recommendations", heading_style))
            recommendations = analysis_data.get('priority_recommendations', [])
            
            if recommendations:
                for i, rec in enumerate(recommendations[:5], 1):  # Limit to top 5
                    rec_title = rec.get('title', 'Recommendation')
                    rec_desc = rec.get('description', '')
                    rec_priority = rec.get('priority', 'N/A')
                    rec_impact = rec.get('impact', 'N/A')
                    rec_effort = rec.get('effort', 'N/A')
                    
                    elements.append(Paragraph(f"<b>{i}. {rec_title}</b>", subheading_style))
                    elements.append(Paragraph(rec_desc, normal_style))
                    elements.append(Paragraph(
                        f"<i>Priority: {rec_priority} | Impact: {rec_impact} | Effort: {rec_effort}</i>",
                        styles['Normal']
                    ))
                    elements.append(Spacer(1, 0.15*inch))
            else:
                elements.append(Paragraph("No recommendations available", normal_style))
            
            elements.append(PageBreak())
            
            # Detailed Analysis Sections
            sections = [
                ('UX Analysis', 'ux_analysis'),
                ('SEO Analysis', 'seo_analysis'),
                ('Performance Analysis', 'performance_analysis'),
                ('Content Analysis', 'content_analysis')
            ]
            
            for section_title, section_key in sections:
                section_data = analysis_data.get(section_key, {})
                score = section_data.get('score', 0)
                
                elements.append(Paragraph(section_title, heading_style))
                elements.append(Paragraph(f"<b>Score: {score:.0f}/100</b>", subheading_style))
                
                # Issues
                elements.append(Paragraph("<b>Issues Found:</b>", subheading_style))
                issues = section_data.get('issues', [])
                if issues:
                    for issue in issues[:10]:  # Limit to 10 issues
                        elements.append(Paragraph(f"• {issue}", normal_style))
                else:
                    elements.append(Paragraph("No issues found", normal_style))
                
                elements.append(Spacer(1, 0.1*inch))
                
                # Recommendations
                elements.append(Paragraph("<b>Recommendations:</b>", subheading_style))
                recs = section_data.get('recommendations', [])
                if recs:
                    for rec in recs[:10]:  # Limit to 10 recommendations
                        elements.append(Paragraph(f"• {rec}", normal_style))
                else:
                    elements.append(Paragraph("No recommendations", normal_style))
                
                elements.append(Spacer(1, 0.25*inch))
            
            # Footer
            elements.append(Spacer(1, 0.5*inch))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            elements.append(Paragraph(
                "Generated by AI Website Analyzer | © 2026 WebAnalyzer AI",
                footer_style
            ))
            
            # Build PDF
            print(f"📄 Building PDF document...")
            doc.build(elements)
            print(f"✅ PDF created successfully: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"❌ PDF generation failed: {e}")
            import traceback
            traceback.print_exc()
            raise
