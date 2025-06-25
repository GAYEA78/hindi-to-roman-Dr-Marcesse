import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
import os
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

uploaded_file = st.file_uploader(
    "Upload your file (.xlsx, .csv, .txt, .zip)", 
    type=["xlsx", "csv", "txt", "zip"]
)

@st.cache_data
def load_file(file, name):
    ext = os.path.splitext(name)[1].lower()
    if ext == '.xlsx':
        return pd.read_excel(file)
    elif ext in ['.csv', '.txt']:
        return pd.read_csv(file, encoding='utf-8', delimiter=None)
    else:
        raise ValueError("Unsupported file format")

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

# App logic
if uploaded_file is not None:
    try:
        filename = uploaded_file.name

        # Handle .zip files
        if filename.endswith(".zip"):
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                if not file_list:
                    raise ValueError("The ZIP file is empty.")
                st.info(f"Extracting: {file_list[0]}")
                with zip_ref.open(file_list[0]) as extracted_file:
                    df = load_file(extracted_file, file_list[0])
        else:
            df = load_file(uploaded_file, filename)

        st.subheader("Original Data Preview (Top 100 Rows)")
        st.dataframe(df.head(100))

        df_transliterated = transliterate_dataframe(df.copy(), selected_scheme)

        st.subheader("Transliterated Data Preview (Top 100 Rows)")
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
