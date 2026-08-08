import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from reportlab.lib.units import inch



def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()

    canvas.setFont("Helvetica", 9)

    canvas.setFillColorRGB(0.4, 0.4, 0.4)

    canvas.drawRightString(
        7.5 * inch,
        0.5 * inch,
        f"Page {page_num}"
    )

    canvas.drawString(
        0.7 * inch,
        0.5 * inch,
        "AI Resume Screening System"
    )


def generate_report(
    filename,
    candidate,
    match,
    similarity,
    ats_score,
    ats_rating,
    ats_breakdown,
    matched,
    missing,
    recommendation,
    education_status,
    experience_status,
    project_count,
    certificate_count,
    feedback,
    recommendations
):

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    doc = SimpleDocTemplate(filename)

    elements = []

    # ==================================
    # Title
    # ==================================

    elements.append(
    Paragraph(
        "<font color='#1E88E5'><b>AI RESUME SCREENING REPORT</b></font>",
        title_style
    )
)

    elements.append(Spacer(1, 15))

    # ==================================
    # Candidate Information
    # ==================================

    elements.append(
        Paragraph("<b>👤 Candidate Information</b>", styles["Heading2"])
    )

    candidate_table = Table([
        ["Field", "Value"],
        ["Name", candidate["name"]],
        ["Email", candidate["email"]],
        ["Phone", candidate["phone"]],
        ["LinkedIn", candidate["linkedin"]],
        ["GitHub", candidate["github"]],
    ])

    candidate_table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1E88E5")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("GRID", (0,0), (-1,-1), 1, colors.grey),

        ("BACKGROUND", (0,1), (-1,-1), colors.whitesmoke),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

        ("BOTTOMPADDING", (0,0), (-1,0), 8),

    ]))

    elements.append(candidate_table)

    elements.append(Spacer(1,15))

    # ==================================
    # Scores
    # ==================================

    elements.append(
        Paragraph("<b>Overall Scores</b>", styles["Heading2"])
    )

    elements.append(
        Paragraph(f"Match Percentage : {match}%", styles["Normal"])
    )

    elements.append(
        Paragraph(f"Resume Similarity : {similarity}%", styles["Normal"])
    )

    elements.append(
        Paragraph(f"ATS Score : {ats_score}/100", styles["Normal"])
    )

    elements.append(
        Paragraph(f"ATS Rating : {ats_rating}", styles["Normal"])
    )

    elements.append(Spacer(1, 15))

    # ==================================
    # Education
    # ==================================

    elements.append(
        Paragraph("<b>Education Match</b>", styles["Heading2"])
    )

    elements.append(
        Paragraph(education_status, styles["Normal"])
    )

    elements.append(Spacer(1, 10))

    # ==================================
    # Experience
    # ==================================

    elements.append(
        Paragraph("<b>Experience Match</b>", styles["Heading2"])
    )

    elements.append(
        Paragraph(experience_status, styles["Normal"])
    )

    elements.append(Spacer(1, 15))

    # ==================================
    # ATS Breakdown
    # ==================================

    elements.append(
        Paragraph("<b>ATS Score Breakdown</b>", styles["Heading2"])
    )

    ats_data = [["Category", "Score"]]

    for key, value in ats_breakdown.items():
        ats_data.append([key, str(value)])

    ats_data.append(["Total ATS Score", f"{ats_score}/100"])

    ats_table = Table(ats_data)

    ats_table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1E88E5")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("GRID", (0,0), (-1,-1), 1, colors.grey),

        ("BACKGROUND", (0,1), (-1,-1), colors.beige),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

        ("BOTTOMPADDING", (0,0), (-1,0), 8),

    ]))

    elements.append(ats_table)

    elements.append(Spacer(1,15))
   
    # Resume Statistics
    
    elements.append(
        Paragraph("<b>📈 Resume Statistics</b>", styles["Heading2"])
    )

    stats_data = [
        ["Metric", "Count"],
        ["Projects", str(project_count)],
        ["Certifications", str(certificate_count)],
        ["Matched Skills", str(len(matched))],
        ["Missing Skills", str(len(missing))]
    ]

    stats_table = Table(stats_data)

    stats_table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#43A047")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),

        ("GRID", (0, 0), (-1, -1), 1, colors.grey),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

    ]))

    elements.append(stats_table)

    elements.append(Spacer(1, 15))
    # ==================================
    # Matched Skills
    # ==================================

    elements.append(
        Paragraph("<b>Matched Skills</b>", styles["Heading2"])
    )

    if matched:

        for skill in matched:

            elements.append(
                Paragraph(f"• {skill}", styles["Normal"])
            )

    else:

        elements.append(
            Paragraph("No matched skills", styles["Normal"])
        )

    elements.append(Spacer(1, 15))

    # ==================================
    # Missing Skills
    # ==================================

    elements.append(
        Paragraph("<b>Missing Skills</b>", styles["Heading2"])
    )

    if missing:

        for skill in missing:

            elements.append(
                Paragraph(f"• {skill}", styles["Normal"])
            )

    else:

        elements.append(
            Paragraph("No missing skills", styles["Normal"])
        )

    elements.append(Spacer(1, 15))

    # ==================================
    # Recommendation
    # ==================================

    elements.append(
        Paragraph("<b>Recommendation</b>", styles["Heading2"])
    )

    elements.append(
        Paragraph(recommendation, styles["Normal"])
    )

    elements.append(Spacer(1, 15))

    # ==================================
    # AI Feedback
    # ==================================

    elements.append(
        Paragraph("<b>Resume Insights</b>", styles["Heading2"])
    )

    for item in feedback:

        elements.append(
            Paragraph(item, styles["Normal"])
        )

    elements.append(Spacer(1, 15))

    # ==================================
    # Learning Resources
    # ==================================

    elements.append(
        Paragraph("<b>Free Learning Resources</b>", styles["Heading2"])
    )

    if recommendations:

        for item in recommendations:

            elements.append(
                Paragraph(
                    f"<b>{item['skill']}</b>",
                    styles["Normal"]
                )
            )

            elements.append(
                Paragraph(
                    f"Course : {item['course']}",
                    styles["Normal"]
                )
            )

            elements.append(
                Paragraph(
                    f"Certificate : {item['certificate']}",
                    styles["Normal"]
                )
            )

            elements.append(Spacer(1, 8))

    else:

        elements.append(
            Paragraph(
                "No recommendations required.",
                styles["Normal"]
            )
        )
    # Generated Date
    

    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph("<b>Generated On</b>", styles["Heading2"])
    )

    generated_date = datetime.now().strftime("%d %B %Y, %I:%M %p")

    elements.append(
        Paragraph(generated_date, styles["Normal"])
    )

    elements.append(Spacer(1, 20))

    # ==================================
    # Footer
    # ==================================

    elements.append(
        Paragraph(
            "<font size=9 color='grey'>"
            "Generated by AI Resume Screening System"
            "<br/>Python | Streamlit | Machine Learning"
            "</font>",
            styles["Normal"]
        )
    )
    # Make sure the output directory exists


    doc.build(
        elements,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )
    