"""
import MenuItem_Export.csv and menu_items_export_r365.csv
compare the "Name" column in both files
drop all items from the MenuItem_Export.csv that are not in the menu_items_export_r365.csv
print the new file to a new csv file
"""

import os

import pandas as pd


def main():
    # read in the two csv files
    menu_item_export = pd.read_csv(
        "./downloads/MenuItem_Export.csv",
        usecols=["Name", "Created Date", "Archived"],
        encoding="ISO-8859-1",
    )
    # drop all rows where the Archived column is Yes
    menu_item_export = menu_item_export[menu_item_export["Archived"] == "No"]
    # drop the Archived column
    menu_item_export = menu_item_export.drop(columns=["Archived"])
    # change the Created Date column to datetime
    menu_item_export["Created Date"] = pd.to_datetime(menu_item_export["Created Date"])
    menu_item_export = menu_item_export.sort_values(
        by=["Created Date"], ascending=[False]
    )

    r365_menu_items = pd.read_csv(
        "./downloads/menu_items_export_r365.csv",
        usecols=["Name", "Category1", "Category2", "Category3"],
        encoding="ISO-8859-1",
    )
    # drop all rows that do not have "Casual" or "Steakhouse" in Name column
    r365_menu_items = r365_menu_items[
        r365_menu_items["Name"].str.contains("Casual|Steakhouse")
    ]

    # remove the prefix from r365_menu_items Name column
    r365_menu_items["Name"] = (
        r365_menu_items["Name"]
        .str.replace("Casual - ", "")
        .str.replace("Steakhouse - ", "")
    )
    # remove rows with any value in Category1, Category2 or Category3 columns from r365_menu_items
    unmapped_menu_items = r365_menu_items[
        r365_menu_items[["Category1", "Category2", "Category3"]].isnull().all(axis=1)
    ]

    # compare the Name columns in both files and drop rows from MenuItem_Export that are in unmapped_menu_items
    new_menu_items = menu_item_export[
        menu_item_export["Name"].isin(unmapped_menu_items["Name"])
    ]

    unordered_menu_items = menu_item_export[
        ~menu_item_export["Name"].isin(unmapped_menu_items["Name"])
    ]
    # sort the new file by Name
    new_menu_items = new_menu_items.sort_values(
        by=["Created Date", "Name"], ascending=[False, True]
    )
    unordered_menu_items = unordered_menu_items.sort_values(
        by=["Created Date", "Name"], ascending=[False, True]
    )
    # remove duplicates from the new file
    new_menu_items = new_menu_items.drop_duplicates("Name")
    new_menu_items = new_menu_items[
        ~new_menu_items["Name"].isin(pd.read_csv("./specialty.txt", header=None)[0])
    ]
    # drop all items that being with "No " or "Seat " from the new file
    new_menu_items = new_menu_items[~new_menu_items["Name"].str.startswith("No ")]
    new_menu_items = new_menu_items[~new_menu_items["Name"].str.startswith("Seat ")]
    new_menu_items = new_menu_items[~new_menu_items["Name"].str.startswith("& ")]
    new_menu_items = new_menu_items[~new_menu_items["Name"].str.startswith("Splash ")]
    new_menu_items = new_menu_items[~new_menu_items["Name"].str.endswith(" Allergy")]
    new_menu_items = new_menu_items[~new_menu_items["Name"].str.endswith("for Salad")]
    new_menu_items = new_menu_items[~new_menu_items["Name"].str.endswith("for Steak")]
    new_menu_items = new_menu_items[~new_menu_items["Name"].str.endswith("for Sand")]
    new_menu_items = new_menu_items[~new_menu_items["Name"].str.endswith("for Taco")]
    new_menu_items = new_menu_items[
        ~new_menu_items["Name"].str.endswith("for Cali-Club")
    ]
    new_menu_items = new_menu_items[~new_menu_items["Name"].str.endswith("for Edge")]

    # write the new file to a csv file
    new_menu_items.to_csv("./output/new_menu_item_export.csv", index=False)
    # clear screen and print the new file
    os.system("cls" if os.name == "nt" else "clear")
    print(new_menu_items.head(30))
    print(new_menu_items.info())

    # drop all rows where the Created Date column is before 2023-03-21
    # open_items = menu_item_export[menu_item_export["Created Date"] > "2023-03-21"]
    # compare the Name columns in both files and drop rows from unmapped_menu_items that are not in MenuItem_Export
    open_items = unmapped_menu_items[
        ~unmapped_menu_items["Name"].isin(new_menu_items["Name"])
    ]
    # sort the open_items file by Name
    open_items = open_items.sort_values(by=["Name"])
    # remove duplicates from the open_items file
    open_items = open_items.drop_duplicates()
    # write the open_items file to a csv file
    open_items.to_csv("./output/open_items.csv", index=False)


if __name__ == "__main__":
    main()
