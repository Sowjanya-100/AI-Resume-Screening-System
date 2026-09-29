# 🤖 AI Resume Screening System

An AI-powered resume analysis and job matching web application built with **Python, Flask, NLP techniques, HTML, CSS, and JavaScript**.

The system helps job seekers evaluate their resumes for ATS compatibility and compare their resumes with a specific job description.

---

## 🚀 Project Overview

Modern recruitment systems often use **Applicant Tracking Systems (ATS)** to screen resumes before they reach recruiters.

This project provides a simple web interface where users can:

* Check their resume's ATS compatibility
* Identify possible formatting and structure issues
* View ATS score and recommendations
* Compare a resume with a job description
* Identify matched and missing skills
* View resume-to-job-description similarity
* Generate downloadable PDF reports
---
## 🌐 Live Demo

Try the deployed application:

**AI Resume Screening System — [Live Demo](https://ai-resume-screening-system-n5ys.onrender.com)**

> Note: The application is hosted on Render's Free plan, so the first request after a period of inactivity may take some time while the service starts.
---

## ✨ Key Features

### 📄 ATS Resume Checker

Upload a **PDF or DOCX resume** and analyze:

* Resume structure
* Contact information
* Resume sections
* Date formatting
* ATS readability
* Formatting issues
* Tables and layout-related issues
* Missing or incomplete information
* Overall ATS compatibility

The system provides:

> **ATS Score + Score Breakdown + Warnings + Recommendations**

---

### 🎯 Job Description Matcher

Compare your resume against a job description.

The system identifies:

* Detected job role
* Required skills
* Preferred skills
* Matched skills
* Missing skills
* Keyword match percentage
* Resume-JD similarity
* ATS score

The matching process uses **TF-IDF vectorization and cosine similarity** for text-based similarity.

---

### 📊 Analysis Dashboard

The result dashboard presents the analysis in an easy-to-understand format.

Users can view:

* Overall scores
* Score breakdown
* Matching skills
* Missing skills
* Resume information
* Recommendations
* Analysis warnings

---

### 📥 PDF Reports

The system generates downloadable PDF reports containing the analysis results.

Reports can include:

* Candidate information
* Resume information
* ATS score
* Match percentage
* Resume similarity
* Matching skills
* Missing skills
* Recommendations

---

### 🎨 User Interface

The application includes:

* Responsive web interface
* Home page
* About page
* ATS Checker
* Job Matcher
* Result dashboards
* Resume preview
* Light/Dark theme
* Learning resources
* Downloadable reports

---

## 🔄 How It Works

### ATS Analysis

```text
📄 Upload Resume
       ↓
📖 Extract Resume Text
       ↓
🔍 Analyze Resume Structure
       ↓
📝 Analyze Formatting
       ↓
📞 Check Contact Information
       ↓
📅 Analyze Dates
       ↓
📊 Calculate ATS Score
       ↓
💡 Generate Recommendations
       ↓
📥 Download Report
```

### Job Matching

```text
📄 Resume
   +
📋 Job Description
       ↓
🔍 Extract Information
       ↓
🎯 Detect Job Role
       ↓
🧩 Extract Required Skills
       ↓
🤝 Match Resume Skills
       ↓
📊 Calculate Match Percentage
       ↓
📈 Calculate Text Similarity
       ↓
📋 Combine ATS Analysis
       ↓
📥 Generate PDF Report
```

---

## 🛠️ Technologies Used

| Category          | Technologies              |
| ----------------- | ------------------------- |
| Backend           | Python, Flask             |
| Frontend          | HTML, CSS, JavaScript     |
| PDF Processing    | pdfplumber                |
| DOCX Processing   | python-docx               |
| Fuzzy Matching    | RapidFuzz                 |
| Text Similarity   | scikit-learn              |
| Similarity Method | TF-IDF, Cosine Similarity |
| PDF Reports       | ReportLab                 |
| Data              | CSV                       |
| Development       | VS Code                   |

---

## 📁 Project Structure

```text
AI-Resume-Screening-System/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── nlp/
│   ├── analyzer.py
│   ├── extractor.py
│   ├── structure_checker.py
│   ├── formatting_checker.py
│   └── keyword_matcher.py
│
├── templates/
│   ├── index.html
│   ├── about.html
│   ├── ats_checker.html
│   ├── ats_result.html
│   ├── ats_dashboard.html
│   ├── job_matcher.html
│   └── job_matcher_result.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── theme.js
│
├── skills.csv
└── role_skills.csv
```

---

## 💻 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Sowjanya-100/AI-Resume-Screening-System.git
```

### 2. Open the project

```bash
cd AI-Resume-Screening-System
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

Open the local Flask address shown in the terminal.

---

## 📄 Supported Resume Formats

Currently supported:

* PDF
* DOCX

Maximum upload size:

**10 MB**

---

## 🔐 Privacy & Security

Uploaded resumes and generated reports are intended to be handled locally during development.

Temporary uploaded files and generated reports are excluded from the GitHub repository through `.gitignore`.

Do not upload real resumes, personal documents, or other sensitive information to GitHub.

For production deployment, additional security, storage, authentication, and data-protection measures should be implemented.

---

## 🎯 Project Goals

This project was developed to explore how NLP and automated document analysis can be used to assist with:

* Resume screening
* ATS compatibility analysis
* Job-description matching
* Skill gap identification
* Resume improvement

The goal is to provide users with **clear, actionable resume feedback** rather than only displaying a single score.

---

## 🔮 Future Enhancements

Possible future improvements include:

* Advanced semantic resume matching
* More comprehensive skill extraction
* Additional job-role categories
* User authentication
* Database integration
* Secure cloud storage
* Resume history
* Personalized career recommendations
* More advanced ATS rules
* Production-level security
* Cloud deployment

---

## 📌 Current Version

This repository contains the **Flask-based version** of the project.

An earlier Streamlit prototype was developed during the initial stage of the project. The current implementation was redesigned using Flask with a separate HTML/CSS/JavaScript frontend and Python analysis modules.

---

## ⚠️ Disclaimer

The scores and recommendations generated by this application are intended for guidance and should not be considered a guarantee of how a specific ATS or employer will evaluate a resume.

---

## 👩‍💻 Author

**Dokkari Sowjanya**

B.Tech(Computer Science and Engineering)

Interested in:

* Python
* Data Analytics
* Salesforce
* Cloud Technologies
* AI/NLP
* Software Development


