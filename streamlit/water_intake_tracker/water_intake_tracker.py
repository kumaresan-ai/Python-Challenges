import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
import io

st.set_page_config(page_title="Hydration Tracker", layout="wide")

# App header
st.markdown("""
# 💧 Hydration Tracker
Track your water intake, see progress toward your daily goal, and view a weekly hydration chart.
""")

# --- Sidebar settings ---
with st.sidebar:
    st.header("Settings")
    goal_liters = st.number_input("Daily goal (liters)", min_value=0.5, max_value=10.0, value=3.0, step=0.1)
    goal_ml = int(goal_liters * 1000)
    st.caption(f"Current goal: {goal_liters:.1f} L ({goal_ml} ml)")
    st.write("---")
    st.markdown("**Export / Manage data**")

# Initialize session state storage
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["timestamp", "amount_ml"])  # timestamp: ISO string

# --- Input form ---
st.subheader("Add water intake")
with st.form("add_entry", clear_on_submit=True):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        intake_date = st.date_input("Date", value=date.today())
    with col2:
        intake_time = st.time_input("Time", value=datetime.now().time())
    with col3:
        amount_ml = st.number_input("Amount (ml)", min_value=10, max_value=5000, value=250, step=10)

    submitted = st.form_submit_button("Add entry")

if submitted:
    ts = datetime.combine(intake_date, intake_time)
    new = {"timestamp": ts.isoformat(timespec='seconds'), "amount_ml": int(amount_ml)}
    st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new])], ignore_index=True)
    st.success(f"Added {amount_ml} ml at {ts.strftime('%Y-%m-%d %H:%M:%S')}")

# --- Controls under header ---
colA, colB = st.columns([3, 1])
with colB:
    if st.button("Clear all entries"):
        st.session_state.data = pd.DataFrame(columns=["timestamp", "amount_ml"])
        st.success("All entries cleared.")

    # Provide CSV download
    if not st.session_state.data.empty:
        csv_bytes = st.session_state.data.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download CSV", data=csv_bytes, file_name="hydration_data.csv", mime="text/csv")

# --- Data processing ---
# Convert timestamps back to datetimes
if not st.session_state.data.empty:
    df = st.session_state.data.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
else:
    df = pd.DataFrame(columns=['timestamp', 'amount_ml'])

# Today's stats
today = date.today()
today_mask = (df['timestamp'].dt.date == today) if not df.empty else pd.Series([], dtype=bool)
today_total = int(df.loc[today_mask, 'amount_ml'].sum()) if not df.empty else 0

# --- Suggestion logic ---
def polite_suggestion(total_ml: int, goal_ml: int) -> str:
    if total_ml == 0:
        return ("I noticed you haven't logged any water today. Keeping hydrated helps concentration and energy — "
                f"aim for around {goal_ml//1000} L (about {goal_ml} ml) today.")
    if total_ml < goal_ml:
        diff = goal_ml - total_ml
        return ("You're currently a bit below your daily goal. "
                f"Consider drinking an extra {diff} ml today to reach {goal_ml//1000} L.")
    elif total_ml > goal_ml * 1.4:
        # guardrail: if significantly above (possible overhydration) show gentle advice
        diff = total_ml - goal_ml
        return ("You're above your daily goal by a noticeable margin. "
                "While staying hydrated is good, drinking excessive water can be unnecessary — "
                f"consider reducing by about {diff} ml if you feel fine.")
    else:
        return ("Great — you're meeting or close to meeting your daily goal. Keep up the good hydration! ")

suggestion_raw = polite_suggestion(today_total, goal_ml)

# Re-write suggestion professionally and politely (Report requirement)
def rewrite_polite(text: str) -> str:
    # Small rephrasing to sound professional and courteous
    return ("Recommendation: " + text + " If you have any medical conditions or take medications that affect fluid balance, "
            "please consult a healthcare professional before changing your water intake.")

suggestion = rewrite_polite(suggestion_raw)

# --- UI: Overview ---
st.subheader("Today's summary")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.metric(label="Today's total", value=f"{today_total} ml", delta=f"{(today_total - goal_ml)} ml")
with col2:
    progress = min(1.0, today_total / goal_ml) if goal_ml > 0 else 0
    st.progress(progress)
    st.caption(f"{progress*100:.0f}% of {goal_liters:.1f} L goal")
with col3:
    st.info(suggestion)

# Short friendly note (Few shots tone)
if today_total < goal_ml:
    st.warning("You are drinking less than your daily goal. Please try to drink more water throughout the day.")
elif today_total > goal_ml:
    st.success("You are drinking more than your daily goal. If you feel well, that's fine — otherwise consider moderating intake.")

# --- Weekly hydration chart ---
st.subheader("Weekly hydration chart (last 7 days)")

def weekly_sums(df: pd.DataFrame, days: int = 7) -> pd.DataFrame:
    today_dt = pd.to_datetime(datetime.combine(date.today(), datetime.min.time()))
    start = today_dt - pd.Timedelta(days=days-1)
    # create full day index
    idx = [ (start + pd.Timedelta(days=i)).date() for i in range(days) ]
    sums = {d: 0 for d in idx}
    if not df.empty:
        df['date'] = df['timestamp'].dt.date
        grouped = df.groupby('date')['amount_ml'].sum()
        for k, v in grouped.items():
            if k in sums:
                sums[k] = int(v)
    res = pd.DataFrame({'date': list(sums.keys()), 'amount_ml': list(sums.values())})
    return res

weekly = weekly_sums(df, days=7)

# Plot using matplotlib
fig, ax = plt.subplots(figsize=(9, 3))
ax.bar(range(len(weekly)), weekly['amount_ml'])
ax.plot(range(len(weekly)), [goal_ml]*len(weekly), linestyle='--')
ax.set_xticks(range(len(weekly)))
ax.set_xticklabels([d.strftime('%a %d') for d in weekly['date']], rotation=45)
ax.set_ylabel('ml')
ax.set_title('Last 7 days — total water intake per day')
ax.set_ylim(0, max(max(weekly['amount_ml'].max(), goal_ml) * 1.2, 500))
st.pyplot(fig)

# Detailed hydration chart per entry (today)
st.subheader("Detailed entries (recent)")
if df.empty:
    st.info("No entries yet — add your first water intake using the form above.")
else:
    # show last 20 entries
    show_df = df.tail(20).copy()
    show_df['time'] = show_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    show_df = show_df[['time', 'amount_ml']].reset_index(drop=True)
    st.dataframe(show_df, use_container_width=True)

# Helpful tips
st.markdown("---")
st.subheader("Healthy hydration tips")
st.write(
    "• Sip water regularly rather than gulping large amounts at once.\n"
    "• If you exercise or it's hot, increase intake accordingly.\n"
    "• Signs you may need more water: dark urine, dry mouth, dizziness.\n"
    "• If you have kidney, heart problems, or take diuretics, consult a clinician about how much to drink."
)

# End note and small footer
st.markdown("---")
st.caption("This tracker is for general guidance only and does not replace professional medical advice.")

# EOF