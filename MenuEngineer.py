import csv
import os
import pandas as pd
import numpy as np

df_product = pd.DataFrame()
df_cost = pd.DataFrame()
df_MenuEng = pd.DataFrame()
MenuEngineer = {}

#pd.set_option('display.max_rows', 100)


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


def make_dataframe(catg):
    df = df_product.drop(df_product[df_product.Textbox27 != catg].index)
    return df


def make_dataframe1(catg):
    df = df_cost.drop(df_cost[df_cost.Location != catg].index)
    return df


def menucatagory(catg):
    # Create a separate dataframe for each menu category
    df = MenuEng.drop(MenuEng[MenuEng.Cat2 != catg].index)
    return df


os.system('clear')
print()
print('### Download "PRODUCT MIX.CSV" and "MENU PRICE ANALYSIS.CSV" files before you continue ###')
print()
input('Press "Enter" when you are ready to continue')

df_product = pd.read_csv('Product Mix.csv',
                         skiprows=3, sep=',', thousands=',')
df_cost = pd.read_csv('Menu Price Analysis.csv',
                      skiprows=3, sep=',', thousands=',')

store_list = df_product['Textbox27']
store_list = removedups(store_list)
# Make dictionary of dataframes for each location
product_dict = {store: make_dataframe(store) for store in store_list}
price_dict = {store: make_dataframe1(store) for store in store_list}
for key in product_dict.keys():
    product_dict[key][['Location', 'MenuItem']
                      ] = product_dict[key]['TransferDate'].str.split(' - ', expand=True)
    product_dict[key].rename(
        columns={'Cost': 'Price', 'Total': 'Sales'}, inplace=True)
    product_dict[key].drop(columns={'Textbox3', 'Textbox27', 'TransferDate',
                                    'ToLocationName', 'dm_Quantity', 'Textbox17', 'Textbox20'}, inplace=True)
    df_pmix = product_dict[key].reindex(
        columns=['Location', 'MenuItem', 'Qty', 'Price', 'Sales', 'Cat1', 'Cat2', 'Cat3'])
    product_dict[key] = df_pmix
#    print(product_dict[key])

# Menu Price Analysis used for food cost info.
for key in price_dict.keys():
    price_dict[key][['X', 'MenuItem']
                    ] = price_dict[key]['MenuItemName'].str.split(' - ', expand=True)
    price_dict[key].drop(columns={'X', 'MenuItemName', 'Cost1', 'Profit1', 'Textbox43', 'PriceNeeded1', 'AvgPrice1', 'Textbox35',
                                  'TargetMargin1', 'Profit', 'ProfitPercent', 'TargetMargin', 'Variance', 'PriceNeeded'}, inplace=True)
    df_pmix = price_dict[key].reindex(
        columns=['Location', 'MenuItem', 'Cost', 'AvgPrice'])
    price_dict[key] = df_pmix
#    print(price_dict[key])

# Combine the two imports into one dataframe and clean the data.
for store in store_list:
    MenuEng = pd.merge(
        product_dict[store], price_dict[store], on='MenuItem', how='left', sort=False)
    MenuEng.rename(columns={'Location_x': 'Location'}, inplace=True)
    MenuEng.drop(columns={'Location_y', 'AvgPrice'}, inplace=True)
    df_pmix = MenuEng.reindex(columns=[
                              'Location', 'MenuItem', 'Qty', 'Price', 'Sales', 'Cost', 'Cat1', 'Cat2', 'Cat3'])
    MenuEng = df_pmix.drop(df_pmix[df_pmix.Price == 0].index)

# Get list of categories from data
    cat1_list = MenuEng['Cat1']
    cat1_list = removedups(cat1_list)
    cat2_list = MenuEng['Cat2']
    cat2_list = removedups(cat2_list)
    MenuEng['FoodCost'] = MenuEng.apply(lambda row: row.Cost/row.Price, axis=1)
    MenuEng['Margin'] = MenuEng.apply(
        lambda row: row.Price - row.Cost, axis=1)
    df_pmix = MenuEng.reindex(columns=['Location', 'MenuItem', 'Qty', 'Price',
                                       'FoodCost', 'Sales', 'Cost', 'Margin', 'Cat1', 'Cat2', 'Cat3'])
    MenuEng = df_pmix

    for loc in cat1_list:
        with pd.ExcelWriter(f'./output/MenuEngineering-{store}.xlsx') as writer:    # pylint: disable=abstract-class-instantiated
            for cat in cat2_list:
                df = menucatagory(cat)
                df = engineer(df)
                df['rating'] = df.apply(rating, axis=1)
                df.sort_values(by='Sales', inplace=True,
                               ascending=False, ignore_index=True)
                location = df.loc[0, 'Location']
                df.drop(columns={'Location', 'Cat3',
                                 'qty_mn', 'mrg_mn'}, inplace=True)
                print()
                print(f'{cat} Menu Engineering for {location}')
                print(df)
                df.to_excel(writer, sheet_name=cat, index=False)

    for loc in cat1_list:
        with open('MenuEngineering.html', 'w', newline='') as writer:
            for cat in cat2_list:
                df = menucatagory(cat)
                df = engineer(df)
                df['rating'] = df.apply(rating, axis=1)
                df.sort_values(by='Sales', inplace=True,
                               ascending=False, ignore_index=True)
                location = df.loc[0, 'Location']
                df.drop(columns={'Location', 'Cat3',
                                 'qty_mn', 'mrg_mn'}, inplace=True)
                html = df.to_html(justify='center')
                writer.write(f'Menu Engineering for {cat}s at {store}')
                writer.write(html)
