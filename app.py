import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io
import time

# Try to import Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

st.set_page_config(page_title="Data Separation Tool", layout="wide", initial_sidebar_state="collapsed")

# Original UI CSS (No emojis, Inter font)
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
    .stButton>button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 12px; font-weight: 600; height: 3rem; width: 100%; transition: all 0.3s ease; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4); }
    .preview-btn>button { background: #f1f5f9 !important; color: #1e293b !important; border: 1px solid #e2e8f0 !important; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

class ProductDetector:
    def __init__(self, api_key):
        self.categories = {
            'Fans': {
                'keywords': ['fan', 'fans', 'ceiling fan', 'exhaust fan', 'ventilator', 'blower', 'cfm', 'airflow', 'blade', 'downrod', 'motor', 'oscillating', 'hvls', 'bldc'],
                'exclude': ['light', 'lamp', 'bulb', 'umbrella']
            },
            'Lighting': {
                'keywords': ['light', 'lamp', 'bulb', 'led', 'chandelier', 'pendant', 'sconce', 'vanity', 'lumens', 'kelvin', 'fixture', 'ceiling mount', 'wall mount', 'flush mount', 'recessed', 'track lighting', 'dimmer'],
                'exclude': ['fan', 'blower', 'umbrella']
            },
            'Umbrellas': {
                'keywords': ['umbrella', 'umbrellas', 'parasol', 'patio umbrella', 'cantilever', 'offset', 'sunshade', 'canopy', 'umbrella base', 'umbrella stand'],
                'exclude': ['ceiling fan', 'chandelier']
            },
            'Decor': {
                'keywords': ['decor', 'decoration', 'vase', 'mirror', 'clock', 'wall art', 'sculpture', 'figurine', 'candle', 'picture frame', 'rug', 'carpet', 'cushion'],
                'exclude': ['sofa', 'table', 'chair', 'bed']
            }
        }
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_row(self, row, enabled_cats):
        full_text = " ".join([str(val).lower() for val in row.values if pd.notna(val)])
        best_cat = "Uncategorized"
        max_score = 0
        
        for cat in enabled_cats:
            if cat in self.categories:
                score = 0
                for kw in self.categories[cat]['keywords']:
                    if kw in full_text:
                        score += 60 if kw in ['ceiling mount', 'wall mount', 'umbrella'] else 30
                for excl in self.categories[cat].get('exclude', []):
                    if excl in full_text: score -= 50
                if score > max_score:
                    max_score = score
                    best_cat = cat
        
        if max_score < 25 and self.api_key:
            try:
                prompt = f"Categorize this: {full_text}. Options: {enabled_cats}. Return only category name."
                response = self.model.generate_content(prompt)
                ai_res = response.text.strip()
                if ai_res in enabled_cats: return ai_res
            except: pass
        return best_cat

def create_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def main():
    st.markdown('<div class="hero-header"><h1 class="hero-title">Data Separation Tool</h1><p class="hero-subtitle">Professional product categorization system</p></div>', unsafe_allow_html=True)

    api_key = st.secrets.get("GEMINI_API_KEY")
    
    st.markdown('<div class="premium-card"><h3 class="card-title">Upload File</h3>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=['xlsx'], label_visibility="collapsed")
    
    if uploaded:
        xl = pd.ExcelFile(uploaded)
        selected_sheet = st.selectbox("Select sheet to detect", xl.sheet_names)
        df = pd.read_excel(uploaded, sheet_name=selected_sheet)
        st.markdown(f'<div class="success-box">File loaded: {len(df)} rows detected</div>', unsafe_allow_html=True)
        
        detector = ProductDetector(api_key)
        all_cats = list(detector.categories.keys())
        selected_cats = st.multiselect("Select categories", all_cats, default=['Lighting', 'Fans', 'Umbrellas', 'Decor'])

        if st.button("Start Processing"):
            result_df = df.copy()
            assigned_list = []
            progress = st.progress(0)
            for i in range(len(result_df)):
                cat = detector.analyze_row(result_df.iloc[i], selected_cats)
                assigned_list.append(cat)
                progress.progress((i + 1) / len(df))

            result_df['Assigned_Category'] = assigned_list
            st.session_state.processed_data = result_df
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # OUTPUT SECTION
    if 'processed_data' in st.session_state:
        res = st.session_state.processed_data
        st.markdown('<div class="premium-card"><h3 class="card-title">Categorized Files</h3>', unsafe_allow_html=True)
        
        found_cats = res['Assigned_Category'].unique()
        
        # We process each category separately
        for cat in found_cats:
            cat_df = res[res['Assigned_Category'] == cat].drop(columns=['Assigned_Category'])
            
            # Row for each category
            with st.container():
                c1, c2, c3 = st.columns([2, 2, 4])
                with c1:
                    st.markdown(f"**{cat}** ({len(cat_df)} items)")
                with c2:
                    # Individual Preview Expander inside the file section
                    with st.expander(f"Preview {cat}"):
                        st.dataframe(cat_df.head(10))
                with c3:
                    st.download_button(
                        label=f"Download {cat} Excel",
                        data=create_excel(cat_df),
                        file_name=f"{cat}_data.xlsx",
                        key=f"dl_{cat}"
                    )
                st.markdown("---")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
