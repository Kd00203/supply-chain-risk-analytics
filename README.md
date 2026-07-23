# Supply Chain Risk & Demand Analytics Platform

An end-to-end analytics project analyzing ~180,000 e-commerce orders to predict 
and explain late-delivery risk, combining data analysis, machine learning, and 
LLM-powered plain-English insights.

## 🔗 Live Links
- **Interactive App:** [Streamlit link here — add once deployed]
- **Power BI Dashboard:** see `powerbi/README.md`

## 📊 Project Layers

**1. Data Analyst Layer** — Cleaning, EDA, and business narrative
- Cleaned ~180K rows, removed PII, fixed inconsistent data (see `notebooks/01_cleaning.ipynb`)
- Key finding: 54.8% of orders are late; shipping mode SLAs are the dominant driver
- Full write-up: [`narrative.md`](narrative.md)

**2. Data Scientist Layer** — Predictive modeling with explainability
- Compared Logistic Regression, Random Forest, and XGBoost (see `notebooks/02_modeling.ipynb`)
- SHAP analysis confirms Shipping Mode as the primary risk driver, consistent with EDA
- Honest discussion of precision/recall tradeoffs across models

**3. AI/LLM Layer** — Plain-English risk narratives
- Streamlit app (`app/app.py`) combines the trained model, SHAP explanations, and 
  Groq's LLM API to generate grounded, business-readable risk summaries per order

## 🛠️ Tech Stack
Python, pandas, scikit-learn, XGBoost, SHAP, Streamlit, Groq API, Power BI

## 🚀 Run Locally
```bash
pip install -r requirements.txt
cd app
streamlit run app.py
```

## 📁 Structure
```
├── notebooks/       # Cleaning, EDA, and modeling notebooks
├── data/processed/  # Cleaned dataset
├── src/             # Saved model, encoders, SHAP explainer
├── app/             # Streamlit app
├── powerbi/         # Dashboard files and charts
└── narrative.md     # Full business write-up
```