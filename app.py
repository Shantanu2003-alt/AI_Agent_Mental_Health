import streamlit as st
from PIL import Image
import time

# --- THEME SETUP ---
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
            background: #23272f !important;
            color: #e0e6f0 !important;
        }
        .safe-space {
            background: rgba(40,40,60,0.92);
            border-radius: 1.2em;
            padding: 2em 2em 1em 2em;
            box-shadow: 0 4px 32px 0 rgba(30,30,40,0.16);
        }
        .big-title { font-size: 2.7rem; font-weight: bold; color: #e0e6f0; margin-bottom: 0.5em; }
        .agent-badge { font-size: 1.5rem; margin-right: 0.5em; }
        .heart { color: #ffb6c1; font-size: 2.2rem; vertical-align: middle; }
        .stTextInput > div > input, .stTextArea > div > textarea, .stSelectbox > div > div, .stMultiSelect > div > div {
            background: #23272f !important;
            color: #e0e6f0 !important;
        }
        [data-testid="stSidebar"], .css-1d391kg {
            background: #23272f !important;
            color: #e0e6f0 !important;
        }
        .stAlert, .stInfo, .stSuccess, .stWarning {
            background-color: #2c3140 !important;
            color: #e0e6f0 !important;
        }
        .markdown-text-container, .stMarkdown {
            color: #e0e6f0 !important;
        }
        </style>
        """, unsafe_allow_html=True)

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Mental Wellbeing Agent",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- MODE SELECTOR ---
with st.sidebar:
    st.title("🌓 Theme & Mode")
    mode = st.radio("Choose Mode", ["Light", "Dark"], horizontal=True)
    set_theme(mode)
    agent_mode = st.radio("Choose Agent", ["Support Plan", "Listener (Vent & Comfort)"], horizontal=True)

# --- HEADER & HERO SECTION ---
st.markdown('<div class="big-title">🧠 Mental Wellbeing Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="safe-space">', unsafe_allow_html=True)
st.markdown("""
<span class="agent-badge">🧠</span> <b>Assessment Agent:</b> Analyzes your situation and emotional needs  
<span class="agent-badge">🎯</span> <b>Action Agent:</b> Creates an immediate action plan and connects you with resources  
<span class="agent-badge">🔄</span> <b>Follow-up Agent:</b> Designs your long-term support strategy  
""", unsafe_allow_html=True)
st.markdown('<span class="heart">♥️</span> <i>This is a safe, judgment-free zone.<br>Be as open as you wish—your feelings matter here.</i>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- GRAPHICS ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image(
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
        caption="You are not alone. This is your space.",
        use_container_width=True  # FIXED DEPRECATION WARNING
    )

# --- SUPPORT PLAN MODE ---
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

def action_agent(state, responses):
    action = ""
    if "Anxiety" in state['current_symptoms']:
        action += "- Try the 5-4-3-2-1 grounding technique when anxious.\n"
        action += "- Practice slow, deep breathing (inhale 4, hold 4, exhale 6) for 5 minutes.\n"
        if responses.get("breathing_script"):
            action += "\n**Guided Breathing:**\n- Inhale slowly for 4 seconds.\n- Hold for 4 seconds.\n- Exhale gently for 6 seconds.\n- Repeat for 5 cycles.\n"
    if "Fatigue" in state['current_symptoms']:
        action += "- Take brief breaks every hour, even if it's just stretching.\n"
        action += "- Stay hydrated and try to get some natural light during the day.\n"
    if "interview" in (state['recent_changes'] or "").lower():
        if responses.get("interview_tips"):
            action += "- Prepare answers to common questions and practice aloud.\n"
            action += "- Visualize yourself succeeding in the interview.\n"
            action += "- Remember: it's normal to feel nervous, and interviewers expect it.\n"
    if "family" in (state['recent_changes'] or "").lower():
        if responses.get("family_tips"):
            action += "- Try 'I feel' statements to express your needs without blame.\n"
            action += "- Set boundaries around work and personal time if possible.\n"
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

# --- LISTENER MODE ---
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

# --- MAIN LOGIC ---
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
            responses = {}

            with st.spinner("Analyzing your situation..."):
                time.sleep(1.2)
                st.success("Assessment complete.")

            if "Anxiety" in current_symptoms:
                responses["breathing_script"] = st.checkbox(
                    "Would you like a short guided script for breathing exercises?", value=True
                )
            if "interview" in (recent_changes or "").lower():
                responses["interview_tips"] = st.checkbox(
                    "Would you like practical tips for managing interview anxiety?", value=True
                )
            if "family" in (recent_changes or "").lower():
                responses["family_tips"] = st.checkbox(
                    "Would you like communication strategies for family issues?", value=True
                )

            st.markdown("## 📝 Situation Assessment")
            st.info(assessment_agent(state))

            st.markdown("## 🎯 Action Plan & Resources")
            st.success(action_agent(state, responses))

            st.markdown("## 🔄 Long-term Support Strategy")
            st.warning(followup_agent(state))

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
        else:
            st.warning("Please write something to share.")

    # Display conversation
    for speaker, msg in st.session_state.vent_history:
        if speaker == "user":
            st.markdown(f"<div style='background:#e0c3fc;padding:0.7em 1em;border-radius:0.8em;margin-bottom:0.2em;'><b>You:</b> {msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#f8f9fa;padding:0.7em 1em;border-radius:0.8em;margin-bottom:1em;'><b>Agent:</b> {msg}</div>", unsafe_allow_html=True)

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
