"""
AI Powered Quiz Generator - Streamlit Application

An application that extracts text from PPT/PPTX files and generates
interactive MCQ quizzes using OpenAI's API.
"""

import streamlit as st
import time
import json
import os
from datetime import datetime, timedelta

from utils.ppt_parser import extract_text_from_pptx, get_text_preview, get_combined_text
from utils.quiz_generator import generate_quiz
from utils.scoring import calculate_score, get_grade, get_performance_message

# ─── Page Configuration ───────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS for Dark Modern UI ────────────────────────────────────────────

def load_css():
    st.markdown("""
    <style>
        /* ── Global ─────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .stApp {
            background: #0a0a0f;
            background: linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0d0d14 100%);
        }

        /* ── Hide Streamlit Branding ──────────────────────── */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        .stDeployButton { display: none; }
        header { display: none; }

        /* ── Typography ───────────────────────────────────── */
        h1, h2, h3, h4, h5, h6, p, span, div, label {
            font-family: 'Inter', sans-serif !important;
        }

        /* ── Main Container ──────────────────────────────── */
        .main-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }

        .app-header {
            text-align: center;
            margin-bottom: 2.5rem;
        }

        .app-title {
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
        }

        .app-subtitle {
            color: #8888aa;
            font-size: 1.1rem;
            font-weight: 300;
        }

        /* ── Cards ───────────────────────────────────────── */
        .card {
            background: #151520;
            background: linear-gradient(145deg, #151520 0%, #1a1a28 100%);
            border: 1px solid #2a2a3a;
            border-radius: 16px;
            padding: 1.8rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .card:hover {
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.4);
        }

        .card-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 1.2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #2a2a3a;
        }

        .card-header h3 {
            color: #e0e0f0;
            font-size: 1.2rem;
            font-weight: 600;
            margin: 0;
        }

        .card-icon {
            font-size: 1.5rem;
        }

        /* ── File Info ───────────────────────────────────── */
        .file-info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }

        .file-info-item {
            background: #1e1e2e;
            border-radius: 12px;
            padding: 1rem 1.2rem;
            border: 1px solid #2a2a3a;
        }

        .file-info-label {
            color: #6666aa;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }

        .file-info-value {
            color: #e0e0f0;
            font-size: 1.1rem;
            font-weight: 600;
            margin-top: 4px;
        }

        /* ── Text Preview ────────────────────────────────── */
        .text-preview {
            background: #1a1a28;
            border: 1px solid #2a2a3a;
            border-radius: 12px;
            padding: 1.2rem;
            max-height: 300px;
            overflow-y: auto;
            color: #b0b0cc;
            font-size: 0.9rem;
            line-height: 1.6;
            white-space: pre-wrap;
            font-family: 'SF Mono', 'Fira Code', monospace;
        }

        .text-preview::-webkit-scrollbar {
            width: 6px;
        }
        .text-preview::-webkit-scrollbar-track {
            background: #1a1a28;
        }
        .text-preview::-webkit-scrollbar-thumb {
            background: #3a3a5a;
            border-radius: 3px;
        }

        /* ── Question Display ────────────────────────────── */
        .question-counter {
            text-align: center;
            color: #6666aa;
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            letter-spacing: 0.5px;
        }

        .question-progress {
            display: flex;
            justify-content: center;
            gap: 6px;
            margin-bottom: 1.5rem;
        }

        .progress-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #2a2a3a;
            transition: all 0.3s ease;
        }

        .progress-dot.active {
            background: #667eea;
            box-shadow: 0 0 12px rgba(102, 126, 234, 0.5);
        }

        .progress-dot.answered {
            background: #4a4a6a;
        }

        .progress-dot.correct {
            background: #00c853;
            box-shadow: 0 0 12px rgba(0, 200, 83, 0.3);
        }

        .progress-dot.wrong {
            background: #ff1744;
            box-shadow: 0 0 12px rgba(255, 23, 68, 0.3);
        }

        .question-text {
            color: #f0f0ff;
            font-size: 1.25rem;
            font-weight: 600;
            line-height: 1.5;
            margin-bottom: 1.5rem;
            padding: 1rem;
            background: #1a1a28;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }

        /* ── Radio Buttons Styling ───────────────────────── */
        .stRadio > div {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .stRadio > div > label {
            background: #1e1e30 !important;
            border: 2px solid #2a2a3a !important;
            border-radius: 12px !important;
            padding: 0.8rem 1rem !important;
            transition: all 0.2s ease !important;
            color: #c0c0dd !important;
            font-weight: 500 !important;
        }

        .stRadio > div > label:hover {
            border-color: #667eea !important;
            background: #252540 !important;
        }

        .stRadio > div > label[data-selected="true"] {
            border-color: #667eea !important;
            background: #252545 !important;
            box-shadow: 0 0 20px rgba(102, 126, 234, 0.15) !important;
        }

        /* ── Navigation Buttons ──────────────────────────── */
        .nav-buttons {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-top: 1.5rem;
        }

        .stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 0.6rem 1.5rem !important;
            transition: all 0.2s ease !important;
            border: none !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
        }

        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
        }

        .stButton > button[kind="secondary"] {
            background: #2a2a3a !important;
            color: #c0c0dd !important;
            border: 1px solid #3a3a5a !important;
        }

        .stButton > button[kind="secondary"]:hover {
            background: #353550 !important;
            border-color: #667eea !important;
        }

        /* ── Timer ───────────────────────────────────────── */
        .timer-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .timer-badge {
            background: linear-gradient(135deg, #1a1a2e, #2a1a3e);
            border: 1px solid #3a2a5a;
            border-radius: 50px;
            padding: 0.4rem 1rem;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
            color: #c0c0dd;
            font-weight: 500;
        }

        .timer-badge.warning {
            border-color: #ff6b35;
            animation: pulse-warning 1s infinite;
        }

        .timer-badge.danger {
            border-color: #ff1744;
            animation: pulse-danger 0.5s infinite;
        }

        @keyframes pulse-warning {
            0%, 100% { box-shadow: 0 0 0 0 rgba(255, 107, 53, 0.4); }
            50% { box-shadow: 0 0 20px 5px rgba(255, 107, 53, 0.2); }
        }

        @keyframes pulse-danger {
            0%, 100% { box-shadow: 0 0 0 0 rgba(255, 23, 68, 0.4); }
            50% { box-shadow: 0 0 20px 5px rgba(255, 23, 68, 0.2); }
        }

        /* ── Score Display ──────────────────────────────── */
        .score-container {
            text-align: center;
            padding: 1.5rem 0;
        }

        .score-circle {
            width: 160px;
            height: 160px;
            border-radius: 50%;
            background: linear-gradient(135deg, #1a1a2e, #2a1a3e);
            border: 4px solid #667eea;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem;
            box-shadow: 0 0 40px rgba(102, 126, 234, 0.2);
        }

        .score-number {
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1;
        }

        .score-total {
            color: #8888aa;
            font-size: 1rem;
            margin-top: 4px;
        }

        .score-grade {
            font-size: 1.5rem;
            font-weight: 700;
            color: #f0f0ff;
            margin-top: 0.5rem;
        }

        .score-message {
            color: #b0b0cc;
            font-size: 1rem;
            margin-top: 0.3rem;
        }

        .score-bar {
            width: 100%;
            height: 8px;
            background: #2a2a3a;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 1rem;
        }

        .score-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 4px;
            transition: width 1s ease;
        }

        /* ── Result Item ─────────────────────────────────── */
        .result-item {
            background: #1e1e30;
            border: 1px solid #2a2a3a;
            border-radius: 12px;
            padding: 1.2rem;
            margin-bottom: 1rem;
        }

        .result-item.correct {
            border-left: 4px solid #00c853;
        }

        .result-item.wrong {
            border-left: 4px solid #ff1744;
        }

        .result-question {
            color: #e0e0f0;
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.8rem;
        }

        .result-answers {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.8rem;
            margin-bottom: 0.8rem;
        }

        .result-answer-tag {
            padding: 0.5rem 0.8rem;
            border-radius: 8px;
            font-size: 0.85rem;
        }

        .result-answer-tag.user {
            background: #2a1a1a;
            border: 1px solid #4a2a2a;
            color: #ff6b6b;
        }

        .result-answer-tag.correct {
            background: #1a2a1a;
            border: 1px solid #2a4a2a;
            color: #69f0ae;
        }

        .result-explanation {
            background: #151520;
            border-radius: 8px;
            padding: 0.8rem;
            color: #8888cc;
            font-size: 0.85rem;
            line-height: 1.5;
        }

        .result-explanation strong {
            color: #b0b0dd;
        }

        /* ── Action Buttons ──────────────────────────────── */
        .action-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 2rem;
        }

        /* ── Settings (Select Sliders & Dropdowns) ────────── */
        div[data-testid="stSelectbox"] > div > div {
            background: #1e1e30 !important;
            border: 2px solid #2a2a3a !important;
            border-radius: 10px !important;
            color: #e0e0f0 !important;
        }

        div[data-testid="stSelectbox"] > div > div:hover {
            border-color: #667eea !important;
        }

        div[data-testid="stSelectbox"] > div > div:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
        }

        div[data-testid="stSlider"] > div {
            padding: 0.5rem 0;
        }

        div[data-testid="stSlider"] > div > div > div {
            color: #e0e0f0 !important;
        }

        div[data-testid="stSlider"] > div > div > div > div {
            background: #667eea !important;
        }

        /* ── File Uploader ───────────────────────────────── */
        .stFileUploader > div {
            background: #151520 !important;
            border: 2px dashed #3a3a5a !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            transition: all 0.3s ease !important;
        }

        .stFileUploader > div:hover {
            border-color: #667eea !important;
            background: #1a1a28 !important;
        }

        .stFileUploader > div > div > div > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            border-radius: 10px !important;
            color: white !important;
            font-weight: 600 !important;
        }

        /* ── Success / Info / Error Messages ─────────────── */
        .stAlert {
            background: #1a1a28 !important;
            border: 1px solid #2a2a3a !important;
            border-radius: 12px !important;
            color: #c0c0dd !important;
        }

        .stAlert > div > div > svg {
            color: #667eea !important;
        }

        /* ── Expander ────────────────────────────────────── */
        .streamlit-expanderHeader {
            background: #1a1a28 !important;
            border: 1px solid #2a2a3a !important;
            border-radius: 10px !important;
            color: #c0c0dd !important;
            font-weight: 500 !important;
        }

        .streamlit-expanderContent {
            background: #151520 !important;
            border: 1px solid #2a2a3a !important;
            border-top: none !important;
            border-radius: 0 0 10px 10px !important;
        }

        /* ── Spinner ─────────────────────────────────────── */
        .stSpinner > div > div {
            border-color: #667eea transparent transparent transparent !important;
        }

        /* ── Divider ─────────────────────────────────────── */
        hr {
            border-color: #2a2a3a !important;
            margin: 1.5rem 0 !important;
        }

        /* ── Responsive ──────────────────────────────────── */
        @media (max-width: 768px) {
            .app-title {
                font-size: 2rem;
            }
            .file-info-grid {
                grid-template-columns: 1fr;
            }
            .result-answers {
                grid-template-columns: 1fr;
            }
            .nav-buttons {
                flex-direction: column;
            }
            .nav-buttons .stButton {
                width: 100%;
            }
            .nav-buttons .stButton > button {
                width: 100%;
            }
            .action-buttons {
                flex-direction: column;
            }
            .action-buttons .stButton {
                width: 100%;
            }
            .score-circle {
                width: 120px;
                height: 120px;
            }
            .score-number {
                font-size: 2rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)


# ─── Session State Initialization ──────────────────────────────────────────────

def init_session_state():
    defaults = {
        "page": "upload",          # upload, quiz, results
        "parsed_data": None,
        "questions": None,
        "current_q": 0,
        "user_answers": {},
        "quiz_start_time": None,
        "quiz_active": False,
        "timer_end": None,
        "show_explanation": False,
        "quiz_submitted": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ─── Upload Page ───────────────────────────────────────────────────────────────

def render_upload_page():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="app-header">
        <div class="app-title">🧠 AI Quiz Generator</div>
        <div class="app-subtitle">Upload a presentation to generate an interactive quiz</div>
    </div>
    """, unsafe_allow_html=True)

    # Upload Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="card-header">
        <span class="card-icon">📂</span>
        <h3>Upload Presentation</h3>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose a PPT or PPTX file",
        type=["ppt", "pptx"],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_file.name)

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            with st.spinner("📖 Extracting text from slides..."):
                parsed_data = extract_text_from_pptx(temp_path)

            st.session_state.parsed_data = parsed_data
            st.session_state.uploaded_file_path = temp_path

            # Show file info
            st.markdown('<div class="file-info-grid">', unsafe_allow_html=True)

            cols = st.columns(3)
            with cols[0]:
                st.markdown(f"""
                <div class="file-info-item">
                    <div class="file-info-label">File Name</div>
                    <div class="file-info-value">📄 {parsed_data['file_name']}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f"""
                <div class="file-info-item">
                    <div class="file-info-label">Slides</div>
                    <div class="file-info-value">📊 {parsed_data['slide_count']}</div>
                </div>
                """, unsafe_allow_html=True)
            with cols[2]:
                st.markdown(f"""
                <div class="file-info-item">
                    <div class="file-info-label">File Size</div>
                    <div class="file-info-value">💾 {parsed_data['file_size']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Text preview
            preview_text = get_text_preview(parsed_data["slides"], max_chars=800)
            with st.expander("📝 Preview Extracted Text", expanded=False):
                st.markdown(
                    f'<div class="text-preview">{preview_text}</div>',
                    unsafe_allow_html=True
                )

        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.session_state.parsed_data = None
            return

    st.markdown('</div>', unsafe_allow_html=True)  # end card

    # Quiz Settings Card (only show if file is parsed)
    if st.session_state.parsed_data is not None:
        st.markdown('<div class="card" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
        st.markdown("""
        <div class="card-header">
            <span class="card-icon">⚙️</span>
            <h3>Quiz Settings</h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            num_questions = st.slider(
                "Number of Questions",
                min_value=5,
                max_value=30,
                value=10,
                step=1,
                help="Select how many questions you want in the quiz"
            )

        with col2:
            difficulty = st.selectbox(
                "Difficulty Level",
                options=["Simple", "Medium", "Complex"],
                index=1,
                help="Choose the difficulty level for questions"
            )

        st.markdown('<div style="text-align: center; margin-top: 1.5rem;">', unsafe_allow_html=True)
        if st.button("🚀 Generate Quiz", type="primary", use_container_width=True):
            text_content = get_combined_text(st.session_state.parsed_data["slides"])

            if not text_content.strip():
                st.error("❌ No text content found in the presentation. Please upload a file with text content.")
                return

            try:
                with st.spinner(f"🧠 Generating {num_questions} {difficulty.lower()} questions..."):
                    questions = generate_quiz(text_content, num_questions, difficulty)

                st.session_state.questions = questions
                st.session_state.current_q = 0
                st.session_state.user_answers = {}
                st.session_state.quiz_start_time = datetime.now()
                st.session_state.quiz_active = True
                st.session_state.show_explanation = False
                st.session_state.quiz_submitted = False

                # Set timer based on number of questions (30 seconds per question, min 5 min, max 30 min)
                timer_seconds = min(max(num_questions * 30, 300), 1800)
                st.session_state.timer_end = datetime.now() + timedelta(seconds=timer_seconds)

                st.session_state.page = "quiz"
                st.rerun()

            except Exception as e:
                st.error(f"❌ Failed to generate quiz: {str(e)}")
                st.info("💡 Make sure your Mistral API key is set in the environment variable MISTRAL_API_KEY.")

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ─── Quiz Page ────────────────────────────────────────────────────────────────

def render_quiz_page():
    questions = st.session_state.questions
    if not questions:
        st.session_state.page = "upload"
        st.rerun()
        return

    total = len(questions)
    current = st.session_state.current_q

    # Check timer
    if st.session_state.timer_end and datetime.now() > st.session_state.timer_end:
        st.session_state.quiz_submitted = True
        st.session_state.page = "results"
        st.rerun()
        return

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Header with timer and progress
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.markdown("""
        <div style="text-align: left;">
            <span style="color: #8888aa; font-size: 0.85rem; font-weight: 500;">🧠 Quiz</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(
            f'<div class="question-counter">Question {current + 1} of {total}</div>',
            unsafe_allow_html=True
        )

    with col3:
        # Timer display
        if st.session_state.timer_end:
            remaining = (st.session_state.timer_end - datetime.now()).total_seconds()
            mins = int(remaining // 60)
            secs = int(remaining % 60)

            if remaining <= 60:
                timer_class = "danger"
            elif remaining <= 180:
                timer_class = "warning"
            else:
                timer_class = ""

            st.markdown(
                f"""
                <div class="timer-container">
                    <div class="timer-badge {timer_class}">
                        ⏱️ {mins:02d}:{secs:02d}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Progress dots
    dots_html = '<div class="question-progress">'
    for i in range(total):
        cls = "progress-dot"
        if i == current:
            cls += " active"
        elif i in st.session_state.user_answers:
            cls += " answered"
        dots_html += f'<div class="{cls}"></div>'
    dots_html += '</div>'
    st.markdown(dots_html, unsafe_allow_html=True)

    # Question card
    st.markdown('<div class="card">', unsafe_allow_html=True)

    q = questions[current]
    st.markdown(f'<div class="question-text">Q{current + 1}: {q["question"]}</div>', unsafe_allow_html=True)

    # Options
    selected = st.session_state.user_answers.get(current, None)
    options = q["options"]

    # Create radio button with letters
    option_labels = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)]
    option_mapping = {label: opt for label, opt in zip(option_labels, options)}

    selected_label = None
    if selected:
        for label, opt in option_mapping.items():
            if opt == selected:
                selected_label = label
                break

    answer = st.radio(
        "Select your answer:",
        options=option_labels,
        index=option_labels.index(selected_label) if selected_label else None,
        key=f"q_{current}",
        label_visibility="collapsed"
    )

    if answer:
        st.session_state.user_answers[current] = option_mapping[answer]

    st.markdown('</div>', unsafe_allow_html=True)

    # Navigation buttons
    st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if current > 0:
            if st.button("◀ Previous", key="prev", use_container_width=True):
                st.session_state.current_q -= 1
                st.rerun()

    with col2:
        if current < total - 1:
            disabled = current not in st.session_state.user_answers
            if st.button("Next ▶", key="next", type="primary", use_container_width=True, disabled=disabled):
                st.session_state.current_q += 1
                st.rerun()

    with col3:
        # Submit button
        answered_count = len(st.session_state.user_answers)
        if answered_count == total or current == total - 1:
            if st.button("📊 Submit Quiz", key="submit", type="primary", use_container_width=True):
                st.session_state.quiz_submitted = True
                st.session_state.page = "results"
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Auto-refresh for timer
    if st.session_state.timer_end:
        remaining = (st.session_state.timer_end - datetime.now()).total_seconds()
        if remaining > 0:
            time.sleep(0.1)
            st.rerun()


# ─── Results Page ─────────────────────────────────────────────────────────────

def render_results_page():
    questions = st.session_state.questions
    user_answers = st.session_state.user_answers

    if not questions:
        st.session_state.page = "upload"
        st.rerun()
        return

    # Calculate score
    result = calculate_score(user_answers, questions)
    grade = get_grade(result["percentage"])
    message = get_performance_message(result["percentage"])

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="app-header">
        <div class="app-title">📊 Quiz Results</div>
        <div class="app-subtitle">Review your performance and answers</div>
    </div>
    """, unsafe_allow_html=True)

    # Score card
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-container">
        <div class="score-circle">
            <div class="score-number">{result["score"]}</div>
            <div class="score-total">/ {result["total"]}</div>
        </div>
        <div class="score-grade">Grade: {grade}</div>
        <div class="score-message">{message}</div>
        <div class="score-bar">
            <div class="score-bar-fill" style="width: {result["percentage"]}%;"></div>
        </div>
        <div style="color: #8888aa; margin-top: 0.5rem; font-size: 0.9rem;">
            {result["percentage"]}% Accuracy
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Detailed review
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="card-header">
        <span class="card-icon">📝</span>
        <h3>Detailed Review</h3>
    </div>
    """, unsafe_allow_html=True)

    # Filter selection
    filter_option = st.selectbox(
        "Show:",
        options=["All Questions", "Correct Only", "Wrong Only"],
        index=0,
        label_visibility="collapsed"
    )

    for i, q in enumerate(questions):
        user_ans = user_answers.get(i, "Not answered")
        correct_ans = q["correct_answer"]
        is_correct = user_ans == correct_ans

        # Apply filter
        if filter_option == "Correct Only" and not is_correct:
            continue
        if filter_option == "Wrong Only" and is_correct:
            continue

        result_class = "correct" if is_correct else "wrong"
        icon = "✅" if is_correct else "❌"

        st.markdown(f"""
        <div class="result-item {result_class}">
            <div class="result-question">{icon} Q{i + 1}: {q["question"]}</div>
            <div class="result-answers">
                <div class="result-answer-tag user">
                    🧑 Your answer: {user_ans}
                </div>
                <div class="result-answer-tag correct">
                    ✓ Correct answer: {correct_ans}
                </div>
            </div>
            <div class="result-explanation">
                <strong>💡 Explanation:</strong> {q["explanation"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Action buttons
    st.markdown('<div class="action-buttons">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Retake Quiz", type="primary", use_container_width=True):
            st.session_state.current_q = 0
            st.session_state.user_answers = {}
            st.session_state.quiz_start_time = datetime.now()
            st.session_state.quiz_submitted = False
            st.session_state.page = "quiz"

            # Reset timer
            total = len(st.session_state.questions)
            timer_seconds = min(max(total * 30, 300), 1800)
            st.session_state.timer_end = datetime.now() + timedelta(seconds=timer_seconds)

            st.rerun()

    with col2:
        if st.button("📂 Upload New PPT", key="new_upload", use_container_width=True):
            # Reset everything
            for key in list(st.session_state.keys()):
                if key not in ["page"]:
                    del st.session_state[key]
            st.session_state.page = "upload"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─── Main App ─────────────────────────────────────────────────────────────────

def main():
    load_css()
    init_session_state()

    # Route to appropriate page
    if st.session_state.page == "upload":
        render_upload_page()
    elif st.session_state.page == "quiz":
        render_quiz_page()
    elif st.session_state.page == "results":
        render_results_page()


if __name__ == "__main__":
    main()