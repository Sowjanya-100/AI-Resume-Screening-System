import os
import re
import csv
from dataclasses import dataclass, field
from typing import List, Dict, Set

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKILLS_FILE = os.path.join(BASE_DIR, "skills.csv")
ROLE_SKILLS_FILE = os.path.join(BASE_DIR, "role_skills.csv")


# ---------------------------------------------------------
# DATA CLASSES
# ---------------------------------------------------------

@dataclass
class KeywordMatchResult:
    required_keywords: List[str] = field(default_factory=list)
    preferred_keywords: List[str] = field(default_factory=list)

    matched_required: List[str] = field(default_factory=list)
    missing_required: List[str] = field(default_factory=list)

    matched_preferred: List[str] = field(default_factory=list)
    missing_preferred: List[str] = field(default_factory=list)

    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)

    required_match_score: float = 0.0
    preferred_match_score: float = 0.0
    overall_keyword_score: float = 0.0

    similarity_score: float = 0.0

    detected_role: str = ""


# ---------------------------------------------------------
# LOAD SKILLS.CSV
# ---------------------------------------------------------

def load_skills() -> List[str]:
    """
    Load the official skill list from skills.csv.
    """

    skills = []

    if not os.path.exists(SKILLS_FILE):
        return skills

    try:
        with open(SKILLS_FILE, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:
                skill = row.get("Skill", "").strip()

                if skill:
                    skills.append(skill)

    except Exception:
        return []

    return skills


# ---------------------------------------------------------
# LOAD ROLE_SKILLS.CSV
# ---------------------------------------------------------

def load_role_skills() -> Dict[str, List[str]]:
    """
    Load role -> skills mapping from role_skills.csv.
    """

    role_skills = {}

    if not os.path.exists(ROLE_SKILLS_FILE):
        return role_skills

    try:
        with open(ROLE_SKILLS_FILE, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row in reader:

                role = row.get("Role", "").strip()
                skill = row.get("Skill", "").strip()

                if not role or not skill:
                    continue

                role_key = role.lower()

                if role_key not in role_skills:
                    role_skills[role_key] = []

                if skill not in role_skills[role_key]:
                    role_skills[role_key].append(skill)

    except Exception:
        return {}

    return role_skills


# Load once when the application starts
ALL_SKILLS = load_skills()
ROLE_SKILLS = load_role_skills()


# ---------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normalize text for matching.
    """

    if not text:
        return ""

    text = text.lower()

    # Replace common separators
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = text.replace("_", " ")

    # Remove extra punctuation
    text = re.sub(r"[^a-z0-9+#.\s]", " ", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill name.
    """

    skill = normalize_text(skill)

    # Common variations
    replacements = {
        "reactjs": "react",
        "nodejs": "node.js",
        "powerbi": "power bi",
        "ms excel": "excel",
        "microsoft excel": "excel",
        "postgres": "postgresql",
        "scikit learn": "scikit-learn",
        "sklearn": "scikit-learn",
        "machine learning": "machine learning",
        "natural language processing": "nlp",
    }

    return replacements.get(skill, skill)


# ---------------------------------------------------------
# SKILL ALIAS MATCHING
# ---------------------------------------------------------

SKILL_ALIASES = {
    "react.js": ["react", "reactjs", "react js"],
    "node.js": ["node", "nodejs", "node js"],
    "power bi": ["powerbi", "power bi"],
    "sql server": ["microsoft sql server", "sql server"],
    "postgresql": ["postgres", "postgresql"],
    "scikit-learn": ["sklearn", "scikit learn", "scikit-learn"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"],
    "natural language processing": [
        "natural language processing",
        "nlp"
    ],
    "data analysis": [
        "data analysis",
        "data analytics"
    ],
    "data visualization": [
        "data visualization",
        "data viz"
    ],
    "object oriented programming": [
        "object oriented programming",
        "object-oriented programming",
        "oop"
    ],
    "data structures": [
        "data structures",
        "data structure"
    ],
    "algorithms": [
        "algorithm",
        "algorithms"
    ],
    "artificial intelligence": [
        "artificial intelligence",
        "ai"
    ],
}


# ---------------------------------------------------------
# COMMON JD SKILL FALLBACKS
# ---------------------------------------------------------
# Used when a JD contains important skills that are not yet
# present in skills.csv. This keeps matching useful across
# different job roles and job-description wording.

JD_SKILL_ALIASES = {
    "sql": ["sql", "structured query language"],
    "databases": ["database", "databases", "dbms"],
    "data analysis": ["data analysis", "data analytics"],
    "business intelligence": ["business intelligence", "bi"],
    "data warehousing": ["data warehousing", "data warehouse"],
    "etl": [
        "etl",
        "extract transform load",
        "extraction transformation loading"
    ],
    "data extraction": ["data extraction", "extracting data", "extraction"],
    "data transformation": [
        "data transformation",
        "transforming data",
        "transformation"
    ],
    "data validation": ["data validation", "validate data", "validating data"],
    "quality checks": ["quality checks", "quality check", "quality assurance"],
    "testing": ["testing", "test and validate", "testing and validating"],
    "dashboards": ["dashboard", "dashboards"],
    "reporting": ["reporting", "reports", "business reports", "operational reports"],
    "data visualization": ["data visualization", "visualization", "visualisation"],
    "documentation": ["documentation", "documenting"],
    "business requirements": [
        "business requirements",
        "client requirements",
        "requirements"
    ],
    "client interaction": [
        "client interaction",
        "client interactions",
        "client relationships"
    ],
    "communication": [
        "communication",
        "written communication",
        "oral communication",
        "verbal communication"
    ],
    "interpersonal skills": ["interpersonal skills", "interpersonal"],
    "attention to detail": ["attention to detail"],
    "organization": ["organized", "organised", "well organized", "well organised"],
    "time management": ["meet deadlines", "time management", "on time"],
    "problem solving": ["problem solving", "problem-solving"],
    "initiative": ["initiative", "takes initiative"],
    "ownership": ["ownership", "take ownership"],
}



# ---------------------------------------------------------
# PHRASE MATCHING
# ---------------------------------------------------------

def contains_skill(text: str, skill: str) -> bool:
    """
    Check whether a skill occurs in text.
    """

    normalized_text = normalize_text(text)
    normalized_skill = normalize_skill(skill)

    if not normalized_skill:
        return False

    # Check aliases
    aliases = SKILL_ALIASES.get(skill.lower(), [])

    candidates = [normalized_skill]

    for alias in aliases:
        candidates.append(normalize_skill(alias))

    for candidate in candidates:

        if not candidate:
            continue

        # Word boundary matching
        pattern = r"(?<!\w)" + re.escape(candidate) + r"(?!\w)"

        if re.search(pattern, normalized_text):
            return True

    return False


# ---------------------------------------------------------
# EXTRACT SKILLS FROM TEXT
# ---------------------------------------------------------

def extract_skills(text: str) -> List[str]:
    """
    Find skills from skills.csv that appear in the text.
    """

    if not text:
        return []

    found = []

    for skill in ALL_SKILLS:

        if contains_skill(text, skill):

            if skill not in found:
                found.append(skill)

    return found


# ---------------------------------------------------------
# DETECT ROLE
# ---------------------------------------------------------

def detect_role(text: str) -> str:
    """
    Detect a job role using role_skills.csv.

    Role names are treated separately from skills.
    Therefore 'Data Analyst' will NOT become a skill.
    """

    if not text:
        return ""

    normalized_text = normalize_text(text)

    detected_roles = []

    for role_key in ROLE_SKILLS.keys():

        role_words = role_key.replace("-", " ")

        pattern = r"(?<!\w)" + re.escape(role_words) + r"(?!\w)"

        if re.search(pattern, normalized_text):

            detected_roles.append(role_key)

    if not detected_roles:
        return ""

    # Prefer the longest matching role
    detected_roles.sort(key=len, reverse=True)

    detected = detected_roles[0]

    # Return original-style capitalization
    for role in ROLE_SKILLS.keys():

        if role == detected:
            return role.title()

    return detected.title()


# ---------------------------------------------------------
# REQUIRED / PREFERRED SECTION EXTRACTION
# ---------------------------------------------------------

def extract_requirement_sections(jd_text: str):
    """
    Separate required and preferred sections of the JD.
    """

    normalized = normalize_text(jd_text)

    required_text = ""
    preferred_text = ""

    required_markers = [
        "required skills",
        "required qualifications",
        "required",
        "must have",
        "must have skills",
        "essential skills",
        "essential qualifications"
    ]

    preferred_markers = [
        "preferred skills",
        "preferred qualifications",
        "preferred",
        "nice to have",
        "good to have",
        "desired skills",
        "bonus skills"
    ]

    required_positions = []
    preferred_positions = []

    for marker in required_markers:

        position = normalized.find(marker)

        if position != -1:
            required_positions.append(position)

    for marker in preferred_markers:

        position = normalized.find(marker)

        if position != -1:
            preferred_positions.append(position)

    # No explicit sections
    if not required_positions and not preferred_positions:
        return jd_text, ""

    first_required = min(required_positions) if required_positions else None
    first_preferred = min(preferred_positions) if preferred_positions else None

    if first_required is not None:

        if first_preferred is not None and first_preferred > first_required:
            required_text = normalized[first_required:first_preferred]
        else:
            required_text = normalized[first_required:]

    if first_preferred is not None:
        preferred_text = normalized[first_preferred:]

    return required_text, preferred_text


# ---------------------------------------------------------
# SKILL LIST FROM ROLE
# ---------------------------------------------------------

def get_role_skills(role: str) -> List[str]:
    """
    Return skills associated with a detected role.
    """

    if not role:
        return []

    return ROLE_SKILLS.get(role.lower(), [])


# ---------------------------------------------------------
# MATCH SKILLS
# ---------------------------------------------------------

def match_skill_list(resume_text: str, skills: List[str]):
    """
    Compare resume against a list of skills.
    """

    matched = []
    missing = []

    for skill in skills:

        if contains_skill(resume_text, skill):
            matched.append(skill)
        else:
            missing.append(skill)

    return matched, missing


# ---------------------------------------------------------
# REMOVE ROLE NAMES FROM SKILLS
# ---------------------------------------------------------

def remove_roles_from_skills(
    skills: List[str],
    detected_role: str
) -> List[str]:

    if not detected_role:
        return skills

    role_normalized = normalize_skill(detected_role)

    result = []

    for skill in skills:

        if normalize_skill(skill) == role_normalized:
            continue

        result.append(skill)

    return result


# ---------------------------------------------------------
# EXTRACT EXPLICIT JD SKILLS
# ---------------------------------------------------------

def extract_jd_skills(jd_text: str) -> List[str]:
    """
    Extract skills from the JD using both skills.csv and a
    built-in fallback vocabulary for common technical and
    professional requirements.
    """

    if not jd_text:
        return []

    skills = extract_skills(jd_text)

    # Add common JD skills that may not exist in skills.csv.
    normalized_jd = normalize_text(jd_text)

    for canonical, aliases in JD_SKILL_ALIASES.items():
        candidates = [canonical] + aliases

        for candidate in candidates:
            normalized_candidate = normalize_text(candidate)

            if not normalized_candidate:
                continue

            pattern = r"(?<!\w)" + re.escape(normalized_candidate) + r"(?!\w)"

            if re.search(pattern, normalized_jd):
                if canonical not in skills:
                    skills.append(canonical)
                break

    detected_role = detect_role(jd_text)

    skills = remove_roles_from_skills(
        skills,
        detected_role
    )

    return list(dict.fromkeys(skills))


# ---------------------------------------------------------
# TF-IDF SIMILARITY
# ---------------------------------------------------------

def calculate_similarity(resume_text: str, jd_text: str) -> float:
    """
    Calculate resume-JD textual similarity.
    """

    if not resume_text or not jd_text:
        return 0.0

    try:

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2)
        )

        vectors = vectorizer.fit_transform(
            [resume_text, jd_text]
        )

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )[0][0]

        return round(float(similarity) * 100, 2)

    except Exception:
        return 0.0


# ---------------------------------------------------------
# MAIN MATCHING FUNCTION
# ---------------------------------------------------------

def match_keywords(
    resume_text: str,
    jd_text: str
) -> KeywordMatchResult:

    result = KeywordMatchResult()

    if not resume_text or not jd_text:
        return result

    # -----------------------------------------------------
    # Detect role
    # -----------------------------------------------------

    detected_role = detect_role(jd_text)

    result.detected_role = detected_role

    # -----------------------------------------------------
    # Get required/preferred JD sections
    # -----------------------------------------------------

    required_text, preferred_text = extract_requirement_sections(
        jd_text
    )

    # -----------------------------------------------------
    # Explicit skills from JD
    # -----------------------------------------------------

    jd_skills = extract_jd_skills(jd_text)

    required_skills = extract_jd_skills(required_text)
    preferred_skills = extract_jd_skills(preferred_text)

    # -----------------------------------------------------
    # If role is detected, use role_skills.csv
    # -----------------------------------------------------

    role_skills = get_role_skills(detected_role)

    # Skills from role mapping
    role_required_skills = []

    for skill in role_skills:

        if contains_skill(required_text, skill):

            if skill not in role_required_skills:
                role_required_skills.append(skill)

    # If no explicit required skills were detected,
    # use role skills as additional requirements.
    if not required_skills and role_skills:

        required_skills = role_skills.copy()

    # Add role-based skills to explicit required skills
    for skill in role_required_skills:

        if skill not in required_skills:
            required_skills.append(skill)

    # Remove duplicates
    required_skills = list(dict.fromkeys(required_skills))
    preferred_skills = list(dict.fromkeys(preferred_skills))

    # Prevent the same skill from appearing in both lists
    preferred_skills = [
        skill
        for skill in preferred_skills
        if skill not in required_skills
    ]

    # -----------------------------------------------------
    # MATCH REQUIRED
    # -----------------------------------------------------

    matched_required, missing_required = match_skill_list(
        resume_text,
        required_skills
    )

    # -----------------------------------------------------
    # MATCH PREFERRED
    # -----------------------------------------------------

    matched_preferred, missing_preferred = match_skill_list(
        resume_text,
        preferred_skills
    )

    # -----------------------------------------------------
    # Scores
    # -----------------------------------------------------

    if required_skills:

        required_score = (
            len(matched_required) /
            len(required_skills)
        )

    else:
        required_score = 0.0

    if preferred_skills:

        preferred_score = (
            len(matched_preferred) /
            len(preferred_skills)
        )

    else:
        preferred_score = 0.0

    # Required skills are more important
    if required_skills and preferred_skills:

        overall_score = (
            required_score * 0.70
            + preferred_score * 0.30
        )

    elif required_skills:

        overall_score = required_score

    elif preferred_skills:

        overall_score = preferred_score

    else:
        overall_score = 0.0

    # -----------------------------------------------------
    # ALL JD SKILLS
    # -----------------------------------------------------

    all_jd_skills = list(
        dict.fromkeys(
            required_skills + preferred_skills
        )
    )

    matched_all, missing_all = match_skill_list(
        resume_text,
        all_jd_skills
    )

    # -----------------------------------------------------
    # Similarity
    # -----------------------------------------------------

    similarity = calculate_similarity(
        resume_text,
        jd_text
    )

    # -----------------------------------------------------
    # Save results
    # -----------------------------------------------------

    result.required_keywords = required_skills
    result.preferred_keywords = preferred_skills

    result.matched_required = matched_required
    result.missing_required = missing_required

    result.matched_preferred = matched_preferred
    result.missing_preferred = missing_preferred

    result.matched_skills = matched_all
    result.missing_skills = missing_all

    result.required_match_score = round(
        required_score,
        4
    )

    result.preferred_match_score = round(
        preferred_score,
        4
    )

    result.overall_keyword_score = round(
        overall_score,
        4
    )

    result.similarity_score = similarity

    return result