import csv
import pandas as pd
import numpy as np

cat_list = ['Star', 'Opportunity', 'Puzzle', 'Dog']
df = pd.read_csv('/home/wandored/Dropbox/Restaurant365/Report_Data/Menu Item Analysis.csv',
                 skiprows=3, sep=',', thousands=',')
df[['Location', 'MenuItem']] = df['ItemName'].str.split('- ', expand=True)
df.rename(columns={'Textbox293': 'Price', 'Textbox294': 'Cost', 'Textbox297': 'Qty', 'Textbox298': 'Sales$',
                   'Textbox301': 'TheoCost', 'Textbox302': 'Profit', 'Textbox52': 'Category'}, inplace=True)

df.drop(columns={'Textbox295', 'Textbox296', 'Textbox299', 'Textbox300', 'Textbox107', 'ItemName', 'Textbox86', 'Textbox26', 'Textbox24', 'EachMargin', 'Textbox4', 'TotalQuantity', 'TotalSales', 'Textbox46', 'Textbox10', 'TheoCost', 'TotalProfit', 'Textbox41', 'EachPrice3', 'EachCost3', 'EachMargin3',
                 'Textbox129', 'TotalQuantity3', 'TotalSales3', 'Textbox130', 'Textbox131', 'TheoCost3', 'TotalProfit3', 'Textbox133', 'Textbox134', 'Textbox135', 'Textbox136', 'Textbox138', 'Textbox141', 'Textbox142'}, inplace=True)
df_pmix = df.reindex(columns=['Location', 'MenuItem',  'Price',
                              'Cost', 'Margin', 'FC%', 'Qty', 'Sales$', 'Profit', 'Category'])
# df_pmix.groupby(['MenuItem']).agg(
#    {'Qty': 'sum', 'MenuPrice': 'max', 'Total': 'sum'})
df_pmix.sort_values(by='Category', ascending=False,
                    ignore_index=True, inplace=True)
x = df_pmix['Margin'].mean()
y = df_pmix['Qty'].mean()
print(df_pmix['Cost'].add(1.6))

print(df_pmix)
#
# with pd.ExcelWriter('/home/wandored/Dropbox/Restaurant365/Report_Data/Product Mix.xlsx') as writer:
#    df_pmix.to_excel(writer, index=False)
#
# for cat in cat_list:
#    filt = (df_pmix['Category'] == f'{cat}')
#    print(df_pmix.loc[filt].sort_values(by='Qty', ascending=False))
