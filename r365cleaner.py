import csv
import pandas as pd
import numpy as np

cat_list = ['Appetizer', 'Salad', 'Entree', 'Side', 'Sandwich', 'Dessert']
df = pd.read_csv('/home/wandored/Dropbox/Restaurant365/Report_Data/Product Mix.csv',
                 skiprows=3, sep=',', thousands=',')
df[['remove', 'MenuItem']] = df['TransferDate'].str.split('- ', expand=True)
df.rename(columns={'Textbox27': 'Location',
                   'Cost': 'MenuPrice', 'Cat2': 'Category'}, inplace=True)

df.drop(columns={'Textbox3', 'Textbox17', 'Textbox20', 'ToLocationName', 'TransferDate',
                 'dm_Quantity', 'Cat1',  'Cat3', 'remove'}, inplace=True)
df_pmix = df.reindex(columns=['Location', 'Category', 'MenuItem', 'Qty',
                              'MenuPrice', 'Total'])
df_pmix.groupby(['MenuItem']).agg(
    {'Qty': 'sum', 'MenuPrice': 'max', 'Total': 'sum'})
# df_pmix.sort_values(by='Qty', ascending=False,
#                        ignore_index=True, inplace=True)

print(df_pmix)

with pd.ExcelWriter('/home/wandored/Dropbox/Restaurant365/Report_Data/Product Mix.xlsx') as writer:
    df_pmix.to_excel(writer, index=False)

for cat in cat_list:
    filt = (df_pmix['Category'] == f'{cat}')
    print(df_pmix.loc[filt].sort_values(by='Qty', ascending=False))

