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
        cur.execute("SELECT name FROM restaurants WHERE id = %s", (store,))
        store_name = cur.fetchone()[0]
        bread_str = r"Bread.*Basket"
        try:
            cur.execute(
                "SELECT location, recipe_cost FROM recipe_cost WHERE id = %s AND menu_item ~* %s",
                (store, bread_str),
            )
            matching_rows = pd.DataFrame(cur.fetchall(), columns=["location", "cost"])
            if not matching_rows.empty:
                bb_cost = matching_rows["cost"].iloc[0]
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
            new_row = {
                "location": store_name,
                "store_id": store,
                "concept": "Steakhouse",
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

    print(menu_engineering.info())

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
    # year: int = input("Enter year: ")
    period: int = input("Enter period: ")
    week: int = input("Enter week: ")
    year = 2024
    # period = 8
    # week = 4

    print(f"Year: {year}, Period: {period}, Week: {week}")

    product_mix = "./downloads/Product Mix.csv"
    menu_price_analysis = "./downloads/Menu Price Analysis.csv"
    main(product_mix, menu_price_analysis, year, period, week, engine, conn, cur)
