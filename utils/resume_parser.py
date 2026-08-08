import re


def extract_candidate_info(text):
    info = {}

    # Email
    email = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )
    info["email"] = email[0] if email else "Not Found"

    # Phone Number
    phone = re.findall(
        r"(?:\+91[- ]?)?[6-9]\d{9}",
        text
    )
    info["phone"] = phone[0] if phone else "Not Found"

    # LinkedIn
    linkedin = re.findall(
        r"https?://(?:www\.)?linkedin\.com/\S+",
        text
    )
    info["linkedin"] = linkedin[0] if linkedin else "Not Found"

    # GitHub
    github = re.findall(
        r"https?://(?:www\.)?github\.com/\S+",
        text
    )
    info["github"] = github[0] if github else "Not Found"

    # Candidate Name
    lines = text.split("\n")

    name = "Not Found"

    for line in lines:
        line = line.strip()

        if (
            len(line.split()) <= 4
            and len(line) > 2
            and not any(
                x in line.lower()
                for x in [
                    "@",
                    "resume",
                    "curriculum",
                    "vitae",
                    "phone",
                    "email"
                ]
            )
        ):
            name = line
            break

    info["name"] = name

    return info