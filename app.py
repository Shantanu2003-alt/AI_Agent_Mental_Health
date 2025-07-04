import streamlit as st
import datetime
import pandas as pd
import io
from textblob import TextBlob
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
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
        use_container_width=True
    )

# --- Mood Tracker ---
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

with st.expander("📊 Daily Mood Tracker"):
    today = datetime.date.today()
    mood_score = st.slider("Mood (1-10)", 1, 10, 5, key="mood_score")
    stress_score = st.slider("Stress (1-10)", 1, 10, 5, key="stress_score")
    sleep_hours = st.slider("Sleep Hours", 0, 12, 7, key="sleep_hours")

    if st.button("Log Today"):
        st.session_state.mood_log.append({
            "date": today,
            "mood": mood_score,
            "stress": stress_score,
            "sleep": sleep_hours
        })
        st.success("Entry saved for today.")

    if st.session_state.mood_log:
        df = pd.DataFrame(st.session_state.mood_log)
        df = df.drop_duplicates(subset=["date"], keep="last").sort_values("date")
        st.line_chart(df.set_index("date"))

# --- Sentiment Analysis ---
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.5:
        return "Very Positive"
    elif polarity > 0:
        return "Positive"
    elif polarity < -0.5:
        return "Very Negative"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# --- Journal Export (.txt) ---
def create_journal_export():
    content = "--- Session Journal ---\n"
    for speaker, msg in st.session_state.get("vent_history", []):
        content += f"{speaker.title()}: {msg}\n\n"
    return io.StringIO(content)

with st.expander("📓 Export Journal"):
    if st.session_state.get("vent_history"):
        buffer = create_journal_export()
        st.download_button("Download Journal (.txt)", buffer, file_name="journal.txt")
    else:
        st.info("No journal content yet.")

# --- Guided Audio ---
with st.expander("🎧 Guided Relaxation Audio"):
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
    st.markdown("Guided audio for calming and focus. More tracks coming soon.")

# --- Plan/Assessment Export (PDF/Image) ---
def export_to_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.multi_cell(0, 10, line)
    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

def export_to_image(content):
    font = ImageFont.load_default()
    lines = content.split("\n")
    width = 800
    height = 20 * (len(lines) + 4)
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)
    y = 20
    for line in lines:
        draw.text((30, y), line, fill="black", font=font)
        y += 20
    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output

with st.expander("📤 Export Your Support Plan"):
    if "last_plan" in st.session_state:
        full_text = st.session_state["last_plan"]
        col1, col2 = st.columns(2)
        with col1:
            pdf_data = export_to_pdf(full_text)
            st.download_button("📄 Download as PDF", data=pdf_data.getvalue(), file_name="support_plan.pdf")
        with col2:
            image_data = export_to_image(full_text)
            st.download_button("🖼️ Download as Image", data=image_data.getvalue(), file_name="support_plan.png", mime="image/png")
    else:
        st.info("No plan generated yet. Generate one in Support Plan mode first.")

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

# --- FOLLOW-UP TIPS DATA ---
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
    st.info("That's perfectly okay. Remember, you can always revisit these resources later. You're doing your best, and that's enough. 💜")

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

            with st.spinner("Analyzing your situation..."):
                time.sleep(1.2)
                st.success("Assessment complete.")

            st.markdown("## 📝 Situation Assessment")
            assessment = assessment_agent(state)
            st.info(assessment)

            st.markdown("## 🎯 Action Plan & Resources")
            action = action_agent(state)
            st.success(action)

            st.markdown("## 🔄 Long-term Support Strategy")
            followup = followup_agent(state)
            st.warning(followup)

            # Save plan for export
            st.session_state["last_plan"] = (
                "Situation Assessment:\n" + assessment + "\n"
                "Action Plan & Resources:\n" + action + "\n"
                "Long-term Support Strategy:\n" + followup
            )

            # --- INTERACTIVE FOLLOW-UP ---
            follow_up_questions = []
            if "Anxiety" in current_symptoms:
                follow_up_questions.append({
                    "key": "breathing_script",
                    "question": "Would you like a short guided script for breathing exercises?"
                })
            if "interview" in (recent_changes or "").lower():
                follow_up_questions.append({
                    "key": "interview_tips",
                    "question": "Would you like practical tips for managing interview anxiety?"
                })
            if "family" in (recent_changes or "").lower():
                follow_up_questions.append({
                    "key": "family_tips",
                    "question": "Would you like communication strategies for family issues?"
                })

            if follow_up_questions:
                st.markdown("## 🔁 Follow-up")
                followup_answers = {}
                for item in follow_up_questions:
                    followup_answers[item["key"]] = st.radio(
                        item["question"], ["Yes", "No"], key=f"followup_{item['key']}"
                    )

                if st.button("Show Follow-up Tips"):
                    for item in follow_up_questions:
                        key = item["key"]
                        if followup_answers[key] == "Yes":
                            show_followup_tips(key)
                        else:
                            comforting_lines()

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
