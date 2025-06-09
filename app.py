import streamlit as st
import pandas as pd
from io import BytesIO
import traceback

from indic_transliteration.sanscript import (
    transliterate,
    DEVANAGARI,
    ITRANS, HK, IAST, SLP1, VELTHUIS
)

st.title("Hindi to Roman Transliteration – Dr. Marcesse, By Arona Gaye")

# Mapping
scheme_options = {
    "ITRANS": ITRANS,
    "HK": HK,
    "IAST": IAST,
    "SLP1": SLP1,
    "VELTHUIS": VELTHUIS
}

selected_label = st.selectbox("Select Romanization Scheme:", list(scheme_options.keys()))
selected_scheme = scheme_options[selected_label]

uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])

def transliterate_dataframe(df, scheme):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).apply(lambda x: transliterate(x, DEVANAGARI, scheme))
    return df

#Converts DataFrame to Excel file in memory
def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

#App logic
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.subheader("Original Data Preview")
        st.dataframe(df.head())

        df_transliterated = transliterate_dataframe(df, selected_scheme)

        st.subheader("Transliterated Data Preview")
        st.dataframe(df_transliterated.head())

        excel_data = to_excel_bytes(df_transliterated)

        st.download_button(
            label="Download Transliterated Excel",
            data=excel_data,
            file_name=f"transliterated_{selected_label.lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception:
        st.error("❌ Error processing file:")
        st.text(traceback.format_exc())
