import pandas as pd
import re

skills_df = pd.read_csv("skills.csv")
SKILLS = set(skills_df["Skill"].dropna().str.lower().str.strip())


def extract_skills(text):
    text = text.lower()

    found_skills = []

    for skill in SKILLS:
        skill = skill.strip()

        # Avoid matching very short skills such as "c"
        # inside normal words like "customer" or "communication".
        if len(skill) <= 2:
            pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        else:
            pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"

        if re.search(pattern, text):
            found_skills.append(skill.title())

    return sorted(list(set(found_skills)))
