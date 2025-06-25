import streamlit as st
import pandas as pd
from io import BytesIO
import traceback
import os

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

uploaded_file = st.file_uploader("Upload your file (.xlsx, .csv, .txt)", type=["xlsx", "csv", "txt"])

# Function to load file
@st.cache_data
def load_file(file, name):
    ext = os.path.splitext(name)[1].lower()
    if ext == '.xlsx':
        return pd.read_excel(file)
    elif ext in ['.csv', '.txt']:
        return pd.read_csv(file, encoding='utf-8', delimiter=None)
    else:
        raise ValueError("Unsupported file format")

# Transliteration
def transliterate_dataframe(df, scheme):
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).apply(lambda x: transliterate(x, DEVANAGARI, scheme))
    return df

# Converts DataFrame to Excel bytes
def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

# App Logic
if uploaded_file is not None:
    try:
        df = load_file(uploaded_file, uploaded_file.name)
        st.subheader("Original Data Preview (Top 100 rows)")
        st.dataframe(df.head(100))

        df_transliterated = transliterate_dataframe(df.copy(), selected_scheme)

        st.subheader("Transliterated Data Preview (Top 100 rows)")
        st.dataframe(df_transliterated.head(100))

        excel_data = to_excel_bytes(df_transliterated)

        st.download_button(
            label="Download Transliterated Excel",
            data=excel_data,
            file_name=f"transliterated_{selected_label.lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception:
        st.error(" Error processing file:")
        st.text(traceback.format_exc())
