from datetime import datetime
from bson import ObjectId
from typing import List, Dict
import asyncio

from app.core.database import get_database
from app.analyzers.ux_analyzer import UXAnalyzer
from app.analyzers.seo_analyzer import SEOAnalyzer
from app.analyzers.performance_analyzer import PerformanceAnalyzer
from app.analyzers.content_analyzer import ContentAnalyzer
from app.analyzers.security_analyzer import SecurityAnalyzer
from app.analyzers.image_analyzer import ImageAnalyzer
from app.services.ai_service import AIService
from app.services.comparison_pdf_service import ComparisonPDFService


class ComparisonService:
    """Service for competitor analysis"""
    
    def __init__(self):
        self.db = get_database()
        self.ai_service = AIService()
    
    async def create_comparison(self, your_url: str, competitor_urls: List[str], user_id: str = None) -> str:
        """Create a new comparison analysis"""
        
        # Create comparison record
        comparison = {
            "user_id": user_id,
            "your_website": {
                "url": your_url,
                "analysis_data": None
            },
            "competitors": [
                {"url": url, "analysis_data": None} for url in competitor_urls
            ],
            "rankings": None,
            "insights": None,
            "ai_summary": None,
            "pdf_url": None,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "completed_at": None
        }
        
        result = await self.db.comparisons.insert_one(comparison)
        comparison_id = str(result.inserted_id)
        
        print(f"📊 Comparison {comparison_id}: Created")
        
        # Start analysis in background
        asyncio.create_task(self.perform_comparison(comparison_id))
        
        return comparison_id
    
    async def perform_comparison(self, comparison_id: str):
        """Perform the actual comparison analysis"""
        try:
            print(f"📊 Comparison {comparison_id}: Starting analysis...")
            
            # Update status
            await self.db.comparisons.update_one(
                {"_id": ObjectId(comparison_id)},
                {"$set": {"status": "processing"}}
            )
            
            # Get comparison data
            comparison = await self.db.comparisons.find_one({"_id": ObjectId(comparison_id)})
            
            your_url = comparison["your_website"]["url"]
            competitor_urls = [c["url"] for c in comparison["competitors"]]
            
            # Analyze all websites in parallel
            print(f"📊 Comparison {comparison_id}: Analyzing {len(competitor_urls) + 1} websites...")
            
            all_urls = [your_url] + competitor_urls
            analysis_results = await self._analyze_websites(all_urls)
            
            # Separate your website from competitors
            your_analysis = analysis_results[0]
            competitor_analyses = analysis_results[1:]
            
            print(f"📊 Comparison {comparison_id}: Analysis complete, calculating rankings...")
            
            # Calculate rankings
            rankings = self._calculate_rankings(your_analysis, competitor_analyses, your_url, competitor_urls)
            
            # Identify strengths, weaknesses, opportunities
            insights = self._generate_insights(your_analysis, competitor_analyses, rankings)
            
            # Generate AI summary
            print(f"📊 Comparison {comparison_id}: Generating AI insights...")
            ai_summary = await self._generate_ai_summary(your_url, your_analysis, competitor_analyses, insights)
            
            # Generate PDF report
            print(f"📊 Comparison {comparison_id}: Generating PDF report...")
            pdf_url = None
            try:
                pdf_service = ComparisonPDFService()
                
                # Prepare data for PDF
                pdf_data = {
                    '_id': comparison_id,
                    'your_website': {
                        'url': your_url,
                        'analysis_data': your_analysis
                    },
                    'competitors': [
                        {
                            'url': competitor_urls[i],
                            'analysis_data': competitor_analyses[i]
                        }
                        for i in range(len(competitor_urls))
                    ],
                    'rankings': rankings,
                    'insights': insights,
                    'ai_summary': ai_summary
                }
                
                # Generate PDF
                pdf_path = await pdf_service.generate_comparison_report(pdf_data)
                pdf_filename = f"comparison_{comparison_id}.pdf"
                pdf_url = f"/static/pdfs/{pdf_filename}"
                
                print(f"✅ Comparison PDF generated: {pdf_url}")
                
            except Exception as pdf_error:
                print(f"⚠️  PDF generation error: {pdf_error}")
                import traceback
                traceback.print_exc()
            
            # Update comparison with results
            await self.db.comparisons.update_one(
                {"_id": ObjectId(comparison_id)},
                {
                    "$set": {
                        "your_website.analysis_data": your_analysis,
                        "competitors": [
                            {
                                "url": competitor_urls[i],
                                "analysis_data": competitor_analyses[i]
                            }
                            for i in range(len(competitor_urls))
                        ],
                        "rankings": rankings,
                        "insights": insights,
                        "ai_summary": ai_summary,
                        "pdf_url": pdf_url,
                        "status": "completed",
                        "completed_at": datetime.utcnow()
                    }
                }
            )
            
            print(f"✅ Comparison {comparison_id}: Completed successfully!")
            
        except Exception as e:
            print(f"❌ Comparison {comparison_id}: Failed with error: {e}")
            import traceback
            traceback.print_exc()
            
            await self.db.comparisons.update_one(
                {"_id": ObjectId(comparison_id)},
                {
                    "$set": {
                        "status": "failed",
                        "error_message": str(e),
                        "completed_at": datetime.utcnow()
                    }
                }
            )
    
    async def _analyze_websites(self, urls: List[str]) -> List[Dict]:
        """Analyze multiple websites in parallel with enhanced accuracy"""
        
        async def analyze_single_website(url: str) -> Dict:
            """Analyze a single website with retry logic and validation"""
            max_retries = 2
            retry_count = 0
            
            while retry_count <= max_retries:
                try:
                    print(f"🔍 Analyzing {url} (attempt {retry_count + 1}/{max_retries + 1})")
                    
                    # Initialize analyzers
                    ux_analyzer = UXAnalyzer()
                    seo_analyzer = SEOAnalyzer()
                    performance_analyzer = PerformanceAnalyzer()
                    content_analyzer = ContentAnalyzer()
                    security_analyzer = SecurityAnalyzer()
                    image_analyzer = ImageAnalyzer()
                    
                    # Run all analyzers in parallel with timeout
                    results = await asyncio.wait_for(
                        asyncio.gather(
                            ux_analyzer.analyze(url),
                            seo_analyzer.analyze(url),
                            performance_analyzer.analyze(url),
                            content_analyzer.analyze(url),
                            security_analyzer.analyze(url),
                            image_analyzer.analyze(url),
                            return_exceptions=True
                        ),
                        timeout=120  # 2 minute timeout per website
                    )
                    
                    ux_result, seo_result, perf_result, content_result, security_result, image_result = results
                    
                    # Enhanced error handling with detailed logging
                    def safe_result(result, analyzer_name, default_score=0):
                        if isinstance(result, Exception):
                            print(f"⚠️  {analyzer_name} failed for {url}: {result}")
                            return {
                                "score": default_score, 
                                "issues": [f"{analyzer_name} analysis failed"],
                                "recommendations": [],
                                "error": str(result)
                            }
                        
                        # Validate result structure
                        if not isinstance(result, dict) or "score" not in result:
                            print(f"⚠️  {analyzer_name} returned invalid data for {url}")
                            return {
                                "score": default_score,
                                "issues": [f"{analyzer_name} returned invalid data"],
                                "recommendations": []
                            }
                        
                        # Ensure score is within valid range
                        score = result.get("score", default_score)
                        if not isinstance(score, (int, float)) or score < 0 or score > 100:
                            print(f"⚠️  {analyzer_name} returned invalid score: {score}")
                            result["score"] = max(0, min(100, default_score))
                        
                        return result
                    
                    ux_result = safe_result(ux_result, "UX")
                    seo_result = safe_result(seo_result, "SEO")
                    perf_result = safe_result(perf_result, "Performance")
                    content_result = safe_result(content_result, "Content")
                    security_result = safe_result(security_result, "Security")
                    image_result = safe_result(image_result, "Image")
                    
                    # Enhanced weighted scoring with industry standards
                    # Weights optimized for competitive analysis accuracy
                    weights = {
                        'seo': 0.22,        # SEO is critical for visibility
                        'performance': 0.20, # Performance affects user experience
                        'ux': 0.18,         # UX drives conversions
                        'content': 0.17,    # Content quality matters
                        'security': 0.15,   # Security builds trust
                        'images': 0.08      # Image optimization is important but less critical
                    }
                    
                    overall_score = (
                        ux_result.get("score", 0) * weights['ux'] +
                        seo_result.get("score", 0) * weights['seo'] +
                        perf_result.get("score", 0) * weights['performance'] +
                        content_result.get("score", 0) * weights['content'] +
                        security_result.get("score", 0) * weights['security'] +
                        image_result.get("score", 0) * weights['images']
                    )
                    
                    # Calculate confidence score based on successful analyzers
                    successful_analyzers = sum([
                        1 for r in [ux_result, seo_result, perf_result, content_result, security_result, image_result]
                        if not r.get('error')
                    ])
                    confidence = (successful_analyzers / 6) * 100
                    
                    # Calculate category grades
                    def get_grade(score):
                        if score >= 90: return 'A'
                        elif score >= 80: return 'B'
                        elif score >= 70: return 'C'
                        elif score >= 60: return 'D'
                        else: return 'F'
                    
                    analysis_data = {
                        "url": url,
                        "overall_score": round(overall_score, 2),
                        "confidence": round(confidence, 1),
                        "overall_grade": get_grade(overall_score),
                        "ux_analysis": ux_result,
                        "seo_analysis": seo_result,
                        "performance_analysis": perf_result,
                        "content_analysis": content_result,
                        "security_analysis": security_result,
                        "image_analysis": image_result,
                        "category_grades": {
                            "ux": get_grade(ux_result.get("score", 0)),
                            "seo": get_grade(seo_result.get("score", 0)),
                            "performance": get_grade(perf_result.get("score", 0)),
                            "content": get_grade(content_result.get("score", 0)),
                            "security": get_grade(security_result.get("score", 0)),
                            "images": get_grade(image_result.get("score", 0))
                        },
                        "weights_used": weights,
                        "analysis_timestamp": datetime.utcnow().isoformat()
                    }
                    
                    print(f"✅ {url}: Score={overall_score:.1f}, Confidence={confidence:.1f}%, Grade={get_grade(overall_score)}")
                    return analysis_data
                    
                except asyncio.TimeoutError:
                    retry_count += 1
                    if retry_count > max_retries:
                        print(f"❌ {url}: Analysis timeout after {max_retries + 1} attempts")
                        return {
                            "url": url,
                            "overall_score": 0,
                            "confidence": 0,
                            "error": "Analysis timeout - website may be slow or unresponsive"
                        }
                    print(f"⏱️  {url}: Timeout, retrying...")
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        print(f"❌ {url}: Analysis failed after {max_retries + 1} attempts: {e}")
                        return {
                            "url": url,
                            "overall_score": 0,
                            "confidence": 0,
                            "error": str(e)
                        }
                    print(f"⚠️  {url}: Error, retrying... {e}")
                    await asyncio.sleep(2)
        
        # Analyze all websites in parallel with progress tracking
        print(f"🚀 Starting parallel analysis of {len(urls)} websites...")
        results = await asyncio.gather(*[analyze_single_website(url) for url in urls])
        
        # Log summary
        successful = sum(1 for r in results if r.get('overall_score', 0) > 0)
        print(f"📊 Analysis complete: {successful}/{len(urls)} websites analyzed successfully")
        
        return results
    
    def _calculate_rankings(self, your_analysis: Dict, competitor_analyses: List[Dict], 
                           your_url: str, competitor_urls: List[str]) -> Dict:
        """Calculate rankings for all categories"""
        
        all_analyses = [your_analysis] + competitor_analyses
        all_urls = [your_url] + competitor_urls
        
        def rank_category(category_key: str) -> List[Dict]:
            """Rank websites by a specific category"""
            scores = []
            for i, analysis in enumerate(all_analyses):
                if category_key == "overall":
                    score = analysis.get("overall_score", 0)
                else:
                    score = analysis.get(f"{category_key}_analysis", {}).get("score", 0)
                
                scores.append({
                    "url": all_urls[i],
                    "score": round(score, 1),
                    "is_yours": i == 0
                })
            
            # Sort by score (descending)
            scores.sort(key=lambda x: x["score"], reverse=True)
            
            # Add ranks and medals
            for rank, item in enumerate(scores, 1):
                item["rank"] = rank
                if rank == 1:
                    item["medal"] = "1st"
                elif rank == 2:
                    item["medal"] = "2nd"
                elif rank == 3:
                    item["medal"] = "3rd"
                else:
                    item["medal"] = ""
            
            return scores
        
        return {
            "overall": rank_category("overall"),
            "ux": rank_category("ux"),
            "seo": rank_category("seo"),
            "performance": rank_category("performance"),
            "content": rank_category("content"),
            "security": rank_category("security"),
            "images": rank_category("image")
        }
    
    def _generate_insights(self, your_analysis: Dict, competitor_analyses: List[Dict], 
                          rankings: Dict) -> Dict:
        """Generate enhanced competitive insights with deeper analysis"""
        
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []
        competitive_advantages = []
        
        # Find your rank in each category
        your_ranks = {}
        your_scores = {}
        leader_scores = {}
        average_scores = {}
        
        for category, ranking in rankings.items():
            for item in ranking:
                if item["is_yours"]:
                    your_ranks[category] = item["rank"]
                    your_scores[category] = item["score"]
                    break
            
            # Calculate leader and average scores
            leader_scores[category] = ranking[0]["score"]
            average_scores[category] = sum(r["score"] for r in ranking) / len(ranking)
        
        # Identify strengths (where you rank 1st or significantly above average)
        for category, rank in your_ranks.items():
            your_score = your_scores[category]
            avg_score = average_scores[category]
            
            if rank == 1:
                second_score = rankings[category][1]["score"] if len(rankings[category]) > 1 else 0
                gap = your_score - second_score
                
                # Determine strength level
                if gap >= 20:
                    strength_level = "Dominant"
                elif gap >= 10:
                    strength_level = "Strong"
                else:
                    strength_level = "Leading"
                
                strengths.append({
                    "category": category.title(),
                    "rank": 1,
                    "score": your_score,
                    "gap": round(gap, 1),
                    "strength_level": strength_level,
                    "message": f"{strength_level} position in {category.title()} - leading by {gap:.1f} points",
                    "recommendation": f"Maintain and leverage your {category.title()} advantage in marketing"
                })
                
                # Add to competitive advantages
                competitive_advantages.append({
                    "category": category.title(),
                    "advantage": f"Market leader in {category.title()}",
                    "score": your_score
                })
            
            elif your_score > avg_score + 5:
                # Above average but not #1
                gap_to_avg = your_score - avg_score
                strengths.append({
                    "category": category.title(),
                    "rank": rank,
                    "score": your_score,
                    "gap": round(gap_to_avg, 1),
                    "strength_level": "Above Average",
                    "message": f"Above average in {category.title()} by {gap_to_avg:.1f} points",
                    "recommendation": f"Push harder in {category.title()} to reach #1 position"
                })
        
        # Identify weaknesses with severity levels
        for category, rank in your_ranks.items():
            if rank > 1:
                category_ranking = rankings[category]
                leader = category_ranking[0]
                your_item = next(item for item in category_ranking if item["is_yours"])
                gap = leader["score"] - your_item["score"]
                avg_score = average_scores[category]
                
                # Determine severity
                if gap >= 30:
                    severity = "Critical"
                    priority = 1
                elif gap >= 20:
                    severity = "High"
                    priority = 2
                elif gap >= 10:
                    severity = "Medium"
                    priority = 3
                else:
                    severity = "Low"
                    priority = 4
                
                # Check if below average
                below_average = your_item["score"] < avg_score
                
                weakness_data = {
                    "category": category.title(),
                    "rank": rank,
                    "your_score": your_item["score"],
                    "leader_score": leader["score"],
                    "average_score": round(avg_score, 1),
                    "gap": round(gap, 1),
                    "severity": severity,
                    "priority": priority,
                    "below_average": below_average,
                    "leader_url": leader["url"],
                    "message": f"{severity} gap in {category.title()} - {gap:.1f} points behind leader",
                    "recommendation": self._get_category_recommendation(category, gap, severity)
                }
                
                weaknesses.append(weakness_data)
                
                # Add to threats if critical
                if severity in ["Critical", "High"]:
                    threats.append({
                        "category": category.title(),
                        "threat": f"Significant competitive disadvantage in {category.title()}",
                        "gap": round(gap, 1),
                        "action": f"Immediate action required to improve {category.title()}"
                    })
        
        # Sort weaknesses by priority and gap
        weaknesses.sort(key=lambda x: (x["priority"], -x["gap"]))
        
        # Identify opportunities (quick wins and strategic moves)
        for weakness in weaknesses:
            gap = weakness["gap"]
            category = weakness["category"]
            
            # Quick wins (small gaps)
            if 5 <= gap < 15:
                opportunities.append({
                    "category": category,
                    "type": "Quick Win",
                    "gap": gap,
                    "effort": "Low to Medium",
                    "impact": "Medium",
                    "message": f"Quick win in {category} - only {gap:.1f} points behind",
                    "action": f"Focus on top 3-5 improvements in {category} for quick gains"
                })
            
            # Strategic opportunities (medium gaps with high impact)
            elif 15 <= gap < 25:
                opportunities.append({
                    "category": category,
                    "type": "Strategic",
                    "gap": gap,
                    "effort": "Medium to High",
                    "impact": "High",
                    "message": f"Strategic opportunity in {category} - {gap:.1f} points gap",
                    "action": f"Develop 3-6 month improvement plan for {category}"
                })
        
        # Calculate competitive position score
        total_categories = len(your_ranks)
        first_place_count = sum(1 for r in your_ranks.values() if r == 1)
        top_3_count = sum(1 for r in your_ranks.values() if r <= 3)
        
        competitive_position = {
            "overall_rank": your_ranks.get("overall", 0),
            "overall_score": your_scores.get("overall", 0),
            "categories_leading": first_place_count,
            "categories_top_3": top_3_count,
            "categories_behind": len(weaknesses),
            "competitive_strength": self._calculate_competitive_strength(your_ranks, your_scores, average_scores)
        }
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
            "threats": threats,
            "competitive_advantages": competitive_advantages,
            "competitive_position": competitive_position,
            "summary": {
                "total_categories": total_categories,
                "leading_in": first_place_count,
                "top_3_in": top_3_count,
                "behind_in": len(weaknesses),
                "quick_wins": len([o for o in opportunities if o.get("type") == "Quick Win"]),
                "strategic_opportunities": len([o for o in opportunities if o.get("type") == "Strategic"]),
                "critical_gaps": len([w for w in weaknesses if w.get("severity") == "Critical"])
            }
        }
    
    def _get_category_recommendation(self, category: str, gap: float, severity: str) -> str:
        """Get specific recommendations based on category and gap"""
        recommendations = {
            "ux": {
                "Critical": "Conduct comprehensive UX audit and user testing immediately",
                "High": "Implement responsive design improvements and accessibility fixes",
                "Medium": "Optimize navigation and improve mobile experience",
                "Low": "Fine-tune user flows and add micro-interactions"
            },
            "seo": {
                "Critical": "Hire SEO expert for complete site optimization and technical SEO fixes",
                "High": "Fix critical SEO issues: meta tags, site structure, and backlink strategy",
                "Medium": "Improve on-page SEO and content optimization",
                "Low": "Enhance internal linking and schema markup"
            },
            "performance": {
                "Critical": "Implement CDN, optimize images, and reduce server response time urgently",
                "High": "Optimize JavaScript/CSS, enable caching, and compress assets",
                "Medium": "Reduce page weight and optimize third-party scripts",
                "Low": "Fine-tune loading priorities and lazy loading"
            },
            "content": {
                "Critical": "Develop comprehensive content strategy with professional copywriting",
                "High": "Improve content quality, readability, and add more valuable content",
                "Medium": "Enhance existing content and add multimedia elements",
                "Low": "Refine messaging and update outdated content"
            },
            "security": {
                "Critical": "Implement HTTPS, security headers, and conduct security audit immediately",
                "High": "Add missing security headers and fix SSL/TLS configuration",
                "Medium": "Implement CSP and improve cookie security",
                "Low": "Add additional security headers and monitoring"
            },
            "images": {
                "Critical": "Implement image optimization pipeline and convert to modern formats",
                "High": "Compress images, add lazy loading, and use responsive images",
                "Medium": "Optimize image sizes and add WebP support",
                "Low": "Fine-tune image loading and add better alt texts"
            }
        }
        
        return recommendations.get(category, {}).get(severity, f"Improve {category} to close the gap")
    
    def _calculate_competitive_strength(self, ranks: Dict, scores: Dict, averages: Dict) -> str:
        """Calculate overall competitive strength"""
        # Calculate how many categories are above average
        above_avg = sum(1 for cat, score in scores.items() if score > averages.get(cat, 0))
        total = len(scores)
        
        # Calculate average rank
        avg_rank = sum(ranks.values()) / len(ranks)
        
        if above_avg >= total * 0.8 and avg_rank <= 1.5:
            return "Market Leader"
        elif above_avg >= total * 0.6 and avg_rank <= 2:
            return "Strong Competitor"
        elif above_avg >= total * 0.4:
            return "Average Competitor"
        else:
            return "Needs Improvement"
    
    async def _generate_ai_summary(self, your_url: str, your_analysis: Dict, 
                                   competitor_analyses: List[Dict], insights: Dict) -> str:
        """Generate enhanced AI-powered competitive analysis summary"""
        
        try:
            # Extract detailed metrics
            your_score = your_analysis.get('overall_score', 0)
            your_grade = your_analysis.get('overall_grade', 'N/A')
            confidence = your_analysis.get('confidence', 0)
            
            # Get competitive position
            comp_position = insights.get('competitive_position', {})
            comp_strength = comp_position.get('competitive_strength', 'Unknown')
            
            # Get top competitors
            competitor_scores = [c.get('overall_score', 0) for c in competitor_analyses]
            avg_competitor_score = sum(competitor_scores) / len(competitor_scores) if competitor_scores else 0
            
            # Build detailed prompt
            prompt = f"""
You are a senior competitive intelligence analyst. Provide a comprehensive strategic analysis.

## YOUR WEBSITE ANALYSIS
URL: {your_url}
Overall Score: {your_score:.1f}/100 (Grade: {your_grade})
Analysis Confidence: {confidence:.1f}%
Competitive Position: {comp_strength}
Overall Rank: #{comp_position.get('overall_rank', 'N/A')}

## COMPETITIVE LANDSCAPE
Total Competitors Analyzed: {len(competitor_analyses)}
Average Competitor Score: {avg_competitor_score:.1f}/100
Your Score vs Average: {(your_score - avg_competitor_score):+.1f} points

## PERFORMANCE BREAKDOWN
Categories Leading: {comp_position.get('categories_leading', 0)}/{insights['summary']['total_categories']}
Categories in Top 3: {comp_position.get('categories_top_3', 0)}/{insights['summary']['total_categories']}
Critical Gaps: {insights['summary'].get('critical_gaps', 0)}

## KEY STRENGTHS
{chr(10).join([f"• {s['message']} ({s.get('strength_level', 'Strong')})" for s in insights['strengths'][:5]])}

## CRITICAL WEAKNESSES
{chr(10).join([f"• {w['message']} (Severity: {w.get('severity', 'Unknown')}, Priority: {w.get('priority', 'N/A')})" for w in insights['weaknesses'][:5]])}

## OPPORTUNITIES
Quick Wins: {insights['summary'].get('quick_wins', 0)}
Strategic Opportunities: {insights['summary'].get('strategic_opportunities', 0)}
{chr(10).join([f"• {o['message']} (Type: {o.get('type', 'Unknown')}, Effort: {o.get('effort', 'N/A')})" for o in insights['opportunities'][:5]])}

## COMPETITIVE ADVANTAGES
{chr(10).join([f"• {a['advantage']} (Score: {a['score']:.1f})" for a in insights.get('competitive_advantages', [])[:3]])}

## THREATS
{chr(10).join([f"• {t['threat']} (Gap: {t['gap']:.1f} points)" for t in insights.get('threats', [])[:3]])}

Provide a strategic analysis with:

1. **Executive Summary** (2-3 sentences)
   - Overall competitive position
   - Key finding

2. **Competitive Strengths** (3-4 points)
   - What you're doing better than competitors
   - How to leverage these advantages

3. **Critical Gaps** (3-4 points)
   - Most important areas to improve
   - Why these matter for competitive position

4. **Strategic Recommendations** (5-6 actionable items)
   - Prioritized by impact and effort
   - Specific, measurable actions
   - Timeline suggestions (quick wins vs long-term)

5. **Market Position Strategy**
   - How to defend strengths
   - How to close critical gaps
   - Differentiation opportunities

Keep it strategic, data-driven, and actionable. Use business language appropriate for executives.
"""
            
            summary = await self.ai_service.generate_text(prompt)
            return summary
            
        except Exception as e:
            print(f"Error generating AI summary: {e}")
            import traceback
            traceback.print_exc()
            
            # Return detailed fallback summary
            return f"""
## Competitive Analysis Summary

**Overall Position:** Your website scored {your_analysis.get('overall_score', 0):.1f}/100, ranking #{insights.get('competitive_position', {}).get('overall_rank', 'N/A')} among competitors.

**Key Strengths:**
{chr(10).join([f"- {s['message']}" for s in insights['strengths'][:3]])}

**Areas for Improvement:**
{chr(10).join([f"- {w['message']}" for w in insights['weaknesses'][:3]])}

**Quick Win Opportunities:**
{chr(10).join([f"- {o['message']}" for o in insights['opportunities'][:3]])}

**Recommendation:** Focus on addressing the critical gaps while maintaining your competitive advantages. Prioritize quick wins for immediate impact.
"""
    
    async def get_comparison(self, comparison_id: str) -> Dict:
        """Get comparison results"""
        try:
            comparison = await self.db.comparisons.find_one({"_id": ObjectId(comparison_id)})
            
            if not comparison:
                return None
            
            # Convert ObjectId to string
            comparison["_id"] = str(comparison["_id"])
            
            return comparison
            
        except Exception as e:
            print(f"Error getting comparison: {e}")
            return None
