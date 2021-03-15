import csv
import os
import sys
import pandas as pd
import numpy as np

# os.system("/home/wandored/Projects/r365cleaner/csvCleaner.sh")
os.system('sed -i "s/CHOPHOUSE\ -\ NOLA/CHOPHOUSE-NOLA/g" Product\ Mix.csv')
os.system('sed -i "s/CHOPHOUSE\ -\ NOLA/CHOPHOUSE-NOLA/g" Menu\ Price\ Analysis.csv')
os.system('sed -i "s/\ -\ /-/g2" Product\ Mix.csv')
os.system('sed -i "s/\ -\ /-/g2" Menu\ Price\ Analysis.csv')
os.system('sed -i "s/CAFÉ/CAFE/g" Product\ Mix.csv')
os.system('sed -i "s/CAFÉ/CAFE/g" Menu\ Price\ Analysis.csv')

with open('Product Mix.csv', newline='') as f:
    reader = csv.reader(f)
    next(reader)
    x = next(reader)
    start_date = [i.split(' - ', 1)[0] for i in x]
    end_date = [i.split(' - ', 1)[1] for i in x]


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
    df = df_menu.drop(df_menu[df_menu.Cat2 != catg].index)
    return df


def removeSpecial(df):
    # Removes specialty items from the dataframes
    file = open('./specialty.txt')
    specialty_list = file.read().split('\n')
    file.close
    for item in specialty_list:
        df = df.drop(df[df.MenuItem == item].index)
    return df


os.system('clear')

df_product = pd.read_csv('Product Mix.csv',
                         skiprows=3, sep=',', thousands=',')
df_cost = pd.read_csv('Menu Price Analysis.csv',
                      skiprows=3, sep=',', thousands=',')
df_nonetab = pd.DataFrame()
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

# Menu Price Analysis used for food cost info.
for key in price_dict.keys():
    price_dict[key][['X', 'MenuItem']
                    ] = price_dict[key]['MenuItemName'].str.split(' - ', expand=True)
    price_dict[key].drop(columns={'X', 'MenuItemName', 'Cost1', 'Profit1', 'Textbox43', 'PriceNeeded1', 'AvgPrice1', 'Textbox35',
                                  'TargetMargin1', 'Profit', 'ProfitPercent', 'TargetMargin', 'Variance', 'PriceNeeded'}, inplace=True)
    df_pmix = price_dict[key].reindex(
        columns=['Location', 'MenuItem', 'Cost', 'AvgPrice'])
    price_dict[key] = df_pmix

# Combine the two imports into one dataframe and clean the data.
for store in store_list:
    df_menu = pd.merge(
        product_dict[store], price_dict[store], on='MenuItem', how='left', sort=False)
    df_menu.rename(columns={'Location_x': 'Location'}, inplace=True)
    df_menu.drop(columns={'Location_y', 'AvgPrice'}, inplace=True)
    df_pmix = df_menu.reindex(columns=[
                              'Location', 'MenuItem', 'Qty', 'Price', 'Sales', 'Cost', 'Cat1', 'Cat2', 'Cat3'])
    df_menu = removeSpecial(df_pmix)
# Get list of categories from data
#    cat1_list = df_menu['Cat1']
#    cat1_list = removedups(cat1_list)
    cat2_list = df_menu['Cat2']
    cat2_list = removedups(cat2_list)
    df_menu['Cost'].fillna(0, inplace=True)
    df_menu['Cost %'] = df_menu.apply(
        lambda row: row.Cost/row.Price if row.Price else 0, axis=1)
    df_menu['Margin'] = df_menu.apply(
        lambda row: row.Price - row.Cost, axis=1)
    df_menu['Total Cost'] = df_menu.apply(
        lambda row: row.Qty * row.Cost, axis=1)
    df_menu['Profit'] = df_menu.apply(lambda row: row.Qty * row.Margin, axis=1)
    df_pmix = df_menu.reindex(columns=['Location', 'MenuItem', 'Qty', 'Price', 'Cost', 'Margin',
                                       'Cost %', 'Sales', 'Total Cost', 'Profit', 'Cat1', 'Cat2', 'Cat3'])
    df_menu = df_pmix
    df_none = df_menu.drop(df_menu[df_menu.Cat2 != 'None'].index)
    df_nonetab = df_nonetab.append(df_none, ignore_index=True)
    df_nonetab.drop(columns={'Location'}, inplace=True)

    with pd.ExcelWriter(f'./output/{store}.xlsx') as writer:    # pylint: disable=abstract-class-instantiated
        for cat in cat2_list:
            df = menucatagory(cat)
            df = engineer(df)
            df['rating'] = df.apply(rating, axis=1)
            df.sort_values(by='Profit', inplace=True,
                           ascending=False, ignore_index=True)
            df.drop(columns={'Location', 'Cat3',
                             'qty_mn', 'mrg_mn'}, inplace=True)
            df.loc['Total'] = pd.Series(
                df[['Qty', 'Sales', 'Total Cost', 'Profit']].sum())
            if df.at['Total', 'Sales']:
                df.at['Total', 'Cost %'] = df.at['Total',
                                                 'Total Cost']/df.at['Total', 'Sales']
            else:
                df.at['Total', 'Cost %'] = 1
            df.to_excel(writer, sheet_name=cat, index=False)

with pd.ExcelWriter('./output/NoneTab.xlsx') as writer:     # pylint: disable=abstract-class-instantiated
    df_nonetab = df_nonetab.groupby(['MenuItem']).sum()
    df_nonetab.sort_values(by='Qty', inplace=True,
                           ascending=False)
    print(df_nonetab.head(25))
    df_nonetab.to_excel(writer)
    print()
    print("--------------------------------------------------------------------")
    print(df_nonetab.info())
    print(df_nonetab.describe())

os.system("cp /home/wandored/Projects/r365cleaner/output/*.xlsx /home/wandored/Dropbox/Restaurant365/Report_Data")


#   with open(f'./output/{store}.html', 'w', newline='') as writer:
#       for cat in cat2_list:
#           df = menucatagory(cat)
#           df = engineer(df)
#           df['rating'] = df.apply(rating, axis=1)
#           df.sort_values(by='Profit', inplace=True,
#                          ascending=False, ignore_index=True)
#           df.drop(columns={'Location', 'Cat3',
#                            'qty_mn', 'mrg_mn'}, inplace=True)
#           df.loc['Total'] = pd.Series(
#               df[['Qty', 'Sales', 'Total Cost', 'Profit']].sum())
#           if df.at['Total', 'Sales']:
#               df.at['Total', 'Cost %'] = df.at['Total',
#                                              'Total Cost']/df.at['Total', 'Sales']
#           else:
#               df.at['Total', 'Cost %'] = 1
#           html = df.to_html(justify='center')
#           writer.write(f'Menu Engineering for {cat}s at {store}')
#           writer.write(html)
