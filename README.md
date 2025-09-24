readme_md = """
# 🚀 100B Jobs - AI Hiring Platform

## Overview
Full-stack hiring application built for the Mercor challenge. Analyze hundreds of candidates and build a diverse team of 5 exceptional hires using AI-powered insights.

## 🎯 Challenge Scenario  
- Just raised $100M seed round
- Need to hire 5 people immediately  
- Hundreds of LinkedIn applicants to analyze
- 1hr 45min to build, deploy & demo

## ✨ Features

### 📊 Smart Analytics Dashboard
- Real-time hiring metrics
- Salary analysis & budgeting
- Geographic distribution insights
- Education level breakdown

### 🤖 AI-Powered Candidate Scoring
- Comprehensive 100-point scoring system
- Education assessment (30% weight)
- Experience evaluation (40% weight)  
- Skills analysis (30% weight)
- Top university bonuses
- Leadership role recognition

### 👥 Advanced Candidate Management
- Search & filter functionality
- Interactive candidate cards
- Real-time selection tracking
- 5-person team limit enforcement

### 🎯 Team Builder Interface
- Drag-and-drop team assembly
- Live diversity metrics calculation
- Budget tracking & optimization
- Role distribution analysis

### 📈 Strategic Hiring Analytics
- Team composition insights
- Diversity scoring (geographic + skills)
- Hiring justification generator
- Executive summary reports

## 🚀 Deployment

### GitHub + Streamlit Cloud (Recommended)
1. Clone this repository
2. Upload to your GitHub account
3. Connect to Streamlit Cloud
4. Deploy with one click
5. Share live URL in demo video

### Local Development
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📊 Data Structure
Uses form-submissions.json with candidate profiles including:
- Personal info (name, email, location)
- Work experience & companies
- Education & degrees
- Skills & technologies
- Salary expectations

## 🎥 Demo Instructions
1. Access the live Streamlit app
2. Explore Dashboard tab for insights
3. Browse Candidates tab with AI scoring
4. Build team using Team Builder
5. Generate final report in Analytics
6. Record 5-minute screen sharing demo

## 🏆 Selection Criteria Applied

### Technical Excellence (40%)
- Senior engineering roles
- Multiple company experience  
- Full-stack capabilities
- Modern tech stacks

### Educational Foundation (30%)
- Advanced degrees preferred
- Top university bonuses
- Relevant field of study
- Strong GPA indicators

### Strategic Value (30%)
- Leadership potential
- Geographic diversity
- Unique skill combinations
- Salary-value optimization

## 💡 Key Differentiators

**Engineering Excellence**: Production-ready code with error handling, caching, and responsive design

**Creative Problem Solving**: Novel AI scoring algorithm combining multiple candidate dimensions

**Intuitive UX**: Clean interface with real-time updates and visual feedback

**Strategic Thinking**: Balances technical skills, diversity, and budget constraints

**Scalable Architecture**: Built to handle "100 billion jobs" scale with efficient data processing

## 📧 Contact
Built for: danielhe@mercor.com  
Demo URL: [Streamlit Cloud Link]  
GitHub Repo: [Repository Link]

---
*Built in 1hr 45min for Mercor's 100B Jobs Challenge*
"""

# Create the data processor module
data_processor_py = """
import json
import pandas as pd
import re
from typing import Dict, List, Any

class CandidateAnalyzer:
    '''Advanced candidate analysis and scoring system'''
    
    def __init__(self, data_path: str = 'form-submissions.json'):
        self.data_path = data_path
        self.candidates_df = None
        
    def load_data(self) -> pd.DataFrame:
        '''Load candidate data from JSON file'''
        try:
            with open(self.data_path, 'r') as f:
                candidates = json.load(f)
            self.candidates_df = pd.DataFrame(candidates)
            return self.candidates_df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def calculate_experience_score(self, experiences: List[Dict]) -> int:
        '''Calculate experience score based on roles and companies'''
        if not experiences:
            return 0
            
        score = 0
        
        # Base score for number of experiences
        score += min(len(experiences) * 5, 25)
        
        # Senior role bonus
        senior_keywords = ['senior', 'lead', 'principal', 'manager', 'director', 'vp', 'cto', 'ceo']
        for exp in experiences:
            role = exp.get('roleName', '').lower()
            if any(keyword in role for keyword in senior_keywords):
                score += 15
                break
        
        # Top company bonus (simplified)
        top_companies = ['google', 'microsoft', 'apple', 'amazon', 'facebook', 'meta', 'netflix', 'uber', 'airbnb']
        for exp in experiences:
            company = exp.get('company', '').lower()
            if any(top_comp in company for top_comp in top_companies):
                score += 10
                break
                
        return min(score, 40)
    
    def calculate_education_score(self, education: Dict) -> int:
        '''Calculate education score based on degrees and institutions'''
        if not education:
            return 0
            
        score = 0
        
        # Highest level bonus
        highest_level = education.get('highest_level', '')
        if 'phd' in highest_level.lower() or 'doctorate' in highest_level.lower():
            score += 25
        elif 'master' in highest_level.lower():
            score += 20
        elif 'bachelor' in highest_level.lower():
            score += 15
        
        # Top school bonus
        degrees = education.get('degrees', [])
        for degree in degrees:
            if degree.get('isTop50', False):
                score += 10
                break
                
        return min(score, 30)
    
    def calculate_skills_score(self, skills: List[str]) -> int:
        '''Calculate skills score based on quantity and relevance'''
        if not skills:
            return 0
            
        # Base score for number of skills
        score = min(len(skills) * 2, 20)
        
        # High-value skills bonus
        high_value_skills = [
            'machine learning', 'ai', 'python', 'java', 'react', 'node.js', 
            'aws', 'docker', 'kubernetes', 'tensorflow', 'pytorch', 'sql'
        ]
        
        skill_text = ' '.join(skills).lower()
        for valuable_skill in high_value_skills:
            if valuable_skill in skill_text:
                score += 2
                
        return min(score, 30)
    
    def calculate_overall_score(self, candidate: Dict) -> Dict[str, Any]:
        '''Calculate comprehensive candidate score'''
        
        # Component scores
        experience_score = self.calculate_experience_score(candidate.get('work_experiences', []))
        education_score = self.calculate_education_score(candidate.get('education', {}))
        skills_score = self.calculate_skills_score(candidate.get('skills', []))
        
        # Overall score
        total_score = experience_score + education_score + skills_score
        
        # Salary value calculation
        salary_str = candidate.get('annual_salary_expectation', {}).get('full-time', '$0')
        salary_value = int(re.sub(r'[^0-9]', '', salary_str)) if salary_str else 0
        
        # Value ratio (score per salary dollar)
        value_ratio = (total_score / salary_value * 100000) if salary_value > 0 else 0
        
        return {
            'name': candidate.get('name', 'Unknown'),
            'total_score': total_score,
            'experience_score': experience_score,
            'education_score': education_score,
            'skills_score': skills_score,
            'salary_expectation': salary_value,
            'value_ratio': value_ratio,
            'location': candidate.get('location', 'Unknown')
        }
    
    def get_top_candidates(self, n: int = 10) -> List[Dict]:
        '''Get top N candidates by overall score'''
        if self.candidates_df is None:
            self.load_data()
            
        scored_candidates = []
        for _, candidate in self.candidates_df.iterrows():
            score_data = self.calculate_overall_score(candidate.to_dict())
            scored_candidates.append(score_data)
        
        # Sort by total score descending
        scored_candidates.sort(key=lambda x: x['total_score'], reverse=True)
        return scored_candidates[:n]
    
    def analyze_diversity(self, selected_candidates: List[str]) -> Dict:
        '''Analyze diversity metrics for selected team'''
        if self.candidates_df is None:
            self.load_data()
            
        team_data = self.candidates_df[self.candidates_df['name'].isin(selected_candidates)]
        
        # Geographic diversity
        locations = team_data['location'].unique()
        geographic_diversity = len(locations)
        
        # Skill diversity
        all_skills = []
        for _, candidate in team_data.iterrows():
            skills = candidate.get('skills', [])
            if isinstance(skills, list):
                all_skills.extend(skills)
        skill_diversity = len(set(all_skills))
        
        # Education diversity
        education_levels = []
        for _, candidate in team_data.iterrows():
            education = candidate.get('education', {})
            if isinstance(education, dict):
                level = education.get('highest_level', 'Unknown')
                education_levels.append(level)
        education_diversity = len(set(education_levels))
        
        return {
            'geographic_diversity': geographic_diversity,
            'skill_diversity': skill_diversity, 
            'education_diversity': education_diversity,
            'team_locations': list(locations),
            'unique_skills': list(set(all_skills))
        }
"""

print("✅ All files generated successfully!")
print("\n📁 Complete file structure:")
print("├── streamlit_app.py (main application)")
print("├── requirements.txt (dependencies)")
print("├── data_processor.py (analysis engine)")  
print("├── README.md (documentation)")
print("└── form-submissions.json (your data file)")

print(f"\n🔧 Requirements.txt content:\n{requirements_txt}")
print(f"\n📖 README.md preview:\n{readme_md[:500]}...")
print(f"\n🧮 Data processor preview:\n{data_processor_py[:500]}...")
