import streamlit as st
import re
import pandas as pd
import os

# Page config
st.set_page_config(page_title="Eco Sarees - Sign Up", page_icon="🌿", layout="centered")

# Company Header
st.markdown("<h1 style='text-align: center; color: green;'>Eco Sarees</h1>", unsafe_allow_html=True)
st.markdown("---")

# File to store signups
CSV_FILE = "eco_sarees_users.csv"

# Sign Up Form
with st.form("signup_form"):
    st.subheader("Sign Up")

    # Inputs
    name = st.text_input("Full Name")
    age = st.slider("Age", min_value=1, max_value=100, value=25)
    phone = st.text_input("Phone Number", max_chars=15, placeholder="e.g., +919876543210")

    # Submit button
    submitted = st.form_submit_button("Sign Up")

    if submitted:
        # Basic validations
        if not name.strip():
            st.error("⚠️ Please enter your name.")
        elif not phone.strip():
            st.error("⚠️ Please enter your phone number.")
        elif not re.fullmatch(r"^\+?\d{10,15}$", phone):
            st.error("⚠️ Please enter a valid phone number (10–15 digits, optional +).")
        else:
            # Save to CSV
            new_entry = pd.DataFrame([[name.strip(), age, phone.strip()]],
                                     columns=["Name", "Age", "Phone"])

            if os.path.exists(CSV_FILE):
                existing = pd.read_csv(CSV_FILE)
                updated = pd.concat([existing, new_entry], ignore_index=True)
                updated.to_csv(CSV_FILE, index=False)
            else:
                new_entry.to_csv(CSV_FILE, index=False)

            st.success(f"🎉 Welcome {name}! You have successfully signed up for Eco Sarees.")
            st.info("✅ Your details have been saved.")

# Show registered users (optional, for admin view)
if os.path.exists(CSV_FILE):
    st.subheader("📋 Registered Users")
    users = pd.read_csv(CSV_FILE)
    st.dataframe(users, use_container_width=True)