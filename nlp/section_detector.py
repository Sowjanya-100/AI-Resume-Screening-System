import re


# Different headings that can represent the same resume section
SECTION_ALIASES = {

    "summary": [
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "career summary",
        "career objective",
        "objective",
        "objectives",
        "career profile",
        "about me"
    ],

    "education": [
        "education",
        "academic qualification",
        "academic qualifications",
        "educational qualification",
        "educational qualifications",
        "academic background",
        "educational background",
        "academic history"
    ],

    "skills": [
        "skills",
        "technical skills",
        "technical skill",
        "core skills",
        "key skills",
        "technical competencies",
        "core competencies",
        "competencies",
        "technical expertise",
        "soft skills",
        "soft skill",
        "professional skills",
        "areas of expertise",
        "areas of expertise"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "internship experience",
        "internship",
        "internships",
        "professional background"
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
    ],

    "activities": [
        "activities",
        "extracurricular activities",
        "extra curricular activities",
        "co-curricular activities",
        "volunteer experience",
        "volunteering"
    ]
}


def normalize_heading(text):
    """
    Normalize a possible section heading.
    """

    text = text.lower().strip()

    # Remove common punctuation
    text = re.sub(r"[:\-–—|]+$", "", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def detect_section_heading(line):
    """
    Check whether a line matches one of our known
    resume section headings.
    """

    normalized_line = normalize_heading(line)

    for section, aliases in SECTION_ALIASES.items():

        for alias in aliases:

            if normalized_line == alias:
                return section

    return None


def detect_sections(text):
    """
    Detect sections from cleaned resume text.

    Returns a dictionary containing the detected
    sections and their text.
    """

    lines = text.split("\n")

    sections = {}
    current_section = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        detected_section = detect_section_heading(line)

        if detected_section:

            current_section = detected_section

            if current_section not in sections:
                sections[current_section] = []

            continue

        if current_section:
            sections[current_section].append(line)

    # Convert lists into strings
    for section in sections:
        sections[section] = "\n".join(sections[section])

    return sections
