"""
structure_checker.py
--------------------

Dynamic resume structure and contact information checker.

Designed to work with different resume formats and different
resume types, including:

- Freshers
- Students
- Experienced professionals
- Technical resumes
- Data/Analytics resumes
- Cloud resumes
- Software development resumes

The checker does NOT assume that every resume must contain
every possible section.

Only essential resume sections affect the section completeness
score. Optional sections such as Publications, Interests,
Languages, Activities, and Achievements do not reduce the score.
"""

import re
from dataclasses import dataclass, field

from rapidfuzz import fuzz


# ============================================================
# SECTION PATTERNS
# ============================================================

SECTION_PATTERNS = {

    # --------------------------------------------------------
    # Professional Summary
    # --------------------------------------------------------

    "summary": re.compile(
        r"""
        ^\s*
        (?:
            professional\s+summary |
            career\s+summary |
            summary |
            profile |
            professional\s+profile |
            career\s+profile |
            about\s+me |
            about
        )
        \s*[:\-]?\s*$
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE
    ),

    # --------------------------------------------------------
    # Career Objective
    # --------------------------------------------------------

    "objective": re.compile(
        r"""
        ^\s*
        (?:
            career\s+objective |
            objective |
            career\s+goal |
            professional\s+objective
        )
        \s*[:\-]?\s*$
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE
    ),

    # --------------------------------------------------------
    # Work Experience
    # --------------------------------------------------------

    "experience": re.compile(
        r"""
        ^\s*
        (?:
            work\s+experience |
            professional\s+experience |
            employment\s+history |
            employment |
            career\s+history |
            work\s+history |
            professional\s+background |
            experience
        )
        \s*[:\-]?\s*$
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE
    ),

    # --------------------------------------------------------
    # Internship
    # --------------------------------------------------------

    "internships": re.compile(
        r"""
        ^\s*
        (?:
            internships? |
            internship\s+experience |
            industrial\s+training |
            training\s+experience
        )
        \s*[:\-]?\s*$
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE
    ),

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    "education": re.compile(
        r"""
        ^\s*
        (?:
            education |
            educational\s+background |
            academic\s+background |
            academic\s+qualification(?:s)? |
            educational\s+qualification(?:s)? |
            academic\s+history
        )
        \s*[:\-]?\s*$
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE
    ),

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    "skills": re.compile(
        r"""
        ^\s*
        (?:
            skills |
            technical\s+skills |
            core\s+skills |
            key\s+skills |
            technical\s+expertise |
            core\s+competencies |
            technical\s+competencies |
            competencies |
            areas\s+of\s+expertise |
            skills\s+summary |
            professional\s+skills
        )
        \s*[:\-]?\s*$
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE
    ),

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    "projects": re.compile(
        r"""
        ^\s*
        (?:
            projects |
            academic\s+projects |
            personal\s+projects |
            technical\s+projects |
            major\s+projects |
            selected\s+projects |
            project\s+experience
        )
        \s*[:\-]?\s*$
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE
    ),

    # --------------------------------------------------------
    # Certifications
    # --------------------------------------------------------

    "certifications": re.compile(
        r"""
        ^\s*
        (?:
            certifications? |
            professional\s+certifications? |
            certificates? |
            licenses?\s+and\s+certifications? |
            certifications?\s+and\s+training
        )
        \s*[:\-]?\s*$
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE
    ),

    # --------------------------------------------------------
    # Achievements
    # --------------------------------------------------------

    "achievements": re.compile(
        r"""
        ^\s*
        (?:
            achievements? |
            accomplishments? |
            awards?\s+and\s+achievements? |
            honors?\s+and\s+awards? |
            awards?
        )
        \s*[:\-]?\s*$
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE
    ),

    # --------------------------------------------------------
    # Activities
    # --------------------------------------------------------

    "activities": re.compile(
        r"""
        ^\s*
        (?:
            activities |
            extracurricular\s+activities |
            extra[-\s]?curricular\s+activities |
            leadership\s+activities |
            volunteer\s+activities |
            co[-\s]?curricular\s+activities
        )
        \s*[:\-]?\s*$
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE
    ),

    # --------------------------------------------------------
    # Publications
    # --------------------------------------------------------

    "publications": re.compile(
        r"""
        ^\s*
        (?:
            publications? |
            research\s+publications? |
            papers? |
            research\s+papers?
        )
        \s*[:\-]?\s*$
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE
    ),

    # --------------------------------------------------------
    # Languages
    # --------------------------------------------------------

    "languages": re.compile(
        r"""
        ^\s*
        (?:
            languages |
            language\s+skills |
            linguistic\s+skills
        )
        \s*[:\-]?\s*$
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE
    ),

    # --------------------------------------------------------
    # Interests
    # --------------------------------------------------------

    "interests": re.compile(
        r"""
        ^\s*
        (?:
            interests? |
            hobbies? |
            hobbies?\s+and\s+interests?
        )
        \s*[:\-]?\s*$
        """,
        re.IGNORECASE | re.VERBOSE | re.MULTILINE
    ),
}


# ============================================================
# CONTACT INFORMATION
# ============================================================

EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+\."
    r"[A-Za-z]{2,}\b"
)


PHONE_RE = re.compile(
    r"""
    (?:
        \+?\d{1,3}[\s.-]?
    )?
    (?:
        \(?\d{2,4}\)?[\s.-]?
    )?
    \d{3,4}[\s.-]?\d{3,4}
    """,
    re.IGNORECASE | re.VERBOSE
)


LINKEDIN_RE = re.compile(
    r"""
    (?:
        https?://
    )?
    (?:
        www\.
    )?
    linkedin\.com/
    [A-Za-z0-9_./%-]+
    """,
    re.IGNORECASE | re.VERBOSE
)


# ============================================================
# DATE DETECTION
# ============================================================

MONTH_PATTERN = (
    r"(?:"
    r"Jan(?:uary)?|"
    r"Feb(?:ruary)?|"
    r"Mar(?:ch)?|"
    r"Apr(?:il)?|"
    r"May|"
    r"Jun(?:e)?|"
    r"Jul(?:y)?|"
    r"Aug(?:ust)?|"
    r"Sep(?:tember)?|"
    r"Oct(?:ober)?|"
    r"Nov(?:ember)?|"
    r"Dec(?:ember)?"
    r")"
)


DATE_RANGE_RE = re.compile(
    rf"""
    (?:
        # Month Year - Month Year
        {MONTH_PATTERN}
        \s+\d{{4}}
        \s*(?:-|–|—|\||to)\s*
        (?:
            {MONTH_PATTERN}\s+\d{{4}} |
            Present |
            Current
        )

        |

        # Year - Year / Present
        \d{{4}}
        \s*(?:-|–|—|\||to)
        (?:\d{{4}}|Present|Current)

        |

        # Month Year
        {MONTH_PATTERN}
        \s+\d{{4}}

        |

        # Numeric month/year
        \d{{1,2}}[/-]\d{{4}}

        |

        # Year only
        \b\d{{4}}\b
    )
    """,
    re.IGNORECASE | re.VERBOSE
)


# ============================================================
# RESULT DATACLASS
# ============================================================

@dataclass
class StructureCheckResult:

    # Overall section score
    section_completeness_score: float = 0.0

    # All detected sections
    sections_found: dict = field(default_factory=dict)

    # Important missing sections
    missing_sections: list = field(default_factory=list)

    # Optional sections that are absent
    #
    # Kept for compatibility with the existing application,
    # but these sections DO NOT affect the ATS score and DO NOT
    # generate warnings.
    optional_missing_sections: list = field(default_factory=list)

    # Contact information
    has_email: bool = False
    has_phone: bool = False
    has_linkedin: bool = False

    contact_score: float = 0.0

    # Dates
    date_parse_score: float = 0.0
    date_ranges_found: list = field(default_factory=list)

    # Job title similarity
    title_similarity: float = 1.0

    # Warnings
    warnings: list = field(default_factory=list)


# ============================================================
# SECTION HEADING NORMALIZATION
# ============================================================

def _prepare_text(text: str) -> str:

    """
    Normalize line endings and whitespace while preserving
    individual lines so section headings can be detected.
    """

    text = text or ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    lines = []

    for line in text.split("\n"):

        line = re.sub(
            r"[ \t]+",
            " ",
            line
        ).strip()

        lines.append(line)

    return "\n".join(lines)


# ============================================================
# SECTION DETECTION
# ============================================================

def _detect_sections(text: str) -> dict:

    """
    Detect common resume sections.

    Section patterns are anchored to lines so that a sentence
    such as:

        "Experience with Python and SQL"

    is NOT incorrectly interpreted as an Experience section.
    """

    sections = {}

    for section_name, pattern in SECTION_PATTERNS.items():

        sections[section_name] = bool(
            pattern.search(text)
        )

    # --------------------------------------------------------
    # Summary and Objective are considered the same category
    # --------------------------------------------------------

    if sections["summary"] or sections["objective"]:

        sections["summary"] = True

    return sections


# ============================================================
# SECTION SCORE
# ============================================================

def _calculate_section_score(
    sections: dict
) -> float:

    """
    Calculate section completeness using only essential
    resume sections.

    Essential sections:
        1. Education
        2. Skills
        3. At least one of:
           - Experience
           - Internships
           - Projects

    Optional sections do NOT affect the score:
        - Summary / Objective
        - Certifications
        - Achievements
        - Activities
        - Publications
        - Languages
        - Interests

    Scoring:
        Education              = 35%
        Skills                 = 35%
        Career content         = 30%

    Therefore, a resume with all three essential areas
    detected receives 100% section completeness.
    """

    score = 0.0

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    if sections.get("education", False):

        score += 0.35

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    if sections.get("skills", False):

        score += 0.35

    # --------------------------------------------------------
    # Career / practical content
    #
    # A fresher may have:
    # - Projects
    # - Internships
    #
    # An experienced candidate may have:
    # - Experience
    #
    # Only one of these is required.
    # --------------------------------------------------------

    career_content = any(
        sections.get(section, False)
        for section in (
            "experience",
            "projects",
            "internships",
        )
    )

    if career_content:

        score += 0.30

    return round(
        min(score, 1.0),
        4
    )


# ============================================================
# DETERMINE MISSING IMPORTANT SECTIONS
# ============================================================

def _get_missing_sections(
    sections: dict
) -> tuple:

    """
    Determine only the genuinely important missing sections.

    Optional sections are intentionally separated and are NOT
    treated as problems.
    """

    missing_important = []

    optional_missing = []

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    if not sections.get("education", False):

        missing_important.append(
            "education"
        )

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    if not sections.get("skills", False):

        missing_important.append(
            "skills"
        )

    # --------------------------------------------------------
    # Experience / Projects / Internships
    #
    # At least ONE is required.
    # --------------------------------------------------------

    has_career_content = any(
        sections.get(section, False)
        for section in (
            "experience",
            "projects",
            "internships",
        )
    )

    if not has_career_content:

        missing_important.append(
            "experience or projects or internships"
        )

    # --------------------------------------------------------
    # Optional sections
    #
    # These are recorded only for compatibility with the
    # existing application.
    #
    # They DO NOT affect ATS score.
    # They DO NOT create warnings.
    # --------------------------------------------------------

    optional_sections = [
        "summary",
        "certifications",
        "achievements",
        "activities",
        "publications",
        "languages",
        "interests",
    ]

    for section in optional_sections:

        if section == "summary":

            detected = sections.get(
                "summary",
                False
            )

        else:

            detected = sections.get(
                section,
                False
            )

        if not detected:

            optional_missing.append(
                section
            )

    return (
        missing_important,
        optional_missing
    )


# ============================================================
# CONTACT VALIDATION
# ============================================================

def _check_contact_information(
    text: str,
    result: StructureCheckResult
) -> None:

    """
    Detect email, phone and LinkedIn.
    """

    result.has_email = bool(
        EMAIL_RE.search(text)
    )

    result.has_phone = bool(
        PHONE_RE.search(text)
    )

    result.has_linkedin = bool(
        LINKEDIN_RE.search(text)
    )

    contact_points = 0

    if result.has_email:

        contact_points += 1

    if result.has_phone:

        contact_points += 1

    if result.has_linkedin:

        contact_points += 1

    result.contact_score = round(
        contact_points / 3,
        4
    )


# ============================================================
# DATE DETECTION
# ============================================================

def _check_dates(
    text: str,
    result: StructureCheckResult
) -> None:

    """
    Detect date information.

    Multiple date formats are supported.
    """

    matches = DATE_RANGE_RE.findall(text)

    normalized_dates = []

    for match in matches:

        if isinstance(match, tuple):

            values = [
                value
                for value in match
                if value
            ]

            if values:

                normalized_dates.append(
                    " ".join(values)
                )

        else:

            normalized_dates.append(
                match
            )

    # Remove duplicates
    result.date_ranges_found = list(
        dict.fromkeys(
            normalized_dates
        )
    )

    date_count = len(
        result.date_ranges_found
    )

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    if date_count >= 2:

        result.date_parse_score = 1.0

    elif date_count == 1:

        result.date_parse_score = 0.5

    else:

        result.date_parse_score = 0.0


# ============================================================
# TITLE SIMILARITY
# ============================================================

def _calculate_title_similarity(
    text: str,
    target_title: str
) -> float:

    """
    Compare a target job title with the resume text.

    ATS-only analysis passes an empty target title, so no
    penalty is applied in that situation.
    """

    if not target_title.strip():

        return 1.0

    resume_text_lower = text.lower()

    target_title_lower = (
        target_title
        .lower()
        .strip()
    )

    if not resume_text_lower:

        return 0.0

    similarity = fuzz.partial_ratio(
        target_title_lower,
        resume_text_lower
    )

    return round(
        similarity / 100,
        4
    )


# ============================================================
# WARNING GENERATION
# ============================================================

def _generate_section_warnings(
    result: StructureCheckResult
) -> None:

    """
    Generate warnings ONLY for important missing sections.

    Optional sections such as Publications, Languages,
    Interests, Activities, Achievements, Certifications,
    and Summary/Objective do NOT generate warnings.
    """

    for section in result.missing_sections:

        result.warnings.append(
            f"Missing or unrecognized important section: "
            f"{section}. Use a clear ATS-friendly heading."
        )


# ============================================================
# MAIN STRUCTURE CHECKER
# ============================================================

def check_structure(
    resume_text: str,
    target_title: str = ""
) -> StructureCheckResult:

    """
    Analyze resume structure dynamically.

    Parameters
    ----------
    resume_text:
        Extracted resume text.

    target_title:
        Optional job title used for title similarity.

    Returns
    -------
    StructureCheckResult
    """

    result = StructureCheckResult()

    # --------------------------------------------------------
    # Prepare text
    # --------------------------------------------------------

    text = _prepare_text(
        resume_text
    )

    # --------------------------------------------------------
    # Section detection
    # --------------------------------------------------------

    result.sections_found = _detect_sections(
        text
    )

    # --------------------------------------------------------
    # Section score
    # --------------------------------------------------------

    result.section_completeness_score = (
        _calculate_section_score(
            result.sections_found
        )
    )

    # --------------------------------------------------------
    # Missing sections
    # --------------------------------------------------------

    (
        result.missing_sections,
        result.optional_missing_sections
    ) = _get_missing_sections(
        result.sections_found
    )

    # --------------------------------------------------------
    # Contact information
    # --------------------------------------------------------

    _check_contact_information(
        text,
        result
    )

    # --------------------------------------------------------
    # Date information
    # --------------------------------------------------------

    _check_dates(
        text,
        result
    )

    # --------------------------------------------------------
    # Job title similarity
    # --------------------------------------------------------

    result.title_similarity = (
        _calculate_title_similarity(
            text,
            target_title
        )
    )

    # --------------------------------------------------------
    # Generate warnings
    # --------------------------------------------------------

    _generate_section_warnings(
        result
    )

    return result