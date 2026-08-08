import re


def extract_experience(text):

    text = text.lower()

    # Detect Fresher
    if "fresher" in text:
        return {
            "years": 0,
            "internship": False,
            "text": "Fresher"
        }

    # Detect Internship
    internship = (
        "internship" in text or
        "intern" in text or
        "training" in text
    )

    # Detect Years
    year_match = re.search(r'(\d+)\+?\s*(year|years)', text)

    if year_match:
        years = int(year_match.group(1))
    else:
        years = 0

    # Detect Months
    month_match = re.search(r'(\d+)\s*(month|months)', text)

    months = 0

    if month_match:
        months = int(month_match.group(1))

        if months >= 12:
            years = months // 12

    return {
        "years": years,
        "internship": internship,
        "text": f"{years} Year(s)"
    }


def match_experience(resume_text, jd_text):

    resume = extract_experience(resume_text)
    jd = extract_experience(jd_text)

    # Job Description doesn't mention experience
    if jd["years"] == 0 and not jd["internship"]:

        return (
            "Not Specified",
            resume,
            jd
        )

    # Fresher Job
    if jd["years"] == 0:

        if resume["internship"] or resume["years"] == 0:

            return (
                "Matched",
                resume,
                jd
            )

        else:

            return (
                "Matched",
                resume,
                jd
            )

    # Exact Match
    if resume["years"] >= jd["years"]:

        return (
            "Matched",
            resume,
            jd
        )

    # Internship but fewer years
    if resume["internship"]:

        return (
            "Partially Matched",
            resume,
            jd
        )

    return (
        "Not Matched",
        resume,
        jd
    )