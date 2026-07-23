import streamlit as st
import pandas as pd
import joblib
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

st.set_page_config(page_title="Supply Chain Risk Analytics", layout="wide")

# --- Load model artifacts ---
@st.cache_resource
def load_artifacts():
    model = joblib.load('../src/model.pkl')
    encoders = joblib.load('../src/encoders.pkl')
    explainer = joblib.load('../src/shap_explainer.pkl')
    feature_cols = joblib.load('../src/feature_cols.pkl')
    return model, encoders, explainer, feature_cols

@st.cache_data
def load_data():
    df = pd.read_csv('../data/processed/cleaned_orders.csv')
    df = df[df['Delivery Status'] != 'Shipping canceled'].copy()
    df['order date (DateOrders)'] = pd.to_datetime(df['order date (DateOrders)'])
    df['order_month'] = df['order date (DateOrders)'].dt.month
    df['order_dayofweek'] = df['order date (DateOrders)'].dt.dayofweek
    return df

model, encoders, explainer, feature_cols = load_artifacts()
df = load_data()

categorical_cols = ['Shipping Mode', 'Order Region', 'Market', 'Category Name', 'Customer Segment']

def prepare_features(row):
    """Convert a raw dataframe row into encoded features the model expects."""
    X_row = row[feature_cols].copy()
    for col in categorical_cols:
        le = encoders[col]
        X_row[col] = le.transform([X_row[col]])[0]
    return X_row.to_frame().T.astype(float)

def get_shap_explanation(X_row, original_row):
    """Return top features, their SHAP contributions, and original (human-readable) values."""
    shap_vals = explainer.shap_values(X_row)[0]
    contributions = []
    for feat, val in zip(feature_cols, shap_vals):
        original_val = original_row[feat]
        contributions.append((feat, val, original_val))
    contributions.sort(key=lambda x: abs(x[1]), reverse=True)
    return contributions[:5]

def generate_risk_narrative(order_context, top_features):
    """Call Groq to generate a plain-English explanation, grounded in SHAP values."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    features_text = "\n".join([
        f"- {feat} = {val_orig} → SHAP {val:+.3f} "
        f"({'increases' if val > 0 else 'decreases'} risk, "
        f"magnitude {'large' if abs(val) > 0.5 else 'moderate' if abs(val) > 0.1 else 'small'})"
        for feat, val, val_orig in top_features
    ])

    prompt = f"""You are a supply chain analyst assistant writing for a procurement manager.

Order: {order_context}

SHAP-based risk factors for this order, ranked by importance:
{features_text}

Write a natural 3-4 sentence summary that:
1. States the overall predicted risk level
2. Names the single largest driver by magnitude and its actual value (e.g. "Shipping Mode 
   (Standard Class)"), and says whether it increases or decreases risk
3. Briefly mentions 1-2 secondary factors and their direction
4. Ends with one plain observation - e.g. if all factors point the same direction, say so

RULES: Only state what the SHAP signs and magnitudes show. Do not invent explanations for 
*why* a factor matters (e.g. do not claim a category "requires special handling" or a 
shipping mode is "inherently slow") - you do not have that information. Vary your sentence 
structure - do not repeat "it decreases/increases late-delivery risk" verbatim for every item.
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content

# --- UI ---
st.title("📦 Supply Chain Risk & Demand Analytics")
st.markdown("Predict late-delivery risk and get plain-English explanations powered by AI.")

st.header("Dashboard Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Orders", f"{len(df):,}")
col2.metric("Late Delivery Rate", f"{df['Late_delivery_risk'].mean()*100:.1f}%")
col3.metric("Avg Delay (days)", f"{df['delivery_delay_days'].mean():.2f}")

st.markdown("---")
st.header("🔍 Analyze a Specific Order")

order_idx = st.number_input("Select an order (row number)", min_value=0, max_value=len(df)-1, value=0)
selected_row = df.iloc[order_idx]

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Order Details")
    st.write(f"**Shipping Mode:** {selected_row['Shipping Mode']}")
    st.write(f"**Order Region:** {selected_row['Order Region']}")
    st.write(f"**Category:** {selected_row['Category Name']}")
    st.write(f"**Sales:** ${selected_row['Sales']:.2f}")
    st.write(f"**Scheduled Days:** {selected_row['Days for shipment (scheduled)']}")

with col_b:
    st.subheader("Risk Prediction")
    X_row = prepare_features(selected_row)
    risk_proba = model.predict_proba(X_row)[0][1]
    st.metric("Predicted Late-Delivery Risk", f"{risk_proba*100:.1f}%")
    actual_status = "Late" if selected_row['Late_delivery_risk'] == 1 else "On-time"
    st.write(f"**Actual outcome:** {actual_status}")

st.markdown("---")

if st.button("🤖 Generate AI Risk Explanation"):
    with st.spinner("Analyzing risk factors..."):
        top_features = get_shap_explanation(X_row, selected_row)
        order_context = (
            f"Shipping Mode: {selected_row['Shipping Mode']}, "
            f"Region: {selected_row['Order Region']}, "
            f"Category: {selected_row['Category Name']}, "
            f"Predicted risk: {risk_proba*100:.1f}%"
        )
        narrative = generate_risk_narrative(order_context, top_features)
        st.subheader("📝 AI-Generated Risk Summary")
        st.write(narrative)

        with st.expander("See raw SHAP contributions"):
            for feat, val, val_orig in top_features:
                direction = "increases" if val > 0 else "decreases"
                st.write(f"- **{feat}** = {val_orig}: {val:+.3f} ({direction} risk)")