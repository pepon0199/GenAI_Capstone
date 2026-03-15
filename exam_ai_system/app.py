import streamlit as st
from orchestrator.exam_orchestrator import ExamOrchestratorAgent

st.set_page_config(
    page_title="AI Certification Exam",
    page_icon="🎓",
    layout="wide"
)

st.title("AI Certification Exam Generator")

# Sidebar (Professional Exam Info)
with st.sidebar:

    st.header("Exam Information")

    st.write("""
**Certification:** AI Fundamentals  
**Number of Questions:** 5  
**Passing Score:** 70%
""")

    st.write("---")

    st.write("""
**Instructions**

• Select the best answer for each question  
• Only one option is correct  
• Click **Submit Exam** when finished
""")

topic = st.text_input("Training Topic")

exam_type = st.selectbox(
    "Exam Type",
    ["Practice Exam", "Certification Exam", "Assessment Test"]
)

level = st.selectbox(
    "Certification Level",
    ["Beginner", "Intermediate", "Advanced"]
)

num_questions = st.selectbox(
    "Number of Questions",
    [5, 10, 15]
)


# Session state initialization
if "exam" not in st.session_state:
    st.session_state.exam = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Generate Exam
if st.button("Generate Exam"):

    if topic.strip() == "":
        st.warning("Please enter a topic.")
    else:

        with st.spinner("Generating AI Certification Exam..."):

            orchestrator = ExamOrchestratorAgent()
            exam = orchestrator.generate_exam(topic, exam_type, level, num_questions)

            st.session_state.exam = exam
            st.session_state.submitted = False

# Display Exam
if st.session_state.exam:

    exam = st.session_state.exam

    st.header(f"Certification Exam: {exam.topic}")

    st.write(f"Total questions generated: {len(exam.questions)}")

    progress_bar = st.progress(0)

    # Questions
    for i, q in enumerate(exam.questions, 1):

        progress = i / len(exam.questions)
        progress_bar.progress(progress)

        with st.container():

            st.subheader(f"Question {i}")

            st.write(q.question)

            choice = st.radio(
                f"Select answer for Question {i}",
                q.options,
                key=f"question_{i}"
            )

            difficulty = q.difficulty.lower()

            if difficulty == "easy":
                st.success(f"Difficulty: {q.difficulty}")

            elif difficulty == "medium":
                st.warning(f"Difficulty: {q.difficulty}")

            else:
                st.error(f"Difficulty: {q.difficulty}")

            st.divider()

    # Submit Exam
    if st.button("Submit Exam"):

        score = 0

        for i, q in enumerate(exam.questions, 1):

            user_choice = st.session_state.get(f"question_{i}")

            if user_choice == q.answer:
                score += 1

        total = len(exam.questions)
        percentage = (score / total) * 100

        st.header("Certification Result")

        col1, col2 = st.columns(2)

        col1.metric("Score", f"{score} / {total}")
        col2.metric("Percentage", f"{percentage:.2f}%")

        if percentage >= 70:

            st.success("🎉 Congratulations! You passed the AI Certification.")
            st.balloons()

        else:

            st.error("❌ Unfortunately you did not pass. Please try again.")