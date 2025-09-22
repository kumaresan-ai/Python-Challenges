"""
Rock Paper Scissors - Streamlit Game Center

Single-file Streamlit app. Features:
- Dark-themed UI (custom CSS)
- Player vs Computer gameplay
- Game modes: Single Round, Best of N, Race to Score
- Computer difficulty: Easy / Medium / Hard (strategy options)
- Keeps per-session score and round history
- Persistent leaderboard saved to `leaderboard.csv` (same dir)
- Charts, stats, and CSV export / clear options

Run:
    pip install streamlit pandas matplotlib
    streamlit run streamlit_rps_app.py

Created for a children's game center — feel free to customize graphics, add sounds, or connect to a central DB.
"""

import streamlit as st
import pandas as pd
import random
from datetime import datetime
import os
import io
import matplotlib.pyplot as plt

# --- Page config and CSS (dark theme) ---
st.set_page_config(page_title="RPS Game Center", layout="wide", initial_sidebar_state="expanded")

DARK_CSS = """
<style>
:root{--bg:#0b0f14;--card:#0f1720;--muted:#94a3b8;--accent:#10b981;--panel:#0b1220;}
body, .stApp {background: linear-gradient(180deg,#07101a 0%, #04111a 100%);} 
.reportview-container .main .block-container{padding-top:1rem;}
.main .block-container{color:#e6eef6}
.row-widget.stButton > button{border-radius:16px; padding:18px 22px; font-size:18px}
h1{font-weight:800}
.stButton>button{background:linear-gradient(90deg,#0ea5a1,#06b6d4); color:white}
.big-move{display:flex; align-items:center; justify-content:center; font-size:48px; padding:14px 18px; border-radius:14px}
.score-box{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:12px; border-radius:12px}
.small-muted{color:var(--muted); font-size:13px}
.leader-card{background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.006)); padding:12px; border-radius:10px}
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

# --- Constants and helper utilities ---
MOVES = ["Rock", "Paper", "Scissors"]
EMOJI = {"Rock": "✊", "Paper": "🖐️", "Scissors": "✌️"}
LEADERBOARD_FILE = "leaderboard.csv"

# ensure leaderboard file exists
def init_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        df = pd.DataFrame(columns=["player", "wins", "losses", "draws", "score", "date"])
        df.to_csv(LEADERBOARD_FILE, index=False)

init_leaderboard()

# determine winner
def determine_winner(player, computer):
    if player == computer:
        return "Draw"
    wins = {("Rock", "Scissors"), ("Scissors", "Paper"), ("Paper", "Rock")}
    return "Player" if (player, computer) in wins else "Computer"

# counter move
def counter_move(move):
    if move == "Rock":
        return "Paper"
    if move == "Paper":
        return "Scissors"
    if move == "Scissors":
        return "Rock"
    return random.choice(MOVES)

# computer move strategies
def comp_move_easy(_history):
    return random.choice(MOVES)

def comp_move_medium(history):
    # Mix: 60% random, 40% counter to player's last
    if not history or random.random() < 0.6:
        return comp_move_easy(history)
    last = history[-1]["player_move"]
    return counter_move(last)

def comp_move_hard(history):
    # Frequency analysis + small randomness
    if not history:
        return comp_move_easy(history)
    counts = {m: 0 for m in MOVES}
    for r in history:
        counts[r["player_move"]] += 1
    most_common = max(counts, key=counts.get)
    # slight chance to randomize
    if random.random() < 0.15:
        return comp_move_easy(history)
    return counter_move(most_common)

def choose_computer_move(difficulty, history, use_strategy=True):
    if not use_strategy:
        return comp_move_easy(history)
    if difficulty == "Easy":
        return comp_move_easy(history)
    if difficulty == "Medium":
        return comp_move_medium(history)
    return comp_move_hard(history)

# leaderboard helpers
@st.cache_data
def load_leaderboard():
    try:
        return pd.read_csv(LEADERBOARD_FILE)
    except Exception:
        init_leaderboard()
        return pd.read_csv(LEADERBOARD_FILE)

def save_score_to_leaderboard(player, wins, losses, draws):
    df = load_leaderboard()
    score = int(wins) - int(losses)
    new_row = {
        "player": player,
        "wins": int(wins),
        "losses": int(losses),
        "draws": int(draws),
        "score": int(score),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(LEADERBOARD_FILE, index=False)
    st.cache_data.clear()  # refresh cache
    return df

def clear_leaderboard_file():
    df = pd.DataFrame(columns=["player", "wins", "losses", "draws", "score", "date"])
    df.to_csv(LEADERBOARD_FILE, index=False)
    st.cache_data.clear()

# --- Session state init ---
if "player_name" not in st.session_state:
    st.session_state.player_name = "Guest"
if "player_score" not in st.session_state:
    st.session_state.player_score = 0
if "comp_score" not in st.session_state:
    st.session_state.comp_score = 0
if "draws" not in st.session_state:
    st.session_state.draws = 0
if "rounds_played" not in st.session_state:
    st.session_state.rounds_played = 0
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts with round info
if "game_mode" not in st.session_state:
    st.session_state.game_mode = "Single Round"
if "best_of" not in st.session_state:
    st.session_state.best_of = 3
if "target_score" not in st.session_state:
    st.session_state.target_score = 3
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Medium"
if "use_strategy" not in st.session_state:
    st.session_state.use_strategy = True
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "last_result" not in st.session_state:
    st.session_state.last_result = ""
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "last_winner" not in st.session_state:
    st.session_state.last_winner = None

# --- Sidebar controls ---
with st.sidebar:
    st.header("Game Center Controls")
    st.session_state.player_name = st.text_input("Player name", value=st.session_state.player_name)
    st.session_state.game_mode = st.radio("Game mode", options=["Single Round", "Best of N", "Race to Score"], index=["Single Round", "Best of N", "Race to Score"].index(st.session_state.game_mode) if st.session_state.game_mode in ["Single Round","Best of N","Race to Score"] else 0)

    if st.session_state.game_mode == "Best of N":
        st.session_state.best_of = st.number_input("Best of (odd number)", min_value=1, max_value=99, value=st.session_state.best_of, step=2)
    elif st.session_state.game_mode == "Race to Score":
        st.session_state.target_score = st.number_input("Target score", min_value=1, max_value=50, value=st.session_state.target_score)

    st.session_state.difficulty = st.selectbox("Computer difficulty", options=["Easy", "Medium", "Hard"], index=["Easy","Medium","Hard"].index(st.session_state.difficulty))
    st.session_state.use_strategy = st.checkbox("Computer uses strategy", value=st.session_state.use_strategy)
    st.markdown("---")
    if st.button("Reset current game"):
        # reset scores and history but keep player name and settings
        st.session_state.player_score = 0
        st.session_state.comp_score = 0
        st.session_state.draws = 0
        st.session_state.rounds_played = 0
        st.session_state.history = []
        st.session_state.game_over = False
        st.session_state.last_result = ""
        st.session_state.streak = 0
        st.session_state.last_winner = None
        st.success("Game reset — ready for a fresh match!")

    st.markdown("---")
    st.subheader("Leaderboard")
    lb = load_leaderboard()
    if st.button("Clear leaderboard (permanent)"):
        clear_leaderboard_file()
        st.success("Leaderboard cleared")
    csv = lb.to_csv(index=False)
    st.download_button("Download leaderboard CSV", data=csv, file_name="leaderboard.csv", mime="text/csv")
    st.markdown("\n\n\n")
    st.caption("Tip: Ask staff to backup leaderboard.csv if you want a permanent store.")

# --- Main layout ---
st.markdown("# 🎮 Rock — Paper — Scissors (Game Center)")
st.markdown("A friendly, dark-themed RPS app for quick matches and a persistent leaderboard.")

left, right = st.columns([2, 1])

with left:
    # Scoreboard
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.markdown(f"<div class='score-box'><h3>Player</h3><h2>{st.session_state.player_name}</h2><div class='small-muted'>Wins: {st.session_state.player_score}</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='score-box'><h3>VS</h3><h2>Computer</h2><div class='small-muted'>Wins: {st.session_state.comp_score}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='score-box'><h3>Draws</h3><h2>{st.session_state.draws}</h2><div class='small-muted'>Rounds played: {st.session_state.rounds_played}</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # Play area
    st.subheader("Make your move")
    move_cols = st.columns(3)

    def play_round(player_move: str):
        if st.session_state.game_over:
            return
        computer_move = choose_computer_move(st.session_state.difficulty, st.session_state.history, st.session_state.use_strategy)
        winner = determine_winner(player_move, computer_move)
        st.session_state.rounds_played += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = {
            "round": st.session_state.rounds_played,
            "player_move": player_move,
            "computer_move": computer_move,
            "winner": winner,
            "time": timestamp,
        }
        st.session_state.history.append(entry)
        if winner == "Player":
            st.session_state.player_score += 1
        elif winner == "Computer":
            st.session_state.comp_score += 1
        else:
            st.session_state.draws += 1

        # track streaks
        if st.session_state.last_winner == winner:
            st.session_state.streak += 1
        else:
            st.session_state.streak = 1
        st.session_state.last_winner = winner

        st.session_state.last_result = f"{EMOJI[player_move]} {player_move} vs {EMOJI[computer_move]} {computer_move} — {winner}!"

        # check game end conditions
        if st.session_state.game_mode == "Single Round":
            st.session_state.game_over = True
        elif st.session_state.game_mode == "Best of N":
            # after best_of rounds, decide
            if st.session_state.rounds_played >= int(st.session_state.best_of):
                st.session_state.game_over = True
        elif st.session_state.game_mode == "Race to Score":
            if st.session_state.player_score >= int(st.session_state.target_score) or st.session_state.comp_score >= int(st.session_state.target_score):
                st.session_state.game_over = True

    # render move buttons
    with move_cols[0]:
        if st.button(f"{EMOJI['Rock']}\nRock", key="move_rock"):
            play_round("Rock")
    with move_cols[1]:
        if st.button(f"{EMOJI['Paper']}\nPaper", key="move_paper"):
            play_round("Paper")
    with move_cols[2]:
        if st.button(f"{EMOJI['Scissors']}\nScissors", key="move_scissors"):
            play_round("Scissors")

    st.markdown("---")
    # result and controls
    if st.session_state.last_result:
        st.info(st.session_state.last_result)

    if st.session_state.game_over:
        # match summary
        st.success("Match finished!")
        wins = st.session_state.player_score
        losses = st.session_state.comp_score
        draws = st.session_state.draws
        if wins > losses:
            st.markdown(f"### 🏆 {st.session_state.player_name} won the match ({wins} — {losses})")
        elif losses > wins:
            st.markdown(f"### 💻 Computer won the match ({losses} — {wins})")
        else:
            st.markdown(f"### 🤝 Match tie ({wins} — {losses})")

        col_save, col_play, col_reset = st.columns(3)
        with col_save:
            if st.button("Save score to leaderboard"):
                save_score_to_leaderboard(st.session_state.player_name, wins, losses, draws)
                st.success("Score saved to leaderboard")
        with col_play:
            if st.button("Play again"):
                # keep player name and settings; reset match stats but not leaderboard
                st.session_state.player_score = 0
                st.session_state.comp_score = 0
                st.session_state.draws = 0
                st.session_state.rounds_played = 0
                st.session_state.history = []
                st.session_state.game_over = False
                st.session_state.last_result = ""
                st.session_state.streak = 0
                st.session_state.last_winner = None
                st.rerun()
        with col_reset:
            if st.button("Reset everything (including name)"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()

    st.markdown("---")

    # Round history and stats
    st.subheader("Round history")
    if st.session_state.history:
        hist_df = pd.DataFrame(st.session_state.history)
        st.dataframe(hist_df.sort_values(by="round", ascending=False).reset_index(drop=True))

    # stats & simple chart
    st.subheader("Match stats & chart")
    st.write(f"**Wins:** {st.session_state.player_score} — **Losses:** {st.session_state.comp_score} — **Draws:** {st.session_state.draws}")
    total = max(1, st.session_state.rounds_played)
    win_rate = round(100 * st.session_state.player_score / total, 1)
    st.write(f"Win rate: {win_rate}% — Current streak: {st.session_state.streak} ({st.session_state.last_winner})")

    # line chart of cumulative score
    if st.session_state.history:
        rounds = [r["round"] for r in st.session_state.history]
        player_cum = []
        comp_cum = []
        p = c = 0
        for r in st.session_state.history:
            if r["winner"] == "Player":
                p += 1
            elif r["winner"] == "Computer":
                c += 1
            player_cum.append(p)
            comp_cum.append(c)
        plt.figure(figsize=(6,3))
        plt.plot(rounds, player_cum, label=st.session_state.player_name)
        plt.plot(rounds, comp_cum, label="Computer")
        plt.xlabel("Round")
        plt.ylabel("Cumulative wins")
        plt.legend()
        st.pyplot(plt)

with right:
    st.header("Leaderboard & Summary")
    lb = load_leaderboard()
    if lb.empty:
        st.info("Leaderboard is empty — play matches and save scores!")
    else:
        # aggregated leaderboard (sum per player)
        agg = lb.groupby("player", as_index=False).agg({
            "wins": "sum",
            "losses": "sum",
            "draws": "sum",
            "score": "sum",
        })
        agg["win_rate"] = agg.apply(lambda r: round(100 * (r.wins / max(1, r.wins + r.losses + r.draws)), 1), axis=1)
        agg = agg.sort_values(by=["score", "wins"], ascending=False).reset_index(drop=True)
        agg.index += 1
        st.markdown("### Top players")
        st.dataframe(agg.head(10))

    st.markdown("---")
    st.subheader("Quick lookup")
    lookup = st.text_input("Show results for player (name)")
    if lookup:
        filtered = lb[lb["player"].str.contains(lookup, case=False, na=False)]
        if filtered.empty:
            st.warning("No entries found for that name")
        else:
            st.dataframe(filtered.sort_values(by="date", ascending=False))

    st.markdown("---")
    st.subheader("Admin tools")
    if st.button("Re-load leaderboard"):
        st.cache_data.clear()
        st.rerun()
    st.caption("Leaderboards are saved in leaderboard.csv in the app folder.")

# --- Footer / tips ---
st.markdown("---")
st.markdown("**Tips for the game center:**\n- Use 'Race to Score' for quick tournaments (e.g., first to 5).\n- Export CSV and maintain a weekly/monthly backup.\n- Consider adding pictures for each move and a tablet-friendly layout for younger players.")

st.markdown("---")
st.markdown("_Built with ❤️ for your Game Center — ask me to add multi-player mode, keyboard controls, or themed skins!_")
