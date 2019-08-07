import pandas as pd


def recommend(score, df):
    if score * 100 < 21:
        return pd.DataFrame(columns=['BANKS', 'LOANS', 'RATES', 'MAX_AMOUNT'])
    elif score * 100 < 30:
        fil = df.RATES > 14
        fil2 = df.RATES < 20
        return df[fil & fil2]
    elif score * 100 < 40:
        fil = df.RATES > 10
        fil2 = df.RATES < 14
        return df[fil & fil2]
    elif score * 100 < 50:
        fil = df.RATES > 5
        fil2 = df.RATES < 10
        return df[fil & fil2]
    else:
        filters = df.RATES < 5
        return df[filters]
