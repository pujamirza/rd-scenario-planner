
import streamlit as st
import pandas as pd

st.title("R&D Resource Scenario Planner")

# Upload CSV
uploaded_file = st.file_uploader("Upload your allocation data (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(
        uploaded_file,
        encoding='utf-8',
        sep=",",
        engine="python",
        on_bad_lines='skip'
    )
    st.success("File loaded!")

    scenario = st.selectbox("Select Scenario", ["Freeze", "Delay"])

    # Hardcoded month list for reliability
    month_cols = [
        "Jan-25", "Feb-25", "Mar-25", "Apr-25", "May-25", "Jun-25",
        "Jul-25", "Aug-25", "Sep-25", "Oct-25", "Nov-25", "Dec-25"
    ]

    if scenario == "Freeze":
        sub_func = st.selectbox("Select Sub-function", sorted(df["Sub function"].dropna().unique()))
        available_months = [col for col in month_cols if col in df.columns]
        month = st.selectbox("Select Month", available_months)

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

    elif scenario == "Delay":
        project = st.selectbox("Select Project", sorted(df["Project Name"].dropna().unique()))
        shift = st.number_input("Delay by how many months?", min_value=1, max_value=12, step=1, value=1)

        available_months = [col for col in month_cols if col in df.columns]
        if st.button("Run Delay Scenario"):
            mask = (df["Project Name"] == project)
            affected = df.loc[mask, available_months].copy()
            df.loc[mask, available_months] = 0

            for i in range(len(available_months)):
                new_index = i + shift
                if new_index < len(available_months):
                    df.loc[mask, available_months[new_index]] = affected.iloc[:, i]

            st.metric("Project Delayed", project)
            st.metric("Months Shifted", shift)
            st.subheader("New FTE Allocation (First 5 Rows)")
            st.dataframe(df.loc[mask].head())

            st.download_button("Download Modified Data", df.to_csv(index=False), file_name="delayed_allocations.csv")
