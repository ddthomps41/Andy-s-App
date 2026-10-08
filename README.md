# My Calm Check-In

A small, autism-friendly stress check-in app built with Streamlit. It has a 1–10 stress slider, immediate suggestions, optional notes, local history, a simple chart, and an editable-by-code calm plan.

## Run locally

1. Install Python 3.10+.
2. Open Terminal in this folder.
3. Run `python -m pip install -r requirements.txt`.
4. Run `python -m streamlit run app.py`.
5. Open the local address printed by Streamlit.

## Data and privacy

Check-ins are saved in `checkins.db` in the same directory as the app. They stay on the host machine unless it is backed up or synced. Do not deploy a public shared instance without authentication and separate user data storage. Many free cloud hosts use ephemeral storage, so entries may disappear after restarts. The app is meant as a self-awareness aid, not medical care.
