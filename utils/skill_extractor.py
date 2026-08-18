import pandas as pd
import re
import os


# ============================================================
# LOAD MASTER SKILLS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

skills_path = os.path.join(BASE_DIR, "skills.csv")
role_skills_path = os.path.join(BASE_DIR, "role_skills.csv")

skills_df = pd.read_csv(skills_path)

SKILLS = set(
    skills_df["Skill"]
    .dropna()
    .astype(str)
    .str.lower()
    .str.strip()
)

SKILL_ALIASES = {
    "microsoft excel": "excel",
    "ms excel": "excel",
    "microsoft word": "word",
    "ms word": "word",
    "microsoft powerpoint": "powerpoint",
    "ms powerpoint": "powerpoint",
}

# ============================================================
# LOAD ROLE-SKILL MAPPING
# ============================================================

role_skills_df = pd.read_csv(role_skills_path)

role_skills_df["Role"] = (
    role_skills_df["Role"]
    .astype(str)
    .str.lower()
    .str.strip()
)

role_skills_df["Skill"] = (
    role_skills_df["Skill"]
    .astype(str)
    .str.lower()
    .str.strip()
)


# Create role → skills dictionary
ROLE_SKILLS = {}

for _, row in role_skills_df.iterrows():

    role = row["Role"]
    skill = row["Skill"]

    if role not in ROLE_SKILLS:
        ROLE_SKILLS[role] = set()

    ROLE_SKILLS[role].add(skill)


# ============================================================
# EXTRACT EXPLICIT SKILLS
# ============================================================

def extract_skills(text):

    text = text.lower()

    found_skills = set()

    # Check longer skills first
    sorted_skills = sorted(SKILLS, key=len, reverse=True)

    for skill in sorted_skills:

        skill = skill.strip()

        pattern = (
            r"(?<![a-zA-Z0-9])"
            + re.escape(skill)
            + r"(?![a-zA-Z0-9])"
        )

        if re.search(pattern, text):

            # Convert aliases to one standard name
            normalized_skill = SKILL_ALIASES.get(skill, skill)

            found_skills.add(normalized_skill)

    return sorted(skill.title() for skill in found_skills)


# ============================================================
# IDENTIFY JOB ROLE
# ============================================================

def identify_role(text):

    text_lower = text.lower()

    matched_roles = []

    for role in ROLE_SKILLS.keys():

        # Match the complete role phrase
        pattern = (
            r"(?<![a-zA-Z0-9])"
            + re.escape(role)
            + r"(?![a-zA-Z0-9])"
        )

        if re.search(pattern, text_lower):
            matched_roles.append(role)

    # Prefer the longest/more specific role
    if matched_roles:
        matched_roles.sort(key=len, reverse=True)
        return matched_roles[0].title()

    return None


# ============================================================
# EXTRACT JD SKILLS WITH ROLE FALLBACK
# ============================================================

def extract_jd_skills(text):

    # First try normal skill extraction
    explicit_skills = extract_skills(text)

    # If skills are explicitly present, use them
    if explicit_skills:
        return explicit_skills

    # Otherwise identify the job role
    role = identify_role(text)

    if not role:
        return []

    role_key = role.lower()

    inferred_skills = ROLE_SKILLS.get(role_key, set())

    normalized_skills = set()
    
    for skill in inferred_skills:
        normalized_skill = SKILL_ALIASES.get(skill, skill)
        normalized_skills.add(normalized_skill)
    
    return sorted(
        skill.title()
        for skill in normalized_skills
    )


# ============================================================
# GET ROLE
# ============================================================

def get_job_role(text):

    return identify_role(text)
