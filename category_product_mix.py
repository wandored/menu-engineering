import pandas as pd



def main():
    # Read the csv file
    data = pd.read_csv('./downloads/category_sales_mix.csv', skiprows=3, sep=",", thousands=",", usecols=['Textbox27', 'Qty', 'Cost', 'Total'])
    data["Textbox27"] = (
        data["Textbox27"]
        .str.replace("Casual - ", "")
        .str.replace("Steakhouse - ", "")
    )
    table = data.pivot_table(
        index=["Textbox27"],
        values=["Qty", "Cost", "Total"],
        aggfunc={"Qty": "sum", "Cost": "mean", "Total": "sum"}
    )
    print(table)
    # Write the new file to a csv file
    table.to_csv("./output/category_sales_mix.csv", index=True)

if __name__ == "__main__":
    main()
