"""
Import sales mix and export menu engineering report to excel
"""

from datetime import datetime

import numpy as np
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.errors import IntegrityError, UniqueViolation
from sqlalchemy import create_engine

from config import Config


def get_date(product_mix_csv):
    with open(product_mix_csv, "r") as f:
        next(f)
        second_line = next(f)
        date_string = second_line.split(" - ")[1].strip()
        date = datetime.strptime(date_string, "%m/%d/%Y").date()
    return date


def get_period(date, cur):
    cur.execute("SELECT period, year FROM calendar WHERE date = %s", (date,))
    result = cur.fetchone()
    period, year = result[0], result[1]
    return period, year


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


def main(product_mix_csv, menu_analysis_csv, date, year, period, engine, conn, cur):
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

    menu_engineering["date"] = date
    menu_engineering["period"] = period
    menu_engineering["year"] = year
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
            "date",
            "year",
            "period",
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
    # print all rows with null values
    print(menu_engineering[menu_engineering.isnull().any(axis=1)].head(50))
    menu_engineering = menu_engineering.dropna()

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
                INSERT INTO {table} (location, store_id, date, year, period, concept, menu_item, quantity, menu_price, menu_cost, margin, cost_pct, sales, total_cost, profit, category1, category2, category3)
                SELECT t.location, t.store_id::integer, t.date, t.year::integer, t.period::integer, t.concept, t.menu_item, t.quantity, t.menu_price, t.menu_cost, t.margin, t.cost_pct, t.sales, t.total_cost, t.profit, t.category1, t.category2, t.category3
                FROM {temp_table} AS t
                ON CONFLICT (location, store_id, date, Menu_item) DO UPDATE
                SET year = EXCLUDED.year,
                period = EXCLUDED.period,
                concept = EXCLUDED.concept,
                quantity = EXCLUDED.quantity,
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
    # period: int = input("Enter period: ")
    # year = 2024
    # # period = 8
    # week = 4

    # print(f"Year: {year}, Period: {period}")

    product_mix = "./downloads/Product Mix.csv"
    menu_price_analysis = "./downloads/Menu Price Analysis.csv"
    date = get_date(product_mix)
    period, year = get_period(date, cur)
    print(f"Date: {date}, Period: {period}, Year: {year}")
    main(product_mix, menu_price_analysis, date, year, period, engine, conn, cur)
