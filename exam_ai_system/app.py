from pathlib import Path

import streamlit as st

from auth.service import AuthService
from config import get_default_provider, validate_provider
from db.supabase_client import (
    create_supabase_client,
    get_supabase_config_errors,
)
from history.service import ExamHistoryService
from llm.errors import LLMProviderError, to_user_message
from logging_utils import configure_logging, get_logger
from orchestrator.exam_orchestrator import ExamOrchestratorAgent

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

configure_logging()
logger = get_logger(__name__)
auth_service = AuthService(create_supabase_client)
history_service = ExamHistoryService(create_supabase_client)


def reset_exam_state():
    st.session_state.exam = None
    st.session_state.submitted = False
    st.session_state.score = 0
    st.session_state.percentage = 0.0
    st.session_state.current_question = 0
    st.session_state.answers = {}
    st.session_state.celebration_shown = False

    for key in list(st.session_state.keys()):
        if key.startswith("question_"):
            del st.session_state[key]

default_provider = get_default_provider()
provider_options = ["groq", "ollama"]

if default_provider not in provider_options:
    default_provider = "groq"

st.set_page_config(
    page_title="AI Certification Exam",
    page_icon="🎓",
    layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "display_name" not in st.session_state:
    st.session_state.display_name = None

css_path = Path(__file__).parent / "styles" / "main.css"
st.markdown(
    f"<style>{css_path.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-kicker">AI Exam Workspace</div>
        <div class="hero-title">AI Certification Exam Generator</div>
        <p class="hero-copy">Configure your exam, choose your inference provider, and complete the full assessment in one guided workflow.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

supabase_errors = get_supabase_config_errors()

if supabase_errors:
    st.error("Supabase is not configured yet for authentication and exam history.")
    for error in supabase_errors:
        st.caption(error)
    st.info(
        "Add `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` to your local `.env` or Streamlit secrets."
    )
    st.stop()

if not st.session_state.logged_in:
    st.markdown(
        """
        <div class="section-title">Sign In To Continue</div>
        <div class="section-copy">Create an account or sign in before taking exams and saving your attempt history.</div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary"):
            try:
                user = auth_service.authenticate_user(login_email, login_password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user["id"]
                    st.session_state.user_email = user["email"]
                    st.session_state.display_name = user["display_name"]
                    reset_exam_state()
                    st.rerun()
                else:
                    st.error("Invalid email or password.")
            except Exception as exc:
                st.error(f"Login failed: {exc}")

    with register_tab:
        register_display_name = st.text_input("Display Name", key="register_display_name")
        register_email = st.text_input("Email", key="register_email")
        register_password = st.text_input(
            "Create a Password",
            type="password",
            key="register_password",
        )

        if st.button("Create Account"):
            try:
                user = auth_service.create_user(
                    register_email,
                    register_password,
                    register_display_name,
                )
                st.session_state.logged_in = True
                st.session_state.user_id = user["id"]
                st.session_state.user_email = user["email"]
                st.session_state.display_name = user["display_name"]
                reset_exam_state()
                st.success("Account created successfully.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Account creation failed: {exc}")

    st.stop()

# Sidebar (Professional Exam Info)
with st.sidebar:

    st.header("Exam Control Panel")

    selected_provider = st.selectbox(
        "LLM Provider",
        provider_options,
        index=provider_options.index(default_provider),
    )

    provider_status = validate_provider(selected_provider)
    active_model = provider_status.model

    st.caption(f"Provider: {selected_provider}")
    st.caption(f"Model: {active_model}")

    if provider_status.is_ready:
        st.success("Provider configuration is ready.")
    else:
        for error in provider_status.errors:
            st.error(error)

    st.markdown(
        f"""
        <div class="sidebar-meta">
            <strong>Signed in as:</strong> {st.session_state.display_name}<br>
            <strong>Email:</strong> {st.session_state.user_email}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Logout"):
        reset_exam_state()
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.session_state.display_name = None
        st.rerun()

    st.markdown("""
**Instructions**

• Select the best answer for each question  
• Only one option is correct  
• Click **Submit Exam** when finished
""")

st.markdown(
    """
    <div class="section-title">1. Configure Your Exam</div>
    <div class="section-copy">Choose the topic, exam style, and question count before generating the exam.</div>
    """,
    unsafe_allow_html=True,
)

setup_col1, setup_col2 = st.columns([1.5, 1])

with setup_col1:
    topic = st.text_input("Training Topic")

with setup_col2:
    num_questions = st.selectbox(
        "Number of Questions",
        [5, 10, 15]
    )

flow_col1, flow_col2 = st.columns(2)

with flow_col1:
    exam_type = st.selectbox(
        "Exam Type",
        ["Practice Exam", "Certification Exam", "Assessment Test"]
    )

with flow_col2:
    level = st.selectbox(
        "Certification Level",
        ["Beginner", "Intermediate", "Advanced"]
    )

with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-meta">
            <strong>Certification:</strong> AI Fundamentals<br>
            <strong>Questions:</strong> {num_questions}<br>
            <strong>Passing Score:</strong> 70%
        </div>
        """,
        unsafe_allow_html=True,
    )

    history_error = None
    try:
        recent_attempts = history_service.list_attempts(st.session_state.user_id, limit=5)
    except RuntimeError as exc:
        logger.warning(
            "exam_history_load_failed user_id=%s error=%s",
            st.session_state.user_id,
            exc,
        )
        recent_attempts = []
        history_error = str(exc)

    with st.expander("Recent Exam History", expanded=False):
        if history_error:
            st.caption(history_error)
            st.divider()
        if recent_attempts:
            for attempt in recent_attempts:
                st.markdown(
                    (
                        f"**{attempt['topic']}**  \n"
                        f"{attempt['exam_type']} | {attempt['level']}  \n"
                        f"Score: {attempt['score']}/{attempt['question_count']} "
                        f"({attempt['percentage']:.2f}%)  \n"
                        f"Provider: {attempt['provider']}  \n"
                        f"Taken: {attempt['created_at']}"
                    )
                )
                st.divider()
        else:
            st.caption("No exam attempts yet.")

st.markdown(
    """
    <div class="section-title">2. Generate And Complete</div>
    <div class="section-copy">Generate the exam once the setup looks right, then answer each question and submit for scoring.</div>
    """,
    unsafe_allow_html=True,
)


# Session state initialization
if "exam" not in st.session_state:
    st.session_state.exam = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "score" not in st.session_state:
    st.session_state.score = 0

if "percentage" not in st.session_state:
    st.session_state.percentage = 0.0

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "celebration_shown" not in st.session_state:
    st.session_state.celebration_shown = False

# Generate Exam
if st.button("Generate Exam"):

    if topic.strip() == "":
        st.warning("Please enter a topic.")
    elif not provider_status.is_ready:
        st.error("Fix the provider configuration before generating an exam.")
    else:

        with st.spinner("Generating AI Certification Exam..."):

            try:
                logger.info(
                    "exam_generation_started provider=%s topic=%s exam_type=%s level=%s num_questions=%s",
                    selected_provider,
                    topic,
                    exam_type,
                    level,
                    num_questions,
                )
                orchestrator = ExamOrchestratorAgent(provider=selected_provider)
                exam = orchestrator.generate_exam(topic, exam_type, level, num_questions)

                st.session_state.exam = exam
                st.session_state.submitted = False
                st.session_state.score = 0
                st.session_state.percentage = 0.0
                st.session_state.current_question = 0
                st.session_state.answers = {}
                st.session_state.celebration_shown = False
                logger.info(
                    "exam_generation_succeeded provider=%s topic=%s generated_questions=%s",
                    selected_provider,
                    topic,
                    len(exam.questions),
                )
            except LLMProviderError as exc:
                st.session_state.exam = None
                logger.exception(
                    "exam_generation_provider_error provider=%s topic=%s exam_type=%s level=%s",
                    selected_provider,
                    topic,
                    exam_type,
                    level,
                )
                st.error(to_user_message(exc))
            except Exception as exc:
                st.session_state.exam = None
                logger.exception(
                    "exam_generation_failed provider=%s topic=%s exam_type=%s level=%s",
                    selected_provider,
                    topic,
                    exam_type,
                    level,
                )
                st.error(to_user_message(exc))

# Display Exam
if st.session_state.exam:

    exam = st.session_state.exam

    st.markdown(
        f"""
        <div class="summary-bar">
            <div style="display:grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.85rem;">
                <div class="summary-tile">
                    <div class="summary-label">Topic</div>
                    <div class="summary-value">{exam.topic}</div>
                </div>
                <div class="summary-tile">
                    <div class="summary-label">Exam Type</div>
                    <div class="summary-value">{exam_type}</div>
                </div>
                <div class="summary-tile">
                    <div class="summary-label">Level</div>
                    <div class="summary-value">{level}</div>
                </div>
                <div class="summary-tile">
                    <div class="summary-label">Questions</div>
                    <div class="summary-value">{len(exam.questions)}</div>
                </div>
                <div class="summary-tile">
                    <div class="summary-label">Provider</div>
                    <div class="summary-value">{selected_provider}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-title">3. Take The Exam</div>
        <div class="section-copy">Move through each question below and submit once you have reviewed all your answers.</div>
        """,
        unsafe_allow_html=True,
    )

    if exam.review_notes:
        st.info("Quality review notes were recorded during generation.")

    total_questions = len(exam.questions)
    current_index = min(st.session_state.current_question, total_questions - 1)
    st.session_state.current_question = current_index
    current_question_number = current_index + 1
    current_answer_key = f"question_{current_question_number}"
    progress_bar = st.progress(current_question_number / total_questions)

    def save_current_answer():
        selected = st.session_state.get(current_answer_key)
        if selected is not None:
            st.session_state.answers[current_answer_key] = selected

    saved_answer = st.session_state.answers.get(current_answer_key)

    if saved_answer is not None and current_answer_key not in st.session_state:
        st.session_state[current_answer_key] = saved_answer

    navigator_col1, navigator_col2, navigator_col3 = st.columns(
        [1, 1.2, 1],
        vertical_alignment="center",
    )

    with navigator_col1:
        if st.button("Previous", disabled=current_index == 0):
            save_current_answer()
            st.session_state.current_question = max(0, current_index - 1)
            st.rerun()

    with navigator_col2:
        st.markdown(
            f"""
            <div class="navigator-caption">
                Question {current_question_number} of {total_questions}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with navigator_col3:
        next_spacer, next_button_col = st.columns([1.8, 1])
        with next_button_col:
            if st.button("Next", disabled=current_index >= total_questions - 1):
                save_current_answer()
                st.session_state.current_question = min(total_questions - 1, current_index + 1)
                st.rerun()

    q = exam.questions[current_index]

    with st.container():
        st.markdown('<div class="question-shell">', unsafe_allow_html=True)

        st.markdown(
            f'<div class="question-kicker">Question {current_question_number}</div>',
            unsafe_allow_html=True,
        )

        st.write(q.question)

        st.radio(
            f"Select answer for Question {current_question_number}",
            q.options,
            index=None,
            key=current_answer_key,
            on_change=save_current_answer,
            disabled=st.session_state.submitted,
        )

        difficulty = (q.difficulty or "Medium").lower()

        if difficulty == "easy":
            st.success(f"Difficulty: {q.difficulty}")
        elif difficulty == "medium":
            st.warning(f"Difficulty: {q.difficulty}")
        else:
            st.error(f"Difficulty: {q.difficulty}")

        if st.session_state.submitted and exam_type == "Practice Exam":
            user_choice = st.session_state.answers.get(current_answer_key)

            if user_choice == q.answer:
                st.success(f"Your answer: {user_choice}")
            else:
                st.error(f"Your answer: {user_choice}")

            st.info(f"Correct answer: {q.answer}")

        st.divider()
        st.markdown("</div>", unsafe_allow_html=True)

    # Submit Exam
    if st.button("Submit Exam"):

        score = 0
        save_current_answer()

        for i, q in enumerate(exam.questions, 1):
            user_choice = st.session_state.answers.get(f"question_{i}")

            if user_choice == q.answer:
                score += 1

        total = len(exam.questions)
        percentage = (score / total) * 100

        st.session_state.submitted = True
        st.session_state.score = score
        st.session_state.percentage = percentage
        st.session_state.celebration_shown = False
        try:
            history_service.record_attempt(
                user_id=st.session_state.user_id,
                topic=exam.topic,
                exam_type=exam_type,
                level=level,
                question_count=total,
                score=score,
                percentage=percentage,
                provider=selected_provider,
            )
        except RuntimeError as exc:
            logger.warning(
                "exam_history_record_failed user_id=%s topic=%s error=%s",
                st.session_state.user_id,
                exam.topic,
                exc,
            )
            st.warning(
                "Your exam was submitted, but the attempt could not be saved to history right now."
            )
        logger.info(
            "exam_submitted provider=%s exam_type=%s level=%s score=%s total=%s percentage=%.2f",
            selected_provider,
            exam_type,
            level,
            score,
            total,
            percentage,
        )
        st.rerun()

    if st.session_state.submitted:
        st.header("Certification Result")

        col1, col2 = st.columns(2)

        col1.metric("Score", f"{st.session_state.score} / {len(exam.questions)}")
        col2.metric("Percentage", f"{st.session_state.percentage:.2f}%")

        if st.session_state.percentage >= 70:

            st.success("🎉 Congratulations! You passed the AI Certification.")
            if not st.session_state.celebration_shown:
                st.balloons()
                st.session_state.celebration_shown = True

        else:

            st.error("❌ Unfortunately you did not pass. Please try again.")
