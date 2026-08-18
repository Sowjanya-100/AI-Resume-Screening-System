
import streamlit as st
import os
from utils.pdf_reader import read_pdf
from utils.docx_reader import read_docx
from utils.skill_extractor import extract_skills, extract_jd_skills
from utils.matcher import calculate_match
from utils.similarity import calculate_similarity
from utils.report_generator import generate_report
from utils.resume_parser import extract_candidate_info
from utils.charts import create_pie_chart
from utils.education_match import match_education
from utils.experience_match import match_experience
from utils.ats_score import calculate_ats_score
from utils.ai_feedback import generate_feedback
from utils.course_recommender import recommend_courses
from utils.resume_status import get_resume_status

st.set_page_config(
    page_title="AI Resume Screening System",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
<style>

/* ==========================
   Main Background
========================== */
.stApp {
    background-color: #0E1117;
    color: #FAFAFA;
}

/* ==========================
   Main Container
========================== */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* ==========================
   Metric Cards
========================== */
[data-testid="stMetric"] {
    background-color: #1C1F26;
    border: 1px solid #2E3440;
    border-radius: 15px;
    padding: 18px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
}

/* Metric Label */
[data-testid="stMetricLabel"] {
    color: #BFC7D5;
}

/* Metric Value */
[data-testid="stMetricValue"] {
    color: white;
}

/* ==========================
   File Uploader
========================== */
[data-testid="stFileUploader"] {
    background-color: #1C1F26;
    border-radius: 15px;
    border: 1px solid #2E3440;
    padding: 10px;
}

/* ==========================
   Text Area
========================== */
textarea {
    background-color: #1C1F26 !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid #2E3440 !important;
}

/* ==========================
   Buttons
========================== */
.stButton > button,
.stDownloadButton > button {
    width: 100%;
    border-radius: 10px;
    background-color: #2563EB;
    color: white;
    font-weight: bold;
    border: none;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background-color: #1D4ED8;
}

/* ==========================
   Expanders
========================== */
.streamlit-expanderHeader {
    font-size: 18px;
    font-weight: 600;
    color: white;
}

/* ==========================
   Headers
========================== */
h1, h2, h3, h4, h5 {
    color: white;
}

/* ==========================
   Horizontal Line
========================== */
hr {
    margin-top: 25px;
    margin-bottom: 25px;
    border: 1px solid #2E3440;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style='text-align:center;color:#2563EB;'>
📄 AI Resume Screening System
</h1>

<h4 style='text-align:center;color:gray;'>
Smart Resume Analysis using AI & ATS Scoring
</h4>
""", unsafe_allow_html=True)

st.markdown("---")

uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf", "docx"]
)

if uploaded_file:

    # Read Resume
    if uploaded_file.name.lower().endswith(".pdf"):
        text = read_pdf(uploaded_file)
    else:
        text = read_docx(uploaded_file)

    st.subheader("Extracted Resume Text")
    st.write(text)

    candidate = extract_candidate_info(text)

    job_description = st.text_area(
        "Paste Job Description",
        height=200
    )

    if st.button("Analyze Resume"):

        if job_description.strip() == "":
            st.warning("Please paste a Job Description.")
            st.stop()

        # Extract Skills
        resume_skills = extract_skills(text)
        
        # Extract JD skills
        # Uses explicit skills first, then role-based skills if no explicit skills are found
        jd_skills = extract_jd_skills(job_description)

        # Calculate Match
        match, matched, missing = calculate_match(
            resume_skills,
            jd_skills
        )
        education_status, resume_education, jd_education = match_education(
            text,
            job_description
        )
        experience_status, resume_exp, jd_exp = match_experience(
            text,
            job_description
        )
        ats_score, ats_rating, ats_breakdown, project_count, certificate_count = calculate_ats_score(
            match,
            education_status,
            experience_status,
            text
        )
        resume_status, resume_message = get_resume_status(
        ats_score
        )
        feedback = generate_feedback(
            ats_score,
            match,
            education_status,
            experience_status,
            missing
        )

        recommendations = recommend_courses(missing)
        # Calculate Similarity
        similarity = calculate_similarity(
            text,
            job_description
        )

        # Recommendation
        

        if matched and not missing:
            recommendation = ( "Excellent! Your resume matches the identified requirements in the job description." )

        elif matched and missing:
            recommendation = ("Your resume partially matches the job description. Consider improving the following missing skills: "+ ", ".join(missing))

        elif not matched and missing:
            recommendation = ("Your resume does not currently match the identified skills in the job description. Consider developing: "+ ", ".join(missing))

        else:
            recommendation = ("No specific skills were identified for comparison in the job description. A skill-based match cannot be determined from the available requirements.")
            


        # Dashboard Metrics


        st.markdown("## 📊 Resume Analysis Dashboard")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="📊 Match %",
                value=f"{match}%"
            )

        with col2:
            st.metric(
                label="📄 Similarity",
                value=f"{similarity}%"
            )

        with col3:
            st.metric(
                label="⭐ ATS Score",
                value=f"{ats_score}/100"
            )

        if ats_score >= 90:
            st.success(f"🏆 ATS Rating: {ats_rating}")

        elif ats_score >= 75:
            st.info(f"✅ ATS Rating: {ats_rating}")

        elif ats_score >= 60:
            st.warning(f"⚠ ATS Rating: {ats_rating}")

        else:
            st.error(f"❌ ATS Rating: {ats_rating}")

        st.markdown("---")
        #Match Progress
        st.subheader("📈 Overall Compatibility")

        st.progress(match / 100)

        st.write(f"**Overall Match:** {match}%")

        # Candidate Information

        st.markdown("## 👤 Candidate Information")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Name:** {candidate['name']}")
            st.write(f"**Email:** {candidate['email']}")
            st.write(f"**Phone:** {candidate['phone']}")

        with col2:
            st.write(f"**LinkedIn:** {candidate['linkedin']}")
            st.write(f"**GitHub:** {candidate['github']}")
        # Education Match
        st.markdown("## 🎓 Education Match")

        if education_status == "Matched":
            st.success("Matched")

        elif education_status == "Partially Matched":
            st.warning("Partially Matched")

        elif education_status == "Not Matched":
            st.error("Not Matched")

        else:
            st.info("Requirement Not Specified")

        #Experience match
        st.markdown("## 💼 Experience Match")

        if experience_status == "Matched":
            st.success("Matched")

        elif experience_status == "Partially Matched":
            st.warning("Partially Matched")

        elif experience_status == "Not Matched":
            st.error("Not Matched")

        else:
            st.info("Requirement Not Specified")

        # Resume Status

        st.markdown("## 📝 Resume Status")

        if ats_score >= 90:

            st.success("🟢 Excellent Resume")

        elif ats_score >= 75:

            st.info("🔵 Good Resume")

        elif ats_score >= 60:

            st.warning("🟡 Average Resume")

        else:

            st.error("🔴 Needs Improvement")

        # Skills + Chart

        left, right = st.columns([2, 1])

        with left:

            skill_col1, skill_col2 = st.columns(2)
        
            with skill_col1:
        
                st.subheader("✅ Matched Skills")
        
                if matched:
        
                    matched_html = "".join(
                        f"<div style='margin-bottom:6px;'>✔️ {skill}</div>"
                        for skill in matched
                    )
        
                    st.markdown(
                        f"""
                        <div style="
                            max-height: 140px;
                            overflow-y: auto;
                            padding: 10px 14px;
                            border: 1px solid #ddd;
                            border-radius: 8px;
                        ">
                            {matched_html}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
                else:
                    st.info("No Matched Skills")
        
        
            with skill_col2:
        
                st.subheader("❌ Missing Skills")
        
                if missing:
        
                    missing_html = "".join(
                        f"<div style='margin-bottom:6px;'>❌ {skill}</div>"
                        for skill in missing
                    )
        
                    st.markdown(
                        f"""
                        <div style="
                            max-height: 140px;
                            overflow-y: auto;
                            padding: 10px 14px;
                            border: 1px solid #ddd;
                            border-radius: 8px;
                        ">
                            {missing_html}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
                else:
                    st.success("No Missing Skills")
        
        
            st.subheader("💡 Recommendation")
            st.info(recommendation)

        with right:

            st.markdown("## 📊 Skill Distribution")
        
            if matched or missing:
                chart = create_pie_chart(matched, missing)
        
                st.pyplot(
                    chart,
                    use_container_width=True
                )
            else:
                st.info("No skill data available.")
        
        st.markdown("---")

       
        # AI Feedback Summary


        st.markdown("## Resume Insights")

        for item in feedback:
            st.write(item)

        st.markdown("---")

        # Detailed ATS Analysis


        with st.expander("📂 View Detailed ATS Analysis"):

            st.subheader("ATS Score Breakdown")

            max_marks = {
                "Skills": 40,
                "Education": 15,
                "Experience": 15,
                "Projects": 10,
                "Certifications": 10,
                "Formatting": 10
            }

            for category, marks in ats_breakdown.items():

                st.write(f"**{category}: {marks}/{max_marks[category]}**")

                st.progress(marks / max_marks[category])

            st.markdown("---")

            st.subheader("Resume Statistics")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Projects", project_count)

            with col2:
                st.metric("Certifications", certificate_count)

            st.markdown("---")

            st.subheader("Education Details")

            st.write("**Required Education:**")

            if jd_education:
                for edu in jd_education:
                    st.write(f"• {edu}")
            else:
                st.write("Not Mentioned")

            st.write("**Resume Education:**")

            if resume_education:
                for edu in resume_education:
                    st.write(f"• {edu}")
            else:
                st.write("Not Found")

            st.write(f"**Status:** {education_status}")

            st.subheader("Experience Details")

            st.write("**Required Experience:**")

            if experience_status == "Not Specified":
                st.write("Fresher / Not Specified")
            else:
                st.write(jd_exp["text"])

            st.write("**Resume Experience:**")

            if resume_exp["internship"]:
                st.write("Internship Found")

            st.write(resume_exp["text"])

            st.write(f"**Years of Experience:** {resume_exp['years']}")

            st.write(f"**Status:** {experience_status}")
            st.subheader("Free Learning Resources")

            if recommendations:

                for item in recommendations:

                    st.markdown(f"### {item['skill']}")

                    st.write(f"Course: {item['course']}")

                    st.write(f"Free Certification: {item['certificate']}")

                    st.markdown("---")

            else:

                st.success("No learning recommendations required.")

        # Generate PDF
        report_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "resume_report.pdf"
        )

        generate_report(
            report_path,
            candidate,
            match,
            similarity,
            ats_score,
            ats_rating,
            ats_breakdown,
            matched,
            missing,
            recommendation,
            education_status,
            experience_status,
            project_count,
            certificate_count,
            feedback,
            recommendations
        )
        with open(report_path, "rb") as pdf:
            st.download_button(
                "Download Report",
                pdf,
                file_name="Resume_Report.pdf",
                mime="application/pdf"
            )
st.markdown("---")

st.markdown(
    """
    <div style='text-align:center;color:gray;font-size:14px'>
        © 2026 AI Resume Screening System • Developed with Python, Streamlit & Machine Learning
    </div>
    """,
    unsafe_allow_html=True
)
        
