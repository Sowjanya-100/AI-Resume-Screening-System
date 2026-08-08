from utils.resume_analyzer import (
    count_projects,
    count_certifications
)


def calculate_ats_score(
    match_percentage,
    education_status,
    experience_status,
    text
):

    score = 0
    breakdown = {}

    # ==========================
    # Skills (40 Marks)
    # ==========================

    skills_score = round((match_percentage / 100) * 40, 1)

    breakdown["Skills"] = skills_score

    score += skills_score

    # ==========================
    # Education (15 Marks)
    # ==========================

    if education_status == "Matched":
        education_score = 15

    elif education_status == "Partially Matched":
        education_score = 8

    else:
        education_score = 0

    breakdown["Education"] = education_score

    score += education_score

    # ==========================
    # Experience (15 Marks)
    # ==========================

    if experience_status == "Matched":
        experience_score = 15

    elif experience_status == "Partially Matched":
        experience_score = 8

    else:
        experience_score = 0

    breakdown["Experience"] = experience_score

    score += experience_score

    # ==========================
    # Projects (10 Marks)
    # ==========================

    project_count, project_score = count_projects(text)

    breakdown["Projects"] = project_score

    score += project_score

    # ==========================
    # Certifications (10 Marks)
    # ==========================

    certificate_count, certification_score = count_certifications(text)

    breakdown["Certifications"] = certification_score

    score += certification_score

    # ==========================
    # Resume Formatting (10 Marks)
    # ==========================

    formatting_score = 10

    if len(text) < 500:
        formatting_score = 7

    if len(text) < 300:
        formatting_score = 4

    breakdown["Formatting"] = formatting_score

    score += formatting_score

    # ==========================
    # Final Score
    # ==========================

    score = round(score)

    # ==========================
    # ATS Rating
    # ==========================

    if score >= 90:
        rating = "Excellent"

    elif score >= 75:
        rating = "Good"

    elif score >= 60:
        rating = "Average"

    else:
        rating = "Needs Improvement"

    return (
        score,
        rating,
        breakdown,
        project_count,
        certificate_count
    )