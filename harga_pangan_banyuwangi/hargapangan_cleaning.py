import pandas as pd
import numpy as np

def clean_excel(file_path):
    df = pd.read_excel('{}.xlsx'.format(file_path))
    df = df.drop([1, 2, 18])
    df = df.dropna(axis=1, how='any')
    df = df.set_index('Komoditas(Rp)')
    for column in df:
        if df.iloc[0][column] == '-':
            df.loc[:,column] = np.nan
    df = df.T
    df = df.bfill()
    df.to_excel('{}.xlsx'.format(file_path))
    
    return df