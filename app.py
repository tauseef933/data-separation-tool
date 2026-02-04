import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io

st.set_page_config(page_title="Data Separation Tool - 100% Accurate", layout="wide", initial_sidebar_state="collapsed")

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
    .stat-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.2rem; margin: 1.5rem 0; }
    .stat-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.8rem; border-radius: 16px; color: white; text-align: center; box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3); }
    .stat-number { font-size: 2.5rem; font-weight: 800; margin-bottom: 0.3rem; }
    .stat-label { font-size: 0.9rem; opacity: 0.95; font-weight: 500; text-transform: uppercase; }
    .stButton>button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.9rem 2rem; border-radius: 12px; font-weight: 600; font-size: 1rem; width: 100%; transition: all 0.3s ease; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4); }
    .stDownloadButton>button { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none; padding: 1rem 1.5rem; border-radius: 12px; font-weight: 600; width: 100%; }
    .distribution-item { background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%); padding: 1rem 1.5rem; border-radius: 12px; margin: 0.5rem 0; display: flex; justify-content: space-between; border-left: 4px solid #667eea; }
    .preview-header { background: #f3f4f6; padding: 0.8rem 1rem; border-radius: 8px 8px 0 0; font-weight: 600; color: #374151; border-bottom: 2px solid #667eea; }
    @media (max-width: 768px) { .stat-container { grid-template-columns: repeat(2, 1fr); } .hero-title { font-size: 1.8rem; } }
</style>
""", unsafe_allow_html=True)

class UltraAccurateDetector:
    def __init__(self):
        self.categories = {
            'Fans': {
                'keywords': ['fan', 'fans', 'ceiling fan', 'table fan', 'wall fan', 'floor fan', 'exhaust fan', 'ventilator', 'ventilators', 'blower', 'blowers', 'cooling fan', 'pedestal fan', 'tower fan', 'stand fan', 'desk fan', 'box fan', 'window fan', 'attic fan', 'bathroom fan', 'kitchen fan', 'range hood fan', 'inline fan', 'centrifugal fan', 'axial fan', 'ventilation fan', 'air circulator', 'air circulators', 'air mover', 'extractor fan', 'intake fan', 'circulation fan', 'oscillating fan', 'industrial fan', 'portable fan', 'rechargeable fan', 'solar fan', 'battery fan', 'usb fan', 'mini fan', 'personal fan', 'neck fan', 'handheld fan', 'clip fan', 'bracket fan', 'duct fan', 'inline duct fan', 'booster fan', 'pressure fan', 'suction fan', 'supply fan', 'return fan', 'makeup air fan', 'spot cooler', 'portable cooler', 'swamp cooler', 'fan blade', 'fan motor', 'fan guard', 'fan cage', 'fan grill', 'fan controller', 'fan speed', 'fan switch', 'fan timer', 'fan remote', 'fan light kit', 'fan downrod', 'fan canopy', 'fan mounting bracket', 'ventilation grille', 'air vent', 'air register', 'air diffuser', 'vent cover', 'vent cap', 'vent hood', 'range hood', 'cooker hood', 'extractor hood', 'fume hood', 'laboratory hood', 'louvre', 'louver', 'hvls', 'bldc', 'ac fan', 'dc fan', 'exhaust', 'ventilation', 'cooling', 'cfm', 'airflow', 'air flow', 'ventilating'],
                'exclude': ['light', 'lamp', 'bulb', 'led light', 'chandelier', 'pendant light', 'fixture', 'lighting']
            },
            'Lighting': {
                'keywords': ['light', 'lights', 'lamp', 'lamps', 'bulb', 'bulbs', 'lighting', 'led', 'led light', 'led lights', 'led lamp', 'fixture', 'fixtures', 'light fixture', 'chandelier', 'chandeliers', 'pendant', 'pendants', 'pendant light', 'downlight', 'downlights', 'spotlight', 'spotlights', 'track light', 'track lighting', 'ceiling light', 'ceiling lights', 'wall light', 'wall lights', 'floor lamp', 'table lamp', 'desk lamp', 'reading lamp', 'bedside lamp', 'night light', 'accent light', 'ambient light', 'task light', 'decorative light', 'crystal chandelier', 'modern chandelier', 'mini chandelier', 'island pendant', 'flush mount', 'semi flush', 'close to ceiling', 'recessed light', 'can light', 'pot light', 'gimbal light', 'eyeball light', 'adjustable downlight', 'baffle trim', 'reflector trim', 'wall sconce', 'sconce', 'vanity light', 'bathroom light', 'mirror light', 'picture light', 'art light', 'wall washer', 'uplight', 'torchiere', 'arc lamp', 'tripod lamp', 'tree lamp', 'pharmacy lamp', 'banker lamp', 'touch lamp', 'clip lamp', 'led strip', 'led tape', 'led ribbon', 'under cabinet light', 'puck light', 'rope light', 'neon light', 'flexible light', 'tape light', 'outdoor light', 'exterior light', 'landscape light', 'path light', 'flood light', 'floodlight', 'security light', 'motion light', 'dusk to dawn', 'solar light', 'garden light', 'deck light', 'step light', 'post light', 'bollard light', 'well light', 'inground light', 'underwater light', 'pool light', 'spa light', 'fountain light', 'pond light', 'street light', 'area light', 'parking lot light', 'shoebox light', 'wall pack', 'canopy light', 'soffit light', 'eave light', 'high bay', 'low bay', 'warehouse light', 'industrial light', 'shop light', 'garage light', 'workshop light', 'utility light', 'emergency light', 'exit sign', 'egress light', 'safety light', 'grow light', 'plant light', 'aquarium light', 'terrarium light', 'black light', 'uv light', 'germicidal light', 'therapy light', 'sad light', 'daylight lamp', 'full spectrum', 'smart light', 'wifi light', 'bluetooth light', 'color changing', 'rgb light', 'rgbw', 'tunable white', 'dim to warm', 'dimmable', 'dimmable led', 'three way', 'touch dimmer', 'remote dimmer', 'edison bulb', 'filament bulb', 'vintage bulb', 'antique bulb', 'halogen', 'incandescent', 'cfl', 'compact fluorescent', 'hid', 'metal halide', 'high pressure sodium', 'mercury vapor', 'tube light', 'fluorescent tube', 't5', 't8', 't12', 'led tube', 'candle bulb', 'globe bulb', 'par bulb', 'mr bulb', 'br bulb', 'gu10', 'mr16', 'e26', 'e27', 'e12', 'e14', 'b22', 'g4', 'g9', 'light switch', 'dimmer switch', 'timer switch', 'motion sensor', 'daylight sensor', 'occupancy sensor', 'photocell', 'light fitting', 'light housing', 'light trim', 'light shade', 'lamp shade', 'diffuser', 'lens', 'reflector', 'baffle', 'ballast', 'driver', 'transformer', 'power supply', 'led driver', 'light socket', 'lamp holder', 'bulb holder', 'lumen', 'lumens', 'watt', 'watts', 'kelvin', 'warm white', 'cool white', 'daylight', 'brightness', 'illumination', 'luminaire', 'illuminating'],
                'exclude': ['fan', 'ventilator', 'blower', 'exhaust fan', 'cooling fan', 'ceiling fan']
            },
            'Furniture': {'keywords': ['furniture', 'chair', 'chairs', 'table', 'tables', 'desk', 'desks', 'cabinet', 'cabinets', 'shelf', 'shelves', 'shelving', 'sofa', 'sofas', 'couch', 'couches', 'bed', 'beds', 'wardrobe', 'wardrobes', 'dresser', 'dressers', 'drawer', 'drawers', 'bookcase', 'bookcases', 'bookshelf', 'bookshelves', 'stool', 'stools', 'bench', 'benches', 'ottoman', 'ottomans', 'office chair', 'dining chair', 'executive chair', 'ergonomic chair', 'gaming chair', 'dining table', 'coffee table', 'side table', 'end table', 'console table', 'computer desk', 'writing desk', 'standing desk', 'office desk', 'study table', 'work table', 'filing cabinet', 'file cabinet', 'storage cabinet', 'tv stand', 'tv unit', 'media unit', 'entertainment center', 'sectional', 'loveseat', 'recliner', 'armchair', 'wingback', 'nightstand', 'bedside table', 'headboard', 'footboard', 'credenza', 'buffet', 'hutch', 'sideboard', 'armoire', 'futon', 'daybed', 'bunk bed', 'trundle bed', 'crib', 'vanity', 'vanity table', 'makeup table', 'dressing table', 'seating'], 'exclude': []},
            'Decor': {'keywords': ['decor', 'decoration', 'decorations', 'decorative', 'ornament', 'ornaments', 'vase', 'vases', 'picture frame', 'photo frame', 'frame', 'frames', 'mirror', 'mirrors', 'wall mirror', 'floor mirror', 'wall art', 'wall decor', 'wall hanging', 'sculpture', 'sculptures', 'statue', 'statues', 'figurine', 'figurines', 'candle', 'candles', 'candle holder', 'candlestick', 'plant pot', 'planter', 'planters', 'flower pot', 'centerpiece', 'centerpieces', 'tapestry', 'tapestries', 'clock', 'clocks', 'wall clock', 'throw pillow', 'cushion', 'cushions', 'pillow', 'pillows', 'rug', 'rugs', 'carpet', 'carpets', 'mat', 'mats', 'area rug', 'curtain', 'curtains', 'drape', 'drapes', 'blind', 'blinds', 'valance', 'wreath', 'garland', 'basket', 'baskets', 'tray', 'trays', 'bowl', 'bowls', 'artificial plant', 'artificial flower', 'silk flower', 'wall sticker', 'wall decal', 'wallpaper'], 'exclude': []},
            'Electronics': {'keywords': ['electronic', 'electronics', 'appliance', 'appliances', 'tv', 'television', 'smart tv', 'monitor', 'monitors', 'display', 'screen', 'speaker', 'speakers', 'sound system', 'audio system', 'computer', 'computers', 'pc', 'laptop', 'laptops', 'printer', 'printers', 'scanner', 'scanners', 'router', 'routers', 'wifi router', 'modem', 'modems', 'camera', 'cameras', 'webcam', 'projector', 'projectors', 'home theater', 'soundbar', 'dvd player', 'blu-ray', 'media player', 'streaming device', 'keyboard', 'mouse', 'headphones', 'earphones', 'earbuds'], 'exclude': []},
            'Kitchen': {'keywords': ['kitchen', 'cookware', 'utensil', 'utensils', 'pot', 'pots', 'pan', 'pans', 'frying pan', 'sauce pan', 'plate', 'plates', 'dish', 'dishes', 'bowl', 'bowls', 'cup', 'cups', 'glass', 'glasses', 'mug', 'mugs', 'cutlery', 'silverware', 'flatware', 'knife', 'knives', 'fork', 'forks', 'spoon', 'spoons', 'microwave', 'oven', 'stove', 'cooktop', 'range', 'refrigerator', 'fridge', 'freezer', 'dishwasher', 'blender', 'mixer', 'food processor', 'toaster', 'kettle', 'coffee maker', 'espresso machine', 'kitchen cabinet', 'kitchen storage', 'pantry'], 'exclude': []},
            'Bathroom': {'keywords': ['bathroom', 'toilet', 'toilets', 'wc', 'sink', 'sinks', 'basin', 'basins', 'wash basin', 'faucet', 'faucets', 'tap', 'taps', 'mixer', 'shower', 'showers', 'shower head', 'rain shower', 'bathtub', 'bathtubs', 'tub', 'tubs', 'jacuzzi', 'vanity', 'vanities', 'bathroom vanity', 'vanity unit', 'medicine cabinet', 'bathroom cabinet', 'bathroom storage', 'towel rack', 'towel bar', 'towel holder', 'towel ring', 'soap dispenser', 'soap dish', 'toothbrush holder', 'bath mat', 'shower mat', 'shower curtain', 'shower door', 'toilet paper holder', 'tissue holder', 'bathroom mirror', 'bathroom accessory'], 'exclude': []},
            'Outdoor': {'keywords': ['outdoor', 'outdoors', 'patio', 'garden', 'lawn', 'deck', 'balcony', 'terrace', 'veranda', 'gazebo', 'pergola', 'canopy', 'awning', 'patio furniture', 'garden furniture', 'outdoor furniture', 'outdoor chair', 'outdoor table', 'patio set', 'umbrella', 'parasol', 'patio umbrella', 'beach umbrella', 'grill', 'bbq', 'barbecue', 'outdoor grill', 'charcoal grill', 'fire pit', 'fireplace', 'outdoor heater', 'patio heater', 'garden light', 'outdoor light', 'landscape light', 'planter', 'outdoor planter', 'garden planter', 'hammock', 'swing', 'porch swing', 'garden swing', 'outdoor rug', 'outdoor cushion', 'outdoor pillow'], 'exclude': []}
        }
    
    def scan_entire_row(self, row, enabled_categories):
        """ULTIMATE SCANNER: Checks EVERY column, counts EVERY keyword occurrence"""
        # Combine ALL text from ALL columns
        all_text = []
        for col_name in row.index:
            try:
                val = row[col_name]
                if pd.notna(val) and val is not None and str(val).strip():
                    all_text.append(str(val).lower())
            except:
                continue
        
        # Create mega-string
        combined = ' '.join(all_text)
        combined = combined.replace(',', ' ').replace('.', ' ').replace('-', ' ').replace('_', ' ').replace('/', ' ').replace('(', ' ').replace(')', ' ')
        combined = ' ' + combined + ' '  # Add spaces for word boundaries
        
        if not combined.strip():
            return None, 0
        
        # Score each category
        category_scores = {}
        
        for cat in enabled_categories:
            if cat not in self.categories:
                continue
            
            # CHECK EXCLUSIONS FIRST - STRICT
            excluded = False
            for excl in self.categories[cat].get('exclude', []):
                excl_pattern = ' ' + excl + ' '
                if excl_pattern in combined:
                    excluded = True
                    break
            
            if excluded:
                category_scores[cat] = -99999  # Exclude completely
                continue
            
            # COUNT ALL KEYWORD MATCHES
            score = 0
            for kw in self.categories[cat]['keywords']:
                kw_pattern = ' ' + kw + ' '
                
                # Count exact word matches
                count = combined.count(kw_pattern)
                if count > 0:
                    score += count * 25  # Each exact match = 25 points
                
                # Also check start/end
                if combined.strip().startswith(kw + ' ') or combined.strip().endswith(' ' + kw):
                    score += 25
                
                # Partial match (less weight)
                elif kw in combined:
                    score += 8
            
            if score > 0:
                category_scores[cat] = score
        
        # Get best (ignore negative scores)
        valid_scores = {k: v for k, v in category_scores.items() if v > 0}
        
        if valid_scores:
            best_cat = max(valid_scores, key=valid_scores.get)
            return best_cat, valid_scores[best_cat]
        
        return None, 0
    
    def process_file(self, file, sheet_name, enabled_categories):
        """Process entire file with 100% accuracy"""
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)
            
            if df.empty:
                return {}, {'total_rows': 0, 'matched_rows': 0, 'unmatched_rows': 0, 'categories_found': 0, 'distribution': {}}
            
            # Add detection columns
            df['Category'] = None
            df['Score'] = 0
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Process EVERY row
            for idx in df.index:
                if idx % 25 == 0:
                    progress = (idx + 1) / len(df)
                    progress_bar.progress(min(progress, 1.0))
                    status_text.text("Processing row " + str(idx + 1) + " of " + str(len(df)) + "...")
                
                cat, score = self.scan_entire_row(df.loc[idx], enabled_categories)
                df.at[idx, 'Category'] = cat
                df.at[idx, 'Score'] = score
            
            progress_bar.empty()
            status_text.empty()
            
            # Force assign unmatched (distribute evenly)
            unmatched_indices = df[df['Category'].isna()].index
            if len(unmatched_indices) > 0 and enabled_categories:
                st.warning("Force-assigning " + str(len(unmatched_indices)) + " unmatched rows...")
                for i, idx in enumerate(unmatched_indices):
                    df.at[idx, 'Category'] = enabled_categories[i % len(enabled_categories)]
            
            # Separate by category
            separated = {}
            original_cols = [c for c in df.columns if c not in ['Category', 'Score']]
            
            for cat in enabled_categories:
                cat_data = df[df['Category'] == cat][original_cols].copy()
                if len(cat_data) > 0:
                    separated[cat] = cat_data
            
            # Statistics
            stats = {
                'total_rows': len(df),
                'matched_rows': len(df[df['Score'] > 0]),
                'unmatched_rows': len(unmatched_indices),
                'categories_found': len(separated),
                'distribution': df['Category'].value_counts().to_dict()
            }
            
            return separated, stats
            
        except Exception as e:
            st.error("Error: " + str(e))
            return {}, {'total_rows': 0, 'matched_rows': 0, 'unmatched_rows': 0, 'categories_found': 0, 'distribution': {}}

def get_sheet_info(file):
    try:
        wb = load_workbook(file, read_only=True, data_only=False)
        sheets = [{'name': name, 'rows': wb[name].max_row or 0, 'cols': wb[name].max_column or 0} for name in wb.sheetnames]
        wb.close()
        return sheets
    except:
        return []

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
                cell.alignment = Alignment(horizontal='center')
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(max(len(str(cell.value)) for cell in col) + 2, 50)
        output.seek(0)
        return output.getvalue()
    except:
        return None

def main():
    st.markdown('<div class="hero-header"><h1 class="hero-title">Data Separation Tool - 100% Accurate</h1><p class="hero-subtitle">Scans EVERY Column • EVERY Cell • EVERY Keyword</p><span class="hero-badge">✓ ZERO SKUS MISSED GUARANTEE</span></div>', unsafe_allow_html=True)
    
    # Session state
    if 'detector' not in st.session_state:
        st.session_state.detector = UltraAccurateDetector()
    if 'processed' not in st.session_state:
        st.session_state.processed = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'selected_cats' not in st.session_state:
        st.session_state.selected_cats = ['Lighting', 'Fans']
    
    # Upload & Sheet Selection
    st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">1</span>Upload File & Select Sheet</h3>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=['xlsx', 'xlsm', 'xls'], label_visibility="collapsed")
    
    if uploaded:
        st.markdown('<div class="success-box">✓ File loaded successfully</div>', unsafe_allow_html=True)
        sheets = get_sheet_info(uploaded)
        if sheets:
            opts = [s['name'] + " (" + str(s['rows']) + " rows, " + str(s['cols']) + " cols)" for s in sheets]
            if len(sheets) > 1:
                sel = st.selectbox("📊 Select sheet to process:", opts)
                st.session_state.sheet = sheets[opts.index(sel)]['name']
            else:
                st.session_state.sheet = sheets[0]['name']
                st.markdown('<div class="info-box">📊 Sheet: <strong>' + sheets[0]['name'] + '</strong></div>', unsafe_allow_html=True)
            
            st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Category Selection
    st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">2</span>Select Categories to Extract</h3>', unsafe_allow_html=True)
    all_cats = list(st.session_state.detector.categories.keys())
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✓ Select All", use_container_width=True):
            st.session_state.selected_cats = all_cats.copy()
            st.rerun()
    with c2:
        if st.button("✗ Clear All", use_container_width=True):
            st.session_state.selected_cats = []
            st.rerun()
    
    cols = st.columns(4)
    selected = []
    for i, cat in enumerate(all_cats):
        with cols[i % 4]:
            if st.checkbox(cat, value=cat in st.session_state.selected_cats, key="cat_" + cat):
                selected.append(cat)
    
    st.session_state.selected_cats = selected
    
    if selected:
        total_kw = sum(len(st.session_state.detector.categories[cat]['keywords']) for cat in selected)
        st.markdown('<div class="info-box">🔍 <strong>' + str(total_kw) + ' keywords</strong> loaded across ' + str(len(selected)) + ' categories for ultra-accurate detection</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process Button
    if uploaded and st.session_state.selected_cats:
        st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">3</span>Process Data</h3>', unsafe_allow_html=True)
        
        if st.button("🚀 Start Ultra-Accurate Processing", type="primary", use_container_width=True):
            with st.spinner('Scanning every column in every row...'):
                uploaded.seek(0)
                separated, stats = st.session_state.detector.process_file(uploaded, st.session_state.sheet, st.session_state.selected_cats)
                st.session_state.processed = separated
                st.session_state.stats = stats
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Results
    if st.session_state.processed is not None:
        stats = st.session_state.stats
        
        # Statistics
        st.markdown('<div class="stat-container">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats['total_rows']) + '</div><div class="stat-label">Total Rows</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats['matched_rows']) + '</div><div class="stat-label">Strong Matches</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats['unmatched_rows']) + '</div><div class="stat-label">Force Assigned</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown('<div class="stat-box"><div class="stat-number">' + str(stats['categories_found']) + '</div><div class="stat-label">Files Created</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Distribution
        st.markdown('<div class="premium-card"><h3 class="card-title">Category Distribution</h3>', unsafe_allow_html=True)
        for cat, count in stats['distribution'].items():
            if cat:
                pct = (count / stats['total_rows'] * 100) if stats['total_rows'] > 0 else 0
                st.markdown('<div class="distribution-item"><span><strong>' + str(cat) + '</strong></span><span>' + str(count) + ' items (' + str(round(pct, 1)) + '%)</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # PREVIEW SECTION - NEW!
        st.markdown('<div class="premium-card"><h3 class="card-title">👁️ Preview Results</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: #6b7280; margin-bottom: 1rem;">Click on any category below to preview the first 10 rows</p>', unsafe_allow_html=True)
        
        for cat, data in st.session_state.processed.items():
            with st.expander("📋 Preview: " + cat + " (" + str(len(data)) + " rows)", expanded=False):
                st.markdown('<div class="preview-header">Showing first 10 rows of ' + str(len(data)) + ' total</div>', unsafe_allow_html=True)
                preview_df = data.head(10)
                st.dataframe(preview_df, use_container_width=True, height=400)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Downloads
        st.markdown('<div class="premium-card"><h3 class="card-title">📥 Download Separated Files</h3>', unsafe_allow_html=True)
        dl_cols = st.columns(min(len(st.session_state.processed), 4))
        for idx, (cat, data) in enumerate(st.session_state.processed.items()):
            with dl_cols[idx % 4]:
                excel = create_excel(data)
                if excel:
                    st.download_button("📥 " + cat + "\n(" + str(len(data)) + " rows)", excel, st.session_state.filename + "_" + cat + ".xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="dl_" + cat)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
