# ==========================================
# PART 2 - DATA VISUALIZATION
# ==========================================

import pandas as pd
import matplotlib.pyplot as plt
import os

# Load raw datasets
customers = pd.read_csv("data/customers.csv")
products = pd.read_csv("data/products.csv")
orders = pd.read_csv("data/orders.csv")

# Standardize payment method
orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)

# Remove duplicate orders
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

orders = orders.drop_duplicates(
    subset=duplicate_cols,
    keep="first"
).reset_index(drop=True)

# Handle missing values
orders["discount_pct"] = orders["discount_pct"].fillna(0)
orders["rating"] = orders["rating"].fillna(
    orders["rating"].median()
)

# Merge datasets
merged = orders.merge(products, on="product_id", how="left")
merged = merged.merge(customers, on="customer_id", how="left")

# Calculate order value
merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)

# Detect quantity outliers using IQR
Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

merged["is_outlier"] = (
    (merged["quantity"] < lower) |
    (merged["quantity"] > upper)
)

# Create visualizations folder if it does not exist
os.makedirs("visualizations", exist_ok=True)

# ==========================================
# Chart 1: Return rate by payment method
# ==========================================

payment_return = (
    merged.groupby("payment_method")["returned"]
    .mean()
    .mul(100)
    .round(2)
    .sort_values(ascending=False)
)

plt.figure(figsize=(8, 5))

bars = plt.bar(
    payment_return.index,
    payment_return.values
)

plt.xlabel("Payment Method")
plt.ylabel("Return Rate (%)")
cod_rate = payment_return["COD"]
card_rate = payment_return["CARD"]

plt.title(f"COD Returns at {cod_rate:.1f}% — {cod_rate / card_rate:.0f}x Card")

plt.bar_label(
    bars,
    fmt="%.1f%%"
)

plt.tight_layout()

plt.savefig(
    "visualizations/return_rate_by_payment.png",
    bbox_inches="tight"
)

plt.close()

# ==========================================
# Chart 2: Outlier-corrected monthly revenue
# ==========================================

merged["order_date"] = pd.to_datetime(merged["order_date"])
merged["year_month"] = merged["order_date"].dt.to_period("M")

monthly_without_outliers = (
    merged[merged["is_outlier"] == False]
    .groupby("year_month")["order_value"]
    .sum()
)

plt.figure(figsize=(9, 5))

plt.plot(
    monthly_without_outliers.index.astype(str),
    monthly_without_outliers.values,
    marker="o"
)

plt.xlabel("Month")
plt.ylabel("Revenue (INR)")
peak_month = monthly_without_outliers.idxmax()

plt.title(f"{peak_month.strftime('%B %Y')} is the True Peak Revenue Month")

plt.tight_layout()

plt.savefig(
    "visualizations/monthly_revenue_trend.png",
    bbox_inches="tight"
)

plt.close()

print("Visualizations created successfully.")
print("Saved: visualizations/return_rate_by_payment.png")
print("Saved: visualizations/monthly_revenue_trend.png")