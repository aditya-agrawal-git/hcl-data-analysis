
import pandas as pd
import re

# Load dataset
df = pd.read_csv("personal_expense_tracker_dirty.csv")

print("Original Dataset Shape:", df.shape)
print("\nMissing Values:\n", df.isnull().sum())

# 1. Remove extra spaces from text columns
text_columns = df.select_dtypes(include="object").columns

for col in text_columns:
    df[col] = df[col].apply(
        lambda x: x.strip() if isinstance(x, str) else x
    )

# 2. Clean date column
df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce",
    dayfirst=True,
    format="mixed"
)

# 3. Clean amount column
def clean_amount(value):
    if pd.isna(value):
        return None

    value = str(value).strip()
    value = value.replace(",", "")
    value = value.replace("₹", "")
    value = value.replace("Rs.", "")
    value = value.replace("rs", "")
    value = value.replace("/-", "")
    value = value.replace(" ", "")

    # Correct common typo: letter O instead of zero
    value = value.replace("O", "0").replace("o", "0")

    try:
        return float(value)
    except ValueError:
        return None

df["Amount"] = df["Amount"].apply(clean_amount)

# 4. Remove invalid amounts
df.loc[df["Amount"] <= 0, "Amount"] = None

# 5. Standardize categories
df["Category"] = df["Category"].str.strip().str.title()

# Replace vague categories
df["Category"] = df["Category"].replace({
    "Misc": "Other"
})

# 6. Standardize payment methods
df["Payment_Method"] = (
    df["Payment_Method"].str.strip().str.title()
)

# 7. Standardize currency
df["Currency"] = "INR"

# 8. Remove duplicate transactions
df = df.drop_duplicates()

# 9. Handle missing values
df["Category"] = df["Category"].fillna("Other")
df["Description"] = df["Description"].fillna("Unknown")
df["Payment_Method"] = df["Payment_Method"].fillna("Unknown")
df["Merchant_or_Location"] = (
    df["Merchant_or_Location"].fillna("Unknown")
)
df["Notes"] = df["Notes"].fillna("")

# Remove rows with invalid dates or missing amounts
df = df.dropna(subset=["Date", "Amount"])

# 10. Format dates
df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

# 11. Save cleaned dataset
df.to_csv("personal_expense_tracker_cleaned.csv", index=False)

# 12. Display results
print("\nCleaning Completed!")
print("Cleaned Dataset Shape:", df.shape)

print("\nRemaining Missing Values:")
print(df.isnull().sum())

print("\nTotal Expenses:", df["Amount"].sum())

print("\nCategory-wise Expenses:")
print(df.groupby("Category")["Amount"].sum().sort_values(ascending=False))

print("\nMonthly Expenses:")
df["Month"] = pd.to_datetime(df["Date"]).dt.to_period("M")
print(df.groupby("Month")["Amount"].sum())

print("\nCleaned file saved successfully!")
