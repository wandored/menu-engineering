"""
Track sales for a list of items
"""
import csv
import os
import pandas as pd

menu_item = [
    "ADD CRAB CAKE",
    "CRAB CAKE",
    "ADD LOBSTER TAIL",
    "CRAB CAKES",
    "FILET OSCAR",
    "FILET+CRABCAKE",
    "FILET+LOBSTER TAIL",
    "FILETS+CRABCAKE",
    "FILETS+LOBSTER TAIL",
    "DATE NIGHT",
    "ULTIMATE DATE NIGHT",
]

df_product = pd.DataFrame()
df_cost = pd.DataFrame()
df_MenuEng = pd.DataFrame()

os.system('sed -i "s/CHOPHOUSE\ -\ NOLA/CHOPHOUSE-NOLA/g" ./downloads/Product\ Mix.csv')
os.system(
    'sed -i "s/CHOPHOUSE\ -\ NOLA/CHOPHOUSE-NOLA/g" ./downloads/Menu\ Price\ Analysis.csv'
)
os.system('sed -i "s/\ -\ /-/g2" ./downloads/Product\ Mix.csv')
os.system('sed -i "s/\ -\ /-/g2" ./downloads/Menu\ Price\ Analysis.csv')
os.system('sed -i "s/CAFÉ/CAFE/g" ./downloads/Product\ Mix.csv')
os.system('sed -i "s/CAFÉ/CAFE/g" ./downloads/Menu\ Price\ Analysis.csv')


with open("./downloads/Product Mix.csv", newline="") as f:
    reader = csv.reader(f)
    next(reader)
    x = next(reader)
    start_date = [i.split(" - ", 1)[0] for i in x]
    end_date = [i.split(" - ", 1)[1] for i in x]


os.system("clear")
print(f"Start Date {start_date}")
print(f"End Date {end_date}")

# Imports and cleans data into dataframe
df_product = pd.read_csv(
    "./downloads/Product Mix.csv", skiprows=3, sep=",", thousands=","
)
df_product[["Location", "MenuItem"]] = df_product["TransferDate"].str.split(
    " - ", expand=True
)
df_product.rename(columns={"Cost": "Price", "Total": "Sales"}, inplace=True)
df_product.drop(
    columns={
        "Textbox3",
        "Textbox27",
        "TransferDate",
        "ToLocationName",
        "dm_Quantity",
        "Textbox17",
        "Textbox20",
    },
    inplace=True,
)
df_product = df_product.reindex(
    columns=["Location", "MenuItem", "Qty", "Price", "Sales", "Cat1", "Cat2", "Cat3"]
)

# Menu Price Analysis used for food cost info.
# df_cost = pd.read_csv(
#    "./downloads/Menu Price Analysis.csv", skiprows=3, sep=",", thousands=","
# )
# df_cost[["Location", "MenuItem"]] = df_cost["MenuItemName"].str.split(
#    " - ", expand=True
# )
# df_cost.drop(
#    columns={
#        "MenuItemName",
#        "Cost1",
#        "Profit1",
#        "Textbox43",
#        "PriceNeeded1",
#        "AvgPrice1",
#        "Textbox35",
#        "TargetMargin1",
#        "Profit",
#        "ProfitPercent",
#        "TargetMargin",
#        "Variance",
#        "PriceNeeded",
#    },
#    inplace=True,
# )
# df_pmix = df_cost.reindex(columns=["Location", "MenuItem", "Cost", "AvgPrice"])
#
## Combine the two imports into one dataframe and clean the data.
df_product = df_product.drop(df_product[~df_product.MenuItem.isin(menu_item)].index)
# df_pmix = df_pmix.drop(df_pmix[~df_pmix.MenuItem.isin(menu_item)].index)
# df_MenuEng = pd.merge(df_pmix, df_product, on="MenuItem", how="left", sort=False)
# df_MenuEng.rename(columns={"Location_x": "Location"}, inplace=True)
# df_MenuEng.drop(columns={"Location_y", "AvgPrice"}, inplace=True)
# df_pmix = df_MenuEng.reindex(
#    columns=[
#        "Location",
#        "MenuItem",
#        "Qty",
#        "Price",
#        "Sales",
#        "Cost",
#        "Cat1",
#        "Cat2",
#        "Cat3",
#    ]
# )
# df_MenuEng = df_pmix.drop(df_pmix[~df_pmix.MenuItem.isin(menu_item)].index)
# df = df_MenuEng.groupby(["Location", "MenuItem"]).agg({"Qty": "sum", "Sales": "sum"})
# df_MenuEng.drop_duplicates(subset=["Location"], keep="last", inplace=True)

with pd.ExcelWriter("./output/sales_track.xlsx") as writer:  # pylint: disable=abstract-class-instantiated
    df_product.to_excel(writer, index=False)

print(df_product)
