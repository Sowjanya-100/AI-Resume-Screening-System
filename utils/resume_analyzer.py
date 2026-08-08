import re


def count_projects(text):

    text = text.lower()

    keywords = [
        "project",
        "developed",
        "implemented",
        "designed",
        "built",
        "created",
        "application",
        "website",
        "system"
    ]

    count = 0

    for word in keywords:
        count += text.count(word)

    # Maximum 10 marks
    if count >= 5:
        score = 10
    elif count >= 3:
        score = 8
    elif count >= 2:
        score = 6
    elif count >= 1:
        score = 4
    else:
        score = 0

    return count, score


def count_certifications(text):

    text = text.lower()

    keywords = [
        "certificate",
        "certification",
        "certified",
        "course",
        "badge"
    ]

    count = 0

    for word in keywords:
        count += text.count(word)

    # Maximum 10 marks
    if count >= 5:
        score = 10
    elif count >= 3:
        score = 8
    elif count >= 2:
        score = 6
    elif count >= 1:
        score = 4
    else:
        score = 0

    return count, score