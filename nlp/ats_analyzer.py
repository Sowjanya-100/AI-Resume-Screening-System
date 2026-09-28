import re


# Common resume sections
SECTION_NAMES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "career objective",
        "objective",
        "about me"
    ],

    "education": [
        "education",
        "academic qualification",
        "academic qualifications",
        "educational qualification",
        "educational qualifications",
        "academic background"
    ],

    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "key skills",
        "technical competencies",
        "core competencies",
        "competencies",
        "soft skills"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "internship experience",
        "internship",
        "internships"
    ],

    "projects": [
        "projects",
        "project",
        "academic projects",
        "personal projects",
        "technical projects",
        "project experience"
    ],

    "certifications": [
        "certifications",
        "certification",
        "certificates",
        "professional certifications",
        "licenses and certifications"
    ],

    "achievements": [
        "achievements",
        "accomplishments",
        "awards",
        "honors",
        "honours"
    ],

    "languages": [
        "languages",
        "language",
        "language skills"
    ]
}


def normalize_text(text):
    """Normalize resume text for analysis."""

    if not text:
        return ""

    text = text.lower()

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def find_sections(text):
    """Detect common resume sections."""

    text = normalize_text(text)

    detected = {}

    for section, names in SECTION_NAMES.items():

        for name in names:

            if name in text:

                detected[section] = True
                break

    return detected


def check_contact_information(text):
    """Check whether basic contact information exists."""

    text = normalize_text(text)

    email_found = bool(
        re.search(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            text
        )
    )

    phone_found = bool(
        re.search(
            r"\b\d{10}\b",
            text
        )
    )

    return {
        "email": email_found,
        "phone": phone_found
    }


def calculate_ats_score(text, sections):
    """
    Calculate an initial ATS score.

    This is the first version.
    We will improve the scoring logic later.
    """

    score = 0

    # Contact information
    contact = check_contact_information(text)

    if contact["email"]:
        score += 5

    if contact["phone"]:
        score += 5


    # Important resume sections

    if sections.get("summary"):
        score += 10

    if sections.get("education"):
        score += 15

    if sections.get("skills"):
        score += 20

    if sections.get("experience"):
        score += 15

    if sections.get("projects"):
        score += 10

    if sections.get("certifications"):
        score += 10

    if sections.get("achievements"):
        score += 5


    # Maximum score
    score = min(score, 100)

    return score


def get_score_status(score):

    if score >= 80:
        return "Excellent"

    elif score >= 60:
        return "Good"

    elif score >= 40:
        return "Average"

    else:
        return "Needs Improvement"


def analyze_resume(text):

    sections = find_sections(text)

    contact = check_contact_information(text)

    score = calculate_ats_score(
        text,
        sections
    )

    status = get_score_status(score)

    return {
        "ats_score": score,
        "status": status,
        "sections": sections,
        "contact": contact
    }