import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math

st.set_page_config(page_title="College Attendance Calculator", layout="centered")

# Simple CSS to control card and colors
st.markdown(
    """
    <style>
    .card {border-radius:12px; padding:18px; box-shadow: 0 6px 18px rgba(0,0,0,0.06);}
    .small {font-size:0.9rem; color: #666}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.title("📊 College Attendance Calculator")
st.write("Calculate how many more classes you need to reach or maintain your target attendance percentage.")

# --- Inputs ---
with st.form("inputs", clear_on_submit=False):
    attended = st.number_input("Number of classes attended", min_value=0, step=1, value=0)
    total = st.number_input("Total number of classes conducted", min_value=1, step=1, value=1)
    target = st.number_input("Target attendance percentage", min_value=1.0, max_value=100.0, value=80.0, format="%.2f")
    submit = st.form_submit_button("Calculate ✅")

# Input validation function
def validate_inputs(attended: int, total: int, target: float):
    errors = []
    if attended < 0:
        errors.append("Attended classes cannot be negative.")
    if total < 1:
        errors.append("Total classes must be at least 1.")
    if attended > total:
        errors.append("Attended classes cannot exceed total classes conducted.")
    if not (1 <= target <= 100):
        errors.append("Target percentage must be between 1 and 100.")
    return errors

# Utility: compute additional classes needed
def additional_classes_needed(attended: int, total: int, target: float) -> int:
    if math.isclose(target, 100.0):
        return 0 if attended == total else -1
    numerator = (target * total) - (100.0 * attended)
    denominator = 100.0 - target
    if denominator == 0:
        return -1
    x = numerator / denominator
    return 0 if x <= 0 else math.ceil(x)

# Utility: compute how many classes can be missed
def classes_can_be_missed(attended: int, total: int, target: float) -> int:
    # If already above target, find max missed classes before falling below target
    missable = ((100 * attended) - (target * total)) / target
    return math.floor(missable) if missable > 0 else 0

# Perform calculation and show results
if submit:
    errors = validate_inputs(attended, total, target)
    if errors:
        for e in errors:
            st.error(f"⚠️ {e}")
    else:
        current_pct = (attended / total) * 100.0
        st.metric(label="Current attendance", value=f"{current_pct:.2f}%")

        # --- Case 1: 100% target but not possible ---
        if math.isclose(target, 100.0) and attended < total:
            st.warning("⚠️ Target of 100% is only achievable if you have already attended all conducted classes.")
            st.info("📌 Tip: Speak to your instructor about make-up classes or policies for 100% requirements.")

        else:
            needed = additional_classes_needed(attended, total, target)

            # --- Case 2: attendance already above target ---
            if current_pct >= target:
                st.success(f"✅ Great! Your current attendance ({current_pct:.2f}%) meets or exceeds the target of {target:.2f}%.")

                can_miss = classes_can_be_missed(attended, total, target)
                if can_miss > 0:
                    st.info(f"🧮 You can afford to miss **{can_miss}** more class{'es' if can_miss > 1 else ''} "
                            f"and still maintain at least **{target:.2f}%** attendance.")
                else:
                    st.info("📊 You cannot afford to miss any more classes if you want to stay above the target.")

            # --- Case 3: below target ---
            elif needed > 0:
                st.warning(f"⚠️ You need to attend at least **{needed}** more class{'es' if needed>1 else ''} "
                           f"to reach {target:.2f}%.")

            # --- Case 4: invalid computation ---
            elif needed == -1:
                st.warning("⚠️ Cannot compute with the given inputs (division by zero).")

            # --- Visual progress bar ---
            progress_value = min(current_pct / target, 1.0)
            st.write("Progress toward target:")
            st.progress(progress_value)

            # --- Chart visualization ---
            future_attended = attended + max(0, needed)
            future_total = total + max(0, needed)
            future_pct = (future_attended / future_total) * 100.0

            fig, ax = plt.subplots(figsize=(5, 2.2))
            bars = ax.bar([0, 1], [current_pct, target], tick_label=["Current %", "Target %"])
            ax.set_ylim(0, max(100, target + 10))
            for i, v in enumerate([current_pct, target]):
                ax.text(i, v + 1, f"{v:.1f}%", ha='center')
            ax.set_title("Attendance vs Target")
            st.pyplot(fig)

            st.info(f"📌 After attending **{max(0, needed)}** more class{'es' if needed>1 else ''}, "
                    f"your attendance would be **{future_pct:.2f}%** (assuming no classes are missed).")

# Footer
st.markdown("---")
st.markdown('<div class="small">By Sourav Lenka</div>', unsafe_allow_html=True)
