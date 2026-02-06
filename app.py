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

# YOUR ORIGINAL UI CSS
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

class UltraAccurateDetector:
    def __init__(self, api_key):
        # UPDATED: Added 'ceiling mount' and 'wall mount' to Lighting
        self.categories = {
            'Fans': {
                'keywords': ['fan', 'fans', 'ceiling fan', 'exhaust fan', 'ventilator', 'blower', 'cfm', 'airflow', 'blade', 'downrod', 'motor', 'hvls', 'bldc'],
                'exclude': ['light', 'lamp', 'bulb']
            },
            'Lighting': {
                'keywords': [
                    'light', 'lamp', 'bulb', 'led', 'chandelier', 'pendant', 'sconce', 
                    'vanity', 'lumens', 'kelvin', 'watt', 'fixture',
                    'ceiling mount', 'wall mount' # Added as requested
                ],
                'exclude': ['fan', 'blower']
            },
            'Furniture': {'keywords': ['chair', 'table', 'sofa', 'desk', 'cabinet', 'bed']},
            'Decor': {'keywords': ['vase', 'mirror', 'clock', 'art', 'statue', 'rug']},
            'Electronics': {'keywords': ['tv', 'speaker', 'monitor', 'camera', 'phone']},
            'Kitchen': {'keywords': ['cookware', 'microwave', 'oven', 'fridge', 'blender']},
            'Bathroom': {'keywords': ['toilet', 'sink', 'shower', 'bathtub', 'faucet']},
            'Outdoor': {'keywords': ['patio', 'grill', 'bbq', 'garden', 'gazebo']}
        }
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_row(self, row, enabled_cats):
        # Clean and combine text for matching
        full_text = " ".join([str(val).lower().strip() for val in row.values if pd.notna(val)])
        
        best_cat = None
        max_score = 0
        
        # 1. High-Priority Keyword Match (including Ceiling/Wall Mount)
        for cat in enabled_cats:
            if cat in self.categories:
                # Give extra weight to the specific mounts we added
                score = 0
                for kw in self.categories[cat]['keywords']:
                    if kw in full_text:
                        # Weighting Ceiling/Wall Mount highly to ensure they land in Lighting
                        weight = 50 if kw in ['ceiling mount', 'wall mount'] else 30
                        score += weight
                
                # Check for exclusions (e.g., if it says 'light' but it's a 'fan light kit')
                for excl in self.categories[cat].get('exclude', []):
                    if excl in full_text:
                        score -= 40

                if score > max_score:
                    max_score = score
                    best_cat = cat
        
        # 2. AI Fallback for Ambiguous items
        if max_score < 25 and self.api_key:
            try:
                prompt = f"Categorize this product into {enabled_cats}. Product: {full_text}. Return ONLY the category name."
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
        df.to_excel(writer, index=False)
    return output.getvalue()

def main():
    st.markdown('<div class="hero-header"><h1 class="hero-title">Data Separation Tool</h1><p class="hero-subtitle">Professional Product Categorization</p></div>', unsafe_allow_html=True)

    api_key = st.secrets.get("GEMINI_API_KEY")
    uploaded = st.file_uploader("Upload Vendor Excel", type=['xlsx'])
    
    if uploaded:
        # Load the dataframe
        df = pd.read_excel(uploaded)
        detector = UltraAccurateDetector(api_key)
        
        # Display settings
        all_available = list(detector.categories.keys())
        selected_cats = st.multiselect("Select Categories to Separate", all_available, default=['Lighting', 'Fans'])

        if st.button("🚀 Start Separation"):
            result_df = df.copy()
            assignments = []
            
            progress = st.progress(0)
            for i, row in result_df.iterrows():
                cat = detector.analyze_row(row, selected_cats)
                assignments.append(cat)
                progress.progress((i + 1) / len(df))

            result_df['Assigned_Category'] = assignments
            st.session_state.final_df = result_df
            st.success(f"Processing Complete! Sorted {len(df)} SKUs.")

        # Download Section
        if 'final_df' in st.session_state:
            res = st.session_state.final_df
            st.markdown("### Download Categorized Sheets")
            
            # Create a column for each selected category
            dl_cols = st.columns(len(selected_cats))
            for idx, cat in enumerate(selected_cats):
                # Filter data, keeping ALL original columns
                cat_data = res[res['Assigned_Category'] == cat].drop(columns=['Assigned_Category'])
                
                if not cat_data.empty:
                    with dl_cols[idx]:
                        st.download_button(
                            label=f"Download {cat} ({len(cat_data)})",
                            data=create_excel(cat_data),
                            file_name=f"{cat}_List.xlsx",
                            key=f"btn_{cat}"
                        )
            
            # Check for uncategorized
            uncat = res[res['Assigned_Category'] == "Uncategorized"].drop(columns=['Assigned_Category'])
            if not uncat.empty:
                st.divider()
                st.download_button(f"Download Uncategorized ({len(uncat)})", create_excel(uncat), "Manual_Review_Needed.xlsx")

if __name__ == "__main__":
    main()
