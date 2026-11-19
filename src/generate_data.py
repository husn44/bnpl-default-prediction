# Output: data/raw/raw_bnpl.csv

# ---------------------------------------------------------------------
# STEP 1 — Setup + demographics
# ---------------------------------------------------------------------
import os
import numpy as np
import pandas as pd

N = 3000                 # number of customers (assignment minimum is 1000)
SEED = 42
TARGET_DEFAULT_RATE = 0.20
rng = np.random.default_rng(SEED)

customer_id = [f"C{i:05d}" for i in range(1, N + 1)]

# BNPL users skew young
age = np.clip(rng.normal(29, 8, N), 18, 60).round().astype(int)

gender = rng.choice(["Male", "Female"], N, p=[0.48, 0.52])

states = ["Selangor", "Kuala Lumpur", "Johor", "Penang", "Perak",
          "Sabah", "Sarawak", "Kedah", "Negeri Sembilan", "Melaka"]
state_p = [0.24, 0.16, 0.12, 0.09, 0.08, 0.08, 0.08, 0.06, 0.05, 0.04]
state = rng.choice(states, N, p=state_p)

# Employment type depends on age (students are young)
emp_types = ["Full-time", "Part-time", "Gig worker", "Student", "Self-employed"]
employment_type = np.empty(N, dtype=object)
for i, a in enumerate(age):
    if a <= 23:
        p = [0.25, 0.20, 0.15, 0.35, 0.05]
    elif a <= 35:
        p = [0.55, 0.10, 0.18, 0.05, 0.12]
    else:
        p = [0.60, 0.08, 0.12, 0.00, 0.20]
    employment_type[i] = rng.choice(emp_types, p=p)

# Monthly income (RM): log-normal, median depends on employment type
income_median = {"Full-time": 4500, "Part-time": 1800, "Gig worker": 2600,
                 "Student": 900, "Self-employed": 4200}
med = np.array([income_median[e] for e in employment_type])
age_boost = 1 + np.clip(age - 25, 0, 20) * 0.02          # older -> earn a bit more
monthly_income = np.clip(med * age_boost * rng.lognormal(0, 0.45, N), 600, 25000).round(2)

# ---------------------------------------------------------------------
# STEP 2 — Financial health (hidden "discipline" trait links these together)
# ---------------------------------------------------------------------
# discipline: hidden trait, high = careful with money (never saved in the CSV)
discipline = rng.normal(0, 1, N)
# impulsiveness: hidden trait, high = impulse buyer (never saved in the CSV)
impulsiveness = rng.normal(0, 1, N)

months_as_customer = rng.integers(1, 49, N)

late_lambda = np.exp(-0.4 - 0.8 * discipline) * (months_as_customer / 24)
past_late_payments = np.clip(rng.poisson(late_lambda), 0, 10)

credit_score = (650 + 55 * discipline + 25 * np.log(monthly_income / 3000)
                - 12 * past_late_payments + rng.normal(0, 35, N))
credit_score = np.clip(credit_score, 300, 850).round().astype(int)

# Existing monthly debt repayments (car loan, PTPTN, credit cards...) in RM
debt_ratio = np.clip(rng.gamma(2.0, 0.12, N) * np.exp(-0.25 * discipline), 0, 1.2)
existing_monthly_debt = (monthly_income * debt_ratio).round(2)

num_credit_cards = np.where(
    np.isin(employment_type, ["Student"]),
    rng.integers(0, 2, N),
    np.clip(rng.poisson(0.5 + monthly_income / 5000), 0, 5),
)

num_active_bnpl_plans = np.clip(
    rng.poisson(np.exp(0.3 - 0.35 * discipline + 0.35 * impulsiveness)), 0, 8)

# ---------------------------------------------------------------------
# STEP 3 — BNPL transaction + app behaviour
# ---------------------------------------------------------------------
providers = ["Atome", "SPayLater", "Grab PayLater", "Boost PayFlex"]
bnpl_provider = rng.choice(providers, N, p=[0.25, 0.35, 0.28, 0.12])

categories = ["Electronics", "Fashion", "Beauty", "Travel", "Groceries", "Furniture"]
base_cat_p = np.array([0.20, 0.25, 0.15, 0.10, 0.18, 0.12])
impulse_cat_shift = np.array([0.05, 0.06, 0.04, 0.0, -0.12, -0.03])  # impulse -> fashion/beauty/gadgets
merchant_category = np.empty(N, dtype=object)
for i in range(N):
    p = np.clip(base_cat_p + impulse_cat_shift * impulsiveness[i], 0.02, None)
    merchant_category[i] = rng.choice(categories, p=p / p.sum())

cat_price_median = {"Electronics": 1500, "Fashion": 250, "Beauty": 150,
                    "Travel": 1200, "Groceries": 120, "Furniture": 1000}
pm = np.array([cat_price_median[c] for c in merchant_category])
purchase_amount = np.clip(pm * (monthly_income / 3500) ** 0.3 * rng.lognormal(0, 0.5, N),
                          50, 6000).round(2)

# Bigger purchases -> more instalments
num_instalments = np.empty(N, dtype=int)
for i, amt in enumerate(purchase_amount):
    if amt < 300:
        p = [0.80, 0.18, 0.02]
    elif amt < 1500:
        p = [0.45, 0.40, 0.15]
    else:
        p = [0.15, 0.40, 0.45]
    num_instalments[i] = rng.choice([3, 6, 12], p=p)
instalment_amount = (purchase_amount / num_instalments).round(2)

# Debt-to-income includes this new instalment
debt_to_income = ((existing_monthly_debt + instalment_amount) / monthly_income).round(3)

# Impulse buyers shop late at night more often
late_night = rng.random(N) < (0.12 + 0.10 * np.clip(impulsiveness, -1, 2))
purchase_hour = np.where(late_night, rng.choice([22, 23, 0, 1, 2], N),
                         rng.integers(8, 22, N))

is_promo_period = (rng.random(N) < np.clip(0.25 + 0.10 * impulsiveness, 0.05, 0.6)).astype(int)

app_logins_per_week = np.clip(
    rng.poisson(np.clip(3 + 2 * impulsiveness + num_active_bnpl_plans, 0.5, None)), 0, 40)

# ---------------------------------------------------------------------
# STEP 4 — Hidden risk score -> default_flag 
# ---------------------------------------------------------------------
emp_risk = {"Full-time": 0.0, "Part-time": 0.35, "Gig worker": 0.45,
            "Student": 0.55, "Self-employed": 0.20}

risk_logit = (
    1.8 * (debt_to_income - 0.35)
    + 0.30 * past_late_payments
    + 0.25 * num_active_bnpl_plans
    - 0.55 * np.log(monthly_income / 3000)
    - 0.006 * (credit_score - 650)
    + np.array([emp_risk[e] for e in employment_type])
    + 0.25 * impulsiveness
    + 0.20 * is_promo_period
    + 0.25 * late_night
    + 0.04 * (num_instalments - 3)
    + rng.normal(0, 0.8, N)                  # noise: real life is messy
)

# Find the intercept that gives ~20% default rate
lo, hi = -10.0, 10.0
for _ in range(60):
    mid = (lo + hi) / 2
    if (1 / (1 + np.exp(-(risk_logit + mid)))).mean() > TARGET_DEFAULT_RATE:
        hi = mid
    else:
        lo = mid
default_prob = 1 / (1 + np.exp(-(risk_logit + lo)))
default_flag = (rng.random(N) < default_prob).astype(int)

# Noisy on purpose so text is helpful but not a perfect giveaway.
# Columns starting with "_" MUST be dropped before modelling.
stress_signal = risk_logit + rng.normal(0, 1.0, N)
_stress_hint = pd.qcut(stress_signal, 3, labels=["low", "medium", "high"]).astype(str)
impulse_signal = impulsiveness + 0.5 * is_promo_period + 0.5 * late_night + rng.normal(0, 0.7, N)
_impulse_hint = np.where(impulse_signal > np.quantile(impulse_signal, 0.6), "high", "low")

# ---------------------------------------------------------------------
# STEP 5 — Assemble, add realistic missing values, save
# ---------------------------------------------------------------------
df = pd.DataFrame({
    "customer_id": customer_id,
    "age": age,
    "gender": gender,
    "state": state,
    "employment_type": employment_type,
    "monthly_income": monthly_income,
    "credit_score": credit_score.astype(float),
    "existing_monthly_debt": existing_monthly_debt,
    "debt_to_income": debt_to_income,
    "num_credit_cards": num_credit_cards,
    "num_active_bnpl_plans": num_active_bnpl_plans,
    "bnpl_provider": bnpl_provider,
    "merchant_category": merchant_category,
    "purchase_amount": purchase_amount,
    "num_instalments": num_instalments,
    "instalment_amount": instalment_amount,
    "purchase_hour": purchase_hour,
    "is_promo_period": is_promo_period,
    "months_as_customer": months_as_customer,
    "past_late_payments": past_late_payments,
    "app_logins_per_week": app_logins_per_week,
    "_stress_hint": _stress_hint,
    "_impulse_hint": _impulse_hint,
    "default_flag": default_flag,
})

# Real data has gaps
for col, frac in [("credit_score", 0.03), ("monthly_income", 0.02), ("employment_type", 0.01)]:
    idx = rng.choice(N, int(N * frac), replace=False)
    df.loc[idx, col] = np.nan

os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/raw_bnpl.csv", index=False)

print(f"Saved data/raw/raw_bnpl.csv  ->  {df.shape[0]} rows x {df.shape[1]} columns")
print(f"Default rate: {df['default_flag'].mean():.1%}")
print(df.head())