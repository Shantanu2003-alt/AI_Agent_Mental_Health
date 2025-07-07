import streamlit as st
from PIL import Image
import time
import io
from fpdf import FPDF
import re

# THEME SETUP
def set_theme(mode):
    if mode == "Light":
        st.markdown("""
        <style>
        body { background: linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 100%); }
        .safe-space { background: rgba(255,255,255,0.85); border-radius: 1.2em; padding: 2em 2em 1em 2em; box-shadow: 0 4px 32px 0 rgba(60,60,124,0.08); }
        .big-title { font-size: 2.7rem; font-weight: bold; color: #3c3c7c; margin-bottom: 0.5em; }
        .agent-badge { font-size: 1.5rem; margin-right: 0.5em; }
        .heart { color: #ff6f91; font-size: 2.2rem; vertical-align: middle; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], .main, .block-container {
            background: #2d2f36 !important;
            color: #fff !important;
        }
        .safe-space {
            background: rgba(50,50,60,0.92);
            border-radius: 1.2em;
            padding: 2em 2em 1em 2em;
            box-shadow: 0 4px 32px 0 rgba(30,30,40,0.12);
        }
        .big-title { font-size: 2.7rem; font-weight: bold; color: #fff; margin-bottom: 0.5em; }
        .agent-badge { font-size: 1.5rem; margin-right: 0.5em; }
        .heart { color: #ffb6c1; font-size: 2.2rem; vertical-align: middle; }
        .stTextInput > div > input, .stTextArea > div > textarea, .stSelectbox > div > div, .stMultiSelect > div > div {
            background: #2d2f36 !important;
            color: #fff !important;
        }
        [data-testid="stSidebar"], .css-1d391kg {
            background: #2d2f36 !important;
            color: #fff !important;
        }
        .stAlert, .stInfo, .stSuccess, .stWarning {
            background-color: #393b41 !important;
            color: #fff !important;
        }
        .markdown-text-container, .stMarkdown {
            color: #fff !important;
        }
        </style>
        """, unsafe_allow_html=True)

# PAGE CONFIG
st.set_page_config(
    page_title="Mental Wellbeing Agent",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="auto"
)

# MODE SELECTOR
with st.sidebar:
    st.title("🌓 Theme & Mode")
    mode = st.radio("Choose Mode", ["Light", "Dark"], horizontal=True)
    set_theme(mode)
    agent_mode = st.radio("Choose Agent", ["Support Plan", "Listener (Vent & Comfort)"], horizontal=True)

# HEADER & HERO SECTION
st.markdown('<div class="big-title">🧠 Mental Wellbeing Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="safe-space">', unsafe_allow_html=True)
st.markdown("""
<span class="agent-badge">🧠</span> <b>Assessment Agent:</b> Analyzes your situation and emotional needs  
<span class="agent-badge">🎯</span> <b>Action Agent:</b> Creates an immediate action plan and connects you with resources  
<span class="agent-badge">🔄</span> <b>Follow-up Agent:</b> Designs your long-term support strategy  
""", unsafe_allow_html=True)
st.markdown('<span class="heart">♥️</span> <i>This is a safe, judgment-free zone.<br>Be as open as you wish—your feelings matter here.</i>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# GRAPHICS
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image(
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
        caption="You are not alone. This is your space.",
        use_container_width=True
    )

# SESSION LOGGING
if "session_log" not in st.session_state:
    st.session_state.session_log = []

def log_session(text):
    st.session_state.session_log.append(text)

# SUPPORT PLAN MODE
def assessment_agent(state):
    assessment = f"""
Thank you for sharing your feelings. You mentioned feeling **{state['mental_state']}**.
Your sleep averages **{state['sleep_pattern']} hours/night** and your stress is **{state['stress_level']}/10**.

**Support system:** {', '.join(state['support_system']) if state['support_system'] else 'None reported'}  
**Recent changes:** {state['recent_changes'] or 'None reported'}  
**Current symptoms:** {', '.join(state['current_symptoms']) if state['current_symptoms'] else 'None reported'}

"""
    if state['stress_level'] >= 8:
        assessment += "- Your stress level is very high. This is a valid concern and deserves attention.\n"
    if "Anxiety" in state['current_symptoms']:
        assessment += "- Anxiety is a dominant theme. Let's focus on strategies for this.\n"
    if "Fatigue" in state['current_symptoms']:
        assessment += "- Fatigue may be linked to stress, sleep, or emotional load.\n"
    if "None" in state['support_system']:
        assessment += "- You reported no current support system. Building support is important for recovery.\n"
    if "interview" in (state['recent_changes'] or "").lower():
        assessment += "- Interview anxiety is a common and manageable challenge.\n"
    if "family" in (state['recent_changes'] or "").lower():
        assessment += "- Family problems can deeply affect mood and stress.\n"
    return assessment

def action_agent(state):
    action = ""
    if "Anxiety" in state['current_symptoms']:
        action += "- Try the 5-4-3-2-1 grounding technique when anxious.\n"
        action += "- Practice slow, deep breathing (inhale 4, hold 4, exhale 6) for 5 minutes.\n"
    if "Fatigue" in state['current_symptoms']:
        action += "- Take brief breaks every hour, even if it's just stretching.\n"
        action += "- Stay hydrated and try to get some natural light during the day.\n"
    if "interview" in (state['recent_changes'] or "").lower():
        action += "- Interview anxiety is a common and manageable challenge.\n"
    if "family" in (state['recent_changes'] or "").lower():
        action += "- Family problems can deeply affect mood and stress.\n"
    if "None" in state['support_system']:
        action += "- Consider reaching out to online support communities (e.g., 7 Cups, Reddit r/mentalhealth).\n"
        action += "- If you ever feel unsafe, please call a crisis line (988 in the US).\n"
    action += "- Keep a daily journal to track mood and triggers.\n"
    action += "- If symptoms worsen, consider reaching out to a mental health professional.\n"
    return action

def followup_agent(state):
    followup = "- Build a consistent daily routine: sleep, meals, movement, downtime.\n"
    followup += "- Track your mood and symptoms weekly. Apps like Daylio or a paper journal work well.\n"
    if "None" in state['support_system']:
        followup += "- Set a goal to connect with at least one supportive person or community in the next month.\n"
    followup += "- Practice self-compassion: setbacks are normal. Celebrate small progress.\n"
    followup += "- Plan for stressful events (like interviews) by preparing, resting, and rewarding yourself after.\n"
    followup += "- If family issues persist, consider family counseling or support groups.\n"
    return followup

# FOLLOW-UP TIPS DATA 
def show_followup_tips(key):
    if key == "breathing_script":
        st.markdown("""
**Guided Breathing (5 Steps):**
1. Sit comfortably and close your eyes if you wish.
2. Inhale slowly through your nose for 4 seconds.
3. Hold your breath for 4 seconds.
4. Exhale gently through your mouth for 6 seconds.
5. Repeat for 5 cycles, focusing on the sensation of your breath.
""")
    elif key == "interview_tips":
        st.markdown("""
**Interview Anxiety Tips (5 Steps):**
1. Prepare answers to common questions and practice aloud.
2. Visualize yourself succeeding in the interview.
3. Remember: it's normal to feel nervous, and interviewers expect it.
4. Practice grounding techniques before the interview.
5. Reward yourself afterwards, regardless of the outcome.
""")
    elif key == "family_tips":
        st.markdown("""
**Family Communication Strategies (5 Steps):**
1. Use "I feel" statements to express your needs without blame.
2. Set clear boundaries around work and personal time.
3. Choose calm moments for important conversations.
4. Listen actively and validate each other's feelings.
5. Seek support from a counselor or support group if needed.
""")

def comforting_lines():
    st.info("That's perfectly okay. Remember, you can always revisit these resources later. You're doing your best, and that's enough.")

# LISTENER MODE
def comforting_response(user_message):
    comforting_phrases = [
        "Thank you for trusting me with your thoughts. I'm here to listen, no judgment.",
        "It's completely okay to feel this way. You are not alone.",
        "Take your time—I'm here for you as long as you need.",
        "Your feelings are valid, and it's brave of you to share them.",
        "Remember, it's okay to have tough days. You are doing your best.",
        "You matter, and your experiences matter.",
        "If you want to talk more, I'm here to listen."
    ]
    import random
    return random.choice(comforting_phrases) + "\n\n" + (
        "Would you like to share more about what's on your mind?"
        if len(user_message.strip().split()) > 10 else
        "Feel free to say as much or as little as you want."
    )

# DOWNLOAD UTILITIES
def remove_emojis(text):
    # Remove all non-latin-1 characters (including emojis)
    return re.sub(r'[^\x00-\xff]', '', text)

def get_full_session_text():
    return "\n\n".join(st.session_state.session_log)

def get_full_session_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in st.session_state.session_log:
        # Remove emojis and non-latin-1 characters for PDF
        safe_line = remove_emojis(line)
        for subline in safe_line.split('\n'):
            pdf.multi_cell(0, 10, subline)
    pdf_output = io.BytesIO()
    pdf.output(pdf_output, 'F')
    pdf_output.seek(0)
    return pdf_output

# MAIN LOGIC
if agent_mode == "Support Plan":
    st.markdown("## 🌱 Personal Information")
    with st.form("wellbeing_form"):
        mental_state = st.text_area("How have you been feeling recently?", 
                                    placeholder="Describe your emotional state, thoughts, or concerns...")
        sleep_pattern = st.slider("Sleep Pattern (hours per night)", 0, 12, 7)
        stress_level = st.slider("Current Stress Level (1-10)", 1, 10, 5)
        support_system = st.multiselect(
            "Current Support System",
            ["Family", "Friends", "Therapist", "Support Groups", "None"],
            default=[]
        )
        recent_changes = st.text_area(
            "Any significant life changes or events recently?",
            placeholder="Job changes, relationships, losses, etc..."
        )
        symptoms_list = [
            "Anxiety", "Depression", "Insomnia", "Fatigue", "Loss of Interest",
            "Difficulty Concentrating", "Changes in Appetite", "Social Withdrawal",
            "Mood Swings", "Physical Discomfort"
        ]
        current_symptoms = st.multiselect(
            "Current Symptoms",
            symptoms_list,
            default=[]
        )
        submit = st.form_submit_button("Get Support Plan", type="primary")

    if submit:
        if not mental_state.strip():
            st.error("Please describe how you're feeling.")
        else:
            state = {
                "mental_state": mental_state.strip(),
                "sleep_pattern": sleep_pattern,
                "stress_level": stress_level,
                "support_system": support_system,
                "recent_changes": recent_changes.strip(),
                "current_symptoms": current_symptoms
            }

            with st.spinner("Analyzing your situation..."):
                time.sleep(1.2)
                st.success("Assessment complete.")

            st.markdown("## 📝 Situation Assessment")
            assessment = assessment_agent(state)
            st.info(assessment)
            log_session("## Situation Assessment\n" + assessment)

            st.markdown("## 🎯 Action Plan & Resources")
            action = action_agent(state)
            st.success(action)
            log_session("## Action Plan & Resources\n" + action)

            st.markdown("## 🔄 Long-term Support Strategy")
            followup = followup_agent(state)
            st.warning(followup)
            log_session("## Long-term Support Strategy\n" + followup)

# STATIC FOLLOW-UP SECTION
st.markdown("## 🔁 Follow-up")
st.markdown("Would you like a short guided script for the following?")

followup_answers = {
    "breathing_script": st.radio(
        "1. Breathing exercises", ["Yes", "No"], key="followup_breathing"
    ),
    "interview_tips": st.radio(
        "2. Managing interview anxiety", ["Yes", "No"], key="followup_interview"
    ),
    "family_tips": st.radio(
        "3. Dealing with family problems", ["Yes", "No"], key="followup_family"
    ),
}

if st.button("Show Follow-up Tips"):
    if followup_answers["breathing_script"] == "Yes":
        st.markdown("""
### 🧘 Guided Breathing Script (5 Steps)
1. Sit in a quiet, comfortable place with your back straight.
2. Close your eyes and inhale slowly through your nose for 4 seconds.
3. Hold your breath for 4 seconds.
4. Exhale slowly through your mouth for 6 seconds.
5. Repeat this cycle for 5–10 rounds, focusing only on your breath.
""")
        log_session("## Follow-up: Breathing Script\n(Tip shown)")
    else:
        comforting_lines()
        log_session("## Follow-up: Breathing Script\n(Comforting line shown)")

    if followup_answers["interview_tips"] == "Yes":
        st.markdown("""
### 🎤 Interview Anxiety Tips (5 Steps)
1. Practice mock interviews and prepare key stories using STAR format.
2. Use positive visualization — imagine yourself succeeding calmly.
3. Write down your strengths and repeat them before the interview.
4. Do a 1-minute grounding breath before logging in or entering the room.
5. Remind yourself: nerves = caring. Interviewers expect nervousness!
""")
        log_session("## Follow-up: Interview Tips\n(Tip shown)")
    else:
        comforting_lines()
        log_session("## Follow-up: Interview Tips\n(Comforting line shown)")

    if followup_answers["family_tips"] == "Yes":
        st.markdown("""
### 🏡 Family Communication Tips (5 Steps)
1. Use calm, "I feel" statements instead of blame ("I feel unheard when...").
2. Set boundaries clearly but kindly — it's okay to protect your peace.
3. Choose calm moments to talk, not during a heated argument.
4. Focus on listening actively instead of reacting.
5. Seek help from a family counselor or group if patterns repeat.
""")
        log_session("## Follow-up: Family Tips\n(Tip shown)")
    else:
        comforting_lines()
        log_session("## Follow-up: Family Tips\n(Comforting line shown)")

   
elif agent_mode == "Listener (Vent & Comfort)":
    st.markdown("## 💬 Vent or Share Anything")
    st.markdown(
        "This space is just for you to express yourself. "
        "The agent will listen and respond with comfort and encouragement. "
        "Type as much or as little as you want."
    )

    if "vent_history" not in st.session_state:
        st.session_state.vent_history = []

    user_message = st.text_area("What's on your mind?", key="vent_input")
    if st.button("Share", key="vent_button"):
        if user_message.strip():
            st.session_state.vent_history.append(("user", user_message.strip()))
            agent_reply = comforting_response(user_message)
            st.session_state.vent_history.append(("agent", agent_reply))
            log_session(f"You: {user_message.strip()}\nAgent: {agent_reply}")
        else:
            st.warning("Please write something to share.")

    # Display conversation
    for speaker, msg in st.session_state.vent_history:
        if speaker == "user":
            st.markdown(f"<div style='background:#e0c3fc;padding:0.7em 1em;border-radius:0.8em;margin-bottom:0.2em;'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#f8f9fa;padding:0.7em 1em;border-radius:0.8em;margin-bottom:1em;'><b>Agent:</b> {msg}</div>", unsafe_allow_html=True)

# STRESS RELIEVER SONG & DOWNLOAD SECTION
st.markdown("""
---
### 🎵 Stress Reliever Song
Listen to "Weightless" by Marconi Union, a scientifically recognized stress-relief track:

<iframe width="100%" height="120" src="https://www.youtube.com/embed/UfcAVejslrU?si=J1AP15Blg4jtAw6L" title="Weightless by Marconi Union" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
""", unsafe_allow_html=True)

st.markdown("""
### ⬇️ Download Your Session
You can download your full session as a text file for your records or to share with a professional.
""")

txt_data = get_full_session_text()
st.download_button(
    label="Download as TXT",
    data=txt_data,
    file_name="mental_wellbeing_session.txt",
    mime="text/plain"
)

# HELPLINE SECTION
st.markdown("""
<div style="background: #fff3cd; border-radius: 1em; padding: 1em; margin-top: 2em;">
<b>⚠️ Important Notice</b><br>
This application is a supportive tool and does not replace professional mental health care.<br>
If you're experiencing thoughts of self-harm or severe crisis:<br>
<ul>
<li>Call National Crisis Hotline: <b>988</b></li>
<li>Call Emergency Services: <b>911</b></li>
<li>Seek immediate professional help</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.balloons()
