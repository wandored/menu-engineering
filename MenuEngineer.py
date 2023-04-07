"""
Import sales mix and export menu engineering report to excel
"""

import csv
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import numpy as np


def upload_product_mix():
    #    root = tk.Tk()
    #    root.title("Product Mix file")
    #    root.withdraw()
    #
    #    # Set the window attributes to disable resizing and to keep the window on top of others
    #    root.resizable(False, False)
    #    root.wm_attributes("-topmost", True)
    #
    #    # Get the dimensions of the monitor that the window is on
    #    monitor_width = root.winfo_screenwidth()
    #    monitor_height = root.winfo_screenheight()
    #
    #    # Calculate the position of the window's top-left corner to be in the center of the monitor
    #    window_width = 300  # Set this to be the width of your window
    #    window_height = 200  # Set this to be the height of your window
    #    x = int((monitor_width - window_width) / 2)
    #    y = int((monitor_height - window_height) / 2)
    #    root.geometry("{}x{}+{}+{}".format(window_width, window_height, x, y))
    #
    #    file_path = filedialog.askopenfilename()
    file_path = "./downloads/Product Mix.csv"
    return file_path


def upload_menu_price_analysis():
    #    root = tk.Tk()
    #    root.title("Menu Price Analysis file")
    #    root.withdraw()
    #
    #    # Get the dimensions of the monitor that the window is on
    #    monitor_width = root.winfo_screenwidth()
    #    monitor_height = root.winfo_screenheight()
    #
    #    # Calculate the position of the window's top-left corner to be in the center of the monitor
    #    window_width = 300  # Set this to be the width of your window
    #    window_height = 200  # Set this to be the height of your window
    #    x = int((monitor_width - window_width) / 2)
    #    y = int((monitor_height - window_height) / 2)
    #    root.geometry("{}x{}+{}+{}".format(window_width, window_height, x, y))
    #
    #    # Set the window attributes to disable resizing and to keep the window on top of others
    #    root.resizable(False, False)
    #    root.wm_attributes("-topmost", True)
    #
    #    file_path = filedialog.askopenfilename()
    file_path = "./downloads/Menu Price Analysis.csv"
    return file_path


def sort_by_profit_or_qty():
    root = tk.Tk()
    root.title("Sort by Profit or Quantity")
    root.withdraw()

    # Ask user to select "Profit" or "Quantity" in tkinter select window
    sort_by = tk.simpledialog.askstring("Sort by Profit or Quantity", "Sort by Profit or Quantity", parent=root)

    return sort_by


def removedups(x):
    """Turn the list into a dict then back to a list to remove duplicates"""
    return list(dict.fromkeys(x))


def engineer(df):
    """Assigns bool if less than mean for Quantity and Margin"""
    qtm = df["Qty"].mean()
    df["qty_mn"] = np.where(df.Qty < qtm, False, True)
    mrgn = df["Margin"].mean()
    df["mrg_mn"] = np.where(df.Margin < mrgn, False, True)
    return df


def rating(df):
    """Assigns rating to each menu item"""
    if df["qty_mn"] is True:
        if df["mrg_mn"] is True:
            return "Star"
        else:
            return "Opportunity"
    if df["qty_mn"] is False:
        if df["mrg_mn"] is True:
            return "Puzzle"
        else:
            return "Dog"


def make_dataframe(catg, product_mix):
    """Separates each store into it's own dataframe"""
    df = product_mix.drop(product_mix[product_mix.Textbox27 != catg].index)
    return df


def make_dataframe1(catg, menu_analysis):
    """Separates each store into it's own dataframe"""
    df = menu_analysis.drop(menu_analysis[menu_analysis.Location != catg].index)
    return df


def menucatagory(catg, df_menu):
    """Create a separate dataframe for each menu category"""
    df = df_menu.drop(df_menu[df_menu.Cat2 != catg].index)
    return df


def removeSpecial(df):
    """Removes specialty items from the dataframes"""
    with open("./specialty.txt") as file:
        specialty_patterns = file.read().split("\n")

    for pattern in specialty_patterns:
        df = df.drop(df[df.MenuItem == pattern].index)

    df = df.drop(df[df.MenuItem.str.contains(r"^No ", na=False, regex=True)].index)
    df = df.drop(df[df.MenuItem.str.contains(r"^Seat ", na=False, regex=True)].index)
    df = df.drop(df[df.MenuItem.str.contains(r"Allergy$", na=False, regex=True)].index)
    df = df.drop(df[df.MenuItem.str.contains(r"for Salad.*", na=False, regex=True)].index)
    df = df.drop(df[df.MenuItem.str.contains(r".*for Steak.*", na=False, regex=True)].index)
    df = df.drop(df[df.MenuItem.str.contains(r".*for Cali-Club.*", na=False, regex=True)].index)
    return df


def main(product_mix_csv, menu_analysis_csv):
    """Main function"""
    sort_unit = sort_by_profit_or_qty()

    product_mix = pd.read_csv(product_mix_csv, skiprows=3, sep=",", thousands=",")
    product_mix.loc[:, "Textbox27"] = product_mix["Textbox27"].str.replace(
        r"CHOPHOUSE\ -\ NOLA", "CHOPHOUSE-NOLA", regex=True
    )
    product_mix.loc[:, "TransferDate"] = product_mix["TransferDate"].str.replace(
        r"CHOPHOUSE\ -\ NOLA", "CHOPHOUSE-NOLA", regex=True
    )
    product_mix.loc[:, "Textbox27"] = product_mix["Textbox27"].str.replace(r"CAFÉ", "CAFE", regex=True)
    product_mix.loc[:, "TransferDate"] = product_mix["TransferDate"].str.replace(r"CAFÉ", "CAFE", regex=True)
    product_mix.loc[:, "Textbox27"] = product_mix["Textbox27"].str.replace(r"^(?:.*?( -)){2}", "-", regex=True)
    product_mix.loc[:, "TransferDate"] = product_mix["TransferDate"].str.replace(r"^(?:.*?( -)){2}", "-", regex=True)

    menu_analysis = pd.read_csv(menu_analysis_csv, skiprows=3, sep=",", thousands=",")
    menu_analysis.loc[:, "Location"] = menu_analysis["Location"].str.replace(
        r"CHOPHOUSE\ -\ NOLA", "CHOPHOUSE-NOLA", regex=True
    )
    menu_analysis.loc[:, "MenuItemName"] = menu_analysis["MenuItemName"].str.replace(
        r"CHOPHOUSE\ -\ NOLA", "CHOPHOUSE-NOLA", regex=True
    )
    menu_analysis.loc[:, "Location"] = menu_analysis["Location"].str.replace(r"CAFÉ", "CAFE", regex=True)
    menu_analysis.loc[:, "MenuItemName"] = menu_analysis["MenuItemName"].str.replace(r"CAFÉ", "CAFE", regex=True)
    menu_analysis.loc[:, "Location"] = menu_analysis["Location"].str.replace(r"^(?:.*?( -)){2}", "-", regex=True)
    menu_analysis.loc[:, "MenuItemName"] = menu_analysis["MenuItemName"].str.replace(
        r"^(?:.*?( -)){2}", "-", regex=True
    )

    menu_analysis["Location"] = menu_analysis["Location"].str.strip()
    df_nonetab = pd.DataFrame()
    store_list = product_mix["Textbox27"]
    store_list = removedups(store_list)

    # Make dictionary of dataframes for each location
    product_dict = {store: make_dataframe(store, product_mix) for store in store_list}
    price_dict = {store: make_dataframe1(store, menu_analysis) for store in store_list}

    for key in product_dict.keys():
        product_dict[key][["x", "MenuItem"]] = product_dict[key]["TransferDate"].str.split(" - ", expand=True)
        # product_dict[key]["Textbox27"].rename("Location", inplace=True)
        product_dict[key].rename(columns={"Cost": "Price", "Total": "Sales"}, inplace=True)
        product_dict[key].drop(
            columns={
                "Textbox3",
                "x",
                "TransferDate",
                "ToLocationName",
                "dm_Quantity",
                "Textbox17",
                "Textbox20",
            },
            inplace=True,
        )
        df_pmix = product_dict[key].reindex(
            columns=[
                "MenuItem",
                "Qty",
                "Price",
                "Sales",
                "Cat1",
                "Cat2",
                "Cat3",
            ]
        )
        # set MenuItem data type to string
        df_pmix["MenuItem"] = df_pmix["MenuItem"].astype(str)
        product_dict[key] = df_pmix

    # Menu Price Analysis used for food cost info.
    for key in price_dict.keys():
        price_dict[key].rename(columns={"Cost1": "Cost"}, inplace=True)
        try:
            price_dict[key][["X", "MenuItem"]] = price_dict[key]["MenuItemName"].str.split(" - ", expand=True)
        except:
            print(f'{price_dict[key]["MenuItemName"]} "key error"')
        df_pmix = price_dict[key].reindex(columns=["Location", "MenuItem", "Cost"])
        df_pmix["MenuItem"] = df_pmix["MenuItem"].astype(str)
        price_dict[key] = df_pmix

    # Combine the two imports into one dataframe and clean the data.
    directory = filedialog.askdirectory()
    print(store_list)
    for store in store_list:
        df_menu = pd.merge(product_dict[store], price_dict[store], on="MenuItem", how="left", sort=False)
        df_menu.rename(columns={"Location_x": "Location"}, inplace=True)
        df_pmix = df_menu.reindex(
            columns=[
                "Location",
                "MenuItem",
                "Qty",
                "Price",
                "Sales",
                "Cost",
                "Cat1",
                "Cat2",
                "Cat3",
            ]
        )
        df_menu = removeSpecial(df_pmix)
        # Get list of categories from data
        #    cat1_list = df_menu['Cat1']
        #    cat1_list = removedups(cat1_list)
        cat2_list = df_menu["Cat2"]
        cat2_list = removedups(cat2_list)
        df_menu["Cost"].fillna(0, inplace=True)
        df_menu["Cost %"] = df_menu.apply(lambda row: row.Cost / row.Price if row.Price else 0, axis=1)
        df_menu["Margin"] = df_menu.apply(lambda row: row.Price - row.Cost, axis=1)
        df_menu["Total Cost"] = df_menu.apply(lambda row: row.Qty * row.Cost, axis=1)
        df_menu["Profit"] = df_menu.apply(lambda row: row.Qty * row.Margin, axis=1)
        df_pmix = df_menu.reindex(
            columns=[
                "Location",
                "MenuItem",
                "Qty",
                "Price",
                "Cost",
                "Margin",
                "Cost %",
                "Sales",
                "Total Cost",
                "Profit",
                "Cat1",
                "Cat2",
                "Cat3",
            ]
        )
        df_menu = df_pmix
        df_none = df_menu.drop(df_menu[df_menu.Cat2 != "None"].index)
        if not df_none.empty:
            df_nonetab = pd.concat([df_nonetab, df_none])

        with pd.ExcelWriter(f"{directory}/{store}.xlsx") as writer:  # pylint: disable=abstract-class-instantiated
            for cat in cat2_list:
                df = menucatagory(cat, df_menu)
                df = engineer(df)
                df["rating"] = df.apply(rating, axis=1)
                df.sort_values(by=["Profit", "Qty"], inplace=True, ascending=False, ignore_index=True)
                df.drop(columns={"Location", "Cat3", "qty_mn", "mrg_mn"}, inplace=True)
                df.loc["Total"] = pd.Series(df[["Qty", "Sales", "Total Cost", "Profit"]].sum())
                if df.at["Total", "Sales"]:
                    df.at["Total", "Cost %"] = df.at["Total", "Total Cost"] / df.at["Total", "Sales"]
                else:
                    df.at["Total", "Cost %"] = 1
                df.to_excel(writer, sheet_name=cat, index=False)

    df_nonetab = df_nonetab.groupby(["MenuItem"]).sum(numeric_only=True)
    df_nonetab.sort_values(by=sort_unit, inplace=True, ascending=False)
    print(df_nonetab.head(25))
    print()
    print("--------------------------------------------------------------------")
    print(df_nonetab.info())
    print(df_nonetab.describe())


if __name__ == "__main__":
    product_mix = upload_product_mix()
    menu_price_analysis = upload_menu_price_analysis()
    main(product_mix, menu_price_analysis)

    os.system("cp /home/wandored/Projects/r365cleaner/output/*.xlsx /home/wandored/Dropbox/Restaurant365/Report_Data")
