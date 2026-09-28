from flask import (
    Flask,
    render_template,
    request,
    send_from_directory,
    send_file
)

import os
import json
import uuid
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from werkzeug.utils import secure_filename

from nlp.analyzer import analyze_resume
from nlp.extractor import extract
from nlp.keyword_matcher import match_keywords


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

REPORT_FOLDER = os.path.join(
    BASE_DIR,
    "reports"
)

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx"
}

MAX_FILE_SIZE = 10 * 1024 * 1024


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["REPORT_FOLDER"] = REPORT_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    REPORT_FOLDER,
    exist_ok=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def allowed_file(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


def save_uploaded_file(file):

    if not file:
        raise ValueError(
            "No file was uploaded."
        )

    if not file.filename:
        raise ValueError(
            "No file was selected."
        )

    if not allowed_file(
        file.filename
    ):
        raise ValueError(
            "Unsupported file type. "
            "Please upload a PDF or DOCX file."
        )

    filename = secure_filename(
        file.filename
    )

    if not filename:
        raise ValueError(
            "Invalid file name."
        )

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(
        file_path
    )

    return filename, file_path


def job_state_path(state_id):
    """Return the server-side path used to preserve Job Matcher state."""
    safe_state_id = re.sub(r"[^a-fA-F0-9]", "", state_id or "")
    if not safe_state_id:
        return None
    return os.path.join(
        app.config["REPORT_FOLDER"],
        f".job_matcher_state_{safe_state_id}.json"
    )


def save_job_state(state):
    """Save Job Matcher state so Back does not lose the inputs."""
    state_id = uuid.uuid4().hex
    path = job_state_path(state_id)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False, indent=2)
    return state_id


def load_job_state(state_id):
    """Load previously saved Job Matcher state."""
    path = job_state_path(state_id)
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return None


def candidate_display_name(filename):
    name = os.path.splitext(filename or "Resume")[0]
    name = name.replace("_", " ").replace("-", " ").strip()
    return name or "Resume"


def extract_candidate_name_from_resume(resume_text, fallback_filename):
    """Find a likely candidate name near the top of the resume.

    If no reliable name-like line is found, use the uploaded filename.
    """
    lines = [
        re.sub(r"\\s+", " ", line).strip(" |,-")
        for line in (resume_text or "").splitlines()
        if line.strip()
    ]

    skip_terms = {
        "resume", "curriculum vitae", "cv", "profile", "objective",
        "summary", "education", "experience", "skills", "projects",
        "certifications", "contact", "professional summary"
    }

    for line in lines[:20]:
        lower = line.lower()

        if lower in skip_terms:
            continue
        if len(line) < 3 or len(line) > 60:
            continue
        if "@" in line or "http://" in lower or "https://" in lower:
            continue
        if re.search(r"\\d{4,}", line):
            continue

        words = line.replace(",", " ").split()

        # Most names in a resume are 2-5 alphabetic words.
        if not 2 <= len(words) <= 5:
            continue

        if all(re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ'.]+", word) for word in words):
            return line

    return candidate_display_name(fallback_filename)


def build_job_matcher_pdf(state, output_path):
    """Create the downloadable Job Matcher PDF report."""

    from datetime import datetime

    report = state.get("report", {})
    filename = state.get("resume_filename", "Resume")

    candidate_name = state.get(
        "candidate_name",
        candidate_display_name(filename)
    )

    # ------------------------------------------------------------
    # STYLES
    # ------------------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=14
    )

    section_style = ParagraphStyle(
        "ReportSection",
        parent=styles["Heading2"],
        spaceBefore=12,
        spaceAfter=8
    )

    small_style = ParagraphStyle(
        "ReportSmall",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12
    )

    date_style = ParagraphStyle(
        "ReportDate",
        parent=styles["BodyText"],
        alignment=2,
        fontSize=9,
        spaceAfter=8
    )

    # ------------------------------------------------------------
    # DOCUMENT
    # ------------------------------------------------------------

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=45
    )

    story = []

    # ------------------------------------------------------------
    # DATE - FIRST PAGE
    # ------------------------------------------------------------

    current_date = datetime.now().strftime("%d %B %Y")

    story.append(
        Paragraph(
            f"Date: {current_date}",
            date_style
        )
    )

    # ------------------------------------------------------------
    # TITLE
    # ------------------------------------------------------------

    story.extend([
        Paragraph(
            "AI Resume Screening System",
            title_style
        ),

        Paragraph(
            "Job Description Match Report",
            styles["Heading1"]
        ),

        Spacer(1, 8)
    ])

    # ------------------------------------------------------------
    # CANDIDATE INFORMATION
    # ------------------------------------------------------------

    info_data = [
        [
            "Candidate / Resume",
            candidate_name
        ],
        [
            "Resume File",
            filename
        ],
        [
            "Detected Role",
            report.get(
                "detected_role",
                "Not detected"
            )
        ],
    ]

    info_table = Table(
        info_data,
        colWidths=[150, 350]
    )

    info_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.whitesmoke
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.lightgrey
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            ),
        ])
    )

    story.append(info_table)

    # ------------------------------------------------------------
    # ANALYSIS SCORES
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "Analysis Scores",
            section_style
        )
    )

    score_data = [
        [
            "Metric",
            "Score"
        ],
        [
            "Match Percentage",
            f'{report.get("match_percentage", 0)}%'
        ],
        [
            "Resume Similarity",
            f'{report.get("resume_similarity", 0)}%'
        ],
        [
            "ATS Score",
            f'{report.get("ats_score", 0)}/100'
        ],
    ]

    score_table = Table(
        score_data,
        colWidths=[300, 200]
    )

    score_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.whitesmoke
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.lightgrey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "CENTER"
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            ),
        ])
    )

    story.append(score_table)

    # ------------------------------------------------------------
    # MATCHING SKILLS
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "Matching Skills",
            section_style
        )
    )

    matched = report.get(
        "matched_skills",
        []
    )

    story.append(
        Paragraph(
            ", ".join(matched)
            if matched
            else "No matching skills found.",
            small_style
        )
    )

    # ------------------------------------------------------------
    # MISSING SKILLS
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "Missing Skills",
            section_style
        )
    )

    missing = report.get(
        "missing_skills",
        []
    )

    story.append(
        Paragraph(
            ", ".join(missing)
            if missing
            else "No missing skills detected.",
            small_style
        )
    )

    # ------------------------------------------------------------
    # RECOMMENDATIONS
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "Recommendations",
            section_style
        )
    )

    if missing:

        recommendations = [
            "Focus on the missing skills identified from the job description.",

            "Highlight relevant skills, projects, certifications, and experience that genuinely match the target role.",

            "Build practical projects using important missing skills.",

            "Continue structured learning and hands-on practice."
        ]

    else:

        recommendations = [
            "Highlight the matching skills, projects, certifications, and experience that genuinely support the target role.",

            "Use the job description terminology naturally where it accurately describes your existing experience.",

            "Prepare examples for interviews that demonstrate the matching skills and responsibilities."
        ]

    for item in recommendations:

        story.append(
            Paragraph(
                "• " + item,
                small_style
            )
        )

        story.append(
            Spacer(1, 4)
        )

    # ------------------------------------------------------------
    # FREE LEARNING & CERTIFICATION RESOURCES
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "Free Learning & Certification Resources",
            section_style
        )
    )

    story.append(
        Paragraph(
            "These resources can help strengthen skills related to the job description.",
            small_style
        )
    )

    courses = [
        [
            "Data Analytics",
            "Introduction to Data Analytics",
            "Simplilearn SkillUp",
            "Free Certificate"
        ],

        [
            "Data Analyst",
            "Free Data Analyst Course",
            "Simplilearn SkillUp",
            "Free Certificate"
        ],

        [
            "Power BI",
            "Prepare Data for Analysis with Power BI",
            "Microsoft Learn",
            "Free Learning"
        ],

        [
            "Python / Data Analysis",
            "Explore and Analyze Data with Python",
            "Microsoft Learn",
            "Free Learning"
        ],

        [
            "Data Science",
            "Introduction to Data Science",
            "Simplilearn SkillUp",
            "Free Certificate"
        ],

        [
            "Python / Data Analysis",
            "Data Analysis with Python",
            "freeCodeCamp",
            "Free Certification"
        ],

        [
            "Data Analytics / SQL / Excel / Tableau",
            "Data Analytics Essentials",
            "Cisco Networking Academy",
            "Free Course + Digital Badge"
        ],
    ]

    course_data = [
        [
            "Skill / Area",
            "Course",
            "Provider",
            "Type"
        ]
    ]

    course_data.extend(courses)

    course_table = Table(
        course_data,
        colWidths=[
            125,
            170,
            105,
            100
        ],
        repeatRows=1
    )

    course_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.whitesmoke
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.lightgrey
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7.5
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                5
            ),
        ])
    )

    story.append(course_table)

    story.append(
        Spacer(1, 12)
    )

    story.append(
        Paragraph(
            "Generated by AI Resume Screening System",
            small_style
        )
    )

    # ------------------------------------------------------------
    # PDF FOOTER + METADATA
    # ------------------------------------------------------------

    def add_page_footer(canvas, document):

        canvas.saveState()

        page_number = canvas.getPageNumber()

        canvas.setStrokeColor(
            colors.lightgrey
        )

        canvas.line(
            40,
            30,
            A4[0] - 40,
            30
        )

        canvas.setFont(
            "Helvetica",
            8
        )

        canvas.setFillColor(
            colors.grey
        )

        canvas.drawString(
            40,
            18,
            "AI Resume Screening System"
        )

        canvas.drawRightString(
            A4[0] - 40,
            18,
            f"Page {page_number}"
        )

        canvas.setTitle(
            f"{candidate_name} - Resume Report"
        )

        canvas.setAuthor(
            "AI Resume Screening System"
        )

        canvas.setSubject(
            "Job Description Match Report"
        )

        canvas.restoreState()

    # ------------------------------------------------------------
    # BUILD PDF
    # ------------------------------------------------------------

    doc.build(
        story,
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )


def build_ats_pdf(report, filename, output_path):
    """Create the downloadable ATS analysis PDF report."""

    from datetime import datetime

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ATSTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=14
    )

    section_style = ParagraphStyle(
        "ATSSection",
        parent=styles["Heading2"],
        spaceBefore=12,
        spaceAfter=8
    )

    small_style = ParagraphStyle(
        "ATSSmall",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12
    )

    # Right aligned date
    # alignment=2 means right aligned in ReportLab.
    date_style = ParagraphStyle(
        "ATSDate",
        parent=styles["BodyText"],
        alignment=2,
        fontSize=9,
        spaceAfter=8
    )

    # ------------------------------------------------------------
    # DOCUMENT
    # ------------------------------------------------------------

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=45
    )

    story = []

    # ------------------------------------------------------------
    # DATE - FIRST PAGE
    # ------------------------------------------------------------

    current_date = datetime.now().strftime("%d %B %Y")

    story.append(
        Paragraph(
            f"Date: {current_date}",
            date_style
        )
    )

    # ------------------------------------------------------------
    # TITLE
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "AI Resume Screening System",
            title_style
        )
    )

    story.append(
        Paragraph(
            "ATS Resume Analysis Report",
            styles["Heading1"]
        )
    )

    story.append(
        Spacer(1, 8)
    )

    # ------------------------------------------------------------
    # RESUME INFORMATION
    # ------------------------------------------------------------

    info_data = [
        [
            "Resume File",
            filename
        ],
        [
            "ATS Score",
            f'{report.get("overall_score", 0)}/100'
        ],
        [
            "Compatibility",
            report.get(
                "score_band",
                "Not available"
            )
        ]
    ]

    info_table = Table(
        info_data,
        colWidths=[150, 350]
    )

    info_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.whitesmoke
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.lightgrey
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(info_table)

    # ------------------------------------------------------------
    # CONTACT INFORMATION
    # ------------------------------------------------------------

    contact_info = report.get(
        "contact_info",
        {}
    )

    story.append(
        Paragraph(
            "Resume Analysis",
            section_style
        )
    )

    analysis_data = [
        [
            "Item",
            "Status"
        ],
        [
            "Email",
            "Detected"
            if contact_info.get("has_email")
            else "Missing"
        ],
        [
            "Phone",
            "Detected"
            if contact_info.get("has_phone")
            else "Missing"
        ],
        [
            "LinkedIn",
            "Detected"
            if contact_info.get("has_linkedin")
            else "Missing"
        ]
    ]

    analysis_table = Table(
        analysis_data,
        colWidths=[250, 250]
    )

    analysis_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.whitesmoke
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.lightgrey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(analysis_table)

    # ------------------------------------------------------------
    # ------------------------------------------------------------
    # DETAILED ATS ANALYSIS
    # ------------------------------------------------------------

    breakdown = report.get(
        "breakdown",
        {}
    )

    story.append(
        Paragraph(
            "Detailed ATS Analysis",
            section_style
        )
    )

    detailed_data = [
        [
            "Metric",
            "Score"
        ]
    ]
    # ------------------------------------------------------------
    # DETAILED ATS ANALYSIS
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "Detailed ATS Analysis",
            section_style
        )
    )

    detailed_data = [
        [
            "Metric",
            "Score"
        ]
    ]

    metric_names = [
        (
            "formatting",
            "Formatting"
        ),
        (
            "section_completeness",
            "Section Completeness"
        ),
        (
            "contact_information",
            "Contact Information"
        ),
        (
            "date_parsing",
            "Date Parsing"
        ),
        (
            "readability",
            "ATS Readability"
        )
    ]

    for key, display_name in metric_names:

        metric = breakdown.get(
            key,
            {}
        )

        score = metric.get(
            "score_pct",
            0
        )

        detailed_data.append([
            display_name,
            f"{score}/100"
        ])

    detailed_table = Table(
        detailed_data,
        colWidths=[300, 200]
    )

    detailed_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.whitesmoke
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.lightgrey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "CENTER"
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    story.append(detailed_table)

    # ------------------------------------------------------------
    # WARNINGS
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "ATS Warnings",
            section_style
        )
    )

    warnings = report.get(
        "warnings",
        []
    )

    if warnings:

        for warning in warnings:

            story.append(
                Paragraph(
                    "• " + str(warning),
                    small_style
                )
            )

            story.append(
                Spacer(1, 4)
            )

    else:

        story.append(
            Paragraph(
                "✓ No major ATS issues detected.",
                small_style
            )
        )

    # ------------------------------------------------------------
    # RECOMMENDATIONS
    # ------------------------------------------------------------

    story.append(
        Paragraph(
            "ATS Recommendations",
            section_style
        )
    )

    recommendations = report.get(
        "recommendations",
        []
    )

    if recommendations:

        for recommendation in recommendations:

            story.append(
                Paragraph(
                    "• " + str(recommendation),
                    small_style
                )
            )

            story.append(
                Spacer(1, 4)
            )

    else:

        story.append(
            Paragraph(
                "✓ No major ATS improvements were identified.",
                small_style
            )
        )

    # ------------------------------------------------------------
    # FOOTER
    # ------------------------------------------------------------

    def add_page_footer(canvas, document):

        canvas.saveState()

        page_number = canvas.getPageNumber()

        # Footer line
        canvas.setStrokeColor(
            colors.lightgrey
        )

        canvas.line(
            40,
            30,
            A4[0] - 40,
            30
        )

        # Footer text
        canvas.setFont(
            "Helvetica",
            8
        )

        canvas.setFillColor(
            colors.grey
        )

        canvas.drawString(
            40,
            18,
            "AI Resume Screening System"
        )

        canvas.drawRightString(
            A4[0] - 40,
            18,
            f"Page {page_number}"
        )

        # PDF metadata
        canvas.setTitle(
            f"{filename} - ATS Resume Report"
        )

        canvas.setAuthor(
            "AI Resume Screening System"
        )

        canvas.setSubject(
            "ATS Resume Analysis Report"
        )

        canvas.restoreState()

    # ------------------------------------------------------------
    # BUILD PDF
    # ------------------------------------------------------------

    doc.build(
        story,
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )
def error_page(
    title,
    message,
    back_url="/"
):

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>{title}</title>

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <style>

            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 60px auto;
                padding: 20px;
                line-height: 1.6;
            }}

            h1 {{
                margin-bottom: 15px;
            }}

            .message {{
                margin: 20px 0;
            }}

            a {{
                text-decoration: none;
            }}

        </style>

    </head>

    <body>

        <h1>{title}</h1>

        <p class="message">
            {message}
        </p>

        <a href="{back_url}">
            ← Back
        </a>

    </body>

    </html>
    """


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )
# ============================================================
# ABOUT PAGE
# ============================================================

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )

# ============================================================
# ATS CHECKER PAGE
# ============================================================

@app.route("/ats-checker")
def ats_checker():

    return render_template(
        "ats_checker.html"
    )


# ============================================================
# JOB DESCRIPTION MATCHER PAGE
# ============================================================

@app.route("/job-matcher")
def job_matcher():

    state_id = request.args.get("state_id", "").strip()
    saved_state = load_job_state(state_id) if state_id else None

    return render_template(
        "job_matcher.html",
        saved_state=saved_state or {},
        state_id=state_id
    )


# ============================================================
# ATS RESUME UPLOAD
# ============================================================

@app.route(
    "/analyze-ats",
    methods=["POST"]
)
def analyze_ats():

    if "resume" not in request.files:

        return error_page(
            "Resume Required",
            "Please upload your resume.",
            "/ats-checker"
        )

    resume = request.files[
        "resume"
    ]

    try:

        filename, file_path = (
            save_uploaded_file(
                resume
            )
        )

    except Exception as e:

        return error_page(
            "Upload Error",
            str(e),
            "/ats-checker"
        )

    return render_template(
        "ats_result.html",
        filename=filename
    )


# ============================================================
# UPLOAD COMPATIBILITY ROUTE
# ============================================================

@app.route(
    "/upload-resume",
    methods=["POST"]
)
def upload_resume_alias():

    return analyze_ats()


# ============================================================
# RESUME PREVIEW
# ============================================================

@app.route(
    "/preview/<filename>"
)
def preview_resume(filename):

    filename = secure_filename(
        filename
    )

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    if not os.path.exists(
        file_path
    ):

        return error_page(
            "File Not Found",
            "The requested resume could not be found.",
            "/ats-checker"
        )

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# ============================================================
# RESUME PREVIEW COMPATIBILITY ROUTE
# ============================================================

@app.route(
    "/preview-resume/<filename>"
)
def preview_resume_alias(filename):

    return preview_resume(
        filename
    )


# ============================================================
# ATS RESULT PAGE
# ============================================================

@app.route(
    "/ats-result/<filename>"
)
def ats_result(filename):

    filename = secure_filename(
        filename
    )

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    if not os.path.exists(
        file_path
    ):

        return error_page(
            "File Not Found",
            "The uploaded resume could not be found.",
            "/ats-checker"
        )

    return render_template(
        "ats_result.html",
        filename=filename
    )


# ============================================================
# ACTUAL ATS ANALYSIS
# ============================================================

@app.route(
    "/analyze-resume",
    methods=["POST"]
)
def analyze_resume_route():

    filename = request.form.get(
        "filename",
        ""
    ).strip()

    if not filename:

        return error_page(
            "Resume Not Found",
            "No resume filename was provided.",
            "/ats-checker"
        )

    filename = secure_filename(
        filename
    )

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    if not os.path.exists(
        file_path
    ):

        return error_page(
            "Resume Not Found",
            "The uploaded resume file could not be found.",
            "/ats-checker"
        )

    try:

        report = analyze_resume(
            file_path,
            jd_text="",
            target_title=""
        )

        return render_template(
            "ats_dashboard.html",
            filename=filename,
            report=report
        )

    except Exception as e:

        return error_page(
            "ATS Analysis Error",
            str(e),
            "/ats-checker"
        )

# ============================================================
# DOWNLOAD ATS REPORT
# ============================================================

@app.route("/download-ats-report/<filename>")
def download_ats_report(filename):

    filename = secure_filename(filename)

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    if not os.path.exists(file_path):

        return error_page(
            "Resume Not Found",
            "The uploaded resume could not be found.",
            "/ats-checker"
        )

    try:

        report = analyze_resume(
            file_path,
            jd_text="",
            target_title=""
        )

    except Exception as e:

        return error_page(
            "ATS Analysis Error",
            str(e),
            "/ats-checker"
        )

    candidate_name = candidate_display_name(
        filename
    )

    report_filename = (
        f"{secure_filename(candidate_name)}"
        "_ATS_Resume_Report.pdf"
    )

    report_path = os.path.join(
        app.config["REPORT_FOLDER"],
        report_filename
    )

    try:

        build_ats_pdf(
            report,
            filename,
            report_path
        )

    except Exception as e:

        return error_page(
            "Report Generation Error",
            str(e),
            "/ats-checker"
        )

    return send_file(
        report_path,
        as_attachment=True,
        download_name=report_filename,
        mimetype="application/pdf"
    )
# ============================================================
# JOB DESCRIPTION MATCHER ANALYSIS
# ============================================================

@app.route(
    "/job-matcher-analyze",
    methods=["POST"]
)
def job_matcher_analyze():

    # 1. CHECK / RESTORE RESUME
    resume = request.files.get("resume")
    existing_resume_filename = request.form.get(
        "existing_resume_filename", ""
    ).strip()

    if resume and resume.filename:
        try:
            resume_filename, resume_path = save_uploaded_file(resume)
        except Exception as e:
            return error_page(
                "Resume Upload Error",
                str(e),
                "/job-matcher"
            )
    elif existing_resume_filename:
        resume_filename = secure_filename(existing_resume_filename)
        resume_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            resume_filename
        )
        if not os.path.exists(resume_path):
            return error_page(
                "Resume Not Found",
                "The previously uploaded resume could not be found. Please upload it again.",
                "/job-matcher"
            )
    else:
        return error_page(
            "Resume Required",
            "Please upload your resume.",
            "/job-matcher"
        )

    # 2. GET / RESTORE JOB DESCRIPTION
    pasted_jd = request.form.get("job_description", "").strip()
    jd_file = request.files.get("jd_file")
    existing_jd_filename = request.form.get(
        "existing_jd_filename", ""
    ).strip()

    jd_text = ""
    jd_filename = ""
    jd_method = ""

    if pasted_jd:
        jd_text = pasted_jd
        jd_method = "paste"

    elif jd_file and jd_file.filename:
        try:
            jd_filename, jd_path = save_uploaded_file(jd_file)
            jd_extraction = extract(jd_path)
            jd_text = (jd_extraction.text or "").strip()
            jd_method = "upload"
        except Exception as e:
            return error_page(
                "Job Description Error",
                str(e),
                "/job-matcher"
            )

    elif existing_jd_filename:
        jd_filename = secure_filename(existing_jd_filename)
        jd_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            jd_filename
        )
        if not os.path.exists(jd_path):
            return error_page(
                "Job Description Not Found",
                "The previously uploaded Job Description could not be found. Please upload it again.",
                "/job-matcher"
            )
        try:
            jd_extraction = extract(jd_path)
            jd_text = (jd_extraction.text or "").strip()
            jd_method = "upload"
        except Exception as e:
            return error_page(
                "Job Description Error",
                str(e),
                "/job-matcher"
            )

    if not jd_text:
        return error_page(
            "Job Description Required",
            "Please either upload a Job Description file or paste the Job Description text.",
            "/job-matcher"
        )

    # 3. EXTRACT RESUME TEXT
    try:
        resume_extraction = extract(resume_path)
        resume_text = (resume_extraction.text or "").strip()
    except Exception as e:
        return error_page(
            "Resume Reading Error",
            str(e),
            "/job-matcher"
        )

    if not resume_text:
        return error_page(
            "Resume Text Could Not Be Extracted",
            "Please upload a text-based PDF or DOCX resume.",
            "/job-matcher"
        )

    # Detect the candidate's actual name for the report.
    candidate_name = extract_candidate_name_from_resume(
        resume_text,
        resume_filename
    )

    # 4. MATCH RESUME WITH JOB DESCRIPTION
    try:
        keyword_result = match_keywords(resume_text, jd_text)
    except Exception as e:
        return error_page(
            "Keyword Matching Error",
            str(e),
            "/job-matcher"
        )

    match_percentage = round(
        keyword_result.overall_keyword_score * 100, 1
    )

    similarity_score = round(
        float(keyword_result.similarity_score), 2
    )

    # 5. ATS ANALYSIS
    try:
        ats_report = analyze_resume(
            resume_path,
            jd_text=jd_text,
            target_title=""
        )
    except Exception as e:
        return error_page(
            "ATS Analysis Error",
            str(e),
            "/job-matcher"
        )

    # 6. COMPLETE REPORT
    report = {
        "filename": resume_filename,
        "match_percentage": match_percentage,
        "resume_similarity": similarity_score,
        "ats_score": ats_report.get("overall_score", 0),
        "ats_score_band": ats_report.get("score_band", ""),
        "detected_role": keyword_result.detected_role,
        "matched_skills": keyword_result.matched_skills,
        "missing_skills": keyword_result.missing_skills,
        "matched_required": keyword_result.matched_required,
        "missing_required": keyword_result.missing_required,
        "matched_preferred": keyword_result.matched_preferred,
        "missing_preferred": keyword_result.missing_preferred,
        "required_keywords": keyword_result.required_keywords,
        "preferred_keywords": keyword_result.preferred_keywords,
        "required_match_score": round(
            keyword_result.required_match_score * 100, 1
        ),
        "preferred_match_score": round(
            keyword_result.preferred_match_score * 100, 1
        ),
        "ats_report": ats_report
    }

    # 7. SAVE STATE FOR BACK + DOWNLOAD REPORT
    state = {
        "resume_filename": resume_filename,
        "candidate_name": candidate_name,
        "jd_filename": jd_filename,
        "jd_method": jd_method,
        "jd_text": jd_text,
        "report": report
    }
    state_id = save_job_state(state)

    return render_template(
        "job_matcher_result.html",
        filename=resume_filename,
        match_percentage=match_percentage,
        similarity_score=similarity_score,
        ats_score=ats_report.get("overall_score", 0),
        detected_role=keyword_result.detected_role,
        matched_skills=keyword_result.matched_skills,
        missing_skills=keyword_result.missing_skills,
        report=report,
        state_id=state_id,
        candidate_name=candidate_name
    )

# ============================================================
# DOWNLOAD JOB MATCHER REPORT
# ============================================================

@app.route("/download-job-report/<state_id>")
def download_job_report(state_id):

    state = load_job_state(state_id)

    if not state:
        return error_page(
            "Report Not Found",
            "The requested report could not be found.",
            "/job-matcher"
        )

    resume_filename = state.get(
        "resume_filename",
        "Resume"
    )

    candidate_name = state.get(
        "candidate_name"
    )

    # If candidate name is missing or anonymous,
    # use the uploaded resume filename.
    if not candidate_name or candidate_name.strip().lower() in [
        "anonymous",
        "(anonymous)",
        "unknown",
        "none",
        "n/a",
        "na"
    ]:
        candidate_name = candidate_display_name(
            resume_filename
        )

    # Update the state used to generate the PDF.
    state["candidate_name"] = candidate_name

    report_filename = (
        f"{secure_filename(candidate_name)}_Resume_Report.pdf"
    )

    report_path = os.path.join(
        app.config["REPORT_FOLDER"],
        report_filename
    )

    try:
        build_job_matcher_pdf(
            state,
            report_path
        )

    except Exception as e:
        return error_page(
            "Report Generation Error",
            str(e),
            "/job-matcher"
        )

    return send_file(
        report_path,
        as_attachment=True,
        download_name=report_filename,
        mimetype="application/pdf"
    )
# ============================================================
# FILE TOO LARGE
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    return error_page(
        "File Too Large",
        "Please upload a file smaller than 10 MB.",
        "/"
    ), 413


# ============================================================
# GENERAL SERVER ERROR
# ============================================================

@app.errorhandler(500)
def internal_server_error(error):

    return error_page(
        "Server Error",
        "Something went wrong while processing your request.",
        "/"
    ), 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )