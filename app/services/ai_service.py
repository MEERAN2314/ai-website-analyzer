import google.generativeai as genai
from typing import List, Dict
from app.core.config import settings

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)


class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
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
        
        response = self.model.generate_content(prompt)
        return response.text
    
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
        
        response = self.model.generate_content(prompt)
        # Parse and return recommendations
        # For now, return a structured format
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
        """Generate response for chat about analysis"""
        
        # Build context from analysis
        context = f"""
        You are an expert website analyst helping a user understand their website analysis. Provide clear, actionable advice.
        
        Website: {analysis.get('website_url')}
        Overall Score: {analysis.get('overall_score', 'N/A')}/100
        
        **Analysis Summary:**
        {analysis.get('ai_summary', 'Analysis in progress')}
        
        **Scores:**
        - UX: {analysis.get('ux_analysis', {}).get('score', 'N/A')}/100
        - SEO: {analysis.get('seo_analysis', {}).get('score', 'N/A')}/100
        - Performance: {analysis.get('performance_analysis', {}).get('score', 'N/A')}/100
        - Content: {analysis.get('content_analysis', {}).get('score', 'N/A')}/100
        """
        
        # Build chat history
        history_text = "\n".join([
            f"{msg['role']}: {msg['message']}"
            for msg in chat_history[-10:]  # Last 10 messages
        ])
        
        prompt = f"""
        {context}
        
        Previous conversation:
        {history_text}
        
        User: {user_message}
        
        Provide a helpful, professional response using markdown formatting. Be specific and actionable. Use:
        - **Bold** for emphasis
        - Bullet points for lists
        - Code formatting for technical terms
        - Clear paragraphs for readability
        
        Keep responses concise but informative (2-4 paragraphs max).
        """
        
        response = self.model.generate_content(prompt)
        return response.text
