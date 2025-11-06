import streamlit as st
import pandas as pd
import json
import re

TEAM_SIZE = 10  # Change this value if you want to update team size in future

st.set_page_config(
    page_title="100B Jobs - AI Hiring Platform",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .candidate-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        background-color: #f9f9f9;
    }
    .selected-candidate {
        border: 2px solid #28a745;
        background-color: #e8f5e9;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_candidate_data():
    try:
        with open('form-submissions.json', 'r', encoding='utf-8') as f:
            candidates = json.load(f)
        return pd.DataFrame(candidates)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

class HiringAnalyzer:
    def __init__(self, df):
        self.df = df

    def calculate_candidate_score(self, candidate):
        score = 0

        # Education score (30%)
        education_score = 0
        education = candidate.get('education', {})
        if isinstance(education, dict):
            highest_level = education.get('highest_level', '').lower()
            if 'phd' in highest_level or 'doctorate' in highest_level:
                education_score = 30
            elif 'master' in highest_level:
                education_score = 25
            elif 'bachelor' in highest_level:
                education_score = 20
            elif 'associate' in highest_level:
                education_score = 15
            degrees = education.get('degrees', [])
            for degree in degrees:
                if degree.get('isTop50', False):
                    education_score += 5
                    break
        # Experience score (40%)
        experience_score = 0
        experiences = candidate.get('work_experiences', [])
        if len(experiences) >= 5:
            experience_score = 30
        elif len(experiences) >= 3:
            experience_score = 25
        elif len(experiences) >= 2:
            experience_score = 20
        elif len(experiences) >= 1:
            experience_score = 15
        senior_keywords = ['senior', 'lead', 'principal', 'manager', 'director', 'vp', 'cto', 'head']
        for exp in experiences:
            role_name = exp.get('roleName', '').lower()
            if any(keyword in role_name for keyword in senior_keywords):
                experience_score += 10
                break
        # Skills score (30%)
        skills = candidate.get('skills', [])
        skills_score = min(len(skills) * 2, 25)
        high_value_skills = ['python', 'machine learning', 'ai', 'react', 'node', 'aws', 'docker', 'sql', 'tensorflow']
        if skills:
            skills_text = ' '.join(skills).lower()
            for skill in high_value_skills:
                if skill in skills_text:
                    skills_score += 1
        total_score = min(education_score + experience_score + skills_score, 100)
        return total_score

    def get_diversity_metrics(self, candidate_names):
        if not candidate_names:
            return {'geographic_diversity': 0, 'skill_diversity': 0}
        selected_candidates = self.df[self.df['name'].isin(candidate_names)]
        locations = selected_candidates['location'].unique()
        geographic_diversity = len(locations)
        all_skills = []
        for _, candidate in selected_candidates.iterrows():
            skills = candidate.get('skills', [])
            if isinstance(skills, list):
                all_skills.extend(skills)
        skill_diversity = len(set(all_skills))
        return {
            'geographic_diversity': geographic_diversity,
            'skill_diversity': skill_diversity,
            'unique_skills': list(set(all_skills)),
            'team_locations': list(locations)
        }

def extract_salary(salary_dict):
    if isinstance(salary_dict, dict):
        salary_str = salary_dict.get('full-time', '$0')
    else:
        salary_str = str(salary_dict)
    numbers = re.findall(r'\d+', salary_str)
    return int(''.join(numbers)) if numbers else 0

def salary_display(candidate):
    salary_raw = candidate.get('annual_salary_expectation', {}).get('full-time', '')
    # Prefer INR if present, also location-based fallback
    if ("₹" in salary_raw) or ("INR" in salary_raw) or ("India" in candidate.get('location', '')):
        return f"💰 {salary_raw}"
    else:
        salary_num = extract_salary(candidate.get('annual_salary_expectation', {}))
        return f"💰 ${salary_num:,}"

def main():
    st.markdown(f'<h1 class="main-header">🚀 100B Jobs - AI Hiring Platform</h1>', unsafe_allow_html=True)
    st.markdown(f"**Mission**: Just raised $100M seed round. Need to hire {TEAM_SIZE} exceptional people immediately!")

    df = load_candidate_data()
    if df.empty:
        st.error("❌ Could not load candidate data. Please ensure 'form-submissions.json' is in the repository.")
        st.info("📁 Upload your form-submissions.json file to the GitHub repository")
        return

    analyzer = HiringAnalyzer(df)
    if 'selected_candidates' not in st.session_state:
        st.session_state.selected_candidates = []

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "👥 Candidates", "🎯 Team Builder", "📈 Analytics"])

    with tab1:
        st.header("📊 Hiring Dashboard")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Applicants", len(df))
        with col2:
            avg_salary = df['annual_salary_expectation'].apply(extract_salary).mean()
            st.metric("Avg Salary Expectation", f"${avg_salary:,.0f}")
        with col3:
            st.metric("Selected for Team", len(st.session_state.selected_candidates))
        with col4:
            remaining = TEAM_SIZE - len(st.session_state.selected_candidates)
            st.metric("Remaining Slots", remaining)
        st.subheader("📈 Application Insights")
        col1, col2 = st.columns(2)
        with col1:
            education_levels = []
            for _, candidate in df.iterrows():
                education = candidate.get('education', {})
                level = education.get('highest_level', 'Unknown') if isinstance(education, dict) else 'Unknown'
                education_levels.append(level)
            education_counts = pd.Series(education_levels).value_counts()
            st.subheader("Education Distribution")
            st.bar_chart(education_counts)
        with col2:
            location_counts = df['location'].value_counts().head(10)
            st.subheader("Top Locations")
            st.bar_chart(location_counts)

    with tab2:
        st.header("👥 Candidate Pool Analysis")
        search_term = st.text_input("🔍 Search candidates by name, skills, or company")
        candidates_with_scores = []
        for idx, candidate in df.iterrows():
            candidate_dict = candidate.to_dict()
            score = analyzer.calculate_candidate_score(candidate_dict)
            candidates_with_scores.append({
                'index': idx,
                'candidate': candidate_dict,
                'score': score
            })
        candidates_with_scores.sort(key=lambda x: x['score'], reverse=True)
        for item in candidates_with_scores:
            candidate = item['candidate']
            score = item['score']
            idx = item['index']
            if search_term:
                search_fields = [
                    str(candidate.get('name', '')).lower(),
                    str(candidate.get('skills', [])).lower(),
                    str(candidate.get('work_experiences', [])).lower()
                ]
                if not any(search_term.lower() in field for field in search_fields):
                    continue
            is_selected = candidate['name'] in st.session_state.selected_candidates
            with st.container():
                if is_selected:
                    st.success(f"✅ SELECTED: {candidate['name']}")
                else:
                    st.info(f"👤 {candidate['name']}")
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"📍 {candidate.get('location', 'Unknown')}")
                    st.write(f"📧 {candidate.get('email', 'Unknown')}")
                    experiences = candidate.get('work_experiences', [])
                    if experiences and len(experiences) > 0:
                        recent_exp = experiences[0]
                        st.write(f"💼 {recent_exp.get('roleName', 'N/A')} at {recent_exp.get('company', 'N/A')}")
                    skills = candidate.get('skills', [])
                    if skills:
                        skills_preview = ', '.join(skills[:4])
                        if len(skills) > 4:
                            skills_preview += f" (+{len(skills)-4} more)"
                        st.write(f"🛠️ **Skills**: {skills_preview}")
                with col2:
                    st.metric("AI Score", f"{score}/100")
                    st.write(salary_display(candidate))
                    education = candidate.get('education', {})
                    if isinstance(education, dict):
                        level = education.get('highest_level', 'N/A')
                        st.write(f"🎓 {level}")
                with col3:
                    if is_selected:
                        if st.button(f"❌ Remove", key=f"remove_{idx}"):
                            st.session_state.selected_candidates.remove(candidate['name'])
                            st.rerun()
                    else:
                        can_select = len(st.session_state.selected_candidates) < TEAM_SIZE
                        if st.button("➕ Select", key=f"select_{idx}", disabled=not can_select):
                            st.session_state.selected_candidates.append(candidate['name'])
                            st.rerun()
                st.divider()

    with tab3:
        st.header("🎯 Build Your Dream Team")
        if not st.session_state.selected_candidates:
            st.info("👈 No candidates selected yet. Go to the **Candidates** tab to start building your team!")
        else:
            st.success(f"✅ Team Progress: {len(st.session_state.selected_candidates)}/{TEAM_SIZE} positions filled")
            progress = len(st.session_state.selected_candidates) / TEAM_SIZE
            st.progress(progress)
            selected_data = df[df['name'].isin(st.session_state.selected_candidates)]
            total_budget = 0
            for idx, (_, candidate) in enumerate(selected_data.iterrows()):
                candidate_dict = candidate.to_dict()
                salary = extract_salary(candidate_dict.get('annual_salary_expectation', {}))
                total_budget += salary
                with st.expander(f"👤 {candidate_dict['name']} - Team Member #{idx + 1}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Email**: {candidate_dict.get('email', 'N/A')}")
                        st.write(f"**Location**: {candidate_dict.get('location', 'N/A')}")
                        st.write(f"**Salary**: {salary_display(candidate_dict)}")
                        experiences = candidate_dict.get('work_experiences', [])
                        if experiences:
                            st.write("**Recent Experience**:")
                            for exp in experiences[:2]:
                                st.write(f"• {exp.get('roleName', 'N/A')} at {exp.get('company', 'N/A')}")
                    with col2:
                        skills = candidate_dict.get('skills', [])
                        if skills:
                            st.write(f"**Skills**: {', '.join(skills[:6])}")
                            if len(skills) > 6:
                                st.write(f"*...and {len(skills)-6} more*")
                        education = candidate_dict.get('education', {})
                        if isinstance(education, dict):
                            level = education.get('highest_level', 'N/A')
                            st.write(f"**Education**: {level}")
                        score = analyzer.calculate_candidate_score(candidate_dict)
                        st.write(f"**AI Score**: {score}/100")
            if len(st.session_state.selected_candidates) > 0:
                st.subheader("📊 Team Composition Metrics")
                diversity_metrics = analyzer.get_diversity_metrics(st.session_state.selected_candidates)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Budget", f"${total_budget:,}")
                with col2:
                    st.metric("Geographic Diversity", diversity_metrics['geographic_diversity'])
                with col3:
                    st.metric("Skill Diversity", diversity_metrics['skill_diversity'])
                with col4:
                    avg_score = sum(analyzer.calculate_candidate_score(df[df['name'] == name].iloc[0].to_dict()) for name in st.session_state.selected_candidates) / len(st.session_state.selected_candidates)
                    st.metric("Team Avg Score", f"{avg_score:.0f}/100")

    with tab4:
        st.header("📈 Final Hiring Analytics & Report")
        if not st.session_state.selected_candidates:
            st.info("Complete your team selection first to generate the final report!")
        else:
            st.subheader("🏆 Final Team Selection Justification")
            selected_data = df[df['name'].isin(st.session_state.selected_candidates)]
            for idx, (_, candidate) in enumerate(selected_data.iterrows()):
                candidate_dict = candidate.to_dict()
                score = analyzer.calculate_candidate_score(candidate_dict)
                st.markdown(f"### {idx + 1}. **{candidate_dict['name']}** (AI Score: {score}/100)")
                justifications = []
                education = candidate_dict.get('education', {})
                if isinstance(education, dict):
                    level = education.get('highest_level', '').lower()
                    if 'master' in level or 'phd' in level:
                        justifications.append("Advanced degree holder")
                    degrees = education.get('degrees', [])
                    for degree in degrees:
                        if degree.get('isTop50', False):
                            justifications.append("Top-tier university graduate")
                            break
                experiences = candidate_dict.get('work_experiences', [])
                if len(experiences) >= 3:
                    justifications.append("Extensive work experience")
                senior_keywords = ['senior', 'lead', 'principal', 'manager', 'director']
                for exp in experiences:
                    role_name = exp.get('roleName', '').lower()
                    if any(keyword in role_name for keyword in senior_keywords):
                        justifications.append("Leadership experience")
                        break
                skills = candidate_dict.get('skills', [])
                if len(skills) >= 5:
                    justifications.append("Diverse skill set")
                high_value_skills = ['python', 'machine learning', 'ai', 'react', 'aws', 'docker']
                if skills:
                    skills_text = ' '.join(skills).lower()
                    for skill in high_value_skills:
                        if skill in skills_text:
                            justifications.append("High-value technical skills")
                            break
                if justifications:
                    st.write(f"✅ **Why chosen**: {', '.join(justifications)}")
                else:
                    st.write("✅ **Why chosen**: Strong overall profile and team fit")
                st.divider()
            if st.button("📋 Generate Executive Summary"):
                st.success("🎉 Executive Hiring Report Generated!")
                total_budget = sum(extract_salary(df[df['name'] == name]['annual_salary_expectation'].iloc[0]) for name in st.session_state.selected_candidates)
                diversity_metrics = analyzer.get_diversity_metrics(st.session_state.selected_candidates)
                st.markdown(f"""
                ### 📊 Executive Summary

                **Total Team Size**: {len(st.session_state.selected_candidates)} members
                **Total Annual Budget**: ${total_budget:,}
                **Average Salary**: ${total_budget//len(st.session_state.selected_candidates):,}
                **Geographic Diversity**: {diversity_metrics['geographic_diversity']} locations
                **Skill Coverage**: {diversity_metrics['skill_diversity']} unique skills

                ### 🎯 Strategic Rationale
                This team was selected to provide:
                - **Technical Excellence**: Strong engineering and development capabilities
                - **Leadership Experience**: Proven track record in senior roles
                - **Educational Foundation**: Mix of advanced degrees and practical experience
                - **Global Perspective**: Diverse geographic representation
                - **Scalable Skillset**: Skills that align with 100B+ scale ambitions

                ### 📧 Next Steps
                1. Send offer letters to selected candidates
                2. Schedule onboarding calls
                3. Prepare equity packages
                4. Plan first team meeting

                **Ready for $100M growth! 🚀**
                """)

if __name__ == "__main__":
    main()
