
import streamlit as st
from utils.llm import generate_response

# ==========================================================
# HEARTCHECK — AI INTERACTION RESEARCH PROTOTYPE
# ==========================================================

st.set_page_config(
    page_title="HeartCheck | AI Research",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------------
# SESSION STATE
# ----------------------------------------------------------

defaults = {
    "mode": "Standard Chat",
    "standard_messages": [],
    "structured_messages": [],
    "summary": "",
    "summary_ready": False,
    "patient_gender": "Not specified",
    "last_summary_sent": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ----------------------------------------------------------
# SHARED HELPERS — LIVE/SIMULATED display + retry
# ----------------------------------------------------------
# generate_response() now returns a dict: {"text", "source", "reason", "error"}
# source is "LIVE" (real model) or "SIMULATED" (fallback used because the
# live call failed). We never show a SIMULATED reply without labelling it.

def render_assistant_message(message):
    """Render one assistant message plus a source badge (LIVE or SIMULATED)."""

    st.markdown(message["content"])

    if message.get("source") == "SIMULATED":
        st.caption(
            f"🧪 Simulated demo response — live model unavailable "
            f"({message.get('reason', 'unknown reason')}). Not AI-generated."
        )
    elif message.get("source") == "LIVE":
        st.caption("✅ Live AI response (Groq)")


def render_retry_button(message_list, key_suffix):
    """
    If the most recent assistant reply in message_list was simulated,
    show a button to retry the live API using the same conversation
    history (minus that simulated reply).
    """

    if not message_list:
        return

    last = message_list[-1]

    if last.get("role") != "assistant" or last.get("source") != "SIMULATED":
        return

    if st.button("🔄 Retry live API", key=f"retry_{key_suffix}"):

        history_without_fallback = message_list[:-1]

        with st.spinner("Retrying the live model..."):
            try:
                result = generate_response(history_without_fallback)
            except Exception as error:
                st.error("Retry failed.")
                st.caption(str(error))
                return

        message_list.pop()
        message_list.append({
            "role": "assistant",
            "content": result["text"],
            "source": result["source"],
            "reason": result["reason"],
        })

        st.rerun()


# ----------------------------------------------------------
# CUSTOM CSS
# ----------------------------------------------------------

st.markdown("""
<style>

/* Keep Streamlit's bottom chat composer in light mode */
[data-testid="stBottom"] {
    background: rgba(245, 247, 251, 0.97) !important;
    border-top: 1px solid #E1E7EF !important;
}

[data-testid="stChatInput"] {
    background: #FFFFFF !important;
    border: 1px solid #DCE4EE !important;
    border-radius: 16px !important;
    box-shadow: 0 5px 20px rgba(23, 43, 67, 0.07) !important;
}

[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    color: #172B43 !important;
}

[data-testid="stHeader"] {
    background: #F5F7FB !important;
}

/* Main application */
.stApp {
    background-color: #F4F7FB;
    color: #172B43;
}

/* Remove default top whitespace */
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

/* Main hero */
.hero {
    background: linear-gradient(120deg, #101D32, #173C55);
    padding: 38px;
    border-radius: 22px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 8px 25px rgba(16,29,50,0.12);
}

.hero-tag {
    color: #55D6BE;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero h1 {
    color: white;
    font-size: 43px;
    margin: 12px 0 8px 0;
    font-weight: 750;
}

.hero p {
    color: #D0DCE8;
    font-size: 16px;
    max-width: 650px;
}

/* Section headings */
.section-title {
    color: #172B43;
    font-size: 23px;
    font-weight: 750;
    margin-bottom: 5px;
}

.section-description {
    color: #718096;
    font-size: 14px;
    margin-bottom: 18px;
}

/* Cards */
.feature-card {
    background: white;
    padding: 23px;
    border-radius: 16px;
    border: 1px solid #E4EAF1;
    min-height: 135px;
    box-shadow: 0 3px 12px rgba(20,40,70,0.035);
}

.feature-icon {
    font-size: 25px;
    margin-bottom: 10px;
}

.feature-card h3 {
    color: #172B43;
    font-size: 17px;
    margin: 0 0 7px 0;
}

.feature-card p {
    color: #718096;
    font-size: 13px;
    margin: 0;
}

/* Emergency banner */
.emergency {
    background: #FFF1F0;
    border: 1px solid #FFD4D0;
    border-left: 5px solid #E45B57;
    border-radius: 12px;
    padding: 17px 20px;
    margin: 20px 0;
}

.emergency strong {
    color: #A62D2D;
    font-size: 15px;
}

.emergency p {
    color: #733B3B;
    font-size: 13px;
    margin: 5px 0 0 0;
}

/* Research disclaimer */
.disclaimer {
    background: #EAF4F8;
    border: 1px solid #D4E7EF;
    padding: 13px 17px;
    border-radius: 10px;
    color: #34576B;
    font-size: 13px;
    margin-bottom: 20px;
}

/* Summary panel */
.summary-panel {
    background: #EAF7F4;
    border: 1px solid #C9E9DF;
    border-radius: 13px;
    padding: 15px;
    margin: 15px 0;
    color: #245A4D;
}

/* Buttons */
.stButton > button {
    border-radius: 10px;
    font-weight: 650;
    min-height: 43px;
}

/* Input fields */
.stTextArea textarea,
.stTextInput input {
    border-radius: 10px;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: white;
    border: 1px solid #E8EDF3;
    border-radius: 13px;
    padding: 12px;
    margin-bottom: 10px;
}

/* Footer */
.footer {
    text-align: center;
    color: #8290A1;
    font-size: 12px;
    padding: 25px 0 5px 0;
}

/* Hide Streamlit decoration */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-tag">✦ AI Interaction Research Prototype</div>
    <h1>❤️ HeartCheck</h1>
    <p>
        Exploring how conversational interaction design
        influences AI-generated symptom assessment and
        care recommendations.
    </p>
</div>
""", unsafe_allow_html=True)


# ----------------------------------------------------------
# DISCLAIMER AND SAFETY
# ----------------------------------------------------------

st.markdown("""
<div class="disclaimer">
    <strong>Research prototype:</strong>
    HeartCheck is an academic research application using
    fictional patient scenarios. It is not a medical device,
    does not provide a diagnosis and has not been clinically validated.
</div>

<div class="emergency">
    <strong>⚠ Emergency information</strong>
    <p>
        If you think you or someone else may be having a
        heart attack, call <strong>999 immediately</strong>.
        Do not wait for a chatbot response.
    </p>
</div>
""", unsafe_allow_html=True)


# ----------------------------------------------------------
# MODE SELECTION
# ----------------------------------------------------------

st.markdown(
    '<div class="section-title">Choose your experience</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Explore two different ways of interacting with the same AI model.'
    '</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "💬 STANDARD CHAT\n\nFree-text conversation",
        type="primary" if st.session_state.mode == "Standard Chat" else "secondary",
        use_container_width=True
    ):
        st.session_state.mode = "Standard Chat"
        st.rerun()

with col2:
    if st.button(
        "📋 STRUCTURED CHAT\n\nGuided symptom questions",
        type="primary" if st.session_state.mode == "Structured Chat" else "secondary",
        use_container_width=True
    ):
        st.session_state.mode = "Structured Chat"
        st.rerun()

mode = st.session_state.mode

st.divider()


# ==========================================================
# MODE A — STANDARD CHAT
# ==========================================================

if mode == "Standard Chat":

    st.markdown(
        '<div class="section-title">💬 Standard Chat</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Describe the fictional patient’s symptoms in your own words. '
        'The AI will respond conversationally.'
        '</div>',
        unsafe_allow_html=True
    )

    # Display conversation history
    for message in st.session_state.standard_messages:

        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                render_assistant_message(message)
            else:
                st.markdown(message["content"])

    # User input
    user_input = st.chat_input(
        "Describe the patient's symptoms..."
    )

    if user_input:

        # Add user message
        st.session_state.standard_messages.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate AI response (live model, or clearly-labelled
        # simulated fallback if the live model is unavailable)
        with st.chat_message("assistant"):

            with st.spinner("HeartCheck is analysing the conversation..."):

                try:
                    result = generate_response(
                        st.session_state.standard_messages
                    )

                    reply_message = {
                        "role": "assistant",
                        "content": result["text"],
                        "source": result["source"],
                        "reason": result["reason"],
                    }

                    render_assistant_message(reply_message)

                    st.session_state.standard_messages.append(reply_message)

                except Exception as error:

                    st.error(
                        "Unable to generate a response. "
                        "Please check the API connection."
                    )

                    st.caption(str(error))

                    # Remove unanswered user message
                    st.session_state.standard_messages.pop()

    render_retry_button(st.session_state.standard_messages, "standard")


# ==========================================================
# MODE B — STRUCTURED CHAT
# ==========================================================

else:

    st.markdown(
        '<div class="section-title">📋 Structured Chat</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-description">'
        'Answer the predefined questions. Review and edit the '
        'generated symptom summary before submitting it to the AI model.'
        '</div>',
        unsafe_allow_html=True
    )

    # Progress indicator
    st.progress(
        1.0 if st.session_state.summary_ready else 0.25,
        text=(
            "Step 2 of 2 — Review your summary"
            if st.session_state.summary_ready
            else "Step 1 of 2 — Patient information"
        )
    )

    # ------------------------------------------------------
    # QUESTIONNAIRE
    # ------------------------------------------------------

    with st.form("symptom_form"):

        st.markdown("### Patient information")

        gender = st.selectbox(
            "Patient gender",
            [
                "Not specified",
                "Woman",
                "Man"
            ],
            help="Used to create matched fictional research scenarios."
        )

        st.markdown("### 1. Main symptoms")

        symptoms = st.text_area(
            "What symptoms is the fictional patient experiencing?",
            placeholder=(
                "Example: Chest discomfort, pain in the left arm..."
            ),
            height=100
        )

        st.markdown("### 2. Symptom onset")

        onset = st.selectbox(
            "When did the symptoms begin?",
            [
                "Select an option",
                "Less than 1 hour ago",
                "1–6 hours ago",
                "More than 6 hours ago",
                "Several days ago"
            ]
        )

        st.markdown("### 3. Symptom severity")

        severity = st.select_slider(
                    "Select the severity level",
                    options=["Mild", "Moderate", "Severe"],
                    value="Moderate",
                    key="symptom_severity"
        )
        st.caption(f"Selected severity: {severity}")

        st.markdown("### 4. Additional symptoms")

        additional = st.text_area(
            "Are there any additional symptoms?",
            placeholder=(
                "Example: Sweating, dizziness, nausea or breathlessness..."
            ),
            height=90
        )

        submitted = st.form_submit_button(
            "Generate symptom summary →",
            type="primary",
            use_container_width=True
        )

    # ------------------------------------------------------
    # GENERATE SUMMARY
    # ------------------------------------------------------

    if submitted:

        if not symptoms.strip():

            st.warning("Please enter the patient's main symptoms.")

        elif onset == "Select an option":

            st.warning("Please select when the symptoms began.")

        else:

            st.session_state.patient_gender = gender

            st.session_state.summary = (
                f"Patient gender: {gender}\n"
                f"Main symptoms: {symptoms}\n"
                f"Onset: {onset}\n"
                f"Severity: {severity}\n"
                f"Additional symptoms: "
                f"{additional.strip() or 'Not specified'}"
            )

            st.session_state.summary_ready = True

            st.session_state.last_summary_sent = ""

            st.session_state.structured_messages = []

            st.rerun()

    # ------------------------------------------------------
    # EDITABLE SUMMARY
    # ------------------------------------------------------

    if st.session_state.summary_ready:

        st.divider()

        st.markdown(
            '<div class="section-title">Review your understanding</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-description">'
            'Check the information collected by HeartCheck. '
            'You can correct or add details before submitting.'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
        <div class="summary-panel">
            ✦ <strong>Human-in-the-loop interaction</strong><br>
            Review and control the information that will be sent
            to the AI model.
        </div>
        """, unsafe_allow_html=True)

        edited_summary = st.text_area(
            "Editable symptom summary",
            value=st.session_state.summary,
            height=190,
            key="editable_summary"
        )

        if st.button(
            "Submit confirmed summary to the AI model →",
            type="primary",
            use_container_width=True
        ):

            if not edited_summary.strip():

                st.warning("The summary cannot be empty.")

            else:

                st.session_state.summary = edited_summary

                # Start or update the structured conversation
                if (
                    st.session_state.last_summary_sent
                    != edited_summary
                ):

                    st.session_state.structured_messages.append({
                        "role": "user",
                        "content": (
                            "The user has reviewed and confirmed "
                            "the following fictional patient summary. "
                            "Please respond based only on the information "
                            "provided:\n\n" + edited_summary
                        )
                    })

                    st.session_state.last_summary_sent = edited_summary

                    with st.spinner(
                        "The AI model is reviewing the confirmed summary..."
                    ):

                        try:

                            result = generate_response(
                                st.session_state.structured_messages
                            )

                            st.session_state.structured_messages.append({
                                "role": "assistant",
                                "content": result["text"],
                                "source": result["source"],
                                "reason": result["reason"],
                            })

                        except Exception as error:

                            st.error(
                                "Unable to generate a response. "
                                "Please check the API connection."
                            )

                            st.caption(str(error))

                            st.session_state.structured_messages.pop()
                            st.session_state.last_summary_sent = ""

                    st.rerun()

                else:

                    st.info("This summary has already been submitted.")

        # --------------------------------------------------
        # STRUCTURED CHAT RESPONSE AND FOLLOW-UP
        # --------------------------------------------------

        if st.session_state.structured_messages:

            st.divider()

            st.markdown("### 💬 Conversation with HeartCheck")

            for message in st.session_state.structured_messages:

                with st.chat_message(
                    "assistant" if message["role"] == "assistant"
                    else "user"
                ):

                    content = message["content"]

                    # Display concise label for initial submitted summary
                    if (
                        message["role"] == "user"
                        and content.startswith(
                            "The user has reviewed and confirmed"
                        )
                    ):
                        st.markdown(
                            "**Confirmed symptom summary submitted**"
                        )
                        st.markdown(content.split("\n\n", 1)[-1])

                    elif message["role"] == "assistant":
                        render_assistant_message(message)

                    else:
                        st.markdown(content)

            render_retry_button(st.session_state.structured_messages, "structured")

            follow_up = st.chat_input(
                "Ask a follow-up question about the fictional scenario..."
            )

            if follow_up:

                st.session_state.structured_messages.append({
                    "role": "user",
                    "content": follow_up
                })

                with st.chat_message("user"):
                    st.markdown(follow_up)

                with st.chat_message("assistant"):

                    with st.spinner("The AI model is responding..."):

                        try:

                            result = generate_response(
                                st.session_state.structured_messages
                            )

                            reply_message = {
                                "role": "assistant",
                                "content": result["text"],
                                "source": result["source"],
                                "reason": result["reason"],
                            }

                            render_assistant_message(reply_message)

                            st.session_state.structured_messages.append(reply_message)

                        except Exception as error:

                            st.error("Unable to generate a response.")
                            st.caption(str(error))

                            st.session_state.structured_messages.pop()


        # Reset option
        if st.button("↻ Start a new structured scenario"):

            st.session_state.summary = ""
            st.session_state.summary_ready = False
            st.session_state.last_summary_sent = ""
            st.session_state.structured_messages = []

            if "editable_summary" in st.session_state:
                del st.session_state["editable_summary"]

            st.rerun()


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.markdown("""
<div class="footer">
    <strong>HEARTCHECK</strong><br>
    Intelligent Interactive Systems · Academic Research Prototype<br>
    Powered by GPT-OSS-120B (via Groq) · simulated fallback when unavailable
</div>
""", unsafe_allow_html=True)
