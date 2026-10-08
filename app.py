import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path
import streamlit as st
import pandas as pd

st.set_page_config(page_title="My Calm Check-In", page_icon="🫧", layout="centered")
DB_PATH = Path(__file__).with_name('checkins.db')

@st.cache_resource
def database():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute('''CREATE TABLE IF NOT EXISTS checkins (
       id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
       stress INTEGER NOT NULL, feelings TEXT, triggers TEXT, body_signals TEXT,
       support TEXT, notes TEXT)''')
    conn.commit()
    return conn

conn = database()
st.markdown('''<style>
.stApp {background: #f7f9fc; color: #1b3150;}
.block-container {max-width: 750px; padding-top: 1.5rem;}
h1,h2,h3 {color: #16365b;}
div[data-testid="stAlert"] {border-radius: 16px;}
.stButton button[kind="primary"] {background: #265f9c; border:0; border-radius:12px;}
</style>''', unsafe_allow_html=True)

st.title('🫧 My Calm Check-In')
st.caption('A private space to notice stress, find what helps, and recognize your effort. No perfect answers needed.')

checkin_tab, history_tab, plan_tab = st.tabs(['☀️ Check in', '📈 My patterns', '🧰 My calm plan'])

with checkin_tab:
    st.subheader('How stressed do I feel right now?')
    level = st.slider('Stress level', 1, 10, 4, help='1 = calm; 10 = completely overwhelmed')
    if level <= 3:
        st.success('**1–3 · Feeling steady**\n\nYou can keep doing what you’re doing. Take note of what helps you feel okay.')
        ideas = ['Enjoy something familiar', 'Drink some water', 'Notice what is going well']
    elif level <= 6:
        st.warning('**4–6 · Stress is building**\n\nIt may help to reduce demands now, before things feel too big.')
        ideas = ['Move somewhere quieter', 'Put on headphones', 'Take a short walk', 'Choose one small next step']
    else:
        st.error('**7–10 · Overwhelmed**\n\nYou do not have to solve the problem right now. First focus on feeling safer and more settled.')
        ideas = ['Pause the conversation', 'Go to a quiet, comfortable place', 'Reduce noise and light', 'Ask for space or support']
    st.markdown('**Things I could try right now:**')
    for idea in ideas:
        st.write('• ' + idea)
    with st.form('save_checkin', clear_on_submit=False):
        feelings = st.multiselect('What am I feeling? (optional)', ['Anxious','Frustrated','Angry','Sad','Overloaded','Confused','Tired','Okay','Not sure'])
        triggers = st.multiselect('What might have contributed? (optional)', ['Unexpected change','Conflict','Uncertainty','Too many tasks','Noise / sensory input','Social situation','Tired / hungry','Something else','Not sure'])
        signals = st.multiselect('What am I noticing in my body? (optional)', ['Fast heartbeat','Tense muscles','Racing thoughts','Restlessness','Headache','Want to withdraw','Not sure'])
        support = st.radio('What would help me right now?', ['Quiet time','Someone to listen','Help making a plan','A familiar activity','I’m not sure'], horizontal=False)
        notes = st.text_area('Anything else I want to remember? (optional)', height=70)
        submitted = st.form_submit_button('Save my check-in', type='primary', use_container_width=True)
        if submitted:
            conn.execute('INSERT INTO checkins(timestamp,stress,feelings,triggers,body_signals,support,notes) VALUES (?,?,?,?,?,?,?)',
                         (datetime.now().isoformat(timespec='seconds'), level, ', '.join(feelings), ', '.join(triggers), ', '.join(signals), support, notes.strip()))
            conn.commit()
            st.success('Saved. Checking in is progress. 💙')

with history_tab:
    df = pd.read_sql_query('SELECT * FROM checkins ORDER BY timestamp DESC', conn)
    if df.empty:
        st.info('Your check-ins will appear here after you save your first one.')
    else:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        st.metric('Check-ins recorded', len(df))
        st.metric('Average stress level', f"{df['stress'].mean():.1f} / 10")
        chart = df.sort_values('timestamp').set_index('timestamp')[['stress']]
        st.line_chart(chart, y_label='Stress (1–10)')
        st.caption('A high number is information, not failure. Look for patterns and what helps.')
        with st.expander('View past check-ins'):
            st.dataframe(df[['timestamp','stress','feelings','triggers','support','notes']], use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button('Download my check-ins (CSV)', csv, 'my_calm_checkins.csv', 'text/csv')

with plan_tab:
    st.subheader('When stress gets big')
    st.markdown('''**Step 1 — Notice:** “My stress is rising. I don't need to judge it.”

**Step 2 — Reduce input:** Find a quieter place, lower the lights, or put on headphones.

**Step 3 — Choose one need:** Space, reassurance, help with a plan, or a familiar activity.

**Step 4 — Return later:** Talk about the situation only after the intensity has dropped.

**Helpful sentence:** “I’m overwhelmed. I need 20 minutes, then I can talk.”

**For another person:** “Would you like space, listening, or help figuring out the next step?”
''')
    st.info('Not every difficult feeling requires exposure or pushing through. Sensory overload and burnout may call for rest and accommodations. Discuss persistent panic with an autism-informed professional.')
    st.caption('Privacy: check-ins are saved in a local SQLite database on the computer/server running this app. If hosted online, they are stored on that host and should not be assumed private or permanent. Do not publish this app publicly without access protection.')
