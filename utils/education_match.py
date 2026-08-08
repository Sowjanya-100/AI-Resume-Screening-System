import re

def extract_education(text):

    text = text.lower()

    education_keywords = [
        "b.tech",
        "btech",
        "b.e",
        "be",
        "bachelor",
        "m.tech",
        "mtech",
        "m.e",
        "me",
        "master",
        "computer science",
        "information technology",
        "electronics",
        "mechanical",
        "civil"
    ]

    found = []

    for keyword in education_keywords:
        if keyword in text:
            found.append(keyword.title())

    return found


def match_education(resume_text, jd_text):

    resume_education = extract_education(resume_text)
    jd_education = extract_education(jd_text)

    matched = []
    missing = []

    for edu in jd_education:
        if edu in resume_education:
            matched.append(edu)
        else:
            missing.append(edu)

    if len(jd_education) == 0:
        status = "Not Specified"

    elif len(missing) == 0:
        status = "Matched"

    elif len(matched) > 0:
        status = "Partially Matched"

    else:
        status = "Not Matched"

    return status, resume_education, jd_education