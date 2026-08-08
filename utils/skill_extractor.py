import pandas as pd

skills_df = pd.read_csv("skills.csv")
SKILLS = set(skills_df["Skill"].str.lower())


def extract_skills(text):
    text = text.lower()

    found_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill.title())

    return sorted(list(set(found_skills)))