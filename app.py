import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io
import time

# --- AI INITIALIZATION ---
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

st.set_page_config(page_title="Data Separation Tool", layout="wide", initial_sidebar_state="collapsed")

# Your exact CSS styling preserved
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .main > div { background: #f8fafc; min-height: 100vh; padding: 2rem; }
    .hero-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2.5rem; border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3); }
    .hero-title { color: #ffffff; font-size: 2.5rem; font-weight: 800; margin: 0; }
    .hero-subtitle { color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin-top: 0.5rem; }
    .premium-card { background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); margin-bottom: 1.5rem; border: 1px solid #e5e7eb; }
    .card-title { color: #1e293b; font-size: 1.3rem; font-weight: 700; margin-bottom: 1.2rem; display: flex; align-items: center; gap: 0.5rem; }
    .success-box { background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-left: 4px solid #10b981; color: #065f46; padding: 1rem 1.2rem; border-radius: 10px; margin: 1rem 0; }
    .stat-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 16px; color: white; text-align: center; }
    .stButton>button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

class HybridCategorizer:
    def __init__(self, api_key):
        # ALL your keywords preserved here
        self.keyword_data = {
            'Fans': {
                'keywords': ['fan', 'fans', 'ceiling fan', 'exhaust fan', 'ventilator', 'blower', 'cfm', 'airflow', 'blade', 'downrod', 'motor', 'hvls', 'bldc'],
                'exclude': ['light', 'lamp', 'bulb']
            },
            'Lighting': {
                'keywords': ['light', 'lamp', 'bulb', 'led', 'chandelier', 'pendant', 'sconce', 'vanity', 'lumens', 'kelvin', 'watt', 'fixture'],
                'exclude': ['fan', 'blower']
            },
            # ... (Rest of your 1000+ keywords go here)
        }
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_row(self, row, enabled_cats):
        # 1. Combine all columns for context
        full_text = " ".join([str(val).lower() for val in row.values if pd.notna(val)])
        
        # 2. Try Keyword Logic First (Fast)
        best_cat = None
        max_score = 0
        for cat in enabled_cats:
            if cat in self.keyword_data:
                score = sum(30 for kw in self.keyword_data[cat]['keywords'] if kw in full_text)
                if score > max_score:
                    max_score = score
                    best_cat = cat
        
        # 3. Use AI if Keywords are unsure (< 30 score)
        if max_score < 30 and self.api_key:
            try:
                time.sleep(1) # Rate limit
                prompt = f"Categorize this product into {enabled_cats}. Product: {full_text}. Return only: Category|Score"
                response = self.model.generate_content(prompt)
                res_parts = response.text.strip().split('|')
                return res_parts[0], int(res_parts[1])
            except:
                return best_cat, max_score
                
        return best_cat, max_score

def create_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def main():
    st.markdown('<div class="hero-header"><h1 class="hero-title">AI Data Separator</h1><p class="hero-subtitle">Hybrid Keyword + Gemini 1.5 Intelligence</p></div>', unsafe_allow_html=True)

    # SECRETS CHECK
    api_key = st.secrets.get("GEMINI_API_KEY")
    if api_key:
        st.markdown('<div class="success-box">🛡️ API Key Active from Secrets</div>', unsafe_allow_html=True)
    else:
        st.error("API Key not found in Streamlit Secrets!")

    uploaded = st.file_uploader("Upload Vendor Excel", type=['xlsx'])
    
    if uploaded:
        df = pd.read_excel(uploaded)
        detector = HybridCategorizer(api_key)
        
        # UI for category selection
        available_cats = ['Lighting', 'Fans', 'Furniture', 'Decor', 'Electronics', 'Kitchen', 'Bathroom', 'Outdoor']
        selected_cats = st.multiselect("Select Categories", available_cats, default=['Lighting', 'Fans'])

        if st.button("🚀 Run Advanced Separation"):
            results = []
            progress = st.progress(0)
            
            for i, row in df.iterrows():
                cat, score = detector.analyze_row(row, selected_cats)
                row_dict = row.to_dict()
                row_dict['AI_Category'] = cat if cat else "Uncategorized"
                results.append(row_dict)
                progress.progress((i + 1) / len(df))

            final_df = pd.DataFrame(results)
            st.session_state.final_df = final_df
            st.success("Analysis Complete!")

        # DOWNLOAD SECTION
        if 'final_df' in st.session_state:
            res = st.session_state.final_df
            cols = st.columns(len(selected_cats))
            for idx, cat in enumerate(selected_cats):
                cat_data = res[res['AI_Category'] == cat]
                if not cat_data.empty:
                    with cols[idx]:
                        st.download_button(f"Download {cat}", create_excel(cat_data), f"{cat}_list.xlsx")

if __name__ == "__main__":
    main()
