import re


def clean_resume_text(text):
    """
    Clean extracted resume text while preserving
    information useful for ATS and NLP analysis.
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Remove standalone bullet characters
    text = re.sub(r"^\s*[●•▪◦○]\s*$", "", text, flags=re.MULTILINE)

    # Remove bullet characters at the beginning of a line
    text = re.sub(r"^\s*[●•▪◦○]\s*", "", text, flags=re.MULTILINE)

    # Remove excessive spaces
    text = re.sub(r"[ ]+", " ", text)

    # Clean spaces around new lines
    lines = []

    for line in text.split("\n"):
        line = line.strip()

        if line:
            lines.append(line)

    # Remove excessive blank lines
    cleaned_lines = []

    previous_blank = False

    for line in lines:
        if not line:
            if not previous_blank:
                cleaned_lines.append(line)
            previous_blank = True
        else:
            cleaned_lines.append(line)
            previous_blank = False

    return "\n".join(cleaned_lines).strip()