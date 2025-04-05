import streamlit as st
import pandas as pd
import requests
import io
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import folium
from streamlit_folium import st_folium

GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="AI Data Visualization Bot", layout="wide")
st.title("📊 Talk2Chart: AI-Powered Data Visualization")
st.markdown("Upload a dataset, describe the visualization you wpython -m pip show matplotlibant, and let AI do the magic ✨")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Dataset Preview")
    st.dataframe(df.head(), use_container_width=True)

    lib_choice = st.selectbox("Select Visualization Library", ["matplotlib", "seaborn", "plotly", "folium"])

    user_prompt = st.text_input("Describe the chart you want to create (e.g., 'bar chart of age distribution')")

    if st.button("Generate Visualization") and user_prompt:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_str = csv_buffer.getvalue()

        messages = [
            {"role": "system", "content": f"You are a data visualization expert. The user will describe a chart they want. Use the library '{lib_choice}' to create a visualization based on the dataframe named df. Return ONLY executable Python code."},
            {"role": "user", "content": f"Here is the dataset:\n{csv_str[:4000]}\nCreate this: {user_prompt}"},
        ]

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
        }

        response = requests.post(GROQ_API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            ai_code = response.json()['choices'][0]['message']['content']
            st.markdown("### 🧠 AI-Generated Code")
            st.code(ai_code, language="python")

            try:
                local_vars = {"df": df.copy(), "plt": plt, "sns": sns, "px": px, "folium": folium, "st_folium": st_folium, "st": st}
                exec(ai_code, {}, local_vars)
            except Exception as e:
                st.error(f"⚠️ Error executing code: {e}")
        else:
            st.error("❌ Failed to fetch visualization code from Groq API.")
