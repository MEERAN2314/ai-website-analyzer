from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import Dict, List
import os
import re
import html


class ComparisonPDFService:
    """Service for generating professional competitor comparison PDF reports"""
    
    def __init__(self):
        self.output_dir = "app/static/pdfs"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Professional color palette
        self.colors = {
            'primary': colors.HexColor('#1E40AF'),
            'primary_light': colors.HexColor('#3B82F6'),
            'secondary': colors.HexColor('#0F172A'),
            'gold': colors.HexColor('#FFD700'),
            'silver': colors.HexColor('#94A3B8'),  # Lighter silver-blue
            'bronze': colors.HexColor('#CD7F32'),
            'success': colors.HexColor('#059669'),
            'warning': colors.HexColor('#D97706'),
            'danger': colors.HexColor('#DC2626'),
            'gray_dark': colors.HexColor('#374151'),
            'gray_medium': colors.HexColor('#6B7280'),
            'gray_light': colors.HexColor('#F3F4F6'),
            'white': colors.white,
            'bg_blue': colors.HexColor('#EFF6FF'),
            'bg_green': colors.HexColor('#ECFDF5'),
            'bg_yellow': colors.HexColor('#FFFBEB'),
            'bg_red': colors.HexColor('#FEF2F2'),
            'bg_purple': colors.HexColor('#F5F3FF'),
            'bg_silver': colors.HexColor('#F1F5F9'),  # Light silver background
            'bg_bronze': colors.HexColor('#FEF3E2'),  # Light bronze background
        }
    
    def _add_page_number(self, canvas, doc):
        """Add page numbers and footer"""
        canvas.saveState()
        
        # Footer line
        canvas.setStrokeColor(self.colors['gray_light'])
        canvas.setLineWidth(1)
        canvas.line(50, 50, A4[0] - 50, 50)
        
        # Page number
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(self.colors['gray_medium'])
        canvas.drawRightString(A4[0] - 50, 35, text)
        
        # Footer text
        canvas.setFillColor(self.colors['gray_medium'])
        canvas.drawString(50, 35, "Competitor Analysis Report")
        
        # Website
        canvas.setFillColor(self.colors['primary'])
        canvas.drawRightString(A4[0] - 50, 20, "WebAnalyzer AI")
        
        canvas.restoreState()
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text for PDF"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"
            "\U0001FA00-\U0001FA6F"
            "\U00002600-\U000026FF"
            "\U00002700-\U000027BF"
            "]+",
            flags=re.UNICODE
        )
        text = emoji_pattern.sub('', text)
        
        # Escape special characters
        text = html.escape(text, quote=False)
        
        return text.strip()
    
    async def generate_comparison_report(self, comparison_data: Dict) -> str:
        """Generate comprehensive comparison PDF report"""
        try:
            comparison_id = comparison_data['_id']
            filename = f"comparison_{comparison_id}.pdf"
            output_path = os.path.join(self.output_dir, filename)
            
            print(f"📄 Creating comparison PDF at: {output_path}")
            
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=60,
                bottomMargin=70
            )
            
            elements = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=36,
                textColor=self.colors['white'],
                spaceAfter=10,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                leading=42
            )
            
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=self.colors['white'],
                alignment=TA_CENTER,
                spaceAfter=5,
                fontName='Helvetica'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=22,
                textColor=self.colors['primary'],
                spaceAfter=15,
                spaceBefore=20,
                fontName='Helvetica-Bold'
            )
            
            subheading_style = ParagraphStyle(
                'CustomSubHeading',
                parent=styles['Heading3'],
                fontSize=16,
                textColor=self.colors['secondary'],
                spaceAfter=10,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                leading=16,
                alignment=TA_LEFT,
                textColor=self.colors['gray_dark'],
                fontName='Helvetica'
            )
            
            # ===== COVER PAGE =====
            elements.append(Spacer(1, 1.5*inch))
            
            # Title with gradient background effect
            cover_title = [[Paragraph("COMPETITIVE ANALYSIS", title_style)]]
            cover_table = Table(cover_title, colWidths=[A4[0] - 100])
            cover_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.colors['primary']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 40),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 40),
                ('ROUNDEDCORNERS', [15, 15, 15, 15])
            ]))
            elements.append(cover_table)
            elements.append(Spacer(1, 0.5*inch))
            
            # Your website info
            your_url = comparison_data['your_website']['url']
            competitor_count = len(comparison_data['competitors'])
            
            info_data = [
                [Paragraph(f"<b>Your Website:</b>", normal_style)],
                [Paragraph(f'<font size="14" color="#1E40AF"><b>{your_url}</b></font>', 
                          ParagraphStyle('', alignment=TA_CENTER, fontSize=14))],
                [Spacer(1, 0.2*inch)],
                [Paragraph(f"<b>Compared Against:</b> {competitor_count} Competitor{'s' if competitor_count > 1 else ''}", 
                          normal_style)],
                [Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                          normal_style)]
            ]
            
            info_table = Table(info_data, colWidths=[A4[0] - 100])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.colors['bg_blue']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ('ROUNDEDCORNERS', [10, 10, 10, 10])
            ]))
            elements.append(info_table)
            
            elements.append(Spacer(1, 1*inch))
            
            # Your Rank Badge
            rankings = comparison_data.get('rankings', {})
            overall_rankings = rankings.get('overall', [])
            your_rank_data = next((r for r in overall_rankings if r.get('is_yours')), None)
            
            if your_rank_data:
                rank = your_rank_data['rank']
                score = your_rank_data['score']
                
                # Rank color based on position with distinct colors
                if rank == 1:
                    rank_color = self.colors['gold']
                    rank_bg = colors.HexColor('#FFF9E6')
                    medal = '1st Place'
                elif rank == 2:
                    rank_color = colors.HexColor('#64748B')  # Slate blue for silver
                    rank_bg = self.colors['bg_silver']
                    medal = '2nd Place'
                elif rank == 3:
                    rank_color = colors.HexColor('#D97706')  # Amber for bronze
                    rank_bg = self.colors['bg_bronze']
                    medal = '3rd Place'
                else:
                    rank_color = self.colors['gray_medium']
                    rank_bg = self.colors['gray_light']
                    medal = f'{rank}th Place'
                
                rank_data = [
                    [Paragraph(f'<font size="16"><b>Your Competitive Position</b></font>', 
                              ParagraphStyle('', alignment=TA_CENTER, textColor=self.colors['gray_dark']))],
                    [Paragraph(f'<font size="60" color="{rank_color}"><b>#{rank}</b></font>', 
                              ParagraphStyle('', alignment=TA_CENTER))],
                    [Paragraph(f'<font size="18" color="{rank_color}"><b>{medal}</b></font>', 
                              ParagraphStyle('', alignment=TA_CENTER))],
                    [Paragraph(f'<font size="14">Overall Score: <b>{score:.1f}/100</b></font>', 
                              ParagraphStyle('', alignment=TA_CENTER, textColor=self.colors['gray_dark']))]
                ]
                
                rank_table = Table(rank_data, colWidths=[3*inch])
                rank_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), rank_bg),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOX', (0, 0), (-1, -1), 3, rank_color),
                    ('ROUNDEDCORNERS', [15, 15, 15, 15]),
                    ('TOPPADDING', (0, 0), (-1, -1), 20),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 20)
                ]))
                
                # Center the rank badge
                rank_wrapper = Table([[rank_table]], colWidths=[A4[0] - 100])
                rank_wrapper.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))
                elements.append(rank_wrapper)
            
            elements.append(PageBreak())
            
            # ===== EXECUTIVE SUMMARY =====
            elements.append(Paragraph("Executive Summary", heading_style))
            elements.append(HRFlowable(width="100%", thickness=3, color=self.colors['primary'], 
                                      spaceBefore=5, spaceAfter=15))
            
            insights = comparison_data.get('insights', {})
            summary_data = insights.get('summary', {})
            
            summary_text = f"""
This competitive analysis compares your website against {competitor_count} competitor{'s' if competitor_count > 1 else ''} 
across 6 key performance categories: UX, SEO, Performance, Content, Security, and Image Optimization.
            """
            
            elements.append(Paragraph(self._sanitize_text(summary_text), normal_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Key metrics boxes
            metrics_data = [
                [
                    Paragraph(f'<font size="32" color="#1E40AF"><b>{summary_data.get("leading_in", 0)}</b></font><br/>'
                             f'<font size="10">Categories<br/>Leading</font>', 
                             ParagraphStyle('', alignment=TA_CENTER)),
                    Paragraph(f'<font size="32" color="#DC2626"><b>{summary_data.get("behind_in", 0)}</b></font><br/>'
                             f'<font size="10">Categories<br/>Behind</font>', 
                             ParagraphStyle('', alignment=TA_CENTER)),
                    Paragraph(f'<font size="32" color="#059669"><b>{summary_data.get("quick_wins", 0)}</b></font><br/>'
                             f'<font size="10">Quick Win<br/>Opportunities</font>', 
                             ParagraphStyle('', alignment=TA_CENTER))
                ]
            ]
            
            metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch, 2*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), self.colors['bg_blue']),
                ('BACKGROUND', (1, 0), (1, 0), self.colors['bg_red']),
                ('BACKGROUND', (2, 0), (2, 0), self.colors['bg_green']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 20),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
                ('BOX', (0, 0), (-1, -1), 1.5, self.colors['gray_light']),
                ('INNERGRID', (0, 0), (-1, -1), 1.5, self.colors['white']),
                ('ROUNDEDCORNERS', [10, 10, 10, 10])
            ]))
            elements.append(metrics_table)
            
            elements.append(Spacer(1, 0.4*inch))
            
            # ===== OVERALL SCORE COMPARISON =====
            elements.append(Paragraph("Overall Score Comparison", heading_style))
            elements.append(HRFlowable(width="100%", thickness=3, color=self.colors['primary'], 
                                      spaceBefore=5, spaceAfter=15))
            
            # Create visual score bars
            score_rows = []
            for i, ranking in enumerate(overall_rankings):
                url = ranking['url']
                score = ranking['score']
                rank = ranking['rank']
                is_yours = ranking.get('is_yours', False)
                
                # Medal and rank with distinct colors
                if rank == 1:
                    medal = '1st'
                    medal_color = self.colors['gold']
                elif rank == 2:
                    medal = '2nd'
                    medal_color = colors.HexColor('#64748B')  # Slate blue for silver
                elif rank == 3:
                    medal = '3rd'
                    medal_color = colors.HexColor('#D97706')  # Amber for bronze
                else:
                    medal = f'{rank}th'
                    medal_color = self.colors['gray_medium']
                
                # URL display
                display_url = url if not is_yours else f"YOUR SITE: {url}"
                url_style = ParagraphStyle('', fontSize=10, textColor=self.colors['primary'] if is_yours else self.colors['gray_dark'])
                
                # Score bar
                bar_width = score / 100 * 4  # 4 inches max
                bar_color = self.colors['primary'] if is_yours else self.colors['gray_medium']
                
                score_rows.append([
                    Paragraph(f'<font color="{medal_color}"><b>{medal}</b></font>', 
                             ParagraphStyle('', fontSize=12, alignment=TA_CENTER)),
                    Paragraph(display_url, url_style),
                    Paragraph(f'<b>{score:.1f}</b>', 
                             ParagraphStyle('', fontSize=14, alignment=TA_RIGHT, 
                                          textColor=self.colors['primary'] if is_yours else self.colors['gray_dark']))
                ])
            
            score_table = Table(score_rows, colWidths=[0.6*inch, 3.5*inch, 0.8*inch])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), self.colors['white']),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('LINEBELOW', (0, 0), (-1, -2), 1, self.colors['gray_light']),
                ('BOX', (0, 0), (-1, -1), 1.5, self.colors['gray_light']),
                ('ROUNDEDCORNERS', [8, 8, 8, 8])
            ]))
            elements.append(score_table)
            
            elements.append(PageBreak())
            
            # ===== CATEGORY COMPARISON TABLE =====
            elements.append(Paragraph("Category-by-Category Comparison", heading_style))
            elements.append(HRFlowable(width="100%", thickness=3, color=self.colors['primary'], 
                                      spaceBefore=5, spaceAfter=15))
            
            # Build comparison table
            categories = ['ux', 'seo', 'performance', 'content', 'security', 'images']
            category_names = {
                'ux': 'UX',
                'seo': 'SEO',
                'performance': 'Performance',
                'content': 'Content',
                'security': 'Security',
                'images': 'Images'
            }
            
            # Header row
            header_row = [Paragraph('<b>Category</b>', ParagraphStyle('', fontSize=11, textColor=self.colors['white']))]
            header_row.append(Paragraph('<b>You</b>', ParagraphStyle('', fontSize=11, alignment=TA_CENTER, textColor=self.colors['white'])))
            for i in range(competitor_count):
                header_row.append(Paragraph(f'<b>Comp {i+1}</b>', 
                                           ParagraphStyle('', fontSize=11, alignment=TA_CENTER, textColor=self.colors['white'])))
            
            table_data = [header_row]
            
            # Data rows
            for category in categories:
                category_rankings = rankings.get(category, [])
                row = [Paragraph(f'<b>{category_names[category]}</b>', 
                                ParagraphStyle('', fontSize=11, textColor=self.colors['gray_dark']))]
                
                # Get all URLs in correct order (your site first, then competitors)
                all_urls = [comparison_data['your_website']['url']] + [c['url'] for c in comparison_data['competitors']]
                
                # Add scores in the correct order
                for url in all_urls:
                    # Find the ranking for this URL
                    ranking = next((r for r in category_rankings if r['url'] == url), None)
                    
                    if ranking:
                        score = ranking['score']
                        rank = ranking['rank']
                        is_yours = ranking.get('is_yours', False)
                        
                        # Medal with distinct colors
                        if rank == 1:
                            medal = '1st'
                            color = self.colors['gold']
                        elif rank == 2:
                            medal = '2nd'
                            color = colors.HexColor('#64748B')  # Slate blue for silver
                        elif rank == 3:
                            medal = '3rd'
                            color = colors.HexColor('#D97706')  # Amber for bronze
                        else:
                            medal = ''
                            color = self.colors['gray_dark']
                        
                        score_text = f'<font color="{color}"><b>{score:.1f}</b></font>'
                        if medal:
                            score_text += f'<br/><font size="8" color="{color}">{medal}</font>'
                        
                        row.append(Paragraph(score_text, ParagraphStyle('', alignment=TA_CENTER, fontSize=12)))
                    else:
                        # No data for this URL
                        row.append(Paragraph('N/A', ParagraphStyle('', alignment=TA_CENTER, fontSize=12)))
                
                table_data.append(row)
            
            col_widths = [1.2*inch] + [0.9*inch] * (competitor_count + 1)
            comparison_table = Table(table_data, colWidths=col_widths)
            comparison_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
                ('BACKGROUND', (0, 1), (-1, -1), self.colors['white']),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LINEBELOW', (0, 1), (-1, -2), 0.5, self.colors['gray_light']),
                ('BOX', (0, 0), (-1, -1), 1.5, self.colors['gray_light']),
                ('ROUNDEDCORNERS', [8, 8, 8, 8])
            ]))
            elements.append(comparison_table)
            
            elements.append(PageBreak())
            
            # ===== STRENGTHS & WEAKNESSES =====
            elements.append(Paragraph("Competitive Analysis", heading_style))
            elements.append(HRFlowable(width="100%", thickness=3, color=self.colors['primary'], 
                                      spaceBefore=5, spaceAfter=15))
            
            # Strengths
            strengths = insights.get('strengths', [])
            if strengths:
                elements.append(Paragraph("Your Competitive Strengths", subheading_style))
                
                for strength in strengths[:5]:
                    strength_data = [[
                        Paragraph(f'<b>{strength["category"]}</b>', 
                                 ParagraphStyle('', fontSize=13, textColor=self.colors['success'])),
                        Paragraph(f'{strength["message"]}', 
                                 ParagraphStyle('', fontSize=11, textColor=self.colors['gray_dark']))
                    ]]
                    
                    strength_table = Table(strength_data, colWidths=[1.5*inch, 4*inch])
                    strength_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), self.colors['bg_green']),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('TOPPADDING', (0, 0), (-1, -1), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                        ('LEFTPADDING', (0, 0), (-1, -1), 15),
                        ('LINEABOVE', (0, 0), (-1, 0), 3, self.colors['success']),
                        ('ROUNDEDCORNERS', [8, 8, 8, 8])
                    ]))
                    elements.append(strength_table)
                    elements.append(Spacer(1, 0.15*inch))
            
            # Weaknesses
            weaknesses = insights.get('weaknesses', [])
            if weaknesses:
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph("Areas for Improvement", subheading_style))
                
                for weakness in weaknesses[:5]:
                    weakness_data = [[
                        Paragraph(f'<b>{weakness["category"]}</b>', 
                                 ParagraphStyle('', fontSize=13, textColor=self.colors['danger'])),
                        Paragraph(f'{weakness["message"]}', 
                                 ParagraphStyle('', fontSize=11, textColor=self.colors['gray_dark']))
                    ]]
                    
                    weakness_table = Table(weakness_data, colWidths=[1.5*inch, 4*inch])
                    weakness_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), self.colors['bg_red']),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('TOPPADDING', (0, 0), (-1, -1), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                        ('LEFTPADDING', (0, 0), (-1, -1), 15),
                        ('LINEABOVE', (0, 0), (-1, 0), 3, self.colors['danger']),
                        ('ROUNDEDCORNERS', [8, 8, 8, 8])
                    ]))
                    elements.append(weakness_table)
                    elements.append(Spacer(1, 0.15*inch))
            
            # Opportunities
            opportunities = insights.get('opportunities', [])
            if opportunities:
                elements.append(PageBreak())
                elements.append(Paragraph("Quick Win Opportunities", subheading_style))
                elements.append(Paragraph("These are areas where you're close to competitors and can quickly improve:", 
                                        normal_style))
                elements.append(Spacer(1, 0.15*inch))
                
                for opp in opportunities[:5]:
                    opp_data = [[
                        Paragraph(f'<b>{opp["category"]}</b>', 
                                 ParagraphStyle('', fontSize=13, textColor=self.colors['warning'])),
                        Paragraph(f'{opp["message"]}', 
                                 ParagraphStyle('', fontSize=11, textColor=self.colors['gray_dark']))
                    ]]
                    
                    opp_table = Table(opp_data, colWidths=[1.5*inch, 4*inch])
                    opp_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), self.colors['bg_yellow']),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('TOPPADDING', (0, 0), (-1, -1), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                        ('LEFTPADDING', (0, 0), (-1, -1), 15),
                        ('LINEABOVE', (0, 0), (-1, 0), 3, self.colors['warning']),
                        ('ROUNDEDCORNERS', [8, 8, 8, 8])
                    ]))
                    elements.append(opp_table)
                    elements.append(Spacer(1, 0.15*inch))
            
            # AI Insights
            ai_summary = comparison_data.get('ai_summary', '')
            if ai_summary:
                elements.append(PageBreak())
                elements.append(Paragraph("AI Strategic Insights", heading_style))
                elements.append(HRFlowable(width="100%", thickness=3, color=self.colors['primary'], 
                                          spaceBefore=5, spaceAfter=15))
                
                # Clean and format AI summary
                ai_text = self._sanitize_text(ai_summary)
                paragraphs = ai_text.split('\n\n')
                
                for para in paragraphs:
                    if para.strip():
                        elements.append(Paragraph(para.strip(), normal_style))
                        elements.append(Spacer(1, 0.12*inch))
            
            # Build PDF
            print(f"📄 Building comparison PDF...")
            doc.build(elements, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
            print(f"✅ Comparison PDF created: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"❌ Comparison PDF generation failed: {e}")
            import traceback
            traceback.print_exc()
            raise
