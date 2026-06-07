import pandas as pd

FILE_NAME = "expense_data.csv"


def add_expense():

    date = input("Enter Date (YYYY-MM-DD): ")
    category = input("Enter Category: ")
    amount = float(input("Enter Amount: "))
    description = input("Enter Description: ")

    new_data = pd.DataFrame({
        "Date": [date],
        "Category": [category],
        "Amount": [amount],
        "Description": [description]
    })

    new_data.to_csv(
        FILE_NAME,
        mode="a",
        header=False,
        index=False
    )

    print("Expense Added Successfully!")


def view_expenses():

    df = pd.read_csv(FILE_NAME)

    print("\nAll Expenses:")
    print(df)


def total_expense():

    df = pd.read_csv(FILE_NAME)

    total = df["Amount"].sum()

    print(f"\nTotal Expense: ₹{total}")


def category_summary():

    df = pd.read_csv(FILE_NAME)

    summary = df.groupby(
        "Category"
    )["Amount"].sum()

    print("\nCategory Wise Expense:")
    print(summary)


def ai_recommendation():

    df = pd.read_csv(FILE_NAME)

    category_totals = (
        df.groupby("Category")["Amount"].sum()
    )

    total = category_totals.sum()

    print("\n===== AI EXPENSE ANALYSIS =====")

    for category, amount in category_totals.items():

        percentage = (
            amount / total
        ) * 100

        print(
            f"{category}: ₹{amount:.2f} "
            f"({percentage:.1f}%)"
        )

        if (
            category.lower() == "food"
            and percentage > 40
        ):
            print(
                "AI Suggestion: "
                "Reduce restaurant spending."
            )

        elif (
            category.lower() == "shopping"
            and percentage > 30
        ):
            print(
                "AI Suggestion: "
                "Avoid unnecessary purchases."
            )

        elif (
            category.lower() == "travel"
            and percentage > 25
        ):
            print(
                "AI Suggestion: "
                "Consider economical travel options."
            )

    print(
        "\nAI Recommendation:"
    )

    print(
        "Try saving at least 20% "
        "of your monthly income."
    )


while True:

    print("\n===== EXPENSE TRACKER =====")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Total Expense")
    print("4. Category Summary")
    print("5. AI Recommendation")
    print("6. Exit")

    choice = input("Enter Choice: ")

    if choice == "1":
        add_expense()

    elif choice == "2":
        view_expenses()

    elif choice == "3":
        total_expense()

    elif choice == "4":
        category_summary()

    elif choice == "5":
        ai_recommendation()

    elif choice == "6":
        print("Thank You")
        break

    else:
        print("Invalid Choice")