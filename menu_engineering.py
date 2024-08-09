"""
Import sales mix and export menu engineering report to excel
"""

import numpy as np
import pandas as pd
import psycopg2
from config import Config
from psycopg2.errors import UniqueViolation, IntegrityError
from psycopg2 import sql
from sqlalchemy import create_engine


def removedups(x):
    """Turn the list into a dict then back to a list to remove duplicates"""
    return list(dict.fromkeys(x))


def engineer(df):
    """Assigns bool if less than mean for Quantity and Margin"""
    qtm = df["quantity"].mean()
    df["qty_mn"] = np.where(df.quantity < qtm, False, True)
    mrgn = df["margin"].mean()
    df["mrg_mn"] = np.where(df.margin < mrgn, False, True)
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
    if df.empty:
        print(f"{catg} is empty")
    return df


def removeSpecial(df):
    """Removes specialty items from the dataframes"""
    with open("./specialty.txt") as file:
        specialty_patterns = file.read().split("\n")

    for pattern in specialty_patterns:
        df = df.drop(df[df.MenuItem == pattern].index)

    # with open("./regex_list.txt") as file:
    #     regex_patterns = file.read().split("\n")

    # Print the regex patterns and the number of rows in df
    #    print("Regex patterns:", regex_patterns)
    #    print("Number of rows in df:", len(df))
    #    pause = input("Press enter to continue")

    #    for pattern in regex_patterns:
    #        print("current pattern:", pattern)
    #        df = df.drop(df[df.MenuItem.str.contains(f'{pattern}', na=False, regex=True)].index)
    #        print("Number of matched rows:", len(df[df.MenuItem.str.contains(f'{pattern}', na=False, regex=True)]))

    df = df.drop(df[df.MenuItem.str.contains(r"^No ", na=False, regex=True)].index)
    df = df.drop(df[df.MenuItem.str.contains(r" Only$", na=False, regex=True)].index)
    df = df.drop(df[df.MenuItem.str.contains(r"^& ", na=False, regex=True)].index)
    df = df.drop(df[df.MenuItem.str.contains(r"^Seat ", na=False, regex=True)].index)
    df = df.drop(df[df.MenuItem.str.contains(r"Allergy$", na=False, regex=True)].index)
    df = df.drop(
        df[df.MenuItem.str.contains(r"for Salad.*", na=False, regex=True)].index
    )
    df = df.drop(
        df[df.MenuItem.str.contains(r".*for Steak.*", na=False, regex=True)].index
    )
    df = df.drop(
        df[df.MenuItem.str.contains(r".*for Sand.*", na=False, regex=True)].index
    )
    df = df.drop(
        df[df.MenuItem.str.contains(r".*for Taco.*", na=False, regex=True)].index
    )
    df = df.drop(
        df[df.MenuItem.str.contains(r".*for Cali-Club.*", na=False, regex=True)].index
    )
    df = df.drop(
        df[df.MenuItem.str.contains(r".*for Edge.*", na=False, regex=True)].index
    )
    df = df.drop(
        df[df.MenuItem.str.contains(r".*See Server.*", na=False, regex=True)].index
    )
    df = df.drop(
        df[df.MenuItem.str.contains(r".*Refund.*", na=False, regex=True)].index
    )
    df = df.drop(
        df[df.MenuItem.str.contains(r".*2 Pens.*", na=False, regex=True)].index
    )
    df = df.drop(
        df[df.MenuItem.str.contains(r".*Anniversary.*", na=False, regex=True)].index
    )
    df = df.drop(
        df[df.MenuItem.str.contains(r".*Birthday.*", na=False, regex=True)].index
    )
    df = df.drop(df[df.MenuItem.str.contains(r".*Rare.*", na=False, regex=True)].index)
    df = df.drop(
        df[df.MenuItem.str.contains(r".*Medium.*", na=False, regex=True)].index
    )
    df = df.drop(df[df.MenuItem.str.contains(r".*Well.*", na=False, regex=True)].index)

    return df


# used for adding bread basket to menu engineering
def add_new_row(location, menu_item, cost, df):
    new_row = pd.DataFrame(
        {"Location": location, "MenuItem": menu_item, "Cost": cost},
        index=[0],
    )
    return pd.concat([df, new_row], ignore_index=True)


def calculate_bread_basket(df):
    stores_w_bread = (4, 9, 11, 15, 16, 17)
    df_bread = df[(df["store_id"].isin(stores_w_bread)) & (df["category2"] == "Entree")]
    for store in stores_w_bread:
        bread_str = "Bread Basket"
        try:
            # TODO this is always empty
            matching_rows = df_bread.loc[
                (df_bread["store_id"] == store)
                & (df_bread["menu_item"].str.contains(bread_str, regex=True)),
                "menu_cost",
            ]
            if not matching_rows.empty:
                bb_cost = matching_rows.iloc[0]
            elif store == 4:
                bb_cost = 0.19
            elif store == 9:
                bb_cost = 0.19
            elif store == 11:
                bb_cost = 0.84
            elif store == 15:
                bb_cost = 0.96
            elif store == 16:
                bb_cost = 0.69
            elif store == 17:
                bb_cost = 0.84

            entree_count = df_bread.loc[df_bread["store_id"] == store, "quantity"].sum()
            print(f"Entree count for {store}: {entree_count}")
            new_row = {
                "store_id": store,
                "menu_item": "Bread Basket per Entree",
                "quantity": entree_count,
                "menu_price": 0,
                "menu_cost": bb_cost,
                "sales": 0,
                "category1": "Food",
                "category2": "No Charge",
                "category3": "None",
            }
            df = pd.concat([df, pd.DataFrame(new_row, index=[0])], ignore_index=True)
        except Exception as e:
            print(e)
            pass

    return df

# def format_excel(file_path):
#     wb = openpyxl.load_workbook(file_path)

#     for sheet_name in wb.sheetnames:
#         sheet = wb[sheet_name]

#         if "currency" not in wb.named_styles:
#             currency_style = NamedStyle(name="currency", number_format="#,##0.00")
#             for col in ["C", "D", "E", "F", "G", "H", "I"]:
#                 for cell in sheet[col]:
#                     cell.style = currency_style

#             for cell in sheet["F"]:
#                 cell.number_format = "0.0%"

#             for col in sheet.columns:
#                 max_length = 0
#                 column = col[0].column_letter
#                 for cell in col:
#                     try:
#                         if len(str(cell.value)) > max_length:
#                             max_length = len(cell.value)
#                     except Exception as e:
#                         print(repr(e))
#                         pass
#                 adjusted_width = (max_length + 2) * 1.2
#                 sheet.column_dimensions[column].width = adjusted_width

#     wb.save(file_path)


def update_location_names(df, engine, conn, cur):
    # import locationid and name from location table
    cur.execute("SELECT locationid, name FROM location")
    location = cur.fetchall()
    location = pd.DataFrame(location, columns=["locationid", "name"])
    location.rename(columns={"name": "location"}, inplace=True)
    df = pd.merge(df, location, on="location", how="left", sort=False)

    cur.execute("SELECT locationid, name, id FROM restaurants")
    restaurants = cur.fetchall()
    restaurants = pd.DataFrame(restaurants, columns=["locationid", "name", "id"])
    restaurants.dropna(inplace=True)
    restaurants.rename(columns={"name": "location", "id": "store_id"}, inplace=True)
    df = pd.merge(df, restaurants, on="locationid", how="left", sort=False)

    df.drop(columns=["locationid", "location_x"], inplace=True)
    df.rename(columns={"location_y": "location"}, inplace=True)
    df[["concept", "menu_item"]] = df["menu_item"].str.split(" - ", n=1, expand=True)
    df = df.reindex(
        columns=[
            "location",
            "store_id",
            "concept",
            "menu_item",
            "quantity",
            "menu_price",
            "sales",
            "category1",
            "category2",
            "category3",
            "menu_cost",
        ]
    )

    return df


def merge_dataframes(df1, df2):
    df = pd.merge(df1, df2, on=["location", "menu_item"], how="left", sort=False)
    return df


def main(product_mix_csv, menu_analysis_csv, year, period, week, engine, conn, cur):
    product_mix = pd.read_csv(
        product_mix_csv,
        skiprows=3,
        sep=",",
        thousands=",",
        usecols=[
            "TransferDate",
            "Textbox27",
            "Qty",
            "Cost",
            "Total",
            "Cat1",
            "Cat2",
            "Cat3",
        ],
    )
    product_mix.rename(
        columns={
            "TransferDate": "menu_item",
            "Textbox27": "location",
            "Qty": "quantity",
            "Cost": "menu_price",
            "Total": "sales",
            "Cat1": "category1",
            "Cat2": "category2",
            "Cat3": "category3",
        },
        inplace=True,
    )
    product_mix.sort_values(by=["menu_item"], inplace=True)
    product_mix["category1"] = product_mix["category1"].fillna("None")
    product_mix["category2"] = product_mix["category2"].fillna("None")
    product_mix["category3"] = product_mix["category3"].fillna("None")

    menu_analysis = pd.read_csv(
        menu_analysis_csv,
        skiprows=3,
        sep=",",
        thousands=",",
        usecols=["Location", "MenuItemName", "UnitCost_Loc"],
    )
    menu_analysis["Location"] = menu_analysis["Location"].str.strip()
    menu_analysis.rename(
        columns={
            "Location": "location",
            "MenuItemName": "menu_item",
            "UnitCost_Loc": "menu_cost",
        },
        inplace=True,
    )
    menu_analysis["menu_cost"] = menu_analysis["menu_cost"].fillna(0)
    df_merge = merge_dataframes(product_mix, menu_analysis)
    menu_engineering = update_location_names(df_merge, engine, conn, cur)
    menu_engineering = calculate_bread_basket(menu_engineering)
    print(menu_engineering)

    # Calculate Bread Basket usage for stores with bread
    # TODO change to store_id
    # stores_w_bread = [
    #     "NEW YORK PRIME-MYRTLE BEACH",
    #     "NEW YORK PRIME-BOCA",
    #     "NEW YORK PRIME-ATLANTA",
    #     "CHOPHOUSE-NOLA",
    #     "CHOPHOUSE '47",
    #     "GULFSTREAM CAFE",
    # ]
    # entree_count = menu_engineering.loc[
    #     menu_engineering["category2"] == "Entree", "quantity"
    # ].sum()
    # print(f"Entree count: {entree_count}")
    # if menu_engineering['location'] in stores_w_bread:
    # # add bread basket to df_menu
    # new_row = {
    #     "menu_item": "Bread Basket per Entree",
    #     "quantity": entree_count,
    #     "menu_price": 0,
    #     "sales": 0,
    #     "category1": "Food",
    #     "category2": "No Charge",
    #     "category3": "None",
    # }
    # menu_engineering = pd.concat(
    #     [menu_engineering, pd.DataFrame(new_row, index=[0])], ignore_index=True
    # )

    # # Define a dictionary to map location names to their respective data.
    # location_data = {
    #     "CHOPHOUSE-NOLA": ("Bread Basket per Entree", 0.35),
    #     "CHOPHOUSE '47": ("Bread Basket per Entree", 0.35),
    #     "GULFSTREAM CAFE": ("Bread Basket per Entree", 0.92),
    #     "NEW YORK PRIME-MYRTLE BEACH": ("Bread Basket per Entree", 0.79),
    #     "NEW YORK PRIME-BOCA": ("Bread Basket per Entree", 0.85),
    #     "NEW YORK PRIME-ATLANTA": ("Bread Basket per Entree", 0.83),
    # }

    # # Check if the location exists in the dictionary, then add the new row.
    # if location in location_data:
    #     menu_item, cost = location_data[location]
    #     df_pmix = add_new_row(location, menu_item, cost, df_pmix)
    # price_dict[key] = df_pmix

    # directory = "/home/wandored/Projects/menu-engineering/output/"
    #     df_menu = removeSpecial(df_pmix)

    #     cat2_list = df_menu["Cat2"]
    #     cat2_list = removedups(cat2_list)
    #     # if "nan" in cat2_list replace it with "None"
    #     cat2_list = [x if str(x) != "nan" else "None" for x in cat2_list]
    menu_engineering["period"] = period
    menu_engineering["year"] = year
    menu_engineering["week"] = week
    menu_engineering["menu_cost"] = menu_engineering["menu_cost"].fillna(0)
    menu_engineering["cost_pct"] = menu_engineering.apply(
        lambda row: row.menu_cost / row.menu_price if row.menu_price else 0, axis=1
    )
    menu_engineering["margin"] = menu_engineering.apply(
        lambda row: row.menu_price - row.menu_cost, axis=1
    )
    menu_engineering["total_cost"] = menu_engineering.apply(
        lambda row: row.quantity * row.menu_cost, axis=1
    )
    menu_engineering["profit"] = menu_engineering.apply(
        lambda row: row.quantity * row.margin, axis=1
    )
    menu_engineering = menu_engineering.reindex(
        columns=[
            "location",
            "store_id",
            "year",
            "period",
            "week",
            "concept",
            "menu_item",
            "quantity",
            "menu_price",
            "menu_cost",
            "margin",
            "cost_pct",
            "sales",
            "total_cost",
            "profit",
            "category1",
            "category2",
            "category3",
        ]
    )
    # menu_engineering = engineer(menu_engineering)
    # menu_engineering["rating"] = menu_engineering.apply(rating, axis=1)

    return

    table_name = "menu_engineering"
    temp_table_name = f"temp_{table_name}"
    try:
        menu_engineering.to_sql(
            temp_table_name,
            engine,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=1000,
        )
        update_query = sql.SQL(
            """
                INSERT INTO {table} (location, store_id, year, period, week, concept, menu_item, quantity, menu_price, menu_cost, margin, cost_pct, sales, total_cost, profit, category1, category2, category3)
                SELECT t.location, t.store_id::integer, t.year::integer, t.period::integer, t.week::integer, t.concept, t.menu_item, t.quantity, t.menu_price, t.menu_cost, t.margin, t.cost_pct, t.sales, t.total_cost, t.profit, t.category1, t.category2, t.category3
                FROM {temp_table} AS t
                ON CONFLICT (location, store_id, year, period, week, concept, menu_item) DO UPDATE
                SET quantity = EXCLUDED.quantity,
                menu_price = EXCLUDED.menu_price,
                menu_cost = EXCLUDED.menu_cost,
                margin = EXCLUDED.margin,
                cost_pct = EXCLUDED.cost_pct,
                sales = EXCLUDED.sales,
                total_cost = EXCLUDED.total_cost,
                profit = EXCLUDED.profit,
                category1 = EXCLUDED.category1,
                category2 = EXCLUDED.category2,
                category3 = EXCLUDED.category3
                """
        ).format(
            table=sql.Identifier(table_name),
            temp_table=sql.Identifier(temp_table_name),
        )
        cur.execute(update_query)
        conn.commit()
    except (IntegrityError, UniqueViolation) as e:
        print(e)
        return 1
    except Exception as e:
        print(e)
        return 1
    finally:
        try:
            cur.execute(f"DROP TABLE IF EXISTS {temp_table_name}")
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
    return 0

    # menu_engineering = df_pmix
    # # select all rows where cat2 is nan
    # df_none = menu_engineering[menu_engineering["Cat2"].isnull()]
    # # Fill NaN values in menu["cat2"] with "None"
    # menu_engineering["Cat2"] = menu_engineering["Cat2"].fillna("None")
    # # columns_to_fill_none = ["Cat1", "Cat2", "Cat3"]
    # # df_none.loc[:, columns_to_fill_none] = (
    # #     df_none.loc[:, columns_to_fill_none].fillna("None").astype(str)
    # # )
    # # # # Fill NaN values in all other columns with 0
    # # df_none = df_none.fillna(0)

    # if not df_none.empty:
    #     df_nonetab = pd.concat([df_nonetab, df_none])

    # # drop nan from cat2_list
    # # cat2_list = [x for x in cat2_list if str(x) != "nan"]

    # with pd.ExcelWriter(f"{directory}/{store}.xlsx") as writer:  # pylint: disable=abstract-class-instantiated
    #     for cat in cat2_list:
    #         df = menucatagory(cat, menu_engineering)
    #         df = engineer(df)
    #         df["rating"] = df.apply(rating, axis=1)
    #         df.sort_values(
    #             by=["Profit", "Qty"],
    #             inplace=True,
    #             ascending=False,
    #             ignore_index=True,
    #         )
    #         df.drop(columns={"Location", "Cat3", "qty_mn", "mrg_mn"}, inplace=True)
    #         df.loc["Total"] = pd.Series(
    #             df[["Qty", "Sales", "Total Cost", "Profit"]].sum()
    #         )
    #         if df.at["Total", "Sales"]:
    #             df.at["Total", "Cost %"] = (
    #                 df.at["Total", "Total Cost"] / df.at["Total", "Sales"]
    #             )
    #         else:
    #             df.at["Total", "Cost %"] = 1
    #         df.to_excel(writer, sheet_name=cat, index=False)

    # Format excel files
    # excel_files = [file for file in os.listdir(directory) if file.endswith(".xlsx")]
    # for file in excel_files:
    #     file_path = os.path.join(directory, file)
    #     format_excel(file_path)

    # if df_nonetab.empty:
    #     print("No items to add")
    # df_nonetab = df_nonetab.groupby(["MenuItem"]).sum(numeric_only=True)
    # df_nonetab.sort_values(by=sort_unit, inplace=True, ascending=False)
    # print(df_nonetab.head(25))
    # print()
    # print("--------------------------------------------------------------------")
    # print(df_nonetab.info())
    # print(df_nonetab.describe())

    return


if __name__ == "__main__":
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    conn = psycopg2.connect(
        host=Config.HOST_SERVER,
        database=Config.PSYCOPG2_DATABASE,
        user=Config.PSYCOPG2_USER,
        password=Config.PSYCOPG2_PASS,
    )
    cur = conn.cursor()

    # user input year, period and week
    year: int = input("Enter year: ")
    period: int = input("Enter period: ")
    week: int = input("Enter week: ")
    # year = 2024
    # period = 8
    # week = 4

    print(f"Year: {year}, Period: {period}, Week: {week}")

    product_mix = "./downloads/Product Mix.csv"
    menu_price_analysis = "./downloads/Menu Price Analysis.csv"
    main(product_mix, menu_price_analysis, year, period, week, engine, conn, cur)

    # os.system(
    #     "cp /home/wandored/Projects/menu-engineering/output/*.xlsx /home/wandored/Dropbox/Restaurant365/Report_Data"
    # )
