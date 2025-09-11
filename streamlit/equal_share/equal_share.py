import streamlit as st
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
from typing import List, Dict, Tuple

# ---------- Page config ----------
st.set_page_config(page_title="Fair Expense Splitter", page_icon="🧮", layout="centered")

# ---------- Helpers ----------
def to_decimal(x) -> Decimal:
    """Safely convert floats/ints/str to Decimal using string constructor."""
    if isinstance(x, Decimal):
        return x
    try:
        return Decimal(str(x))
    except Exception:
        return Decimal(0)


def fmt_money(cents: int, multiplier: int, currency: str) -> str:
    """Format an integer amount of smallest units (e.g., paise/cents) to a money string."""
    amt = Decimal(cents) / Decimal(multiplier)
    # Always show 2 decimals if multiplier is 100, else show up to 2 depending on unit
    # We’ll show up to 2 places; if rounding unit is whole, Streamlit will still show .00 which is fine
    return f"{currency}{amt:,.2f}"


def compute_shares_and_nets(people: List[Dict[str, str | float | int]], rounding_unit: Decimal) -> Tuple[pd.DataFrame, int, int, List[int]]:
    """
    Given a list of people with fields {name, paid}, compute:
      - total in smallest units (int)
      - per-person fair shares in smallest units (int, distributed fairly so sum shares = total)
      - net per person in smallest units (paid - share)
    The rounding unit determines the smallest unit (e.g., 0.01, 1, 0.05). We convert everything into
    integer multiples of that unit to avoid floating errors and guarantee nets sum to zero.
    Returns: (df, total_cents, multiplier, shares_list)
    df has columns: name, paid_cents, share_cents, net_cents
    """
    unit = rounding_unit
    # Convert rounding unit (e.g., 0.01) to integer multiplier (e.g., 100)
    multiplier = int((Decimal(1) / unit).to_integral_value(rounding=ROUND_HALF_UP))

    # Build clean rows and convert paid to cents (integer units of 'unit')
    rows = []
    for p in people:
        name = (p.get("name") or "").strip() or "Person"
        paid_raw = to_decimal(p.get("paid", 0))
        if paid_raw < 0:
            paid_raw = Decimal(0)
        paid_cents = int((paid_raw * multiplier).to_integral_value(rounding=ROUND_HALF_UP))
        rows.append({"name": name, "paid_cents": paid_cents})

    if not rows:
        return pd.DataFrame(columns=["name","paid_cents","share_cents","net_cents"]), 0, multiplier, []

    total_cents = sum(r["paid_cents"] for r in rows)
    n = len(rows)

    # Fair shares: base + distribute remainder to first `remainder` people
    base_share = total_cents // n
    remainder = total_cents % n

    shares = [base_share + (1 if i < remainder else 0) for i in range(n)]

    # Nets are exact and sum to zero by construction
    for i, r in enumerate(rows):
        r["share_cents"] = shares[i]
        r["net_cents"] = r["paid_cents"] - r["share_cents"]

    df = pd.DataFrame(rows, columns=["name", "paid_cents", "share_cents", "net_cents"])
    return df, total_cents, multiplier, shares


def settle_transfers(df: pd.DataFrame) -> List[Tuple[str, str, int]]:
    """Greedy min-cashflow settlement from df with columns name, net_cents.
    Returns list of (debtor_name, creditor_name, amount_cents)."""
    debtors = []  # (name, amount_owed_positive)
    creditors = []  # (name, amount_to_receive_positive)
    for _, row in df.iterrows():
        net = int(row["net_cents"])  # integer cents
        name = row["name"]
        if net < 0:
            debtors.append([name, -net])  # owes
        elif net > 0:
            creditors.append([name, net])  # should receive

    transfers: List[Tuple[str, str, int]] = []
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        d_name, d_amt = debtors[i]
        c_name, c_amt = creditors[j]
        pay = min(d_amt, c_amt)
        if pay > 0:
            transfers.append((d_name, c_name, pay))
        d_amt -= pay
        c_amt -= pay
        # advance pointers / update
        debtors[i][1] = d_amt
        creditors[j][1] = c_amt
        if d_amt == 0:
            i += 1
        if c_amt == 0:
            j += 1

    return transfers


# ---------- Sidebar: global options ----------
st.sidebar.title("⚙️ Settings")
currency = st.sidebar.text_input("Currency symbol", value="₹", help="Examples: ₹, $, €, £")
rounding_choice = st.sidebar.selectbox(
    "Rounding unit (smallest split unit)",
    (
        "0.01 – cents/paise",
        "1 – whole currency",
        "0.05 – 5 cents/paise",
    ),
    index=0,
    help="Controls the smallest unit used when computing shares and settlements.",
)
unit_map = {
    "0.01 – cents/paise": Decimal("0.01"),
    "1 – whole currency": Decimal("1"),
    "0.05 – 5 cents/paise": Decimal("0.05"),
}
rounding_unit = unit_map[rounding_choice]

st.title("🧮 Fair Expense Splitter")
st.caption("Split trip/dinner costs fairly, figure out who pays whom.")

# ---------- Tabs ----------
tab_simple, tab_detailed = st.tabs(["Quick split", "Detailed split & settle"]) 

# --- Tab: Quick split ---
with tab_simple:
    st.subheader("Quick split by headcount")
    with st.form("quick_form", clear_on_submit=False):
        total_amount = st.number_input("Total amount", min_value=0.0, step=0.01, format="%0.2f")
        headcount = st.number_input("Number of people", min_value=1, step=1, value=2)
        submitted = st.form_submit_button("Calculate per-person share")

    if submitted:
        unit = rounding_unit
        multiplier = int((Decimal(1) / unit).to_integral_value(rounding=ROUND_HALF_UP))
        total_cents = int((to_decimal(total_amount) * multiplier).to_integral_value(rounding=ROUND_HALF_UP))
        base_share = total_cents // headcount
        remainder = total_cents % headcount
        shares = [base_share + (1 if i < remainder else 0) for i in range(headcount)]
        # Display table
        data = {
            "Person": [f"Person {i+1}" for i in range(headcount)],
            "Share": [fmt_money(s, multiplier, currency) for s in shares],
        }
        st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)
        st.success(f"Each person owes approximately {fmt_money(base_share, multiplier, currency)} (with {remainder} person(s) paying {fmt_money(base_share+1, multiplier, currency)} due to rounding).")

# --- Tab: Detailed split ---
with tab_detailed:
    st.subheader("Detailed: enter who paid and settle up")

    st.markdown("""
    1. Enter everyone involved and how much each person **actually paid**.
    2. We'll compute a fair share for each person and the **recommended transfers** so everyone is square.
    """)

    # Starter table
    default_rows = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "paid": [0.0, 0.0, 0.0],
        }
    )

    st.caption("Tip: Use the + icon to add rows; you can also paste from a spreadsheet.")
    edited = st.data_editor(
        default_rows,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "name": st.column_config.TextColumn("Name", required=True),
            "paid": st.column_config.NumberColumn("Paid", min_value=0.0, step=0.01, format="%0.2f"),
        },
        key="people_editor",
    )

    # Clean empty rows
    edited = edited.fillna(0)
    edited["name"] = edited["name"].replace("", pd.NA)
    edited = edited.dropna(subset=["name"])

    if len(edited) == 0:
        st.info("Add at least one person to begin.")
        st.stop()

    if st.button("Calculate settlement", type="primary"):
        # Prepare people list for computation
        people = [
            {"name": r["name"], "paid": float(r["paid"]) if pd.notna(r["paid"]) else 0.0}
            for _, r in edited.iterrows()
        ]

        df, total_cents, multiplier, shares = compute_shares_and_nets(people, rounding_unit)

        if len(df) == 0:
            st.warning("Please provide at least one valid row.")
            st.stop()

        n = len(df)
        per_person_avg = total_cents / n if n else 0

        st.subheader("Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total paid", fmt_money(total_cents, multiplier, currency))
        with col2:
            st.metric("Headcount", n)

        # Display per-person table
        view = df.copy()
        view["Paid"] = view["paid_cents"].apply(lambda x: fmt_money(int(x), multiplier, currency))
        view["Fair share"] = view["share_cents"].apply(lambda x: fmt_money(int(x), multiplier, currency))
        view["Net (+receive / -owe)"] = view["net_cents"].apply(lambda x: fmt_money(int(x), multiplier, currency))
        view = view[["name", "Paid", "Fair share", "Net (+receive / -owe)"]].rename(columns={"name": "Name"})

        st.dataframe(view, hide_index=True, use_container_width=True)

        # Compute transfers
        transfers = settle_transfers(df)
        if transfers:
            st.subheader("Who pays whom")
            tdf = pd.DataFrame(
                {
                    "From": [t[0] for t in transfers],
                    "To": [t[1] for t in transfers],
                    "Amount": [fmt_money(t[2], multiplier, currency) for t in transfers],
                }
            )
            st.dataframe(tdf, hide_index=True, use_container_width=True)
        else:
            st.success("Everyone is already settled. No transfers needed ✨")

        # --- Downloads ---
        st.subheader("Export")
        export_df = df.copy()
        export_df.insert(0, "currency", currency)
        export_df["paid"] = export_df["paid_cents"]/multiplier
        export_df["share"] = export_df["share_cents"]/multiplier
        export_df["net"] = export_df["net_cents"]/multiplier
        export_df = export_df[["name","paid","share","net","currency"]]

        csv = export_df.to_csv(index=False)
        st.download_button("Download breakdown (CSV)", data=csv, file_name="fair_split_breakdown.csv", mime="text/csv")

        if transfers:
            t_export = pd.DataFrame(
                {
                    "from": [t[0] for t in transfers],
                    "to": [t[1] for t in transfers],
                    "amount": [Decimal(t[2])/Decimal(multiplier) for t in transfers],
                    "currency": currency,
                }
            )
            t_csv = t_export.to_csv(index=False)
            st.download_button("Download settlements (CSV)", data=t_csv, file_name="fair_settlements.csv", mime="text/csv")

        st.caption("Rounding is handled fairly by distributing the remainder; totals are exact in the selected unit.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit. Adjust rounding in **Settings** and use the **Detailed** tab for precise settlements.")