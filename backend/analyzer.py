import pandas as pd

def analyze_expenses(file):
    df = pd.read_csv(file)

    total_spent = int(df["Amount"].sum())
    transaction_count=len(df)
    days_tracked=df["Date"].nunique()
    avg_per_day=total_spent/days_tracked
    category_spending=df.groupby("Category")["Amount"].sum().to_dict()
    category_percentage = {
    category: round((amount / total_spent) * 100, 2)
    for category, amount in category_spending.items()}
    daily_spending = df.groupby("Date")["Amount"].sum().to_dict()
    highest_spending_day = max(daily_spending, key=daily_spending.get)
    highest_spending_amount = daily_spending[highest_spending_day]
    highest_spending_category = max(category_spending,key=category_spending.get)
    highest_category_amount = category_spending[highest_spending_category]
    insight = f"Over the past {days_tracked} days, you spent ₹{highest_category_amount} on {highest_spending_category}, which was {category_percentage[highest_spending_category]}% of your total spending."
    return {
        "total_spent": total_spent,
        "transaction_count": transaction_count,
        "days_tracked":days_tracked,
        "avg_per_day":avg_per_day,
        "category_spending":category_spending,
        "category_percentage": category_percentage,
        "daily_spending":daily_spending,
        f"total_spending_summary":f"₹{total_spent} over {days_tracked} days across {transaction_count} transactions",
        "highest_spending_day": highest_spending_day,
        "highest_spending_amount": highest_spending_amount,
        "highest_spending_category":highest_spending_category,
        "insight":insight
    }