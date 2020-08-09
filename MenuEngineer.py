import csv
import pandas as pd
import numpy as np

df_product = pd.DataFrame()
df_cost = pd.DataFrame()
df_MenuEng = pd.DataFrame()

def engineer(df):
    qtm = df['Qty'].mean()
    df['qty_mn'] = np.where(df.Qty < qtm, False, True)
    print(qtm)
    mrgn = df['Margin'].mean()
    df['mrg_mn'] = np.where(df.Margin < mrgn, False, True)
    print(mrgn)
    return df

def rating(df):
    if df['qty_mn'] == True:
        if df['mrg_mn'] == True:
            return 'Star'
        else:
            return 'Opportunity'
    if df['qty_mn'] == False:
        if df['mrg_mn'] == True:
            return 'Puzzle'
        else:
            return 'Dog'

df_product= pd.read_csv('Product Mix.csv', skiprows=3, sep=',', thousands=',')

df_product[['Location', 'MenuItem']] = df_product['TransferDate'].str.split('- ', expand=True)

df_product.rename(columns={'Cost': 'Price', 'Total': 'Sales'}, inplace=True)
df_product.drop(columns={'Textbox3', 'Textbox27', 'TransferDate', 'ToLocationName', 'dm_Quantity', 'Textbox17', 'Textbox20'}, inplace=True)
df_pmix = df_product.reindex(columns=['Location', 'MenuItem', 'Qty', 'Price', 'Sales', 'Cat1', 'Cat2', 'Cat3'])
df_product= df_pmix
# print(df_product)

df_cost= pd.read_csv('Menu Price Analysis.csv', skiprows=3, sep=',', thousands=',')
df_cost[['Location', 'MenuItem']] = df_cost['MenuItemName'].str.split('- ', expand=True)
df_cost.drop(columns={'MenuItemName', 'Cost1', 'Profit1', 'Textbox43', 'PriceNeeded1', 'AvgPrice1', 'Textbox35', 'TargetMargin1', 'Profit', 'ProfitPercent', 'TargetMargin', 'Variance', 'PriceNeeded'}, inplace=True)
df_pmix = df_cost.reindex(columns=['Location', 'MenuItem', 'Cost', 'AvgPrice'])
df_cost = df_pmix
# print(df_cost)

df_MenuEng = pd.merge(df_product, df_cost, on='MenuItem', how='left', sort=False)
df_MenuEng.rename(columns={'Location_x': 'Location'}, inplace=True)
df_MenuEng.drop(columns={'Location_y', 'AvgPrice'}, inplace=True)
df_pmix = df_MenuEng.reindex(columns=['Location', 'MenuItem', 'Qty', 'Price', 'Sales', 'Cost', 'Cat1', 'Cat2', 'Cat3'])
df_MenuEng = df_pmix.drop(df_pmix[df_pmix.Price == 0].index)

df_MenuEng['FoodCost'] = df_MenuEng.apply(lambda row: row.Cost/row.Price, axis=1)
df_MenuEng['Margin'] = df_MenuEng.apply(lambda row: row.Price - row.Cost, axis=1)
df_pmix = df_MenuEng.reindex(columns=['Location', 'MenuItem', 'Qty', 'Price', 'FoodCost', 'Sales', 'Cost', 'Margin', 'Cat1', 'Cat2', 'Cat3'])
df_MenuEng = df_pmix

df_apps = df_MenuEng.drop(df_MenuEng[df_MenuEng.Cat2 != 'Appetizer'].index)
df_salad = df_MenuEng.drop(df_MenuEng[df_MenuEng.Cat2 != 'Salad'].index)
df_sand = df_MenuEng.drop(df_MenuEng[df_MenuEng.Cat2 != 'Sandwich'].index)
df_entree = df_MenuEng.drop(df_MenuEng[df_MenuEng.Cat2 != 'Entree'].index)
df_side = df_MenuEng.drop(df_MenuEng[df_MenuEng.Cat2 != 'Side'].index)
df_dessert = df_MenuEng.drop(df_MenuEng[df_MenuEng.Cat2 != 'Dessert'].index)

sort_list = ['Star', 'Opportunity', 'Puzzle', 'Dog']
df_apps = engineer(df_apps)
df_apps['rating'] = df_apps.apply(rating, axis=1)
df_apps.sort_values(by='rating', inplace=True, ascending=False)
print(df_apps)
df_salad = engineer(df_salad)
df_salad['rating'] = df_salad.apply(rating, axis=1)
df_salad.sort_values(by='rating', inplace=True, ascending=False)
print(df_salad)
df_sand = engineer(df_sand)
df_sand['rating'] = df_sand.apply(rating, axis=1)
df_sand.sort_values(by='rating', inplace=True, ascending=False)
print(df_sand)
df_entree = engineer(df_entree)
df_entree['rating'] = df_entree.apply(rating, axis=1)
df_entree.sort_values(by='rating', inplace=True, ascending=False)
print(df_entree)
# df_side = engineer(df_side)
# print(df_side)
df_dessert = engineer(df_dessert)
df_dessert['rating'] = df_dessert.apply(rating, axis=1)
df_dessert.sort_values(by='rating', inplace=True, ascending=False)
print(df_dessert)
