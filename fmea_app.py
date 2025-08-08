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

num_vars = st.number_input("Number of variables to assess", min_value=1, max_value=30, value=5, step=1)

variables = []
severity = []
occurrence = []
detectability = []

st.subheader("Input Variables and Scores")

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
        st.write(f"• {err}")
    st.stop()  # Stop execution here until errors are fixed

# Create DataFrame
df = pd.DataFrame({
    "Variable": variables,
    "Severity": severity,
    "Occurrence": occurrence,
    "Detectability": detectability
})

df["RPN"] = df["Severity"] * df["Occurrence"] * df["Detectability"]

def risk_level(rpn):
    if rpn <= 100:
        return "Low"
    elif 101 <= rpn <= 200:
        return "Medium"
    else:
        return "High"

df["Risk Level"] = df["RPN"].apply(risk_level)

st.subheader("Risk Priority Number (RPN) and Risk Levels")
st.dataframe(df.style.format({"RPN": "{:.0f}"}))

st.subheader("Heatmap Visualization: Severity vs Occurrence (colored by average RPN)")

heatmap_data = df.pivot_table(index='Severity', columns='Occurrence', values='RPN', aggfunc=np.mean)

fig, ax = plt.subplots(figsize=(8,6))
sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlOrRd", cbar_kws={'label': 'RPN'}, ax=ax)
ax.set_title("Heatmap of RPN by Severity and Occurrence")
st.pyplot(fig)

st.subheader("Suggested Variables for DoE (Medium and High Risk)")
doe_vars = df[df["Risk Level"].isin(["Medium", "High"])].reset_index(drop=True)

if not doe_vars.empty:
    st.dataframe(doe_vars[["Variable", "Severity", "Occurrence", "Detectability", "RPN", "Risk Level"]])
else:
    st.write("No variables classified as Medium or High risk, so no variables suggested for DoE.")

show_low = st.checkbox("Show Low Risk Variables (Usually excluded from DoE)", value=False)
if show_low:
    low_vars = df[df["Risk Level"] == "Low"].reset_index(drop=True)
    if not low_vars.empty:
        st.dataframe(low_vars[["Variable", "Severity", "Occurrence", "Detectability", "RPN", "Risk Level"]])
    else:
        st.write("No variables classified as Low risk.")

st.markdown("""
---
### Notes (ICH Q9 Risk Management Context):

- **Severity, Occurrence, and Detectability scores** typically range from 1 (low) to 10 (high).  
- **RPN (Risk Priority Number)** = Severity × Occurrence × Detectability helps prioritize risks.  
- According to ICH Q9 and common pharma practice:  
  - *Low Risk (RPN ≤ 100)*: Acceptable or minimal control needed, often excluded from DoE.  
  - *Medium Risk (101 ≤ RPN ≤ 200)*: Monitor and include in DoE for optimization.  
  - *High Risk (RPN > 200)*: Requires strong control measures, must be included in DoE.  
- This tool helps prioritize your factors to focus your experimental efforts efficiently.  
- **Risk mitigation, verification, and continuous monitoring** should also be considered as per ICH Q9.  
""")
