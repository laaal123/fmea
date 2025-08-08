import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="FMEA Risk Assessment & DoE Factor Selection", layout="wide")

st.title("FMEA Risk Assessment & DoE Factor Selection with Validation")
st.markdown("""
Enter your formulation/process variables with Severity, Occurrence, and Detectability scores (1-10).  
The app calculates the Risk Priority Number (RPN), classifies risk levels per ICH guidelines,  
visualizes risks in a heatmap, and highlights variables suggested for your Design of Experiment (DoE).  
""")

with st.expander("📘 ICH Q9-Based Scoring Guidelines"):
    st.markdown("""
    #### 🔹 Severity (Impact on Product Quality or Patient Safety)
    | Score | Description | Impact |
    |-------|-------------|--------|
    | 10    | Critical    | Life-threatening, recall, regulatory impact |
    | 7-9   | High        | Affects product efficacy or critical quality |
    | 4-6   | Moderate    | Performance affected, not safety-critical |
    | 1-3   | Low         | Aesthetic or negligible impact |

    #### 🔸 Occurrence (Probability of Failure)
    | Score | Frequency | Description |
    |-------|-----------|-------------|
    | 10    | Frequent  | >1 in 2 batches |
    | 7-9   | Likely    | 1 in 10 batches |
    | 4-6   | Occasional| 1 in 50–500 batches |
    | 1-3   | Rare      | Extremely rare or well controlled |

    #### 🔻 Detectability (Can it be Detected Before Release?)
    | Score | Detectability | Description |
    |-------|---------------|-------------|
    | 10    | Impossible    | No detection before reaching patient |
    | 7-9   | Very Low      | Detected only after release (e.g., complaints) |
    | 4-6   | Low–Medium    | Detected in QC or delayed IPC |
    | 1-3   | High          | Detected in real-time (PAT, inline controls) |
    """)

num_vars = st.number_input("Number of variables to assess", min_value=1, max_value=30, value=5, step=1)

variables = []
severity = []
occurrence = []
detectability = []

st.subheader("📝 Input Variables and Risk Scores")

validation_errors = []

for i in range(num_vars):
    var_name = st.text_input(f"Variable {i+1} name", key=f"var_{i}")
    sev = st.slider(f"Severity (1-10) for {var_name or 'Variable ' + str(i+1)}", 1, 10, 5, key=f"sev_{i}")
    occ = st.slider(f"Occurrence (1-10) for {var_name or 'Variable ' + str(i+1)}", 1, 10, 5, key=f"occ_{i}")
    det = st.slider(f"Detectability (1-10) for {var_name or 'Variable ' + str(i+1)}", 1, 10, 5, key=f"det_{i}")

    if not var_name.strip():
        validation_errors.append(f"Variable {i+1} name cannot be empty or whitespace.")
    variables.append(var_name.strip() if var_name.strip() else f"Variable {i+1}")
    severity.append(sev)
    occurrence.append(occ)
    detectability.append(det)

# Check for duplicate variable names
duplicates = [var for var in set(variables) if variables.count(var) > 1]
if duplicates:
    validation_errors.append(f"Duplicate variable names found: {', '.join(duplicates)}")

if validation_errors:
    st.error("Please fix the following errors before proceeding:")
    for err in validation_errors:
        st.write(f"\u2022 {err}")
    st.stop()

# Create DataFrame
df = pd.DataFrame({
    "Variable": variables,
    "Severity": severity,
    "Occurrence": occurrence,
    "Detectability": detectability
})

# Calculate RPN
df["RPN"] = df["Severity"] * df["Occurrence"] * df["Detectability"]

# Assign Risk Levels
def risk_level(rpn):
    if rpn <= 100:
        return "Low"
    elif 101 <= rpn <= 200:
        return "Medium"
    else:
        return "High"

df["Risk Level"] = df["RPN"].apply(risk_level)

st.subheader("📊 Risk Priority Number (RPN) and Risk Levels")
st.dataframe(df.style.format({"RPN": "{:.0f}"}))

# Heatmap
st.subheader("🔥 Heatmap Visualization: Severity vs Occurrence")
heatmap_data = df.pivot_table(index='Severity', columns='Occurrence', values='RPN', aggfunc=np.mean)
fig, ax = plt.subplots(figsize=(8,6))
sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlOrRd", cbar_kws={'label': 'RPN'}, ax=ax)
ax.set_title("Heatmap of RPN by Severity and Occurrence")
st.pyplot(fig)

# DoE Suggestions
st.subheader("🧪 Suggested Variables for DoE (Medium and High Risk)")
doe_vars = df[df["Risk Level"].isin(["Medium", "High"])]

if not doe_vars.empty:
    st.dataframe(doe_vars[["Variable", "Severity", "Occurrence", "Detectability", "RPN", "Risk Level"]])
else:
    st.info("No variables classified as Medium or High risk. Nothing suggested for DoE.")

# Optional: Show Low Risk
show_low = st.checkbox("Show Low Risk Variables (Usually excluded from DoE)", value=False)
if show_low:
    low_vars = df[df["Risk Level"] == "Low"]
    if not low_vars.empty:
        st.dataframe(low_vars[["Variable", "Severity", "Occurrence", "Detectability", "RPN", "Risk Level"]])
    else:
        st.write("No variables classified as Low risk.")

# Context Note
st.markdown("""
---
### 📘 Notes:
- This tool follows **ICH Q9 Risk Management** principles.
- **RPN = Severity × Occurrence × Detectability** helps prioritize risk.
- Use the guidance tables to assign accurate scores.
- High-risk variables should be considered in **control strategy** and **DoE optimization**.
""")
