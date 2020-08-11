import csv
import os
import pandas as pd
import numpy as np

df_product = pd.DataFrame()
df_cost = pd.DataFrame()
df_MenuEng = pd.DataFrame()


def removedups(x):
    # Turn the list into a dict then back to a list to remove duplicates
    return list(dict.fromkeys(x))


def engineer(df):
    # Assigns bool if less than mean for Quantity and Margin
    qtm = df['Qty'].mean()
    df['qty_mn'] = np.where(df.Qty < qtm, False, True)
    mrgn = df['Margin'].mean()
    df['mrg_mn'] = np.where(df.Margin < mrgn, False, True)
    return df


def rating(df):
    # Assigns rating to each menu item
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


def menucatagory(catg):
    # Create a separate dataframe for each menu category
    df = df_MenuEng.drop(df_MenuEng[df_MenuEng.Cat2 != catg].index)
    return df


os.system('clear')
print()
print('### Download "PRODUCT MIX.CSV" and "MENU PRICE ANALYSIS.CSV" files before you continue ###')
print()
input('Press "Enter" when you are ready to continue')

# Imports and cleans data into dataframe
df_product = pd.read_csv('Product Mix.csv', skiprows=3, sep=',', thousands=',')
df_product[['Location', 'MenuItem']
           ] = df_product['TransferDate'].str.split('- ', expand=True)
df_product.rename(columns={'Cost': 'Price', 'Total': 'Sales'}, inplace=True)
df_product.drop(columns={'Textbox3', 'Textbox27', 'TransferDate',
                         'ToLocationName', 'dm_Quantity', 'Textbox17', 'Textbox20'}, inplace=True)
df_pmix = df_product.reindex(
    columns=['Location', 'MenuItem', 'Qty', 'Price', 'Sales', 'Cat1', 'Cat2', 'Cat3'])
df_product = df_pmix

# Menu Price Analysis used for food cost info.
df_cost = pd.read_csv('Menu Price Analysis.csv',
                      skiprows=3, sep=',', thousands=',')
df_cost[['Location', 'MenuItem']
        ] = df_cost['MenuItemName'].str.split('- ', expand=True)
df_cost.drop(columns={'MenuItemName', 'Cost1', 'Profit1', 'Textbox43', 'PriceNeeded1', 'AvgPrice1', 'Textbox35',
                      'TargetMargin1', 'Profit', 'ProfitPercent', 'TargetMargin', 'Variance', 'PriceNeeded'}, inplace=True)
df_pmix = df_cost.reindex(columns=['Location', 'MenuItem', 'Cost', 'AvgPrice'])
df_cost = df_pmix

# Combine the two imports into one dataframe and clean the data.
df_MenuEng = pd.merge(df_product, df_cost, on='MenuItem',
                      how='left', sort=False)
df_MenuEng.rename(columns={'Location_x': 'Location'}, inplace=True)
df_MenuEng.drop(columns={'Location_y', 'AvgPrice'}, inplace=True)
df_pmix = df_MenuEng.reindex(columns=[
    'Location', 'MenuItem', 'Qty', 'Price', 'Sales', 'Cost', 'Cat1', 'Cat2', 'Cat3'])
df_MenuEng = df_pmix.drop(df_pmix[df_pmix.Price == 0].index)

# Get list of categories from data
cat1_list = df_MenuEng['Cat1']
cat1_list = removedups(cat1_list)
cat2_list = df_MenuEng['Cat2']
cat2_list = removedups(cat2_list)

df_MenuEng['FoodCost'] = df_MenuEng.apply(
    lambda row: row.Cost/row.Price, axis=1)
df_MenuEng['Margin'] = df_MenuEng.apply(
    lambda row: row.Price - row.Cost, axis=1)
df_pmix = df_MenuEng.reindex(columns=['Location', 'MenuItem', 'Qty', 'Price',
                                      'FoodCost', 'Sales', 'Cost', 'Margin', 'Cat1', 'Cat2', 'Cat3'])
df_MenuEng = df_pmix

for loc in cat1_list:
    with pd.ExcelWriter(f'MenuEngineering-{loc}.xlsx') as writer:  # pylint: disable=abstract-class-instantiated
        for cat in cat2_list:
            df = menucatagory(cat)
            sort_list = ['Star', 'Opportunity', 'Puzzle', 'Dog']
            df = engineer(df)
            df['rating'] = df.apply(rating, axis=1)
            df.sort_values(by='Sales', inplace=True,
                           ascending=False, ignore_index=True)
            location = df.loc[[0], 'Location']
            df.drop(columns={'Cat3', 'qty_mn', 'mrg_mn'}, inplace=True)
            print(f'{cat} Menu Engineering for {location}')
            print(df)
            df.to_excel(writer, sheet_name=cat, index=False)
