from .extractor import extract
from .structure_checker import check_structure
from .formatting_checker import check_formatting


# ATS scoring weights
WEIGHTS = {
    "formatting": 0.30,
    "sections": 0.25,
    "contact": 0.15,
    "dates": 0.15,
    "readability": 0.15,
}


def analyze_resume(resume_path: str, jd_text: str = "", target_title: str = "") -> dict:

    # ---------------------------------------------------------
    # 1. Extract resume information
    # ---------------------------------------------------------
    extraction = extract(resume_path)

    # ---------------------------------------------------------
    # 2. Analyze resume structure
    # ---------------------------------------------------------
    structure_result = check_structure(
        extraction.text,
        target_title
    )

    # ---------------------------------------------------------
    # 3. Analyze formatting
    # ---------------------------------------------------------
    formatting_result = check_formatting(extraction)

    formatting_score = formatting_result.formatting_score
    section_score = structure_result.section_completeness_score
    contact_score = structure_result.contact_score
    date_score = structure_result.date_parse_score

    # ---------------------------------------------------------
    # 4. Readability analysis
    # ---------------------------------------------------------
    readability_score = 1.0
    readability_issues = []

    if extraction.likely_scanned_image:
        readability_score -= 0.70
        readability_issues.append(
            "Resume appears to be a scanned image with no extractable text."
        )

    if extraction.used_text_boxes:
        readability_score -= 0.25
        readability_issues.append(
            "Text boxes detected. Some ATS parsers may not read their content correctly."
        )

    if extraction.multi_column_layout:
        readability_score -= 0.15
        readability_issues.append(
            "Multi-column layout detected. Reading order may be affected by some ATS parsers."
        )

    readability_score = max(0.0, readability_score)

    # ---------------------------------------------------------
    # 5. Calculate overall ATS score
    # ---------------------------------------------------------
    final_score = (
        WEIGHTS["formatting"] * formatting_score
        + WEIGHTS["sections"] * section_score
        + WEIGHTS["contact"] * contact_score
        + WEIGHTS["dates"] * date_score
        + WEIGHTS["readability"] * readability_score
    )

    final_score = round(final_score * 100, 1)

    # ---------------------------------------------------------
    # 6. Formatting warnings
    # ---------------------------------------------------------
    formatting_messages = _formatting_messages(
        formatting_result.issues
    )

    # ---------------------------------------------------------
    # 7. Combine warnings
    # ---------------------------------------------------------
    all_warnings = []

    all_warnings.extend(extraction.warnings)
    all_warnings.extend(formatting_messages)
    all_warnings.extend(readability_issues)
    all_warnings.extend(structure_result.warnings)

    # Remove duplicates
    all_warnings = list(dict.fromkeys(all_warnings))

    # ---------------------------------------------------------
    # 8. Build ATS report
    # ---------------------------------------------------------
    report = {
        "overall_score": final_score,

        "score_band": _score_band(final_score),

        "breakdown": {

            "formatting": {
                "score_pct": round(formatting_score * 100, 1),
                "weight": WEIGHTS["formatting"],
                "issues": formatting_result.issues,
            },

            "section_completeness": {
                "score_pct": round(section_score * 100, 1),
                "weight": WEIGHTS["sections"],
                "sections_found": structure_result.sections_found,
                "missing_sections": structure_result.missing_sections,
            },

            "contact_information": {
                "score_pct": round(contact_score * 100, 1),
                "weight": WEIGHTS["contact"],
            },

            "date_parsing": {
                "score_pct": round(date_score * 100, 1),
                "weight": WEIGHTS["dates"],
                "date_ranges_found": structure_result.date_ranges_found,
            },

            "readability": {
                "score_pct": round(readability_score * 100, 1),
                "weight": WEIGHTS["readability"],
            },
        },

        "contact_info": {
            "has_email": structure_result.has_email,
            "has_phone": structure_result.has_phone,
            "has_linkedin": structure_result.has_linkedin,
        },

        "warnings": all_warnings,

        # Kept internally for future analysis.
        # It does NOT need to be displayed on the dashboard.
        "extracted_text_preview": extraction.text[:500],
    }

    # ---------------------------------------------------------
    # 9. Generate recommendations dynamically
    # ---------------------------------------------------------
    recommendations = []

    # Formatting recommendations
    if "used_tables" in formatting_result.issues:
        recommendations.append(
            "Avoid tables because some ATS parsers may misread or skip table content."
        )

    if "used_text_boxes" in formatting_result.issues:
        recommendations.append(
            "Avoid text boxes because ATS parsers may not read their content correctly."
        )

    if "multi_column_layout" in formatting_result.issues:
        recommendations.append(
            "Consider using a single-column layout to improve ATS reading order."
        )

    if "used_headers_footers" in formatting_result.issues:
        recommendations.append(
            "Avoid placing important information in headers or footers because some ATS parsers may ignore them."
        )

    # Contact recommendations
    if not structure_result.has_email:
        recommendations.append(
            "Add a professional email address to your contact information."
        )

    if not structure_result.has_phone:
        recommendations.append(
            "Add a phone number to your contact information."
        )

    if not structure_result.has_linkedin:
        recommendations.append(
            "Add a valid LinkedIn profile URL to your contact information."
        )

    # ---------------------------------------------------------
    # Important missing sections
    # ---------------------------------------------------------
    for section in structure_result.missing_sections:

        recommendations.append(
            f"Add a clearly labeled {section.title()} section "
            f"using a standard ATS-friendly heading."
        )

    # ---------------------------------------------------------
    # Date recommendation
    # ---------------------------------------------------------
    if structure_result.date_parse_score < 1.0:
        recommendations.append(
            "Use clear and consistent date formats such as "
            "Month Year – Month Year."
        )

    # ---------------------------------------------------------
    # Scanned resume recommendation
    # ---------------------------------------------------------
    if extraction.likely_scanned_image:
        recommendations.append(
            "Use a text-based PDF or DOCX instead of a scanned image "
            "so ATS software can extract the content."
        )

    # ---------------------------------------------------------
    # No major problems
    # ---------------------------------------------------------
    if not recommendations:
        recommendations.append(
            "No major ATS improvements were identified. "
            "Your resume has good ATS compatibility."
        )

    report["recommendations"] = recommendations

    return report


# =============================================================
# Formatting messages
# =============================================================

def _formatting_messages(issue_flags):

    messages_map = {

        "likely_scanned_image":
            "Resume appears to be a scanned image with no extractable text — "
            "this is close to a guaranteed ATS failure. Re-create as a text-based file.",

        "used_text_boxes":
            "Text boxes detected — content inside them is often invisible to ATS parsers.",

        "used_tables":
            "Tables detected — content inside table cells is frequently skipped or misread.",

        "multi_column_layout":
            "Multi-column layout detected — many parsers read left-to-right "
            "and may scramble the reading order.",

        "used_headers_footers":
            "Content found in a header/footer — some ATS parsers ignore these regions entirely.",
    }

    return [
        messages_map[flag]
        for flag in issue_flags
        if flag in messages_map
    ]


# =============================================================
# ATS score band
# =============================================================

def _score_band(score):

    if score >= 80:
        return "Strong ATS compatibility"

    elif score >= 60:
        return "Moderate ATS compatibility — improvements recommended"

    elif score >= 40:
        return "Weak ATS compatibility — significant improvements needed"

    else:
        return "Poor ATS compatibility — high risk of ATS parsing issues"