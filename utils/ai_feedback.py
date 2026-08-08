def generate_feedback(
    ats_score,
    match_percentage,
    education_status,
    experience_status,
    missing_skills
):

    feedback = []

    # ATS Score
    if ats_score >= 90:
        feedback.append(
            "Excellent ATS score. Your resume is highly optimized for this job."
        )

    elif ats_score >= 75:
        feedback.append(
            "Good ATS score. A few improvements can further strengthen your resume."
        )

    elif ats_score >= 60:
        feedback.append(
            "Your ATS score is average. Improving missing skills will increase your chances."
        )

    else:
        feedback.append(
            "Your ATS score is low. Consider improving your resume before applying."
        )

    # Match Percentage
    if match_percentage >= 80:
        feedback.append(
            "Your skills closely match the job description."
        )

    elif match_percentage >= 60:
        feedback.append(
            "Your resume partially matches the required skills."
        )

    else:
        feedback.append(
            "Many required skills are missing."
        )

    # Education
    if education_status == "Matched":
        feedback.append(
            "Your educational qualifications meet the job requirements."
        )

    elif education_status == "Partially Matched":
        feedback.append(
            "Your education partially matches the job requirements."
        )

    else:
        feedback.append(
            "Your educational qualifications do not fully match the job requirements."
        )

    # Experience
    if experience_status == "Matched":
        feedback.append(
            "Your experience matches the job requirements."
        )

    elif experience_status == "Partially Matched":
        feedback.append(
            "Internship experience is relevant but additional experience may help."
        )

    else:
        feedback.append(
            "Your experience does not fully meet the job requirements."
        )

    # Missing Skills
    if missing_skills:
        feedback.append(
            "Recommended Skills to Learn: " + ", ".join(missing_skills)
        )

    else:
        feedback.append(
            "Great! No important skills are missing."
        )

    # Final Summary
    if ats_score >= 85:
        feedback.append(
            "Overall, your resume is ready for applying to this role."
        )

    else:
        feedback.append(
            "Improve the suggested areas to increase your interview chances."
        )

    return feedback