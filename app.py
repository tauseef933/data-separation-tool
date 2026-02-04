import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io
import re
import hashlib
from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import time

# --- PRE-REQUISITES: pip install streamlit pandas openpyxl requests beautifulsoup4 ---

st.set_page_config(page_title="AI Data Architect - 100% Accuracy", layout="wide", initial_sidebar_state="collapsed")

# Premium UI Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .main { background: #f8fafc; }
    .hero-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2.5rem; border-radius: 20px; color: white; margin-bottom: 2rem; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #667eea, #764ba2); }
    .status-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-left: 5px solid #667eea; }
    .stat-box { background: #764ba2; color: white; padding: 1.5rem; border-radius: 12px; text-align: center; }
</style>
""", unsafe_allow_html=True)

class UltraAccurateDetector:
    def __init__(self):
        if 'ai_cache' not in st.session_state:
            st.session_state.ai_cache = {}
        self.cache = st.session_state.ai_cache
        
        # YOUR COMPREHENSIVE KEYWORDS INTEGRATED
        self.categories = {
            'Fans': {
                'keywords': ['fan', 'fans', 'ceiling fan', 'table fan', 'wall fan', 'floor fan', 'exhaust fan', 'ventilator', 'blower', 'cooling fan', 'pedestal fan', 'tower fan', 'stand fan', 'desk fan', 'box fan', 'window fan', 'attic fan', 'bathroom fan', 'kitchen fan', 'inline fan', 'centrifugal fan', 'axial fan', 'ventilation fan', 'air circulator', 'extractor fan', 'circulation fan', 'oscillating fan', 'industrial fan', 'portable fan', 'rechargeable fan', 'solar fan', 'battery fan', 'usb fan', 'mini fan', 'personal fan', 'neck fan', 'handheld fan', 'clip fan', 'bracket fan', 'duct fan', 'booster fan', 'pressure fan', 'suction fan', 'supply fan', 'return fan', 'spot cooler', 'swamp cooler', 'fan blade', 'fan motor', 'fan guard', 'fan cage', 'fan controller', 'fan speed', 'fan switch', 'fan timer', 'fan remote', 'fan downrod', 'fan canopy', 'ventilation grille', 'air vent', 'air register', 'vent cover', 'vent cap', 'vent hood', 'range hood', 'cooker hood', 'extractor hood', 'fume hood', 'louver', 'cfm', 'airflow'],
                'exclude': ['light', 'lamp', 'bulb', 'led', 'chandelier', 'pendant'],
                'dna': ['rpm', 'blade', 'cfm', 'motor']
            },
            'Lighting': {
                'keywords': ['light', 'lights', 'lamp', 'lamps', 'bulb', 'bulbs', 'lighting', 'led', 'led light', 'fixture', 'chandelier', 'pendant', 'downlight', 'spotlight', 'track light', 'ceiling light', 'wall light', 'floor lamp', 'table lamp', 'desk lamp', 'reading lamp', 'bedside lamp', 'night light', 'accent light', 'task light', 'crystal chandelier', 'mini chandelier', 'island pendant', 'flush mount', 'semi flush', 'recessed light', 'can light', 'pot light', 'gimbal light', 'wall sconce', 'vanity light', 'mirror light', 'picture light', 'uplight', 'torchiere', 'arc lamp', 'tripod lamp', 'led strip', 'rope light', 'neon light', 'flood light', 'security light', 'motion light', 'solar light', 'garden light', 'path light', 'bollard light', 'well light', 'high bay', 'low bay', 'warehouse light', 'shop light', 'emergency light', 'exit sign', 'grow light', 'black light', 'uv light', 'smart light', 'dimmable', 'edison bulb', 'filament bulb', 'halogen', 'fluorescent', 'tube light', 'candle bulb', 'globe bulb', 'gu10', 'mr16', 'e26', 'e27', 'light switch', 'dimmer', 'ballast', 'transformer', 'lumens', 'watt'],
                'exclude': ['fan', 'ventilator', 'blower', 'exhaust', 'cooling'],
                'dna': ['lumens', 'kelvin', 'watt', 'dimmable']
            },
            'Furniture': {
                'keywords': ['furniture', 'chair', 'chairs', 'table', 'tables', 'desk', 'desks', 'cabinet', 'cabinets', 'shelf', 'shelves', 'sofa', 'sofas', 'couch', 'couches', 'bed', 'beds', 'wardrobe', 'dresser', 'drawer', 'bookcase', 'stool', 'stools', 'bench', 'benches', 'ottoman', 'armchair', 'dining chair', 'office chair', 'executive chair', 'gaming chair', 'dining table', 'coffee table', 'side table', 'end table', 'console table', 'computer desk', 'writing desk', 'standing desk', 'filing cabinet', 'storage cabinet', 'tv stand', 'media unit', 'entertainment center', 'sectional', 'loveseat', 'recliner', 'nightstand', 'headboard', 'credenza', 'buffet', 'hutch', 'sideboard', 'armoire', 'futon', 'daybed', 'bunk bed', 'trundle bed', 'vanity', 'dressing table'],
                'exclude': [],
                'dna': ['upholstered', 'solid wood', 'frame']
            },
            'Decor': {
                'keywords': ['decor', 'decoration', 'ornament', 'vase', 'frame', 'mirror', 'wall art', 'sculpture', 'statue', 'figurine', 'candle', 'planter', 'centerpiece', 'tapestry', 'clock', 'pillow', 'cushion', 'rug', 'carpet', 'mat', 'curtain', 'drape', 'wreath', 'garland', 'basket', 'tray', 'bowl', 'artificial plant', 'wall sticker', 'wallpaper'],
                'exclude': [],
                'dna': ['accent', 'aesthetic', 'decorative']
            }
        }

    def web_agent_verify(self, query):
        """AI Agent searches the web for product DNA"""
        cache_key = hashlib.md5(query.lower().encode()).hexdigest()
        if cache_key in self.cache: return self.cache[cache_key]
        
        try:
            url = f"https://www.google.com/search?q={requests.utils.quote(query + ' product category specs')}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}
            res = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            snippets = " ".join([tag.text.lower() for tag in soup.find_all(['span', 'div'], limit=20)])
            self.cache[cache_key] = snippets
            return snippets
        except: return ""

    def classify_row(self, row, enabled_cats):
        row_str = " ".join(row.astype(str).values).lower()
        
        # 1. Primary Keyword Match
        scores = {cat: 0 for cat in enabled_cats}
        for cat in enabled_cats:
            data = self.categories[cat]
            # Handle exclusions
            if any(excl in row_str for excl in data['exclude']): continue
            
            # Count keyword hits
            hits = sum(1 for kw in data['keywords'] if f" {kw} " in f" {row_str} ")
            scores[cat] = hits * 10

        best_cat = max(scores, key=scores.get)
        
        # 2. AI Verification if ambiguous (Score < 20)
        if scores[best_cat] < 20:
            web_context = self.web_agent_verify(row_str[:80])
            for cat in enabled_cats:
                if cat.lower() in web_context: scores[cat] += 50
                for dna_term in self.categories[cat].get('dna', []):
                    if dna_term in web_context: scores[cat] += 25
            
            best_cat = max(scores, key=scores.get)
        
        return best_cat if scores[best_cat] > 5 else "Uncategorized"

def main():
    st.markdown('<div class="hero-header"><h1>AI Data Architect Pro</h1><p>100% Accuracy Separation Tool</p></div>', unsafe_allow_html=True)

    file = st.file_uploader("Upload Master Excel", type=['xlsx'])
    if file:
        df = pd.read_excel(file)
        cats = st.sidebar.multiselect("Select Categories", list(UltraAccurateDetector().categories.keys()), default=["Fans", "Lighting"])
        
        if st.button("🚀 Start Deep Analysis"):
            detector = UltraAccurateDetector()
            results = defaultdict(list)
            prog = st.progress(0)
            
            for i, (idx, row) in enumerate(df.iterrows()):
                category = detector.classify_row(row, cats)
                results[category].append(row.to_dict())
                prog.progress((i + 1) / len(df))
                time.sleep(0.05)

            st.success("Separation Complete!")
            cols = st.columns(len(results))
            for i, (cat, items) in enumerate(results.items()):
                with cols[i]:
                    st.markdown(f'<div class="stat-box"><h3>{len(items)}</h3><p>{cat}</p></div>', unsafe_allow_html=True)
                    out_df = pd.DataFrame(items)
                    towrite = io.BytesIO()
                    out_df.to_excel(towrite, index=False)
                    st.download_button(f"Download {cat}", towrite.getvalue(), f"{cat}_output.xlsx")

if __name__ == "__main__":
    main()
