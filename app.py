import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io
import re
import hashlib
from collections import defaultdict
import requests

st.set_page_config(page_title="Data Separation Tool - AI Powered", layout="wide", initial_sidebar_state="collapsed")

# CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .main > div { background: #f8fafc; min-height: 100vh; padding: 2rem; }
    .hero-header { background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%); padding: 3rem 2.5rem; border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3); }
    .hero-title { color: #ffffff; font-size: 2.5rem; font-weight: 800; margin: 0; }
    .hero-subtitle { color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin-top: 0.5rem; }
    .hero-badge { display: inline-block; background: rgba(16, 185, 129, 0.3); color: white; padding: 0.5rem 1.2rem; border-radius: 50px; font-size: 0.9rem; font-weight: 700; margin-top: 1rem; border: 2px solid #10b981; }
    .premium-card { background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); margin-bottom: 1.5rem; border: 1px solid #e5e7eb; }
    .card-title { color: #1e293b; font-size: 1.3rem; font-weight: 700; margin-bottom: 1.2rem; display: flex; align-items: center; gap: 0.5rem; }
    .card-number { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; font-size: 1rem; font-weight: 700; }
    .success-box { background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-left: 4px solid #10b981; color: #065f46; padding: 1rem 1.2rem; border-radius: 10px; margin: 1rem 0; }
    .warning-box { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-left: 4px solid #f59e0b; color: #92400e; padding: 1rem 1.2rem; border-radius: 10px; margin: 1rem 0; }
    .info-box { background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); border-left: 4px solid #3b82f6; color: #1e40af; padding: 1rem 1.2rem; border-radius: 10px; margin: 1rem 0; font-size: 0.95rem; }
    .ai-box { background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%); border-left: 4px solid #8b5cf6; color: #5b21b6; padding: 1rem 1.2rem; border-radius: 10px; margin: 1rem 0; }
    .stat-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.2rem; margin: 1.5rem 0; }
    .stat-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.8rem; border-radius: 16px; color: white; text-align: center; box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3); }
    .stat-number { font-size: 2.5rem; font-weight: 800; margin-bottom: 0.3rem; }
    .stat-label { font-size: 0.9rem; opacity: 0.95; font-weight: 500; text-transform: uppercase; }
    .stButton>button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.9rem 2rem; border-radius: 12px; font-weight: 600; font-size: 1rem; width: 100%; }
    .stDownloadButton>button { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 1rem 1.5rem; border-radius: 12px; font-weight: 600; width: 100%; }
    .distribution-item { background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%); padding: 1rem 1.5rem; border-radius: 12px; margin: 0.5rem 0; display: flex; justify-content: space-between; border-left: 4px solid #667eea; }
    .preview-header { background: #f3f4f6; padding: 0.8rem 1rem; border-radius: 8px 8px 0 0; font-weight: 600; color: #374151; border-bottom: 2px solid #667eea; }
</style>
""", unsafe_allow_html=True)


class AISearchCache:
    """Cache for AI search results to make it fast"""
    def __init__(self):
        if 'ai_cache' not in st.session_state:
            st.session_state.ai_cache = {}
        self.cache = st.session_state.ai_cache

    def get_key(self, text):
        """Create cache key from text"""
        return hashlib.md5(text.lower().strip().encode()).hexdigest()

    def get(self, text):
        """Get cached result"""
        key = self.get_key(text)
        return self.cache.get(key)

    def set(self, text, category):
        """Cache result"""
        key = self.get_key(text)
        self.cache[key] = category


class AIProductCategorizer:
    """AI Agent that uses web search to categorize ambiguous products"""

    def __init__(self):
        self.cache = AISearchCache()

        # Category indicators from web search
        self.category_indicators = {
            'Fans': ['fan', 'cooling', 'ventilation', 'airflow', 'blower', 'ventilator', 'cfm'],
            'Lighting': ['light', 'lamp', 'bulb', 'led', 'illumination', 'fixture', 'lumens'],
            'Furniture': ['furniture', 'chair', 'table', 'desk', 'cabinet', 'sofa', 'seat'],
            'Decor': ['decor', 'decoration', 'ornament', 'vase', 'mirror', 'art', 'accent'],
            'Electronics': ['electronic', 'device', 'gadget', 'appliance', 'tech', 'digital'],
            'Kitchen': ['kitchen', 'cookware', 'utensil', 'appliance', 'cooking', 'chef'],
            'Bathroom': ['bathroom', 'toilet', 'sink', 'shower', 'bath', 'vanity'],
            'Outdoor': ['outdoor', 'patio', 'garden', 'lawn', 'bbq', 'exterior'],
            'Hardware': ['hardware', 'tool', 'screw', 'bolt', 'fastener', 'hinge'],
            'Plumbing': ['plumbing', 'pipe', 'faucet', 'valve', 'drain', 'water'],
            'Electrical': ['electrical', 'wire', 'cable', 'outlet', 'switch', 'circuit']
        }

    def search_web(self, query):
        """Search web using DuckDuckGo (free, no API key needed)"""
        try:
            # Use DuckDuckGo HTML search
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            return response.text.lower()
        except:
            return ""

    def categorize_with_ai(self, product_text, possible_categories):
        """
        Use web search to determine product category.
        Returns best category from possible_categories.
        """
        if not product_text or not possible_categories:
            return None

        # Check cache first (for speed)
        cached = self.cache.get(product_text)
        if cached and cached in possible_categories:
            return cached

        try:
            # Create search query
            search_query = f"{product_text} product category"

            # Search web
            search_text = self.search_web(search_query)

            if not search_text:
                return None

            # Score each possible category
            best_category = None
            best_score = 0

            for category in possible_categories:
                score = 0
                indicators = self.category_indicators.get(category, [])

                for indicator in indicators:
                    count = search_text.count(indicator.lower())
                    score += count * 10

                # Bonus for exact category name match
                if category.lower() in search_text:
                    score += 50

                if score > best_score:
                    best_score = score
                    best_category = category

            # Cache the result
            if best_category and best_score > 20:
                self.cache.set(product_text, best_category)
                return best_category

            return None

        except Exception as e:
            return None


class UltraAccurateDetector:
    """Ultra accurate detector with AI assistance"""

    def __init__(self):
        self.ai_categorizer = AIProductCategorizer()

        # COMPREHENSIVE KEYWORDS - organized by category
        self.categories = {
            'Fans': {
                'keywords': [
                    'fan', 'fans', 'ceiling fan', 'table fan', 'wall fan', 'floor fan', 
                    'exhaust fan', 'ventilator', 'blower', 'cooling fan', 'pedestal fan',
                    'tower fan', 'stand fan', 'desk fan', 'box fan', 'window fan',
                    'attic fan', 'bathroom fan', 'kitchen fan', 'inline fan',
                    'centrifugal fan', 'axial fan', 'ventilation fan', 'air circulator',
                    'extractor fan', 'circulation fan', 'oscillating fan', 'industrial fan',
                    'portable fan', 'rechargeable fan', 'solar fan', 'battery fan',
                    'usb fan', 'mini fan', 'personal fan', 'neck fan', 'handheld fan',
                    'clip fan', 'bracket fan', 'duct fan', 'booster fan', 'pressure fan',
                    'suction fan', 'supply fan', 'return fan', 'spot cooler', 'swamp cooler',
                    'fan blade', 'fan motor', 'fan guard', 'fan cage', 'fan controller',
                    'fan speed', 'fan switch', 'fan timer', 'fan remote', 'fan downrod',
                    'fan canopy', 'ventilation grille', 'air vent', 'air register',
                    'vent cover', 'vent cap', 'vent hood', 'range hood', 'cooker hood',
                    'extractor hood', 'fume hood', 'louver', 'cfm', 'airflow'
                ],
                'exclude': ['light', 'lamp', 'bulb', 'led', 'chandelier', 'pendant'],
                'context_keywords': ['cooling', 'ventilation', 'air', 'breeze', 'wind']
            },

            'Lighting': {
                'keywords': [
                    'light', 'lights', 'lamp', 'lamps', 'bulb', 'bulbs', 'lighting',
                    'led', 'led light', 'fixture', 'chandelier', 'pendant', 'downlight',
                    'spotlight', 'track light', 'ceiling light', 'wall light', 'floor lamp',
                    'table lamp', 'desk lamp', 'reading lamp', 'bedside lamp', 'night light',
                    'accent light', 'task light', 'crystal chandelier', 'mini chandelier',
                    'island pendant', 'flush mount', 'semi flush', 'recessed light',
                    'can light', 'pot light', 'gimbal light', 'wall sconce', 'vanity light',
                    'mirror light', 'picture light', 'uplight', 'torchiere', 'arc lamp',
                    'tripod lamp', 'led strip', 'rope light', 'neon light', 'flood light',
                    'security light', 'motion light', 'solar light', 'garden light',
                    'path light', 'bollard light', 'well light', 'high bay', 'low bay',
                    'warehouse light', 'shop light', 'emergency light', 'exit sign',
                    'grow light', 'black light', 'uv light', 'smart light', 'dimmable',
                    'edison bulb', 'filament bulb', 'halogen', 'fluorescent', 'tube light',
                    'candle bulb', 'globe bulb', 'gu10', 'mr16', 'e26', 'e27',
                    'light switch', 'dimmer', 'ballast', 'transformer', 'lumens', 'watt'
                ],
                'exclude': ['fan', 'ventilator', 'blower', 'exhaust', 'cooling'],
                'context_keywords': ['illumination', 'bright', 'glow', 'shine', 'beam']
            },

            'Furniture': {
                'keywords': [
                    'furniture', 'chair', 'chairs', 'table', 'tables', 'desk', 'desks',
                    'cabinet', 'cabinets', 'shelf', 'shelves', 'sofa', 'sofas', 'couch',
                    'couches', 'bed', 'beds', 'wardrobe', 'dresser', 'drawer', 'bookcase',
                    'stool', 'stools', 'bench', 'benches', 'ottoman', 'armchair',
                    'dining chair', 'office chair', 'executive chair', 'gaming chair',
                    'dining table', 'coffee table', 'side table', 'end table', 'console table',
                    'computer desk', 'writing desk', 'standing desk', 'filing cabinet',
                    'storage cabinet', 'tv stand', 'media unit', 'entertainment center',
                    'sectional', 'loveseat', 'recliner', 'nightstand', 'headboard',
                    'credenza', 'buffet', 'hutch', 'sideboard', 'armoire', 'futon',
                    'daybed', 'bunk bed', 'trundle bed', 'vanity', 'dressing table'
                ],
                'exclude': [],
                'context_keywords': ['seat', 'storage', 'surface', 'support']
            },

            'Decor': {
                'keywords': [
                    'decor', 'decoration', 'ornament', 'vase', 'frame', 'mirror',
                    'wall art', 'sculpture', 'statue', 'figurine', 'candle', 'planter',
                    'centerpiece', 'tapestry', 'clock', 'pillow', 'cushion', 'rug',
                    'carpet', 'mat', 'curtain', 'drape', 'wreath', 'garland', 'basket',
                    'tray', 'bowl', 'artificial plant', 'wall sticker', 'wallpaper'
                ],
                'exclude': [],
                'context_keywords': ['decorative', 'display', 'accent', 'aesthetic']
            },

            'Electronics': {
                'keywords': [
                    'electronic', 'tv', 'television', 'monitor', 'display', 'speaker',
                    'computer', 'pc', 'laptop', 'printer', 'scanner', 'router', 'modem',
                    'camera', 'webcam', 'projector', 'soundbar', 'keyboard', 'mouse',
                    'headphones', 'earbuds', 'smartphone', 'tablet', 'charger', 'cable'
                ],
                'exclude': [],
                'context_keywords': ['device', 'digital', 'smart', 'wireless']
            },

            'Kitchen': {
                'keywords': [
                    'kitchen', 'cookware', 'utensil', 'pot', 'pan', 'plate', 'dish',
                    'bowl', 'cup', 'glass', 'mug', 'cutlery', 'knife', 'fork', 'spoon',
                    'microwave', 'oven', 'stove', 'refrigerator', 'fridge', 'dishwasher',
                    'blender', 'mixer', 'toaster', 'kettle', 'coffee maker', 'pantry'
                ],
                'exclude': [],
                'context_keywords': ['cooking', 'food', 'meal', 'chef']
            },

            'Bathroom': {
                'keywords': [
                    'bathroom', 'toilet', 'sink', 'basin', 'faucet', 'tap', 'shower',
                    'bathtub', 'tub', 'jacuzzi', 'vanity', 'medicine cabinet',
                    'towel rack', 'soap dispenser', 'bath mat', 'shower curtain'
                ],
                'exclude': [],
                'context_keywords': ['wash', 'bath', 'hygiene', 'plumbing']
            },

            'Outdoor': {
                'keywords': [
                    'outdoor', 'patio', 'garden', 'lawn', 'deck', 'gazebo', 'pergola',
                    'patio furniture', 'garden furniture', 'umbrella', 'grill', 'bbq',
                    'fire pit', 'outdoor heater', 'garden light', 'planter', 'hammock'
                ],
                'exclude': [],
                'context_keywords': ['exterior', 'yard', 'backyard', 'landscape']
            },

            'Hardware': {
                'keywords': [
                    'hardware', 'tool', 'drill', 'saw', 'hammer', 'screw', 'bolt',
                    'nut', 'washer', 'nail', 'hinge', 'handle', 'lock', 'chain'
                ],
                'exclude': [],
                'context_keywords': ['fastener', 'fixture', 'fitting']
            },

            'Plumbing': {
                'keywords': [
                    'plumbing', 'pipe', 'fitting', 'valve', 'faucet', 'drain',
                    'trap', 'water heater', 'pump', 'toilet', 'sewer', 'hose'
                ],
                'exclude': [],
                'context_keywords': ['water', 'flow', 'pressure', 'leak']
            },

            'Electrical': {
                'keywords': [
                    'electrical', 'wire', 'cable', 'outlet', 'switch', 'breaker',
                    'panel', 'conduit', 'bulb', 'extension cord', 'surge protector'
                ],
                'exclude': [],
                'context_keywords': ['power', 'current', 'voltage', 'circuit']
            }
        }

    def clean_text(self, text):
        """Clean text for matching"""
        if pd.isna(text) or text is None:
            return ""
        text = str(text).lower().strip()
        for char in '-_/\|,.;:+=()[]{}':
            text = text.replace(char, ' ')
        text = ' '.join(text.split())
        return text

    def detect_category(self, row_text, enabled_categories, use_ai=False):
        """
        Detect category from combined row text.
        Returns (category, confidence_score, method)
        """
        if not row_text:
            return None, 0, 'none'

        text = ' ' + self.clean_text(row_text) + ' '

        # Score each category
        category_scores = {}

        for cat in enabled_categories:
            if cat not in self.categories:
                continue

            cat_data = self.categories[cat]

            # Check exclusions first
            excluded = False
            for excl in cat_data.get('exclude', []):
                if f' {excl} ' in text:
                    excluded = True
                    break

            if excluded:
                continue

            # Count keyword matches
            score = 0
            matched_keywords = []

            for kw in cat_data['keywords']:
                kw_pattern = f' {kw} '

                # Exact word match (highest score)
                if kw_pattern in text:
                    count = text.count(kw_pattern)
                    score += count * 25
                    matched_keywords.append(kw)
                # Partial match (lower score)
                elif kw in text:
                    score += 5
                    matched_keywords.append(kw)

            if score > 0:
                category_scores[cat] = {
                    'score': score,
                    'keywords': matched_keywords
                }

        # If no matches, return None
        if not category_scores:
            return None, 0, 'none'

        # Get best category
        best_cat = max(category_scores.keys(), key=lambda k: category_scores[k]['score'])
        best_score = category_scores[best_cat]['score']

        # Check if we need AI assistance (ambiguous case)
        sorted_scores = sorted(category_scores.items(), key=lambda x: x[1]['score'], reverse=True)

        needs_ai = False
        if best_score < 30:  # Low confidence
            needs_ai = True
        elif len(sorted_scores) > 1:
            second_score = sorted_scores[1][1]['score']
            if second_score > best_score * 0.7:  # Within 70% of best
                needs_ai = True

        # Use AI for ambiguous cases
        if use_ai and needs_ai:
            ai_category = self.ai_categorizer.categorize_with_ai(row_text, enabled_categories)
            if ai_category:
                return ai_category, best_score, 'ai_verified'

        return best_cat, best_score, 'keyword_match'

    def process_file(self, file, sheet_name, header_row, enabled_categories, use_ai=False):
        """Process file with optional AI assistance"""
        try:
            # Read with header row
            if header_row > 0:
                df = pd.read_excel(file, sheet_name=sheet_name, header=header_row)
            else:
                df = pd.read_excel(file, sheet_name=sheet_name)

            if df.empty:
                return {}, {'total_rows': 0, 'matched': 0, 'unmatched': 0, 'ai_verified': 0}

            # Add result columns
            df['Category'] = None
            df['Confidence'] = 0
            df['Method'] = None

            # Progress
            progress_bar = st.progress(0)
            status = st.empty()

            ai_count = 0

            for idx in df.index:
                if idx % 25 == 0:
                    progress = (idx + 1) / len(df)
                    progress_bar.progress(min(progress, 1.0))
                    status.text(f"Processing {idx + 1} of {len(df)}...")

                # Combine all text from row
                row_text = ' '.join([str(v) for v in df.loc[idx] if pd.notna(v)])

                cat, conf, method = self.detect_category(row_text, enabled_categories, use_ai)

                if cat:
                    df.at[idx, 'Category'] = cat
                    df.at[idx, 'Confidence'] = conf
                    df.at[idx, 'Method'] = method
                    if method == 'ai_verified':
                        ai_count += 1

            progress_bar.empty()
            status.empty()

            # Handle unmatched
            unmatched = df[df['Category'].isna()].index
            if len(unmatched) > 0 and enabled_categories:
                st.warning(f"{len(unmatched)} unmatched rows - using fallback...")
                for i, idx in enumerate(unmatched):
                    df.at[idx, 'Category'] = enabled_categories[i % len(enabled_categories)]
                    df.at[idx, 'Method'] = 'fallback'

            # Separate by category
            separated = {}
            original_cols = [c for c in df.columns if c not in ['Category', 'Confidence', 'Method']]

            for cat in enabled_categories:
                cat_data = df[df['Category'] == cat][original_cols].copy()
                if len(cat_data) > 0:
                    separated[cat] = cat_data

            stats = {
                'total_rows': len(df),
                'matched': len(df[df['Method'] == 'keyword_match']),
                'ai_verified': ai_count,
                'fallback': len(df[df['Method'] == 'fallback']),
                'categories_found': len(separated),
                'distribution': df['Category'].value_counts().to_dict()
            }

            return separated, stats

        except Exception as e:
            st.error(f"Error: {str(e)}")
            return {}, {'total_rows': 0, 'matched': 0, 'ai_verified': 0, 'fallback': 0}


def get_sheet_info(file):
    try:
        wb = load_workbook(file, read_only=True, data_only=False)
        sheets = [{'name': name, 'rows': wb[name].max_row or 0, 'cols': wb[name].max_column or 0} 
                  for name in wb.sheetnames]
        wb.close()
        return sheets
    except:
        return []


def preview_data(file, sheet_name, header_row, num_rows=5):
    """Preview data with header row selection"""
    try:
        if header_row > 0:
            df = pd.read_excel(file, sheet_name=sheet_name, header=header_row, nrows=num_rows)
        else:
            df = pd.read_excel(file, sheet_name=sheet_name, nrows=num_rows)
        return df
    except Exception as e:
        return None


def create_excel(df):
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
            from openpyxl.styles import Font, PatternFill, Alignment
            ws = writer.sheets['Data']
            hf = PatternFill(start_color='667eea', end_color='667eea', fill_type='solid')
            for cell in ws[1]:
                cell.fill = hf
                cell.font = Font(color='FFFFFF', bold=True)
        output.seek(0)
        return output.getvalue()
    except:
        return None


def main():
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">Data Separation Tool - AI Powered</h1>
        <p class="hero-subtitle">Smart Detection with Web Search Verification</p>
        <span class="hero-badge">100% Accuracy Goal</span>
    </div>
    """, unsafe_allow_html=True)

    # Init session state
    if 'detector' not in st.session_state:
        st.session_state.detector = UltraAccurateDetector()
    if 'processed' not in st.session_state:
        st.session_state.processed = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'selected_cats' not in st.session_state:
        st.session_state.selected_cats = ['Lighting', 'Fans']

    # STEP 1: Upload
    st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">1</span>Upload File</h3>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=['xlsx', 'xlsm', 'xls'], label_visibility="collapsed")

    if uploaded:
        st.markdown('<div class="success-box">File uploaded successfully</div>', unsafe_allow_html=True)

        sheets = get_sheet_info(uploaded)
        if sheets:
            opts = [f"{s['name']} ({s['rows']} rows)" for s in sheets]
            sel = st.selectbox("Select sheet:", opts)
            st.session_state.sheet = sheets[opts.index(sel)]['name']
            st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')

    st.markdown('</div>', unsafe_allow_html=True)

    # STEP 2: Header Row Selection
    if uploaded:
        st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">2</span>Select Header Row</h3>', unsafe_allow_html=True)

        header_row = st.number_input(
            "Row number containing column headers (0 = first row):",
            min_value=0, max_value=10, value=0, step=1
        )

        # Preview
        st.caption("Preview of data with selected header row:")
        preview_df = preview_data(uploaded, st.session_state.sheet, header_row)
        if preview_df is not None:
            st.dataframe(preview_df, use_container_width=True)

        st.session_state.header_row = header_row
        st.markdown('</div>', unsafe_allow_html=True)

    # STEP 3: Categories
    if uploaded:
        st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">3</span>Select Categories</h3>', unsafe_allow_html=True)

        all_cats = list(st.session_state.detector.categories.keys())

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Select All", use_container_width=True):
                st.session_state.selected_cats = all_cats.copy()
                st.rerun()
        with c2:
            if st.button("Clear All", use_container_width=True):
                st.session_state.selected_cats = []
                st.rerun()

        cols = st.columns(4)
        selected = []
        for i, cat in enumerate(all_cats):
            with cols[i % 4]:
                if st.checkbox(cat, value=cat in st.session_state.selected_cats, key=f"cat_{cat}"):
                    selected.append(cat)

        st.session_state.selected_cats = selected

        # AI Option
        use_ai = st.checkbox("Use AI Web Search for ambiguous items (slower but more accurate)", value=False)
        st.session_state.use_ai = use_ai

        if use_ai:
            st.markdown('<div class="ai-box">AI will search the web for items with low confidence or multiple possible categories</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # STEP 4: Process
    if uploaded and st.session_state.selected_cats:
        st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">4</span>Process Data</h3>', unsafe_allow_html=True)

        if st.button("Start Processing", type="primary", use_container_width=True):
            with st.spinner('Processing...'):
                uploaded.seek(0)
                separated, stats = st.session_state.detector.process_file(
                    uploaded,
                    st.session_state.sheet,
                    st.session_state.header_row,
                    st.session_state.selected_cats,
                    st.session_state.get('use_ai', False)
                )
                st.session_state.processed = separated
                st.session_state.stats = stats
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # RESULTS
    if st.session_state.processed is not None:
        stats = st.session_state.stats

        # Stats
        st.markdown('<div class="stat-container">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["total_rows"]}</div><div class="stat-label">Total</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["matched"]}</div><div class="stat-label">Keyword Match</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["ai_verified"]}</div><div class="stat-label">AI Verified</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["fallback"]}</div><div class="stat-label">Fallback</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Distribution
        st.markdown('<div class="premium-card"><h3 class="card-title">Category Distribution</h3>', unsafe_allow_html=True)
        for cat, count in stats['distribution'].items():
            if cat:
                pct = (count / stats['total_rows'] * 100) if stats['total_rows'] > 0 else 0
                st.markdown(f'<div class="distribution-item"><span><strong>{cat}</strong></span><span>{count} items ({pct:.1f}%)</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Downloads
        st.markdown('<div class="premium-card"><h3 class="card-title">Download Files</h3>', unsafe_allow_html=True)
        dl_cols = st.columns(min(len(st.session_state.processed), 4))
        for idx, (cat, data) in enumerate(st.session_state.processed.items()):
            with dl_cols[idx % 4]:
                excel = create_excel(data)
                if excel:
                    st.download_button(
                        f"{cat} ({len(data)})",
                        excel,
                        f"{st.session_state.filename}_{cat}.xlsx",
                        use_container_width=True,
                        key=f"dl_{cat}"
                    )
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
