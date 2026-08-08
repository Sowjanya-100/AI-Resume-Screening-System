def get_resume_status(ats_score):

    if ats_score >= 90:
        return (
            "Excellent",
            "Your resume is highly suitable for this job. Ready to apply."
        )

    elif ats_score >= 75:
        return (
            "Good",
            "Your resume is a good match. Minor improvements are recommended."
        )

    elif ats_score >= 60:
        return (
            "Average",
            "Your resume is partially suitable. Improve the missing skills."
        )

    else:
        return (
            "Needs Improvement",
            "Your resume requires significant improvements before applying."
        )