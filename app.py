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

# RESTORING YOUR ORIGINAL UI CONFIG
st.set_page_config(page_title="Data Separation Tool", layout="wide", initial_sidebar_state="collapsed")

# RESTORING YOUR EXACT ORIGINAL CSS
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
        # Your specific category keywords
        self.keyword_data = {
            'Fans': {
                'keywords': ['fan', 'fans', 'ceiling fan', 'exhaust fan', 'ventilator', 'blower', 'cfm', 'airflow', 'blade', 'downrod', 'motor', 'hvls', 'bldc'],
                'exclude': ['light', 'lamp', 'bulb']
            },
            'Lighting': {
                'keywords': ['light', 'lamp', 'bulb', 'led', 'chandelier', 'pendant', 'sconce', 'vanity', 'lumens', 'kelvin', 'watt', 'fixture'],
                'exclude': ['fan', 'blower']
            }
            # Note: You can add the rest of your categories here
        }
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_row(self, row, enabled_cats):
        # Join all row data into one string for analysis
        full_text = " ".join([str(val).lower() for val in row.values if pd.notna(val)])
        
        best_cat = None
        max_score = 0
        
        # 1. Keyword check
        for cat in enabled_cats:
            if cat in self.keyword_data:
                score = sum(30 for kw in self.keyword_data[cat]['keywords'] if kw in full_text)
                if score > max_score:
                    max_score = score
                    best_cat = cat
        
        # 2. AI check for ambiguity (If keywords didn't find a strong match)
        if max_score < 30 and self.api_key:
            try:
                prompt = f"Categorize this product SKU/Description into one of these: {enabled_cats}. Product: {full_text}. Return only the category name."
                response = self.model.generate_content(prompt)
                ai_result = response.text.strip()
                if ai_result in enabled_cats:
                    return ai_result
            except:
                pass
                
        return best_cat if best_cat else "Uncategorized"

def create_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # We ensure the original index/SKUs are kept intact
        df.to_excel(writer, index=False)
    return output.getvalue()

def main():
    # RESTORING ORIGINAL HERO SECTION
    st.markdown('<div class="hero-header"><h1 class="hero-title">Data Separation Tool</h1><p class="hero-subtitle">Professional Product Categorization</p></div>', unsafe_allow_html=True)

    # API Key from Streamlit Secrets
    api_key = st.secrets.get("GEMINI_API_KEY")
    
    uploaded = st.file_uploader("Upload Vendor Excel", type=['xlsx'])
    
    if uploaded:
        # Load the dataframe
        df = pd.read_excel(uploaded)
        st.info(f"Loaded {len(df)} rows.")
        
        detector = HybridCategorizer(api_key)
        available_cats = ['Lighting', 'Fans', 'Furniture', 'Decor', 'Electronics', 'Kitchen', 'Bathroom', 'Outdoor']
        selected_cats = st.multiselect("Select Categories to Separate", available_cats, default=['Lighting', 'Fans'])

        if st.button("🚀 Run Separation"):
            # Create a copy to avoid modifying original until ready
            result_df = df.copy()
            categories = []
            
            progress_bar = st.progress(0)
            for i, row in result_df.iterrows():
                cat = detector.analyze_row(row, selected_cats)
                categories.append(cat)
                progress_bar.progress((i + 1) / len(df))

            result_df['Assigned_Category'] = categories
            st.session_state.final_results = result_df
            st.success("Separation Complete!")

        # DOWNLOAD SECTION
        if 'final_results' in st.session_state:
            res = st.session_state.final_results
            
            st.markdown("### Download Categorized Files")
            cols = st.columns(len(selected_cats))
            
            for idx, cat in enumerate(selected_cats):
                # This ensures we filter the FULL original data for that category
                cat_data = res[res['Assigned_Category'] == cat].drop(columns=['Assigned_Category'])
                
                if not cat_data.empty:
                    with cols[idx]:
                        st.download_button(
                            label=f"Download {cat} ({len(cat_data)})",
                            data=create_excel(cat_data),
                            file_name=f"{cat}_Export.xlsx",
                            key=f"dl_{cat}"
                        )
            
            # Option for uncategorized
            uncat_data = res[res['Assigned_Category'] == "Uncategorized"].drop(columns=['Assigned_Category'])
            if not uncat_data.empty:
                st.download_button("Download Uncategorized Items", create_excel(uncat_data), "Uncategorized.xlsx")

if __name__ == "__main__":
    main()
