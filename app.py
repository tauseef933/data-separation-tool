import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io
import re

st.set_page_config(page_title="Data Separation Tool", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * {font-family: 'Inter', sans-serif;}
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .main {background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%); padding: 1.5rem;}
    .header-box {background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 1.5rem 2rem; border-radius: 10px; margin-bottom: 1.5rem; box-shadow: 0 8px 30px rgba(0,0,0,0.12);}
    .header-title {color: #ffffff; font-size: 2rem; font-weight: 700; margin: 0;}
    .header-subtitle {color: #b8d4f1; font-size: 0.9rem; margin-top: 0.3rem;}
    .card {background: #ffffff; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 1rem;}
    .card-title {color: #1a1a1a; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.8rem; border-bottom: 2px solid #2a5298; padding-bottom: 0.5rem;}
    .info-box {background: #e3f2fd; border-left: 3px solid #1976d2; padding: 0.8rem; border-radius: 5px; margin: 0.8rem 0; font-size: 0.9rem;}
    .success-box {background: #e8f5e9; border-left: 3px solid #4caf50; padding: 0.8rem; border-radius: 5px; margin: 0.8rem 0; font-size: 0.9rem;}
    .warning-box {background: #fff3e0; border-left: 3px solid #f57c00; padding: 0.8rem; border-radius: 5px; margin: 0.8rem 0; font-size: 0.9rem;}
    .stat-box {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 8px; color: white; text-align: center;}
    .stat-number {font-size: 1.8rem; font-weight: 700;}
    .stat-label {font-size: 0.85rem; opacity: 0.9; margin-top: 0.2rem;}
    .stButton>button {background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%); color: white; border: none; padding: 0.7rem 1.5rem; border-radius: 7px; font-weight: 600; font-size: 0.95rem;}
</style>
""", unsafe_allow_html=True)

class ImprovedCategoryDetector:
    def __init__(self):
        # MUCH more specific keywords - fans separated from lighting
        self.categories = {
            'Fans': {
                # Super specific fan keywords - PRIORITY
                'must_match': ['fan', 'ventilator', 'blower', 'exhaust', 'ventilation', 'air circulator', 'cooling'],
                # These EXCLUDE it from being a fan if found
                'exclude': ['light', 'lamp', 'bulb', 'led', 'fixture', 'lighting']
            },
            'Lighting': {
                # Super specific lighting keywords - PRIORITY
                'must_match': ['light', 'lamp', 'bulb', 'lighting', 'led', 'fixture', 'chandelier', 'luminaire', 'illumination', 'lantern'],
                # These EXCLUDE it from being lighting if found
                'exclude': ['fan', 'ventilator', 'blower', 'exhaust', 'cooling']
            },
            'Furniture': {
                'must_match': ['chair', 'table', 'desk', 'cabinet', 'shelf', 'sofa', 'couch', 'bed', 'furniture', 'wardrobe', 'dresser'],
                'exclude': []
            },
            'Decor': {
                'must_match': ['decor', 'decoration', 'vase', 'mirror', 'sculpture', 'cushion', 'rug', 'carpet', 'curtain', 'decorative'],
                'exclude': []
            },
            'Electronics': {
                'must_match': ['tv', 'television', 'monitor', 'speaker', 'computer', 'laptop', 'printer', 'electronic'],
                'exclude': []
            },
            'Kitchen': {
                'must_match': ['kitchen', 'cookware', 'utensil', 'microwave', 'oven', 'refrigerator'],
                'exclude': []
            },
            'Bathroom': {
                'must_match': ['bathroom', 'toilet', 'sink', 'shower', 'bathtub'],
                'exclude': []
            },
            'Outdoor': {
                'must_match': ['outdoor', 'patio', 'garden', 'lawn', 'bbq'],
                'exclude': []
            }
        }
    
    def smart_detect(self, text, enabled_categories):
        """
        SMART DETECTION:
        1. Check if text contains any EXCLUDE keywords for a category
        2. Then check if text contains MUST_MATCH keywords
        3. Return category with highest confidence
        """
        try:
            if pd.isna(text) or text is None:
                return None, 0, "empty"
            
            text_lower = str(text).lower().strip()
            if not text_lower:
                return None, 0, "empty"
            
            # Remove special characters for better matching
            text_clean = re.sub(r'[^a-z0-9\s]', ' ', text_lower)
            
            scores = {}
            reasons = {}
            
            for category in enabled_categories:
                if category not in self.categories:
                    continue
                
                keywords = self.categories[category]
                
                # CHECK EXCLUSIONS FIRST - if any exclude keyword found, skip this category
                excluded = False
                for exclude_word in keywords.get('exclude', []):
                    if exclude_word in text_clean:
                        excluded = True
                        reasons[category] = f"excluded by '{exclude_word}'"
                        break
                
                if excluded:
                    scores[category] = -999  # Very negative score to exclude
                    continue
                
                # Check must_match keywords
                score = 0
                matched_words = []
                for keyword in keywords.get('must_match', []):
                    if keyword in text_clean:
                        score += 10
                        matched_words.append(keyword)
                
                if score > 0:
                    scores[category] = score
                    reasons[category] = f"matched: {', '.join(matched_words)}"
            
            # Get best match (ignore negative scores)
            valid_scores = {k: v for k, v in scores.items() if v > 0}
            
            if valid_scores:
                best_cat = max(valid_scores, key=valid_scores.get)
                return best_cat, valid_scores[best_cat], reasons.get(best_cat, "matched")
            
            return None, 0, "no match"
            
        except Exception as e:
            return None, 0, f"error: {str(e)}"

def get_sheet_info(file):
    """Safely get sheet information"""
    try:
        wb = load_workbook(file, read_only=True, data_only=False)
        sheets = []
        for name in wb.sheetnames:
            try:
                sheet = wb[name]
                sheets.append({
                    'name': name, 
                    'rows': sheet.max_row if sheet.max_row else 0, 
                    'cols': sheet.max_column if sheet.max_column else 0
                })
            except:
                continue
        wb.close()
        return sheets
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return []

def process_file_smart(file, sheet_name, detector, enabled_categories):
    """Process with SMART detection - proper Fan vs Lighting separation"""
    try:
        df = pd.read_excel(file, sheet_name=sheet_name)
        
        if df.empty:
            return {}, {'total_rows': 0, 'well_matched': 0, 'forced_matched': 0, 'categories_found': 0, 'distribution': {}, 'forced_assignments': [], 'match_details': []}
        
        # Add helper columns
        df['Detected_Category'] = None
        df['Match_Score'] = 0
        df['Match_Reason'] = ""
        df['Was_Forced'] = False
        
        # Find category columns
        category_cols = []
        for col in df.columns:
            try:
                col_lower = str(col).lower()
                if any(kw in col_lower for kw in ['type', 'category', 'description', 'item', 'product', 'name', 'title', 'sku']):
                    category_cols.append(col)
            except:
                continue
        
        if not category_cols:
            category_cols = [col for col in df.columns if df[col].dtype == 'object']
        
        # DETECTION PHASE - check ALL text columns together
        match_details = []
        
        for idx in df.index:
            try:
                row = df.loc[idx]
                
                # Combine ALL relevant text from the row for better detection
                all_text_parts = []
                for col in category_cols:
                    try:
                        val = row[col]
                        if pd.notna(val) and val is not None and str(val).strip():
                            all_text_parts.append(str(val))
                    except:
                        continue
                
                combined_text = ' '.join(all_text_parts)
                
                # Smart detect on combined text
                cat, score, reason = detector.smart_detect(combined_text, enabled_categories)
                
                df.at[idx, 'Detected_Category'] = cat
                df.at[idx, 'Match_Score'] = score
                df.at[idx, 'Match_Reason'] = reason
                
                # Store for debugging
                item_id = str(row[category_cols[0]])[:50] if category_cols else f"Row {idx+2}"
                match_details.append({
                    'item': item_id,
                    'text': combined_text[:100],
                    'category': cat if cat else 'None',
                    'score': score,
                    'reason': reason
                })
                
            except Exception as e:
                continue
        
        # FORCE ASSIGNMENT PHASE for unmatched items
        forced_assignments = []
        unmatched_indices = df[df['Detected_Category'].isna()].index
        
        for idx in unmatched_indices:
            try:
                row = df.loc[idx]
                
                # Get item text again
                all_text_parts = []
                for col in category_cols:
                    try:
                        val = row[col]
                        if pd.notna(val) and val is not None:
                            all_text_parts.append(str(val))
                    except:
                        continue
                
                combined_text = ' '.join(all_text_parts).lower()
                
                # Try partial matching - count ANY keyword mentions
                partial_scores = {}
                for category in enabled_categories:
                    score = 0
                    for keyword in detector.categories[category]['must_match']:
                        if keyword in combined_text:
                            score += 1
                    partial_scores[category] = score
                
                # Assign to best partial match OR first category
                if any(s > 0 for s in partial_scores.values()):
                    forced_cat = max(partial_scores, key=partial_scores.get)
                else:
                    # Distribute evenly across selected categories
                    forced_cat = enabled_categories[idx % len(enabled_categories)]
                
                df.at[idx, 'Detected_Category'] = forced_cat
                df.at[idx, 'Was_Forced'] = True
                
                item_name = str(row[category_cols[0]])[:50] if category_cols else f"Row {idx+2}"
                forced_assignments.append({
                    'item': item_name,
                    'assigned_to': forced_cat,
                    'reason': 'no clear match'
                })
                
            except Exception as e:
                if enabled_categories:
                    df.at[idx, 'Detected_Category'] = enabled_categories[0]
                    df.at[idx, 'Was_Forced'] = True
        
        # Separate by category
        separated = {}
        original_cols = [col for col in df.columns if col not in ['Detected_Category', 'Match_Score', 'Match_Reason', 'Was_Forced']]
        
        for category in enabled_categories:
            try:
                cat_data = df[df['Detected_Category'] == category][original_cols].copy()
                if len(cat_data) > 0:
                    separated[category] = cat_data
            except:
                continue
        
        # Statistics
        stats = {
            'total_rows': len(df),
            'well_matched': len(df[df['Match_Score'] >= 10]),
            'forced_matched': len(forced_assignments),
            'categories_found': len(separated),
            'distribution': df['Detected_Category'].value_counts().to_dict(),
            'forced_assignments': forced_assignments,
            'match_details': match_details
        }
        
        return separated, stats
        
    except Exception as e:
        st.error(f"Error processing: {str(e)}")
        return {}, {'total_rows': 0, 'well_matched': 0, 'forced_matched': 0, 'categories_found': 0, 'distribution': {}, 'forced_assignments': [], 'match_details': []}

def create_excel(df):
    """Create Excel file"""
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
            wb = writer.book
            ws = writer.sheets['Data']
            
            from openpyxl.styles import Font, PatternFill, Alignment
            hf = PatternFill(start_color='2a5298', end_color='2a5298', fill_type='solid')
            hfont = Font(color='FFFFFF', bold=True)
            
            for cell in ws[1]:
                cell.fill = hf
                cell.font = hfont
                cell.alignment = Alignment(horizontal='center')
            
            for col in ws.columns:
                max_len = 10
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_len:
                            max_len = len(str(cell.value))
                    except:
                        pass
                ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)
        
        output.seek(0)
        return output.getvalue()
    except Exception as e:
        st.error(f"Error creating Excel: {str(e)}")
        return None

def main():
    st.markdown('<div class="header-box"><h1 class="header-title">Data Separation Tool</h1><p class="header-subtitle">Smart Fan vs Lighting separation with exclusion logic</p></div>', unsafe_allow_html=True)
    
    # Session state
    if 'detector' not in st.session_state:
        st.session_state.detector = ImprovedCategoryDetector()
    if 'processed' not in st.session_state:
        st.session_state.processed = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'selected_cats' not in st.session_state:
        st.session_state.selected_cats = ['Lighting', 'Fans']
    
    # Layout
    col1, col2, col3 = st.columns([1.2, 1, 1.5])
    
    with col1:
        st.markdown('<div class="card"><h3 class="card-title">1. Upload File</h3>', unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=['xlsx', 'xlsm', 'xls'], label_visibility="collapsed")
        
        if uploaded:
            st.markdown('<div class="info-box">✓ File loaded</div>', unsafe_allow_html=True)
            sheets = get_sheet_info(uploaded)
            if sheets:
                opts = [f"{s['name']} ({s['rows']} rows)" for s in sheets]
                sel = st.selectbox("Sheet", opts, label_visibility="collapsed")
                st.session_state.sheet = sheets[opts.index(sel)]['name']
                st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card"><h3 class="card-title">2. Select Categories</h3>', unsafe_allow_html=True)
        
        all_cats = list(st.session_state.detector.categories.keys())
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("All", use_container_width=True, key="sel_all"):
                st.session_state.selected_cats = all_cats.copy()
                st.rerun()
        with c2:
            if st.button("Clear", use_container_width=True, key="clr_all"):
                st.session_state.selected_cats = []
                st.rerun()
        
        selected = []
        for cat in all_cats:
            if st.checkbox(cat, value=cat in st.session_state.selected_cats, key=f"c_{cat}"):
                selected.append(cat)
        
        st.session_state.selected_cats = selected
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="card"><h3 class="card-title">3. Process</h3>', unsafe_allow_html=True)
        
        if uploaded and st.session_state.selected_cats:
            st.markdown(f'<div class="info-box">Ready: {len(st.session_state.selected_cats)} categories</div>', unsafe_allow_html=True)
            
            if st.button("🚀 Process Data", type="primary", use_container_width=True):
                try:
                    with st.spinner('Processing with smart detection...'):
                        uploaded.seek(0)
                        separated, stats = process_file_smart(
                            uploaded, 
                            st.session_state.sheet, 
                            st.session_state.detector,
                            st.session_state.selected_cats
                        )
                        st.session_state.processed = separated
                        st.session_state.stats = stats
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            if not uploaded:
                st.info("Upload file first")
            elif not st.session_state.selected_cats:
                st.warning("Select categories")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Results
    if st.session_state.processed and st.session_state.stats:
        st.markdown("---")
        
        stats = st.session_state.stats
        stat_cols = st.columns(4)
        
        with stat_cols[0]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["total_rows"]}</div><div class="stat-label">Total Rows</div></div>', unsafe_allow_html=True)
        with stat_cols[1]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["well_matched"]}</div><div class="stat-label">Good Match</div></div>', unsafe_allow_html=True)
        with stat_cols[2]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["forced_matched"]}</div><div class="stat-label">Force Assigned</div></div>', unsafe_allow_html=True)
        with stat_cols[3]:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["categories_found"]}</div><div class="stat-label">Files Created</div></div>', unsafe_allow_html=True)
        
        # Show distribution
        st.markdown("### Category Distribution")
        dist_data = []
        for cat, count in stats.get('distribution', {}).items():
            if cat:
                pct = (count / stats['total_rows'] * 100) if stats['total_rows'] > 0 else 0
                dist_data.append({'Category': cat, 'Items': count, 'Percentage': f"{pct:.1f}%"})
        
        if dist_data:
            st.dataframe(pd.DataFrame(dist_data), use_container_width=True, hide_index=True)
        
        # Forced assignments
        if stats['forced_matched'] > 0:
            with st.expander(f"⚠️ {stats['forced_matched']} items force-assigned", expanded=False):
                for item in stats.get('forced_assignments', [])[:20]:
                    st.text(f"• {item.get('item', 'Unknown')} → {item.get('assigned_to', 'Unknown')}")
        
        # Match details for debugging
        if st.checkbox("Show detection details (for debugging)", value=False):
            details_df = pd.DataFrame(stats.get('match_details', [])[:50])
            if not details_df.empty:
                st.dataframe(details_df, use_container_width=True)
        
        # Downloads
        st.markdown("### Download Files")
        
        if st.session_state.processed:
            dl_cols = st.columns(min(len(st.session_state.processed), 4))
            
            for idx, (cat, data) in enumerate(st.session_state.processed.items()):
                with dl_cols[idx % 4]:
                    fname = f"{st.session_state.filename}_{cat}.xlsx"
                    excel = create_excel(data)
                    if excel:
                        st.download_button(
                            f"{cat}\n({len(data)} rows)", 
                            excel, 
                            fname, 
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                            use_container_width=True,
                            key=f"dl_{cat}"
                        )

if __name__ == "__main__":
    main()
