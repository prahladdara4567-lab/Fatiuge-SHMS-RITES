import streamlit as st
import pandas as pd
from fatigue_engine import run_fatigue_analysis

st.title("Bridge Fatigue Assessment Tool")

uploaded_file = st.file_uploader(
    "Upload Stress-Time Excel File",
    type=["xlsx"]
)

detail_category = st.selectbox(
    "Select Detail Category",
    [160, 140, 125, 112, 100, 90, 80, 71, 63, 56, 50, 45, 40, 36]
)

if uploaded_file:

    st.success("File Uploaded Successfully")

    df = pd.read_excel(uploaded_file)

    st.subheader("Input Data Preview")

    st.dataframe(df.head())

    if st.button("Run Fatigue Assessment"):

        with open("uploaded.xlsx", "wb") as f:
            f.write(uploaded_file.getbuffer())

        summary_df = run_fatigue_analysis(
            "uploaded.xlsx",
            detail_category
        )

        st.success("Analysis Completed")

        st.subheader("Fatigue Assessment Summary")

        st.dataframe(summary_df)