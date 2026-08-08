def calculate_match(resume_skills, jd_skills):

    resume = set(skill.lower() for skill in resume_skills)
    job = set(skill.lower() for skill in jd_skills)

    matched = sorted(resume & job)
    missing = sorted(job - resume)

    if len(job) == 0:
        percentage = 0
    else:
        percentage = round(len(matched) / len(job) * 100)

    return percentage, matched, missing