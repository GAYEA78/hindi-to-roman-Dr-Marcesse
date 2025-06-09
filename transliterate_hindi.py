import pandas as pd
from indic_transliteration.sanscript import transliterate
from indic_transliteration.sanscript import DEVANAGARI, ITRANS


df = pd.read_excel("data.xlsx")


def transliterate_dataframe(df):
    for col in df.columns:
        if df[col].dtype == object:  
            df[col] = df[col].astype(str).apply(lambda x: transliterate(x, DEVANAGARI, ITRANS))
    return df


df_roman = transliterate_dataframe(df)

df_roman.to_excel("data_roman.xlsx", index=False)

print("Transliteration complete! File saved as 'data_roman.xlsx'.")