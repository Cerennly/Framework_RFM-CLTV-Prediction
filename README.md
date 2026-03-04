# FLO Customer Lifetime Value (CLTV) & RFM Prediction Framework

This project aims to build a data-driven roadmap for FLO’s sales and marketing strategy by predicting future Customer Lifetime Value (CLTV) and segmenting customers based on behavioral patterns.

---

## Project Objective

Using historical transaction data, this project aims to:

- Analyze past purchasing behavior using RFM Analysis
- Predict future transaction frequency using BG/NBD Model
- Estimate expected average profit per transaction using Gamma-Gamma Model
- Calculate 6-Month CLTV
- Segment customers for marketing optimization

---

## Dataset Story

The dataset consists of omnichannel (Online + Offline) shopping behavior of customers who made purchases between 2020–2021.

Each row represents a unique customer with aggregated transaction history.

### Variables

| Variable | Description |
|----------|------------|
| master_id | Unique customer identifier |
| order_channel | Purchase channel (Android, iOS, Desktop, Mobile, Offline) |
| first_order_date | First purchase date |
| last_order_date | Last purchase date |
| order_num_total | Total number of purchases |
| customer_value_total | Total spending |

---

## Methodology

### 1. Data Preprocessing & Outlier Handling

Probabilistic models are sensitive to extreme values.

- Applied 1st and 99th percentile thresholding
- Created weekly-based features:
  - recency_cltv_weekly
  - T_weekly
  - frequency
  - monetary

---

### 2. BG/NBD Model (Purchase Prediction)

Used to estimate:

- Probability of customer being active
- Expected number of future transactions

Generated features:

- exp_sales_3_month
- exp_sales_6_month

---

### 3. Gamma-Gamma Model (Monetary Prediction)

Used to estimate:

- Expected average profit per transaction

Generated feature:

- exp_average_value

---

### 4. CLTV Calculation & Segmentation

Combined both models to calculate:

6-Month Customer Lifetime Value (CLTV)

Customers segmented into 4 groups:

| Segment | Description |
|----------|------------|
| A | High-value loyal customers |
| B | High potential customers |
| C | Re-engagement needed |
| D | Low-value / churn-risk |

---

## Example Analysis

```python
cltv_df.groupby("cltv_segment").agg(["mean", "count"])
```

---

## Technologies Used

- Python 3.x
- Pandas
- NumPy
- Lifetimes
- Matplotlib
- Seaborn

---

## Business Value

- Enables proactive targeting
- Improves marketing ROI
- Supports data-driven decision making
- Increases long-term profitability

---

## Future Improvements

- Time-based validation
- Model performance comparison
- Dashboard integration
- API deployment
