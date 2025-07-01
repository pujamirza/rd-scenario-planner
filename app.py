import streamlit as st
import pandas as pd

st.title("R&D Resource Scenario Planner")

# Upload CSV
uploaded_file = st.file_uploader("Upload your allocation data (CSV)", type="csv")

if uploaded_file:
df = pd.read_csv(uploaded_file, encoding='utf-8', sep=",", engine="python", on_bad_lines='skip')
    st.success("File loaded!")

    # Show options
    scenario = st.selectbox("Select Scenario", ["Freeze"])
    sub_func = st.selectbox("Select Sub-function", sorted(df["Sub function"].dropna().unique()))
    month = st.selectbox("Select Month", [col for col in df.columns if "25" in col])

    if st.button("Run Scenario"):
        mask = (df["Sub function"] == sub_func)
        total_fte = df.loc[mask, month].fillna(0).sum()
        df.loc[mask, month] = 0
        st.metric("FTEs Freed", round(total_fte, 2))

        top_projects = (
            df.loc[mask]
            .groupby("Project Name")[month]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )
        st.subheader("Top Projects Affected")
        st.dataframe(top_projects)

        st.download_button("Download Modified Data", df.to_csv(index=False), file_name="modified_allocations.csv")
