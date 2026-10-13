import random
import streamlit as st
import sqlite3
from datetime import date

# ----------------------------------
# PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="CampusConnect AI",
    page_icon="🎓",
    layout="wide"
)
# ==========================================
# CAMPUSCONNECT AI — PROFESSIONAL THEME
# ==========================================

st.markdown("""
<style>

/* Main application background */
.stApp {
    background-color: #F5F7FB;
    color: #172B4D;
}

/* Main content spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Main headings */
h1, h2, h3 {
    color: #17365D !important;
    font-weight: 700 !important;
}

/* Paragraphs and general text */
p, label, .stMarkdown {
    color: #334155;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    background-color: #2457C5;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1rem;
    font-weight: 600;
    transition: 0.2s ease;
}

/* Button hover effect */
.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #173F99;
    color: white;
    border: none;
}

/* Input fields */
.stTextInput input,
.stTextArea textarea,
.stDateInput input,
.stTimeInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 8px;
}

/* Section dividers */
hr {
    border-color: #DCE4F0;
}

/* Containers and cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #EAF0FA;
}

/* Metric labels */
div[data-testid="stMetricLabel"] {
    color: #526581;
    font-weight: 600;
}

/* Metric values */
div[data-testid="stMetricValue"] {
    color: #2457C5;
    font-weight: 700;
}

/* Keep layout responsive */
@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
}

</style>
""", unsafe_allow_html=True)

DB_NAME = "campusconnect.db"


# ----------------------------------
# DATABASE FUNCTIONS
# ----------------------------------

def create_database():
    connection = sqlite3.connect(DB_NAME)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            deadline TEXT NOT NULL,
            priority TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()


def add_task(title, category, deadline, priority):
    connection = sqlite3.connect(DB_NAME)

    connection.execute(
        """
        INSERT INTO tasks
        (title, category, deadline, priority)
        VALUES (?, ?, ?, ?)
        """,
        (title, category, deadline.isoformat(), priority)
    )

    connection.commit()
    connection.close()


def get_tasks():
    connection = sqlite3.connect(DB_NAME)

    tasks = connection.execute(
        """
        SELECT id, title, category, deadline, priority, completed
        FROM tasks
        ORDER BY deadline ASC
        """
    ).fetchall()

    connection.close()
    return tasks


def complete_task(task_id):
    connection = sqlite3.connect(DB_NAME)

    connection.execute(
        "UPDATE tasks SET completed = 1 WHERE id = ?",
        (task_id,)
    )

    connection.commit()
    connection.close()


# ----------------------------------
# INITIALIZE APPLICATION
# ----------------------------------

create_database()

st.title("🎓 CampusConnect AI")

st.subheader("Your Smart Campus & Academic Companion")

st.write(
    "Manage your assignments, deadlines, and college events "
    "in one place."
)

st.divider()


# ----------------------------------
# DASHBOARD
# ----------------------------------

tasks = get_tasks()
today = date.today()

assignments = [
    task for task in tasks
    if task[2] == "Assignment"
]

events = [
    task for task in tasks
    if task[2] == "College Event"
]

pending = [
    task for task in tasks
    if task[5] == 0
]

overdue = [
    task for task in pending
    if date.fromisoformat(task[3]) < today
]

approaching = [
    task for task in pending
    if 0 <= (date.fromisoformat(task[3]) - today).days <= 2
]

upcoming = [
    task for task in pending
    if (date.fromisoformat(task[3]) - today).days > 2
]

st.header("📊 Your Academic Dashboard")

# First row of dashboard cards
col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.metric("📚 Assignments", len(assignments))

with col2:
    st.metric("🎓 College Events", len(events))

with col3:
    st.metric("⏳ Pending Tasks", len(pending))

# Second row of dashboard cards
col4, col5, col6 = st.columns(3, gap="medium")

with col4:
    st.metric("🔴 Overdue", len(overdue))

with col5:
    st.metric("⏰ Due Within 2 Days", len(approaching))

with col6:
    st.metric("🟢 Upcoming", len(upcoming))


# ----------------------------------
# ADD ASSIGNMENTS AND EVENTS
# ----------------------------------

st.header("➕ Add an Assignment or Event")

with st.form("task_form"):

    title = st.text_input(
        "Assignment or event name",
        placeholder="e.g. Mathematics assignment"
    )

    category = st.selectbox(
        "Type",
        ["Assignment", "College Event"]
    )

    deadline = st.date_input(
        "Deadline or event date",
        value=today
    )

    priority = st.selectbox(
        "Priority",
        ["High", "Medium", "Low"]
    )

    submitted = st.form_submit_button("Save to Timeline")

    if submitted:

        if not title.strip():
            st.error("Please enter a name first.")

        elif deadline < today:
            st.error("Please choose today or a future date.")

        else:
            add_task(
                title.strip(),
                category,
                deadline,
                priority
            )

            st.success("Saved successfully!")
            st.rerun()


st.divider()


# ----------------------------------
# SMART DEADLINE ALERTS
# ----------------------------------

st.header("📅 Your Assignment & Event Timeline")

tasks = get_tasks()

if not tasks:

    st.info(
        "No tasks yet. Add your first assignment or event above."
    )

else:

    for task in tasks:

        (
            task_id,
            title,
            category,
            deadline_text,
            priority,
            completed
        ) = task

        deadline_date = date.fromisoformat(deadline_text)

        days_left = (deadline_date - today).days

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            with col1:

                st.subheader(title)

                st.write(f"**Type:** {category}")

                st.write(
                    f"**Date:** {deadline_date.strftime('%d %b %Y')}"
                )

                st.write(f"**Priority:** {priority}")

                # Smart deadline alerts

                if completed:
                    st.success("✅ Completed")

                elif days_left < 0:
                    st.error(
                        f"🔴 Overdue by {abs(days_left)} day(s)!"
                    )

                elif days_left == 0:
                    st.error("🚨 Due today!")

                elif days_left == 1:
                    st.warning("🟠 Due tomorrow!")

                elif days_left <= 2:
                    st.warning(
                        f"⚠️ Deadline approaching! "
                        f"{days_left} days left."
                    )

                else:
                    st.success(
                        f"🟢 {days_left} days remaining."
                    )

            with col2:

                if not completed:

                    if st.button(
                        "Mark Complete",
                        key=f"complete_{task_id}"
                    ):
                        complete_task(task_id)
                        st.rerun()

                else:
                    st.write("✅ Done") 

                    # ----------------------------------
# SMART STUDY PLANNER
# ----------------------------------

st.divider()

st.header("📚 Smart Study Planner")

st.write(
    "Create a simple study schedule based on your subjects "
    "and the time you have available."
)

with st.form("study_planner_form"):

    subjects_input = st.text_area(
        "Enter your subjects (one per line)",
        placeholder="Mathematics\nPython\nElectronics\nEnglish"
    )

    available_hours = st.number_input(
        "How many hours can you study today?",
        min_value=1,
        max_value=12,
        value=3
    )

    generate_plan = st.form_submit_button(
        "Generate Study Plan"
    )

if generate_plan:

    subjects = [
        subject.strip()
        for subject in subjects_input.splitlines()
        if subject.strip()
    ]

    if not subjects:
        st.warning("Please enter at least one subject.")

    elif available_hours < len(subjects):
        st.warning(
            "You have more subjects than available study hours. "
            "Increase your study time or enter fewer subjects."
        )

    else:
        st.subheader("🗓️ Your Study Schedule")

        # Give every subject one hour first.
        remaining_hours = int(available_hours) - len(subjects)

        # Distribute the remaining time between subjects.
        study_hours = [1] * len(subjects)

        for i in range(remaining_hours):
            study_hours[i % len(subjects)] += 1

        for index, subject in enumerate(subjects):

            st.write(
                f"**Session {index + 1}: {subject}** "
                f"— {study_hours[index]} hour(s)"
            )

        st.success(
            f"Your study plan is ready! "
            f"Total planned study time: {int(available_hours)} hours."
        )

        # ----------------------------------
# PDF DOCUMENT READER WITH OCR
# ----------------------------------

st.divider()

st.header("📄 AI Document Assistant")

st.write(
    "Upload college notes in PDF format. "
    "CampusConnect AI can extract text from normal "
    "PDFs and use OCR to read scanned pages."
)

uploaded_file = st.file_uploader(
    "Upload your PDF notes",
    type=["pdf"],
    key="pdf_upload"
)

if uploaded_file is not None:

    import fitz
    import pytesseract
    from PIL import Image
    from io import BytesIO

    # Tell Python where Tesseract is installed.
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    if st.button("🔍 Extract Text from PDF"):

        pdf_document = fitz.open(
            stream=uploaded_file.getvalue(),
            filetype="pdf"
        )

        extracted_pages = []
        progress = st.progress(0)

        for page_number, page in enumerate(pdf_document):

            # First, try extracting selectable text.
            page_text = page.get_text().strip()

            # If no text exists, use OCR.
            if not page_text:

                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                    alpha=False
                )

                image = Image.open(
                    BytesIO(pix.tobytes("png"))
                )

                page_text = pytesseract.image_to_string(
                    image,
                    lang="eng"
                ).strip()

            extracted_pages.append(
                f"--- Page {page_number + 1} ---\n{page_text}"
            )

            progress.progress(
                (page_number + 1) / len(pdf_document)
            )

        pdf_document.close()

        extracted_text = "\n\n".join(extracted_pages)

        if extracted_text.strip():
            st.success("PDF text extraction completed!")

            st.write(
                f"Pages processed: {len(extracted_pages)}"
            )

            st.text_area(
                "Extracted PDF Text",
                value=extracted_text,
                height=350
            )

            st.download_button(
                "⬇️ Download Extracted Text",
                data=extracted_text,
                file_name="extracted_notes.txt",
                mime="text/plain"
            )

        else:
            st.warning(
                "No readable text was found in this PDF."
            )

st.divider()

st.header("📄 AI Document Assistant")

st.write(
    "Upload your college notes in PDF format "
    "and extract their text."
)

uploaded_file = st.file_uploader(
    "Upload your PDF notes",
    type=["pdf"]
)

if uploaded_file is not None:

    import fitz

    st.success("PDF uploaded successfully!")

    pdf_document = fitz.open(
        stream=uploaded_file.getvalue(),
        filetype="pdf"
    )

    st.write(f"Total pages: {len(pdf_document)}")

    extracted_text = ""

    for page_number, page in enumerate(pdf_document):
        extracted_text += page.get_text() + "\n"

    pdf_document.close()

    if extracted_text.strip():

        st.subheader("📝 Extracted Text")

        st.text_area(
            "Text from your PDF",
            value=extracted_text,
            height=300
        )

        st.download_button(
            label="Download Extracted Text",
            data=extracted_text,
            file_name="extracted_notes.txt",
            mime="text/plain"
        )

    else:

        st.warning(
            "No selectable text was found. "
            "This PDF may contain scanned images."
        )

        # ----------------------------------
# PDF DOCUMENT READER WITH OCR
# ----------------------------------

st.divider()

st.header("📄 AI Document Assistant")

st.write(
    "Upload college notes in PDF format. "
    "CampusConnect AI can extract text from normal "
    "PDFs and use OCR to read scanned pages."
)

uploaded_file = st.file_uploader(
    "Upload your PDF notes",
    type=["pdf"],
    key="pdf_upload_2"
)

if uploaded_file is not None:

    import fitz
    import pytesseract
    from PIL import Image
    from io import BytesIO

    # Tell Python where Tesseract is installed.
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    if st.button("🔍 Extract Text from PDF"):

        pdf_document = fitz.open(
            stream=uploaded_file.getvalue(),
            filetype="pdf"
        )

        extracted_pages = []
        progress = st.progress(0)

        for page_number, page in enumerate(pdf_document):

            # First, try extracting selectable text.
            page_text = page.get_text().strip()

            # If no text exists, use OCR.
            if not page_text:

                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                    alpha=False
                )

                image = Image.open(
                    BytesIO(pix.tobytes("png"))
                )

                page_text = pytesseract.image_to_string(
                    image,
                    lang="eng"
                ).strip()

            extracted_pages.append(
                f"--- Page {page_number + 1} ---\n{page_text}"
            )

            progress.progress(
                (page_number + 1) / len(pdf_document)
            )

        pdf_document.close()

        extracted_text = "\n\n".join(extracted_pages)

        if extracted_text.strip():
            st.success("PDF text extraction completed!")

            st.write(
                f"Pages processed: {len(extracted_pages)}"
            )

            st.text_area(
                "Extracted PDF Text",
                value=extracted_text,
                height=350
            )

            st.download_button(
                "⬇️ Download Extracted Text",
                data=extracted_text,
                file_name="extracted_notes.txt",
                mime="text/plain"
            )

        else:
            st.warning(
                "No readable text was found in this PDF."
            )

            # ----------------------------------
# KEY POINTS EXTRACTOR
# ----------------------------------

st.divider()

st.header("🔑 Key Points Extractor")

st.write(
    "Find frequently used words in your notes "
    "to help with quick revision."
)

notes_text = st.text_area(
    "Paste your notes here",
    height=200,
    key="key_points_notes",
    placeholder="Paste text from your PDF here..."
)

if st.button("Find Key Points", key="find_key_points"):

    import re
    from collections import Counter

    stop_words = {
        "the", "is", "are", "was", "were", "a", "an",
        "and", "or", "but", "in", "on", "at", "to",
        "of", "for", "with", "by", "from", "as", "it",
        "this", "that", "be", "can", "will", "has",
        "have", "had", "which", "what", "when", "where",
        "who", "how", "their", "there", "these", "those"
    }

    words = re.findall(r"\b[a-zA-Z]{3,}\b", notes_text.lower())

    keywords = [
        word for word in words
        if word not in stop_words
    ]

    counts = Counter(keywords)

    if not notes_text.strip():
        st.warning("Please paste your notes first.")

    elif not counts:
        st.warning("No suitable English words were found.")

    else:
        st.subheader("📌 Frequently Used Terms")

        for word, frequency in counts.most_common(10):
            st.write(f"• **{word.title()}** — appears {frequency} times")

        st.info(
            "These are frequently used terms, not guaranteed "
            "exam-important concepts."
        )

        # ----------------------------------
# AI NOTES SUMMARIZER
# ----------------------------------

st.divider()

st.header("🧠 AI Notes Summarizer")

st.write(
    "Convert long college notes into shorter notes "
    "for quick revision."
)

summary_text = st.text_area(
    "Paste your notes here",
    height=250,
    key="summary_notes_input",
    placeholder="Paste your college notes here..."
)

summary_length = st.selectbox(
    "Choose summary length",
    ["Short", "Medium", "Long"],
    key="summary_length_choice"
)

if st.button("✨ Summarize My Notes", key="summarize_notes_button"):

    import re

    if not summary_text.strip():

        st.warning("Please paste your notes first.")

    else:

        # Split the text into sentences
        sentences = re.split(
            r'(?<=[.!?])\s+',
            summary_text.strip()
        )

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        if len(sentences) <= 2:

            summary = " ".join(sentences)

        else:

            # Remove common words when counting keywords
            stop_words = {
                "the", "is", "are", "was", "were",
                "a", "an", "and", "or", "but",
                "in", "on", "at", "to", "of",
                "for", "with", "by", "from", "as",
                "it", "this", "that", "be", "can",
                "will", "has", "have", "had", "which",
                "what", "when", "where", "who", "how",
                "their", "there", "these", "those",
                "its", "they", "them", "we", "you"
            }

            # Count meaningful words
            words = re.findall(
                r"\b[a-zA-Z]{3,}\b",
                summary_text.lower()
            )

            word_counts = {}

            for word in words:
                if word not in stop_words:
                    word_counts[word] = (
                        word_counts.get(word, 0) + 1
                    )

            # Score sentences by keyword frequency
            sentence_scores = []

            for index, sentence in enumerate(sentences):

                sentence_words = re.findall(
                    r"\b[a-zA-Z]{3,}\b",
                    sentence.lower()
                )

                score = sum(
                    word_counts.get(word, 0)
                    for word in sentence_words
                    if word not in stop_words
                )

                sentence_scores.append(
                    (index, score, sentence)
                )

            # Select the requested number of sentences
            if summary_length == "Short":
                number_to_select = max(
                    1, round(len(sentences) * 0.25)
                )

            elif summary_length == "Medium":
                number_to_select = max(
                    1, round(len(sentences) * 0.50)
                )

            else:
                number_to_select = max(
                    1, round(len(sentences) * 0.75)
                )

            best_sentences = sorted(
                sentence_scores,
                key=lambda item: item[1],
                reverse=True
            )[:number_to_select]

            # Keep the original sentence order
            best_sentences.sort(
                key=lambda item: item[0]
            )

            summary = " ".join(
                item[2] for item in best_sentences
            )

        st.success("Your revision notes are ready!")

        st.subheader("📚 Your Summary")

        st.write(summary)

        st.download_button(
            "⬇️ Download Summary",
            data=summary,
            file_name="campusconnect_summary.txt",
            mime="text/plain",
            key="download_summary_button"
        )

        original_words = len(summary_text.split())
        summary_words = len(summary.split())

        st.caption(
            f"Original: {original_words} words | "
            f"Summary: {summary_words} words"
        )

        st.info(
            "This version selects sentences using word frequency. "
            "Check the summary against your original notes to "
            "make sure important details are not missing."
        )

        # ----------------------------------
# SMART QUIZ GENERATOR
# ----------------------------------

import re
import random

st.divider()
st.header("📝 Smart Quiz Generator")

st.write(
    "Create a multiple-choice practice quiz "
    "from your college notes."
)

quiz_notes = st.text_area(
    "Paste your notes here",
    height=220,
    key="quiz_notes_input",
    placeholder="Paste your study notes here..."
)

if st.button("🎯 Generate Quiz", key="generate_quiz_button"):

    if not quiz_notes.strip():
        st.warning("Please paste your notes first.")

    else:
        sentences = re.split(
            r'(?<=[.!?])\s+',
            quiz_notes.strip()
        )

        sentences = [
            s.strip()
            for s in sentences
            if len(s.split()) >= 5
        ]

        # Extract words that can be used as answers.
        all_words = re.findall(
            r"\b[A-Za-z][A-Za-z'-]*\b",
            quiz_notes
        )

        unique_words = list(dict.fromkeys(
            word for word in all_words
            if len(word) >= 4
        ))

        questions = []

        for sentence in sentences:

            # Prefer the word following a definition phrase.
            match = re.search(
                r"\b(?:is|are|means|refers to)\s+"
                r"([A-Za-z][A-Za-z'-]*)",
                sentence,
                re.IGNORECASE
            )

            if match:
                answer = match.group(1)
            else:
                candidates = re.findall(
                    r"\b[A-Za-z][A-Za-z'-]{4,}\b",
                    sentence
                )

                if not candidates:
                    continue

                answer = max(candidates, key=len)

            # Avoid duplicate questions with the same answer.
            if any(
                q["answer"].lower() == answer.lower()
                for q in questions
            ):
                continue

            question_text = re.sub(
                r"\b" + re.escape(answer) + r"\b",
                "_____",
                sentence,
                count=1,
                flags=re.IGNORECASE
            )

            # Build three alternative answers.
            distractors = [
                word for word in unique_words
                if word.lower() != answer.lower()
            ]

            random.shuffle(distractors)

            options = [answer]

            for word in distractors:
                if word.lower() not in [
                    option.lower() for option in options
                ]:
                    options.append(word)

                if len(options) == 4:
                    break

            # Ensure exactly four choices.
            fallback_options = [
                "Programming",
                "Database",
                "Algorithm",
                "Computer",
                "Network",
                "Software",
                "Hardware"
            ]

            for word in fallback_options:
                if word.lower() not in [
                    option.lower() for option in options
                ]:
                    options.append(word)

                if len(options) == 4:
                    break

            options = options[:4]

            if len(options) == 4:
                random.shuffle(options)

                questions.append({
                    "question": question_text,
                    "answer": answer,
                    "options": options,
                    "sentence": sentence
                })

        if not questions:
            st.warning(
                "Not enough suitable sentences were found. "
                "Please paste a few complete sentences."
            )

        else:
            random.shuffle(questions)

            # Limit the quiz to five questions.
            questions = questions[:5]

            st.session_state["campus_quiz"] = questions
            st.session_state["campus_quiz_notes"] = quiz_notes

            st.success(
                f"Created {len(questions)} practice questions!"
            )


# ----------------------------------
# DISPLAY QUIZ
# ----------------------------------

if "campus_quiz" in st.session_state:

    questions = st.session_state["campus_quiz"]

    st.subheader("📚 Your Practice Quiz")

    with st.form("campus_quiz_form"):

        user_answers = []

        for index, question in enumerate(questions):

            st.write(
                f"**Question {index + 1}:** "
                f"Complete the sentence:"
            )

            st.write(question["question"])

            # Use the four options stored with this question.
            user_answer = st.radio(
                "Select one answer:",
                question["options"],
                index=None,
                key=f"campus_quiz_answer_{index}"
            )

            user_answers.append(user_answer)

        submitted = st.form_submit_button(
            "✅ Check My Answers"
        )

    if submitted:

        score = 0

        st.subheader("📊 Your Results")

        for index, question in enumerate(questions):

            user_answer = user_answers[index]
            correct_answer = question["answer"]

            if (
                user_answer is not None
                and user_answer.lower() == correct_answer.lower()
            ):
                score += 1
                st.success(f"Question {index + 1}: Correct!")

            else:
                st.error(
                    f"Question {index + 1}: "
                    f"Correct answer: {correct_answer}"
                )

            st.caption(
                f"Original note: {question['sentence']}"
            )

        percentage = round(
            score / len(questions) * 100
        )

        st.metric(
            "Your Score",
            f"{score}/{len(questions)}",
            f"{percentage}%"
        )

        st.info(
            "This is a basic rule-based quiz generator. "
            "Some questions and alternative answers may not "
            "be suitable for every topic, so check the "
            "results against your original notes."
        )

        
# ==========================================
# INDIAN YEAR CALENDAR — REDESIGNED
# ==========================================

import calendar
from datetime import date
import sqlite3
import holidays
import streamlit as st

st.divider()
st.header("🇮🇳 Indian Year Calendar")
st.caption(
    "Choose a date, check holidays, and manage your "
    "personal notes, exams, assignments, and college events."
)

# ------------------------------------------
# DATABASE — KEEP EXISTING NOTES
# ------------------------------------------

calendar_connection = sqlite3.connect("campusconnect.db")

calendar_connection.execute("""
    CREATE TABLE IF NOT EXISTS calendar_notes (
        note_date TEXT PRIMARY KEY,
        note_title TEXT,
        note_text TEXT,
        category TEXT
    )
""")
calendar_connection.commit()

try:

    
    # --------------------------------------
    # DATE SELECTION — MONTH AND YEAR
    # --------------------------------------

    st.subheader("📅 Choose a month and year")

    current_date = date.today()

    year_options = list(
        range(current_date.year - 5, current_date.year + 11)
    )

    month_options = {
        calendar.month_name[m]: m
        for m in range(1, 13)
    }

    col_month, col_year = st.columns(2)

    with col_month:
        chosen_month_name = st.selectbox(
            "Month",
            list(month_options.keys()),
            index=current_date.month - 1,
            key="calendar_month_choice"
        )

    with col_year:
        chosen_year = st.selectbox(
            "Year",
            year_options,
            index=year_options.index(current_date.year),
            key="calendar_year_choice"
        )

    selected_month = month_options[chosen_month_name]
    selected_year = chosen_year

    default_day = min(
        current_date.day,
        calendar.monthrange(selected_year, selected_month)[1]
    )

    default_selected_date = date(
        selected_year, selected_month, default_day
    )

    selected_date = st.date_input(
        "Choose a specific date for your note",
        value=default_selected_date,
        key="calendar_date_picker"
    )

    # Keep the dropdowns and selected date in sync.
    if (
        selected_date.month != selected_month
        or selected_date.year != selected_year
    ):
        st.info(
            "The selected date belongs to another month or year. "
            "Choose that month and year above to update the calendar."
        )
        selected_month = selected_date.month
        selected_year = selected_date.year

    selected_date_key = selected_date.isoformat()
    st.session_state["selected_calendar_date"] = selected_date_key

    indian_holidays = holidays.country_holidays(
        "IN",
        years=selected_year,
        observed=True
    )
    holiday_name = indian_holidays.get(selected_date)


    # --------------------------------------
    # SELECTED DATE SUMMARY
    # --------------------------------------

    st.markdown("### 🗓️ Selected Date")

    st.write(
        f"**{selected_date.strftime('%A, %d %B %Y')}**"
    )

    if selected_date == date.today():
        st.info("🔵 Today")

    if holiday_name:
        st.success(f"🎉 Indian holiday: {holiday_name}")

    # --------------------------------------
    # MONTH CALENDAR
    # --------------------------------------

    st.divider()
    st.subheader(
        f"🗓️ {calendar.month_name[selected_month]} {selected_year}"
    )

    st.caption(
        "🎉 Holiday  ·  📝 Saved note  ·  🔵 Today  ·  "
        "The date picker above changes the displayed month."
    )

    month_notes = {
        row[0]: row
        for row in calendar_connection.execute(
            """
            SELECT note_date, note_title, note_text, category
            FROM calendar_notes
            WHERE note_date >= ? AND note_date <= ?
            """,
            (
                date(selected_year, selected_month, 1).isoformat(),
                date(
                    selected_year,
                    selected_month,
                    calendar.monthrange(
                        selected_year,
                        selected_month
                    )[1]
                ).isoformat()
            )
        ).fetchall()
    }

    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday_columns = st.columns(7)

    for index, weekday in enumerate(weekdays):
        weekday_columns[index].markdown(
            f"**{weekday}**"
        )

    month_matrix = calendar.monthcalendar(
        selected_year,
        selected_month
    )

    for week in month_matrix:
        day_columns = st.columns(7)

        for index, day_number in enumerate(week):
            with day_columns[index]:
                if day_number == 0:
                    st.write(" ")
                    continue

                this_date = date(
                    selected_year,
                    selected_month,
                    day_number
                )
                this_key = this_date.isoformat()

                indicators = []

                if this_date in indian_holidays:
                    indicators.append("🎉")

                if this_key in month_notes:
                    indicators.append("📝")

                if this_date == date.today():
                    indicators.append("🔵")

                if this_date == selected_date:
                    st.markdown(f"**➤ {day_number}**")
                else:
                    st.write(f"**{day_number}**")

                if indicators:
                    st.caption(" ".join(indicators))

    # --------------------------------------
    # NOTE EDITOR
    # --------------------------------------

    st.divider()
    st.subheader("📝 Notes & Instructions")

    st.write(
        f"Editing notes for **{selected_date.strftime('%d %B %Y')}**"
    )

    existing_note = calendar_connection.execute(
        """
        SELECT note_title, note_text, category
        FROM calendar_notes
        WHERE note_date = ?
        """,
        (selected_date_key,)
    ).fetchone()

    categories = [
        "Personal",
        "Exam",
        "Holiday",
        "College Event",
        "Assignment"
    ]

    category_index = (
        categories.index(existing_note[2])
        if existing_note and existing_note[2] in categories
        else 0
    )

    with st.form("calendar_notes_form"):
        note_title = st.text_input(
            "Note title",
            value=existing_note[0] if existing_note else "",
            placeholder="e.g. Mathematics exam"
        )

        note_category = st.selectbox(
            "Category",
            categories,
            index=category_index
        )

        note_text = st.text_area(
            "Instructions or details",
            value=existing_note[1] if existing_note else "",
            height=150,
            placeholder="Write your plans, reminders, or instructions here..."
        )

        save_button = st.form_submit_button(
            "💾 Save Note",
            use_container_width=True
        )

    if save_button:
        if note_title.strip() or note_text.strip():
            calendar_connection.execute(
                """
                INSERT INTO calendar_notes
                    (note_date, note_title, note_text, category)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(note_date) DO UPDATE SET
                    note_title = excluded.note_title,
                    note_text = excluded.note_text,
                    category = excluded.category
                """,
                (
                    selected_date_key,
                    note_title.strip(),
                    note_text.strip(),
                    note_category
                )
            )
            calendar_connection.commit()
            st.success("Note saved successfully!")
            st.rerun()
        else:
            st.warning(
                "Enter a title or some details before saving."
            )

    # --------------------------------------
    # SAVED NOTES
    # --------------------------------------

    st.divider()
    st.subheader("📚 Saved Calendar Notes")

    all_notes = calendar_connection.execute(
        """
        SELECT note_date, note_title, note_text, category
        FROM calendar_notes
        ORDER BY note_date
        """
    ).fetchall()

    if all_notes:
        for note_date, title, content, category in all_notes:
            with st.expander(
                f"📌 {note_date} — {title or category}"
            ):
                st.write(f"**Category:** {category}")

                if content:
                    st.write(content)

                if note_date == selected_date_key:
                    st.caption("Currently selected date")

    else:
        st.info(
            "No saved notes yet. Choose a date and add your first note!"
        )

finally:
    calendar_connection.close()

    
# ==========================================
# CAMPUSCONNECT AI — REMINDER MANAGER
# ==========================================

import reminders
from datetime import datetime, timedelta

reminders.initialize_reminders()

st.divider()
st.header("🔔 Smart Reminder Manager")
st.caption(
    "Create reminders for assignments, exams, classes, "
    "and other important deadlines."
)

with st.form("create_reminder_form"):
    reminder_title = st.text_input(
        "Task or assignment title",
        placeholder="e.g. Submit Python assignment"
    )

    due_date = st.date_input(
        "Deadline date",
        value=date.today() + timedelta(days=1),
        key="reminder_due_date"
    )

    due_time = st.time_input(
        "Deadline time",
        value=datetime.now().replace(
            hour=9, minute=0, second=0, microsecond=0
        ).time(),
        key="reminder_due_time"
    )

    reminder_notes = st.text_area(
        "Details (optional)",
        placeholder="What do you need to finish?"
    )

    create_reminder = st.form_submit_button(
        "➕ Save Reminder",
        use_container_width=True
    )

if create_reminder:
    if not reminder_title.strip():
        st.warning("Please enter a task title.")
    else:
        deadline = datetime.combine(due_date, due_time)

        if deadline <= datetime.now():
            st.warning("Please choose a future deadline.")
        else:
            reminders.add_reminder(
                reminder_title,
                deadline.isoformat(timespec="seconds"),
                reminder_notes
            )
            st.success("Reminder saved successfully!")
            st.rerun()

st.subheader("📋 Your Reminders")

saved_reminders = reminders.get_reminders()

if not saved_reminders:
    st.info("No reminders yet. Add your first task above.")
else:
    for (
        reminder_id,
        title,
        due_at,
        notes,
        advance_sent,
        due_sent
    ) in saved_reminders:

        deadline = datetime.fromisoformat(due_at)

        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(
                "Deadline:",
                deadline.strftime("%d %B %Y, %I:%M %p")
            )

            if notes:
                st.caption(notes)

            remaining = deadline - datetime.now()

            if remaining.total_seconds() > 0:
                st.caption(
                    f"Time remaining: {remaining.days} day(s), "
                    f"{remaining.seconds // 3600} hour(s)"
                )
            else:
                st.warning("This deadline has passed.")

            if advance_sent:
                st.caption("✓ One-day alert marked as sent")

            if due_sent:
                st.caption("✓ Deadline alert marked as sent")

            if st.button(
                "🗑️ Delete Reminder",
                key=f"delete_reminder_{reminder_id}"
            ):
                reminders.delete_reminder(reminder_id)
                st.rerun()
