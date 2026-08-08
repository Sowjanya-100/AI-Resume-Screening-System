def recommend_courses(missing_skills):

    resources = {

        "python": {
            "course": "freeCodeCamp - Python for Beginners",
            "certificate": "freeCodeCamp Certification"
        },

        "sql": {
            "course": "SQLBolt",
            "certificate": "HackerRank SQL Certificate"
        },

        "excel": {
            "course": "Microsoft Learn - Excel",
            "certificate": "Microsoft Learn Badge"
        },

        "power bi": {
            "course": "Microsoft Learn - Power BI",
            "certificate": "Microsoft Learn Badge"
        },

        "machine learning": {
            "course": "Kaggle Learn - Machine Learning",
            "certificate": "Kaggle Micro-course Certificate"
        },

        "communication": {
            "course": "Great Learning - Communication Skills",
            "certificate": "Great Learning Certificate"
        },

        "react": {
            "course": "freeCodeCamp - React",
            "certificate": "freeCodeCamp Certification"
        },

        "java": {
            "course": "Oracle Java Tutorials",
            "certificate": "Oracle Learning Explorer"
        },

        "c": {
            "course": "freeCodeCamp - C Programming",
            "certificate": "freeCodeCamp Certification"
        },

        "c++": {
            "course": "LearnCpp",
            "certificate": "SoloLearn Certificate"
        },

        "html": {
            "course": "freeCodeCamp - Responsive Web Design",
            "certificate": "freeCodeCamp Certification"
        },

        "css": {
            "course": "freeCodeCamp - Responsive Web Design",
            "certificate": "freeCodeCamp Certification"
        },

        "javascript": {
            "course": "freeCodeCamp - JavaScript",
            "certificate": "freeCodeCamp Certification"
        },

        "aws": {
            "course": "AWS Skill Builder",
            "certificate": "AWS Skill Builder Badge"
        },

        "salesforce": {
            "course": "Trailhead",
            "certificate": "Trailhead Badge"
        },

        "git": {
            "course": "GitHub Skills",
            "certificate": "GitHub Badge"
        }
    }

    recommendations = []

    for skill in missing_skills:

        key = skill.lower()

        if key in resources:

            recommendations.append({
                "skill": skill,
                "course": resources[key]["course"],
                "certificate": resources[key]["certificate"]
            })

    return recommendations