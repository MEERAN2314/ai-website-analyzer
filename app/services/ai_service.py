import google.generativeai as genai
from typing import List, Dict
import time
import asyncio
from app.core.config import settings

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)


class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.max_retries = 3
        self.base_delay = 2
    
    async def _generate_with_retry(self, prompt: str) -> str:
        """Generate content with retry logic for rate limits"""
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a quota/rate limit error
                if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                    if attempt < self.max_retries - 1:
                        # Exponential backoff
                        delay = self.base_delay * (2 ** attempt)
                        print(f"⏳ Rate limit hit, retrying in {delay} seconds... (attempt {attempt + 1}/{self.max_retries})")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        print(f"❌ Max retries reached. Using fallback response.")
                        return self._get_fallback_response()
                else:
                    # For other errors, raise immediately
                    raise
        
        return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Provide a fallback response when AI is unavailable"""
        return """
## Analysis Overview
The website analysis has been completed successfully. Due to high API usage, detailed AI insights are temporarily unavailable. However, all technical metrics have been analyzed and are available in the detailed sections.

## What You Can Do Now
- **Review Detailed Sections:** Check the UX, SEO, Performance, Content, Security, and Images tabs for specific findings
- **Priority Recommendations:** Focus on the high-priority items listed above for maximum impact
- **Action Plan:** Download the PDF report for a comprehensive overview
- **Try Again:** AI chat will be available again shortly - please try your question in a moment

## Quick Tips
- Start with high-priority, low-effort improvements for quick wins
- Address security issues immediately to protect your users
- Optimize images and performance for better user experience
- Improve SEO metadata for better search visibility

Please review the detailed analysis sections for specific recommendations tailored to your website.
"""
    
    def _get_chat_fallback_response(self, analysis: Dict, user_message: str) -> str:
        """Provide a contextual fallback response for chat when AI is unavailable"""
        overall_score = analysis.get('overall_score', 0)
        
        # Get scores
        ux_score = analysis.get('ux_analysis', {}).get('score', 0)
        seo_score = analysis.get('seo_analysis', {}).get('score', 0)
        perf_score = analysis.get('performance_analysis', {}).get('score', 0)
        content_score = analysis.get('content_analysis', {}).get('score', 0)
        security_score = analysis.get('security_analysis', {}).get('score', 0)
        image_score = analysis.get('image_analysis', {}).get('score', 0)
        
        # Find lowest scoring category
        scores = {
            'UX': ux_score,
            'SEO': seo_score,
            'Performance': perf_score,
            'Content': content_score,
            'Security': security_score,
            'Images': image_score
        }
        lowest_category = min(scores, key=scores.get)
        lowest_score = scores[lowest_category]
        
        return f"""I apologize for the delay in my response. I'm experiencing high demand right now, but I can provide some helpful guidance based on your analysis data.

**Your Question:** "{user_message}"

**Quick Analysis Summary:**
- **Overall Score:** {overall_score:.1f}/100
- **Lowest Scoring Area:** {lowest_category} ({lowest_score:.0f}/100) - This should be your priority focus

**Category Breakdown:**
- UX: {ux_score:.0f}/100
- SEO: {seo_score:.0f}/100  
- Performance: {perf_score:.0f}/100
- Content: {content_score:.0f}/100
- Security: {security_score:.0f}/100
- Images: {image_score:.0f}/100

**Recommended Next Steps:**
1. Review the **{lowest_category}** tab above for specific issues and recommendations
2. Check the **Priority Recommendations** section for high-impact improvements
3. Focus on items marked as "High Priority" and "Low Effort" for quick wins
4. Download the PDF report for a comprehensive action plan

**General Tips:**
- Start with security issues if your Security score is below 80
- Optimize images if your Images score is below 70
- Improve page speed if Performance is below 60
- Add meta descriptions and alt text if SEO is below 70

Please try asking your question again in a moment for a more detailed AI-powered response, or review the detailed analysis sections above."""
    
    async def generate_analysis_summary(self, analysis_data: Dict) -> str:
        """Generate AI summary of the analysis"""
        
        prompt = f"""
        You are a professional website analyst. Analyze the following website analysis data and provide a comprehensive, well-structured summary in markdown format.
        
        Website: {analysis_data.get('website_url')}
        Overall Score: {analysis_data.get('overall_score', 'N/A'):.1f}/100
        
        **Scores Breakdown:**
        - UX Analysis: {analysis_data.get('ux_analysis', {}).get('score', 'N/A')}/100
        - SEO Analysis: {analysis_data.get('seo_analysis', {}).get('score', 'N/A')}/100
        - Performance: {analysis_data.get('performance_analysis', {}).get('score', 'N/A')}/100
        - Content Quality: {analysis_data.get('content_analysis', {}).get('score', 'N/A')}/100
        
        **Key Issues Identified:**
        
        UX Issues:
        {chr(10).join('- ' + issue for issue in analysis_data.get('ux_analysis', {}).get('issues', [])[:3])}
        
        SEO Issues:
        {chr(10).join('- ' + issue for issue in analysis_data.get('seo_analysis', {}).get('issues', [])[:3])}
        
        Performance Issues:
        {chr(10).join('- ' + issue for issue in analysis_data.get('performance_analysis', {}).get('issues', [])[:3])}
        
        Content Issues:
        {chr(10).join('- ' + issue for issue in analysis_data.get('content_analysis', {}).get('issues', [])[:3])}
        
        Please provide a professional analysis summary with the following structure in markdown:
        
        ## 🎯 Overall Assessment
        A brief 2-3 sentence overview of the website's current state and overall health.
        
        ## 🚨 Critical Issues
        List 3-4 most critical issues that need immediate attention. Use bullet points.
        
        ## ⚡ Quick Wins
        List 3-4 easy-to-implement improvements that will have immediate impact. Use bullet points.
        
        ## 📈 Long-term Recommendations
        Provide 3-4 strategic recommendations for sustained growth and improvement. Use bullet points.
        
        ## 💡 Key Takeaway
        A single paragraph summarizing the most important action the website owner should take.
        
        Use clear, actionable language. Be specific and professional. Format using markdown with headers, bold text, and bullet points for readability.
        """
        
        return await self._generate_with_retry(prompt)
    
    async def generate_priority_recommendations(self, analysis_data: Dict) -> List[Dict]:
        """Generate prioritized recommendations"""
        
        prompt = f"""
        Based on this website analysis, provide exactly 5 prioritized recommendations.
        
        Website: {analysis_data.get('website_url')}
        Overall Score: {analysis_data.get('overall_score', 'N/A')}/100
        
        Analysis Data:
        - UX Score: {analysis_data.get('ux_analysis', {}).get('score', 'N/A')}
        - SEO Score: {analysis_data.get('seo_analysis', {}).get('score', 'N/A')}
        - Performance Score: {analysis_data.get('performance_analysis', {}).get('score', 'N/A')}
        - Content Score: {analysis_data.get('content_analysis', {}).get('score', 'N/A')}
        
        For each recommendation, provide:
        1. Title (short, actionable)
        2. Description (2-3 sentences)
        3. Priority (High/Medium/Low)
        4. Impact (High/Medium/Low)
        5. Effort (High/Medium/Low)
        6. Category (UX/SEO/Performance/Content)
        
        Format as JSON array.
        """
        
        # For now, return structured format without AI call to save quota
        # You can enable AI generation when quota is available
        return [
            {
                "title": "Improve Page Load Speed",
                "description": "Optimize images and enable caching to reduce load time by 40%",
                "priority": "High",
                "impact": "High",
                "effort": "Medium",
                "category": "Performance"
            },
            {
                "title": "Add Meta Descriptions",
                "description": "Create unique meta descriptions for all pages to improve SEO",
                "priority": "High",
                "impact": "Medium",
                "effort": "Low",
                "category": "SEO"
            },
            {
                "title": "Enhance Mobile Responsiveness",
                "description": "Fix layout issues on mobile devices for better user experience",
                "priority": "Medium",
                "impact": "High",
                "effort": "Medium",
                "category": "UX"
            },
            {
                "title": "Improve Content Readability",
                "description": "Break up long paragraphs and use more headings",
                "priority": "Medium",
                "impact": "Medium",
                "effort": "Low",
                "category": "Content"
            },
            {
                "title": "Add Clear Call-to-Actions",
                "description": "Place prominent CTAs above the fold to increase conversions",
                "priority": "High",
                "impact": "High",
                "effort": "Low",
                "category": "UX"
            }
        ]
    
    async def chat_about_analysis(
        self,
        analysis: Dict,
        user_message: str,
        chat_history: List[Dict]
    ) -> str:
        """Generate response for chat about analysis with enhanced context and intelligence"""
        
        try:
            # Extract detailed analysis data
            ux_data = analysis.get('ux_analysis', {})
            seo_data = analysis.get('seo_analysis', {})
            perf_data = analysis.get('performance_analysis', {})
            content_data = analysis.get('content_analysis', {})
            security_data = analysis.get('security_analysis', {})
            image_data = analysis.get('image_analysis', {})
            
            # Build comprehensive context
            context = f"""
You are an expert website analyst and digital strategist with deep knowledge in UX design, SEO, web performance, content strategy, security, and image optimization. You're helping a user understand their website analysis and providing actionable recommendations.

**Website Being Analyzed:** {analysis.get('website_url')}
**Overall Score:** {analysis.get('overall_score', 'N/A'):.1f}/100

**Detailed Scores:**
- UX Score: {ux_data.get('score', 'N/A')}/100 - Grade: {ux_data.get('grade', 'N/A')}
- SEO Score: {seo_data.get('score', 'N/A')}/100 - Grade: {seo_data.get('grade', 'N/A')}
- Performance Score: {perf_data.get('score', 'N/A')}/100 - Grade: {perf_data.get('grade', 'N/A')}
- Content Score: {content_data.get('score', 'N/A')}/100 - Grade: {content_data.get('grade', 'N/A')}
- Security Score: {security_data.get('score', 'N/A')}/100 - Grade: {security_data.get('grade', 'N/A')}
- Images Score: {image_data.get('score', 'N/A')}/100 - Grade: {image_data.get('grade', 'N/A')}

**Key Issues Identified:**

UX Issues ({len(ux_data.get('issues', []))} total):
{chr(10).join('- ' + issue for issue in ux_data.get('issues', [])[:5])}

SEO Issues ({len(seo_data.get('issues', []))} total):
{chr(10).join('- ' + issue for issue in seo_data.get('issues', [])[:5])}

Performance Issues ({len(perf_data.get('issues', []))} total):
{chr(10).join('- ' + issue for issue in perf_data.get('issues', [])[:5])}

Content Issues ({len(content_data.get('issues', []))} total):
{chr(10).join('- ' + issue for issue in content_data.get('issues', [])[:5])}

Security Issues ({len(security_data.get('issues', []))} total):
{chr(10).join('- ' + issue for issue in security_data.get('issues', [])[:5])}

Image Issues ({len(image_data.get('issues', []))} total):
{chr(10).join('- ' + issue for issue in image_data.get('issues', [])[:5])}

**Priority Recommendations:**
{chr(10).join('- ' + rec.get('title', '') + ' (' + rec.get('priority', '') + ' priority)' for rec in analysis.get('priority_recommendations', [])[:5])}

**AI Summary:**
{analysis.get('ai_summary', 'Analysis in progress')}
"""
            
            # Build chat history with better formatting
            history_text = ""
            if chat_history:
                recent_history = chat_history[-6:]  # Last 6 messages (3 exchanges)
                history_text = "\n".join([
                    f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['message']}"
                    for msg in recent_history
                ])
            
            # Detect question type for better responses
            question_lower = user_message.lower()
            is_how_to = any(word in question_lower for word in ['how', 'what', 'why', 'when', 'where'])
            is_comparison = any(word in question_lower for word in ['compare', 'vs', 'versus', 'difference', 'better'])
            is_priority = any(word in question_lower for word in ['first', 'priority', 'important', 'urgent', 'start'])
            is_technical = any(word in question_lower for word in ['code', 'implement', 'technical', 'developer', 'css', 'html', 'javascript'])
            is_business = any(word in question_lower for word in ['roi', 'revenue', 'conversion', 'business', 'sales', 'customers'])
            
            # Build enhanced prompt based on question type
            prompt = f"""
{context}

**Previous Conversation:**
{history_text if history_text else "This is the start of the conversation."}

**User Question:** {user_message}

**Instructions for Your Response:**

1. **Be Contextually Aware:** Reference specific data from the analysis above. Use actual scores, issues, and recommendations.

2. **Response Style:**
   - Use markdown formatting for clarity
   - **Bold** key terms and important points
   - Use bullet points for lists
   - Include code examples if discussing technical implementation
   - Keep responses focused and actionable (3-5 paragraphs)

3. **Question Type Guidance:**
   {"- This is a HOW-TO question. Provide step-by-step guidance with specific actions." if is_how_to else ""}
   {"- This is a COMPARISON question. Compare options clearly with pros/cons." if is_comparison else ""}
   {"- This is a PRIORITY question. Rank recommendations by impact and urgency." if is_priority else ""}
   {"- This is a TECHNICAL question. Include code snippets and implementation details." if is_technical else ""}
   {"- This is a BUSINESS question. Focus on ROI, conversions, and business impact." if is_business else ""}

4. **Always Include:**
   - Specific references to their website's data
   - Actionable next steps
   - Expected impact or outcomes
   - Time estimates when relevant
   - Links to resources if helpful (use markdown links)

5. **Tone:** Professional yet friendly, like a knowledgeable consultant. Be encouraging but honest about challenges.

6. **Examples:** When possible, provide concrete examples relevant to their website type and industry.

Provide your response now:
"""
            
            return await self._generate_with_retry(prompt)
            
        except Exception as e:
            print(f"❌ Error in chat_about_analysis: {e}")
            import traceback
            traceback.print_exc()
            # Return contextual fallback
            return self._get_chat_fallback_response(analysis, user_message)

    async def generate_action_plan(self, analysis_data: Dict) -> Dict:
        """Generate 30/60/90 day action plan"""
        
        prompt = f"""
        Based on this website analysis, create a detailed 30/60/90 day improvement roadmap.
        
        Website: {analysis_data.get('website_url')}
        Overall Score: {analysis_data.get('overall_score', 'N/A'):.1f}/100
        
        Scores:
        - UX: {analysis_data.get('ux_analysis', {}).get('score', 'N/A')}/100
        - SEO: {analysis_data.get('seo_analysis', {}).get('score', 'N/A')}/100
        - Performance: {analysis_data.get('performance_analysis', {}).get('score', 'N/A')}/100
        - Content: {analysis_data.get('content_analysis', {}).get('score', 'N/A')}/100
        
        Create a strategic roadmap with:
        
        **30 Days (Quick Wins):**
        - Focus on low-effort, high-impact improvements
        - 3-5 specific actionable tasks
        - Expected outcomes
        
        **60 Days (Foundation Building):**
        - Medium-effort improvements that build on 30-day wins
        - 3-5 specific actionable tasks
        - Expected outcomes
        
        **90 Days (Strategic Growth):**
        - Long-term, high-impact initiatives
        - 3-5 specific actionable tasks
        - Expected outcomes
        
        Format the response in clear markdown with headers and bullet points.
        """
        
        roadmap_text = await self._generate_with_retry(prompt)
        
        return {
            "roadmap": roadmap_text,
            "summary": "Strategic 30/60/90 day improvement plan",
            "total_tasks": 12,
            "estimated_impact": "High"
        }
