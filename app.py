import streamlit as st
import pandas as pd
from io import BytesIO
from indic_transliteration.sanscript import SCHEMES
from indic_transliteration.sanscript import transliterate, DEVANAGARI
import traceback

st.title("Hindi to Roman Transliteration, Dr. Marcesse")

available_schemes = ["ITRANS", "HK", "IAST", "SLP1", "VELTHUIS"]
selected_scheme = st.selectbox("Select Romanization Scheme:", available_schemes, index=0)

uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx"])

def transliterate_dataframe(df, scheme):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).apply(lambda x: transliterate(x, DEVANAGARI, scheme))
    return df

def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

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
            file_name=f"transliterated_{selected_scheme.lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


    except Exception as e:
        st.error("❌ Error processing file:")
        st.text(traceback.format_exc())

