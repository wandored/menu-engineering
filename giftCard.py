""" create report for Gift Card Sales """
import csv
import os
import pandas as pd

# menu_item = input("Enter the product you wish to track: ")
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
df_pmix = df_product.reindex(
    columns=["Location", "MenuItem", "Qty", "Price", "Sales", "Cat1", "Cat2", "Cat3"]
)
df_product = df_pmix

# Menu Price Analysis used for food cost info.
df_cost = pd.read_csv(
    "./downloads/Menu Price Analysis.csv", skiprows=3, sep=",", thousands=","
)
df_cost[["Location", "MenuItem"]] = df_cost["MenuItemName"].str.split(
    " - ", expand=True
)
df_cost.drop(
    columns={
        "MenuItemName",
        "Cost1",
        "Profit1",
        "Textbox43",
        "PriceNeeded1",
        "AvgPrice1",
        "Textbox35",
        "TargetMargin1",
        "Profit",
        "ProfitPercent",
        "TargetMargin",
        "Variance",
        "PriceNeeded",
    },
    inplace=True,
)
df_pmix = df_cost.reindex(columns=["Location", "MenuItem", "Cost", "AvgPrice"])
df_cost = df_pmix

# Combine the two imports into one dataframe and clean the data.
df_MenuEng = pd.merge(df_product, df_cost, on="MenuItem", how="left", sort=False)
df_MenuEng.rename(
    columns={"Location_x": "Location", "Price": "Avg Price"}, inplace=True
)
df_MenuEng.drop(
    columns={"Location_y", "AvgPrice", "Cost", "Cat1", "Cat3"}, inplace=True
)
df_pmix = df_MenuEng.reindex(
    columns=["Location", "MenuItem", "Qty", "Avg Price", "Sales", "Cat2"]
)
df_MenuEng = df_pmix.drop(df_pmix[df_pmix.Cat2 != "Gift Card"].index)
df_MenuEng.drop_duplicates(subset=["Location"], keep="last", inplace=True)

with pd.ExcelWriter("./output/GiftCards.xlsx") as writer:  # pylint: disable=abstract-class-instantiated
    df_MenuEng.sort_values(by="Qty", inplace=True, ascending=False, ignore_index=True)
    df_MenuEng.to_excel(writer, sheet_name="Gift Cards", index=False)

print(df_MenuEng)
