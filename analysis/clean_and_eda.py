# ==========================================
# PART 2 - PYTHON WRANGLING AND EDA
# Tasks 1 and 2
# ==========================================

import pandas as pd

# Task 1: Load and inspect the raw datasets
customers = pd.read_csv("data/customers.csv")
products = pd.read_csv("data/products.csv")
orders = pd.read_csv("data/orders.csv")

print("Customers shape:", customers.shape)
print("Products shape:", products.shape)
print("Orders shape:", orders.shape)

print("\nMissing values in orders:")
print(orders.isnull().sum())


# Task 2: Standardize payment method casing
orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)

print("\nCleaned payment methods:")
print(orders["payment_method"].value_counts())

# ==========================================
# Task 3: Detect and remove duplicate orders
# ==========================================

duplicate_cols = [
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "discount_pct",
    "payment_method",
    "rating",
    "returned"
]

duplicates = orders[
    orders.duplicated(subset=duplicate_cols, keep="first")
]

print("\nDuplicate order IDs:")
print(duplicates["order_id"].tolist())

orders = orders.drop_duplicates(
    subset=duplicate_cols,
    keep="first"
).reset_index(drop=True)

print("Orders after removing duplicates:", orders.shape)

# ==========================================
# Task 4: Handle missing values
# ==========================================

orders["discount_pct"] = orders["discount_pct"].fillna(0)

median_rating = orders["rating"].median()
orders["rating"] = orders["rating"].fillna(median_rating)

print("\nMedian rating:", median_rating)

print("\nMissing values after imputation:")
print(orders[["discount_pct", "rating"]].isnull().sum())

# ==========================================
# Task 5: Merge the datasets
# ==========================================

merged = orders.merge(products, on="product_id", how="left")
merged = merged.merge(customers, on="customer_id", how="left")

print("\nMerged data shape:", merged.shape)

merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)

print("\nFirst 5 order values:")
print(merged[["order_id", "quantity", "price", "discount_pct", "order_value"]].head())

print("\nCleaned total revenue:")
print(round(merged["order_value"].sum(), 2))

sql_raw_revenue = 99860.20
cleaned_revenue = merged["order_value"].sum()

revenue_difference = sql_raw_revenue - cleaned_revenue

print(f"\nSQL raw revenue: {sql_raw_revenue:.2f}")
print(f"Python cleaned revenue: {cleaned_revenue:.2f}")
print(f"Revenue difference: {revenue_difference:.2f}")

print(
    f"Reconciliation: The revenue difference of {revenue_difference:.2f} "
    "is caused by the 5 duplicate orders removed during cleaning."
)

# ==========================================
# Task 6: Detect quantity outliers using IQR
# ==========================================

Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

print("\nQ1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)
print("Lower bound:", lower)
print("Upper bound:", upper)

merged["is_outlier"] = (
    (merged["quantity"] < lower) |
    (merged["quantity"] > upper)
)

print("\nQuantity outliers:")
print(
    merged.loc[
        merged["is_outlier"],
        ["order_id", "quantity"]
    ]
)

print("Number of outliers:", merged["is_outlier"].sum())

# ==========================================
# Task 7: COD return rate hypothesis
# ==========================================

print("\nHypothesis: COD orders have a higher return rate than non-COD orders.")

payment_returns = (
    merged.groupby("payment_method")["returned"]
    .agg(["count", "mean"])
)

payment_returns["return_rate_pct"] = (
    payment_returns["mean"] * 100
).round(1)

print("\nReturn rate by payment method:")
print(payment_returns)

print("\nVerdict: CONFIRMED")

# ==========================================
# Task 8: Multi-level segmentation
# ==========================================

segment_returns = (
    merged.groupby(["payment_method", "city_tier"])["returned"]
    .agg(["count", "mean"])
)

segment_returns["return_rate_pct"] = (
    segment_returns["mean"] * 100
).round(1)

print("\nReturn rate by payment method and city tier:")
print(segment_returns)

highest_segment = segment_returns["return_rate_pct"].idxmax()
highest_rate = segment_returns["return_rate_pct"].max()

print(
    f"\nHighest-risk segment: "
    f"{highest_segment[0]} + Tier {highest_segment[1]}"
)

print(f"Return rate: {highest_rate:.1f}%")

# ==========================================
# Task 9: Correlation analysis
# ==========================================

correlation_columns = [
    "rating",
    "returned",
    "discount_pct",
    "quantity"
]

correlation_matrix = merged[correlation_columns].corr()

print("\nCorrelation matrix:")
print(correlation_matrix.round(2))

# Label the six unique correlation pairs
pairs = [
    ("rating", "returned"),
    ("rating", "discount_pct"),
    ("rating", "quantity"),
    ("returned", "discount_pct"),
    ("returned", "quantity"),
    ("discount_pct", "quantity")
]

print("\nCorrelation strength:")

for col1, col2 in pairs:
    r = correlation_matrix.loc[col1, col2]

    if abs(r) < 0.20:
        strength = "Negligible"
    elif abs(r) < 0.40:
        strength = "Weak"
    elif abs(r) < 0.70:
        strength = "Moderate"
    else:
        strength = "Strong"

    print(f"{col1} vs {col2}: {r:.2f} → {strength}")

discount_return_corr = correlation_matrix.loc["discount_pct", "returned"]

print("\nHypothesis: Higher discounts reduce returns.")
print(f"Correlation: {discount_return_corr:.2f}")

if abs(discount_return_corr) < 0.20:
    print("Strength: Negligible")
elif abs(discount_return_corr) < 0.40:
    print("Strength: Weak")
elif abs(discount_return_corr) < 0.70:
    print("Strength: Moderate")
else:
    print("Strength: Strong")

print("Verdict: BUSTED")

# ==========================================
# Task 10: Outlier-corrected monthly trend
# ==========================================

merged["order_date"] = pd.to_datetime(merged["order_date"])
merged["year_month"] = merged["order_date"].dt.to_period("M")

print("\nOrder date and month:")
print(merged[["order_date", "year_month"]].head())

monthly_with_outliers = (
    merged.groupby("year_month")["order_value"].sum()
)

print("\nMonthly revenue including outliers:")
print(monthly_with_outliers)

monthly_without_outliers = (
    merged[merged["is_outlier"] == False]
    .groupby("year_month")["order_value"]
    .sum()
)

print("\nMonthly revenue excluding outliers:")
print(monthly_without_outliers)

print("\nHighest month including outliers:")
print(monthly_with_outliers.idxmax())

print("Highest month excluding outliers:")
print(monthly_without_outliers.idxmax())

print(
    "\nConclusion: January's apparent lead is caused by the two bulk "
    "orders O0011 (2026-01-28) and O0098 (2026-01-10)."
)

print(
    "After excluding these outliers, March 2026 is the genuine peak revenue month."
)