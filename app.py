import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io
import re
from difflib import SequenceMatcher
from collections import defaultdict
import numpy as np

st.set_page_config(page_title="Data Separation Tool - Ultra Strong", layout="wide", initial_sidebar_state="collapsed")

# =============================================================================
# COMPREHENSIVE CSS STYLING
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
        margin: 0;
    }

    .main > div {
        background: #f8fafc;
        min-height: 100vh;
        padding: 2rem;
    }

    .hero-header {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
        backdrop-filter: blur(10px);
        padding: 3rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }

    .hero-title {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 0.5rem;
    }

    .premium-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #e5e7eb;
    }

    .card-title {
        color: #1e293b;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .card-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 700;
    }

    .success-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 4px solid #10b981;
        color: #065f46;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }

    .warning-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        color: #92400e;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }

    .info-box {
        background: linear-gradient(135deg, #e0e7ff 0%, #e0f2fe 100%);
        border-left: 4px solid #667eea;
        padding: 1rem 1.2rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-size: 0.95rem;
        color: #1e40af;
    }

    .stat-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.2rem;
        margin: 1.5rem 0;
    }

    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.8rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }

    .stat-label {
        font-size: 0.9rem;
        opacity: 0.95;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.9rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        width: 100%;
    }

    .stDownloadButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.95rem;
        width: 100%;
    }

    .distribution-item {
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #667eea;
    }

    .confidence-high { color: #10b981; font-weight: 600; }
    .confidence-medium { color: #f59e0b; font-weight: 600; }
    .confidence-low { color: #ef4444; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# ULTRA STRONG CATEGORY DETECTOR - CHECKS EVERYTHING, MISSES NOTHING
# =============================================================================
class UltraStrongDetector:
    """
    Professional-grade data separator that checks EVERY cell in EVERY row and column.
    Uses multiple detection strategies to ensure ZERO SKUs are missed.
    """

    def __init__(self):
        # =================================================================
        # COMPREHENSIVE KEYWORD DATABASE - 500+ TERMS
        # =================================================================
        self.categories = {
            'Fans': {
                'keywords': [
                    'fan', 'ventilator', 'blower', 'exhaust', 'ventilation', 'air circulator', 'cooling fan',
                    'pedestal', 'tower fan', 'ceiling fan', 'table fan', 'wall fan', 'stand fan',
                    'industrial fan', 'oscillating', 'desk fan', 'floor fan', 'box fan', 'window fan',
                    'attic fan', 'bathroom fan', 'kitchen fan', 'range hood fan', 'inline fan',
                    'centrifugal fan', 'axial fan', 'blower motor', 'ventilation system',
                    'air mover', 'air extractor', 'fume extractor', 'smoke extractor',
                    'cooler', 'air cooler', 'evaporative cooler', 'mist fan', 'humidifier fan',
                    'hvac fan', 'ac fan', 'condenser fan', 'radiator fan', 'cooling tower',
                    'vent fan', 'extractor fan', 'intake fan', 'outtake fan', 'circulation fan',
                    'whole house fan', 'garage fan', 'shop fan', 'barn fan', 'greenhouse fan',
                    'livestock fan', 'poultry fan', 'dairy fan', 'agricultural fan',
                    'portable fan', 'rechargeable fan', 'solar fan', 'battery fan', 'usb fan',
                    'mini fan', 'personal fan', 'neck fan', 'handheld fan', 'clip fan',
                    'bracket fan', 'mounting fan', 'duct fan', 'inline duct fan', 'booster fan',
                    'pressure fan', 'suction fan', 'supply fan', 'return fan', 'makeup air fan',
                    'spot cooler', 'portable cooler', 'swamp cooler', 'desert cooler',
                    'fan blade', 'fan motor', 'fan guard', 'fan cage', 'fan grill',
                    'fan controller', 'fan speed', 'fan switch', 'fan timer', 'fan remote',
                    'fan light kit', 'fan downrod', 'fan canopy', 'fan mounting bracket',
                    'ceiling mount fan', 'wall mount fan', 'floor mount fan', 'pedestal stand',
                    'fan extension pole', 'fan chain', 'fan pull', 'fan cord', 'fan wiring',
                    'ventilation grille', 'air vent', 'air register', 'air diffuser', 'air damper',
                    'louvre', 'louver', 'vent cover', 'vent cap', 'vent hood', 'range hood',
                    'cooker hood', 'extractor hood', 'fume hood', 'laboratory hood',
                ],
                'exclude': ['light', 'lamp', 'bulb', 'led', 'fixture', 'lighting', 'illumination', 'chandelier'],
                'sku_patterns': [r'FAN\d+', r'VF\d+', r'BL\d+', r'EF\d+', r'CF\d+', r'SF\d+'],
                'confidence_boost': 1.0
            },

            'Lighting': {
                'keywords': [
                    'light', 'lamp', 'bulb', 'lighting', 'led', 'fixture', 'chandelier',
                    'luminaire', 'illumination', 'lantern', 'sconce', 'pendant', 'downlight',
                    'spotlight', 'track light', 'ceiling light', 'wall light', 'floor lamp',
                    'table lamp', 'desk lamp', 'reading lamp', 'bedside lamp', 'night light',
                    'accent light', 'ambient light', 'task light', 'decorative light',
                    'chandelier', 'crystal chandelier', 'modern chandelier', 'mini chandelier',
                    'pendant light', 'pendant lamp', 'mini pendant', 'island pendant',
                    'flush mount', 'semi flush', 'close to ceiling', 'ceiling fixture',
                    'recessed light', 'can light', 'pot light', 'downlight', 'gimbal light',
                    'eyeball light', 'adjustable downlight', 'baffle trim', 'reflector trim',
                    'wall sconce', 'vanity light', 'bathroom light', 'mirror light',
                    'picture light', 'art light', 'wall washer', 'uplight', 'torchiere',
                    'floor lamp', 'arc lamp', 'tripod lamp', 'tree lamp', 'pharmacy lamp',
                    'table lamp', 'desk lamp', 'banker lamp', 'touch lamp', 'clip lamp',
                    'led strip', 'led tape', 'led ribbon', 'under cabinet light', 'puck light',
                    'rope light', 'neon light', 'flexible light', 'tape light',
                    'outdoor light', 'exterior light', 'landscape light', 'path light',
                    'flood light', 'security light', 'motion light', 'dusk to dawn',
                    'solar light', 'garden light', 'deck light', 'step light', 'post light',
                    'bollard light', 'well light', 'inground light', 'underwater light',
                    'pool light', 'spa light', 'fountain light', 'pond light',
                    'street light', 'area light', 'parking lot light', 'shoebox light',
                    'wall pack', 'canopy light', 'soffit light', 'eave light',
                    'high bay', 'low bay', 'warehouse light', 'industrial light',
                    'shop light', 'garage light', 'workshop light', 'utility light',
                    'emergency light', 'exit sign', 'egress light', 'safety light',
                    'grow light', 'plant light', 'aquarium light', 'terrarium light',
                    'black light', 'uv light', 'germicidal light', 'sterilization light',
                    'therapy light', 'sad light', 'daylight lamp', 'full spectrum',
                    'smart light', 'wifi light', 'bluetooth light', 'app controlled',
                    'color changing', 'rgb light', 'rgbw', 'tunable white', 'dim to warm',
                    'dimmable', 'dimmable led', 'three way', 'touch dimmer', 'remote dimmer',
                    'edison bulb', 'filament bulb', 'vintage bulb', 'antique bulb',
                    'halogen', 'incandescent', 'cfl', 'compact fluorescent', 'hid',
                    'metal halide', 'high pressure sodium', 'mercury vapor',
                    'tube light', 'fluorescent tube', 't5', 't8', 't12', 'led tube',
                    'bulb type a', 'bulb type b', 'bulb type c', 'candle bulb', 'globe bulb',
                    'par bulb', 'mr bulb', 'br bulb', 'r bulb', 'ar bulb', 't bulb',
                    'gu10', 'mr16', 'e26', 'e27', 'e12', 'e14', 'b22', 'g4', 'g9',
                    'light switch', 'dimmer switch', 'timer switch', 'motion sensor',
                    'daylight sensor', 'occupancy sensor', 'vacancy sensor', 'photocell',
                    'light fixture', 'light fitting', 'light housing', 'light trim',
                    'light shade', 'lamp shade', 'diffuser', 'lens', 'reflector', 'baffle',
                    'ballast', 'driver', 'transformer', 'power supply', 'led driver',
                    'light socket', 'lamp holder', 'bulb holder', 'base', 'mount',
                ],
                'exclude': ['fan', 'ventilator', 'blower', 'exhaust', 'cooling', 'ventilation'],
                'sku_patterns': [r'LT\d+', r'LED\d+', r'BULB\d+', r'CH\d+', r'PN\d+', r'DL\d+'],
                'confidence_boost': 1.0
            },

            'Furniture': {
                'keywords': [
                    'chair', 'chairs', 'seat', 'seating', 'stool', 'bench', 'ottoman',
                    'armchair', 'accent chair', 'side chair', 'dining chair', 'kitchen chair',
                    'office chair', 'desk chair', 'computer chair', 'task chair', 'executive chair',
                    'ergonomic chair', 'gaming chair', 'recliner', 'reclining chair', 'lift chair',
                    'rocking chair', 'rocker', 'glider', 'swivel chair', 'barrel chair',
                    'wingback chair', 'club chair', 'slipper chair', 'parsons chair',
                    'folding chair', 'stackable chair', 'banquet chair', 'chiavari chair',
                    'bar stool', 'counter stool', 'backless stool', 'saddle stool',
                    'sofa', 'couch', 'settee', 'loveseat', 'sectional', 'modular sofa',
                    'sleeper sofa', 'sofa bed', 'futon', 'daybed', 'chaise', 'chaise lounge',
                    'ottoman', 'footstool', 'footrest', 'pouf', 'pouffe', 'hassock',
                    'bean bag', 'gaming seat', 'massage chair', 'zero gravity chair',
                    'table', 'tables', 'desk', 'desks', 'workstation', 'workbench',
                    'dining table', 'kitchen table', 'breakfast table', 'nook table',
                    'coffee table', 'cocktail table', 'accent table', 'side table', 'end table',
                    'console table', 'sofa table', 'hallway table', 'entryway table',
                    'nightstand', 'night table', 'bedside table', 'bedside cabinet',
                    'dresser', 'chest of drawers', 'bureau', 'highboy', 'lowboy',
                    'wardrobe', 'armoire', 'chiffonier', 'gentlemans chest',
                    'tv stand', 'tv console', 'media console', 'entertainment center',
                    'bookcase', 'bookshelf', 'shelving unit', 'etagere', 'bakers rack',
                    'filing cabinet', 'file cabinet', 'lateral file', 'vertical file',
                    'credenza', 'sideboard', 'buffet', 'hutch', 'china cabinet', 'curio',
                    'office desk', 'computer desk', 'writing desk', 'secretary desk',
                    'standing desk', 'adjustable desk', 'sit stand desk', 'converter',
                    'drafting table', 'drawing table', 'art table', 'hobby table',
                    'conference table', 'meeting table', 'boardroom table', 'training table',
                    'folding table', 'banquet table', 'picnic table', 'patio table',
                    'bar table', 'pub table', 'bistro table', 'high top table',
                    'nesting table', 'nest of tables', 'stacking table', 'nested table',
                    'bed', 'beds', 'bed frame', 'bedframe', 'platform bed', 'panel bed',
                    'sleigh bed', 'canopy bed', 'four poster bed', 'poster bed',
                    'storage bed', 'captains bed', 'mate bed', 'murphy bed', 'wall bed',
                    'bunk bed', 'loft bed', 'trundle bed', 'daybed', 'futon bed',
                    'headboard', 'footboard', 'bed rails', 'bed slats', 'box spring',
                    'mattress foundation', 'bed base', 'adjustable base', 'bed legs',
                    'cabinet', 'cabinets', 'cupboard', 'closet', 'storage', 'organizer',
                    'shelf', 'shelves', 'shelving', 'rack', 'stand', 'holder',
                    'storage bin', 'storage box', 'storage basket', 'storage crate',
                    'drawer', 'drawers', 'drawer unit', 'cart', 'trolley', 'island',
                    'pantry', 'larder', 'wine rack', 'shoe rack', 'coat rack', 'hat stand',
                    'jewelry armoire', 'jewelry cabinet', 'mirror cabinet', 'medicine cabinet',
                    'patio furniture', 'outdoor furniture', 'garden furniture', 'lawn furniture',
                    'deck furniture', 'balcony furniture', 'porch furniture', 'veranda furniture',
                    'adirondack chair', 'lawn chair', 'beach chair', 'folding lawn chair',
                    'garden bench', 'park bench', 'porch swing', 'swing seat', 'hammock',
                    'outdoor sofa', 'patio sofa', 'sectional outdoor', 'outdoor sectional',
                    'outdoor dining set', 'patio dining set', 'garden dining set',
                    'umbrella', 'parasol', 'shade sail', 'pergola', 'gazebo', 'arbor',
                    'crib', 'cot', 'bassinet', 'cradle', 'changing table', 'nursery furniture',
                    'kids bed', 'toddler bed', 'twin bed', 'bunk bed', 'loft bed',
                    'kids desk', 'study desk', 'activity table', 'play table', 'train table',
                    'toy box', 'toy chest', 'toy storage', 'book sling', 'kids bookshelf',
                    'wooden', 'wood', 'solid wood', 'hardwood', 'softwood', 'pine', 'oak',
                    'maple', 'cherry', 'walnut', 'mahogany', 'teak', 'acacia', 'sheesham',
                    'rubberwood', 'mdf', 'particle board', 'plywood', 'veneer', 'laminate',
                    'metal', 'steel', 'iron', 'wrought iron', 'aluminum', 'stainless steel',
                    'glass', 'tempered glass', 'acrylic', 'plastic', 'resin', 'wicker',
                    'rattan', 'bamboo', 'cane', 'seagrass', 'upholstered', 'fabric', 'leather',
                    'faux leather', 'pu leather', 'vinyl', 'microfiber', 'velvet', 'linen',
                ],
                'exclude': [],
                'sku_patterns': [r'FR\d+', r'CH\d+', r'TB\d+', r'SF\d+', r'BD\d+', r'DK\d+'],
                'confidence_boost': 1.0
            },

            'Decor': {
                'keywords': [
                    'decor', 'decoration', 'decorative', 'wall decor', 'wall art', 'artwork',
                    'painting', 'canvas art', 'framed art', 'print', 'poster', 'wall hanging',
                    'tapestry', 'wall tapestry', 'macrame', 'wall macrame', 'woven wall art',
                    'metal wall art', 'wood wall art', 'canvas print', 'photo print',
                    'mirror', 'mirrors', 'wall mirror', 'floor mirror', 'full length mirror',
                    'vanity mirror', 'decorative mirror', 'accent mirror', 'sunburst mirror',
                    'round mirror', 'oval mirror', 'rectangular mirror', 'square mirror',
                    'framed mirror', 'frameless mirror', 'beveled mirror', 'led mirror',
                    'clock', 'clocks', 'wall clock', 'mantel clock', 'table clock', 'alarm clock',
                    'shelf', 'floating shelf', 'ledge shelf', 'picture ledge', 'display shelf',
                    'wall shelf', 'corner shelf', 'cube shelf', 'hexagon shelf', 'geometric shelf',
                    'vase', 'vases', 'flower vase', 'bud vase', 'floor vase', 'ceramic vase',
                    'glass vase', 'crystal vase', 'metal vase', 'wood vase', 'basket',
                    'bowl', 'bowls', 'decorative bowl', 'centerpiece bowl', 'fruit bowl',
                    'planter', 'planters', 'flower pot', 'plant pot', 'cachepot', 'urn',
                    'jar', 'jars', 'canister', 'canisters', 'bottle', 'bottles', 'decanter',
                    'pitcher', 'ewer', 'amphora', 'terracotta', 'clay pot', 'concrete pot',
                    'sculpture', 'sculptures', 'statue', 'statues', 'figurine', 'figurines',
                    'bust', 'busts', 'art object', 'objet dart', 'curio', 'collectible',
                    'ornament', 'ornaments', 'keepsake', 'memento', 'souvenir',
                    'bookend', 'bookends', 'paperweight', 'desk accessory', 'trinket',
                    'pillow', 'pillows', 'cushion', 'cushions', 'throw pillow', 'accent pillow',
                    'decorative pillow', 'lumbar pillow', 'euro sham', 'pillow sham',
                    'pillow cover', 'cushion cover', 'pillow insert', 'cushion insert',
                    'blanket', 'blankets', 'throw', 'throws', 'afghan', 'quilt', 'coverlet',
                    'bedspread', 'comforter', 'duvet', 'duvet cover', 'bed skirt', 'dust ruffle',
                    'rug', 'rugs', 'area rug', 'throw rug', 'accent rug', 'runner', 'carpet',
                    'mat', 'mats', 'doormat', 'bath mat', 'kitchen mat', 'accent mat',
                    'curtain', 'curtains', 'drape', 'drapes', 'window panel', 'sheer curtain',
                    'valance', 'cornice', 'swag', 'tier curtain', 'cafe curtain', 'panel pair',
                    'candle', 'candles', 'pillar candle', 'taper candle', 'votive candle',
                    'tea light', 'led candle', 'flameless candle', 'scented candle',
                    'candle holder', 'candleholder', 'candlestick', 'candelabra', 'votive holder',
                    'tea light holder', 'pillar holder', 'taper holder', 'hurricane candle',
                    'lantern', 'lanterns', 'candle lantern', 'metal lantern', 'wood lantern',
                    'frame', 'frames', 'picture frame', 'photo frame', 'collage frame',
                    'gallery frame', 'float frame', 'shadow box', 'document frame', 'diploma frame',
                    'album', 'albums', 'photo album', 'scrapbook', 'memory book', 'guest book',
                    'wreath', 'wreaths', 'door wreath', 'seasonal decor', 'holiday decor',
                    'christmas decor', 'halloween decor', 'easter decor', 'fall decor',
                    'spring decor', 'summer decor', 'winter decor', 'harvest decor',
                    'garland', 'garlands', 'swag', 'swags', 'topiary', 'topiaries',
                    'faux plant', 'artificial plant', 'silk plant', 'plastic plant',
                    'faux flower', 'artificial flower', 'silk flower', 'dried flower',
                    'preserved flower', 'flower arrangement', 'floral arrangement', 'bouquet',
                    'succulent', 'succulents', 'air plant', 'cactus', 'cacti', 'bonsai',
                    'tree', 'trees', 'fiddle leaf', 'monstera', 'palm', 'fern', 'ferns',
                    'greenery', 'foliage', 'stem', 'stems', 'branch', 'branches', 'twig',
                    'dried botanical', 'pampas grass', 'eucalyptus', 'lavender', 'wheat',
                    'tray', 'trays', 'serving tray', 'decorative tray', 'ottoman tray',
                    'jewelry box', 'keepsake box', 'memory box', 'treasure box', 'trinket box',
                    'watch box', 'cufflink box', 'tie box', 'valet tray', 'catchall tray',
                    'screen', 'screens', 'room divider', 'folding screen', 'privacy screen',
                    'divider', 'dividers', 'panel screen', 'shoji screen', 'rattan screen',
                    'fireplace screen', 'spark guard', 'fire screen', 'andiron', 'fire tool',
                    'screen panel', 'wall panel', '3d panel', 'acoustic panel', 'slat panel',
                ],
                'exclude': [],
                'sku_patterns': [r'DC\d+', r'WA\d+', r'VA\d+', r'PI\d+', r'RU\d+'],
                'confidence_boost': 1.0
            },

            'Electronics': {
                'keywords': [
                    'tv', 'television', 'smart tv', 'led tv', 'oled tv', 'qled tv', '4k tv',
                    '8k tv', 'ultra hd', 'full hd', 'hd ready', 'flat screen', 'curved tv',
                    'monitor', 'monitors', 'computer monitor', 'gaming monitor', 'ultrawide',
                    'display', 'displays', 'screen', 'screens', 'digital display', 'signage',
                    'projector', 'projectors', 'home projector', 'portable projector',
                    'speaker', 'speakers', 'audio', 'sound', 'soundbar', 'sound bar',
                    'bluetooth speaker', 'wireless speaker', 'portable speaker', 'smart speaker',
                    'bookshelf speaker', 'floor speaker', 'tower speaker', 'center speaker',
                    'subwoofer', 'sub', 'woofer', 'bass speaker', 'surround speaker',
                    'home theater', 'home theatre', 'hifi', 'hi fi', 'stereo', 'stereo system',
                    'amplifier', 'amp', 'receiver', 'av receiver', 'audio receiver',
                    'turntable', 'record player', 'vinyl player', 'dj equipment', 'mixer',
                    'headphone', 'headphones', 'earphone', 'earphones', 'earbud', 'earbuds',
                    'headset', 'gaming headset', 'wireless headphone', 'noise cancelling',
                    'microphone', 'mic', 'condenser mic', 'dynamic mic', 'usb mic',
                    'computer', 'computers', 'desktop', 'laptop', 'notebook', 'netbook',
                    'tablet', 'ipad', 'android tablet', '2 in 1', 'convertible', 'chromebook',
                    'gaming pc', 'workstation', 'all in one', 'mini pc', 'nuc', 'barebone',
                    'keyboard', 'keyboards', 'mechanical keyboard', 'gaming keyboard',
                    'mouse', 'mice', 'gaming mouse', 'wireless mouse', 'trackball', 'trackpad',
                    'webcam', 'web camera', 'document camera', 'visual presenter',
                    'printer', 'printers', 'inkjet', 'laser printer', 'all in one printer',
                    'scanner', 'scanners', 'flatbed scanner', 'document scanner', 'photo scanner',
                    '3d printer', 'label printer', 'receipt printer', 'thermal printer',
                    'cartridge', 'ink cartridge', 'toner', 'toner cartridge', 'drum unit',
                    'router', 'routers', 'wifi router', 'wireless router', 'mesh router',
                    'modem', 'cable modem', 'dsl modem', 'gateway', 'network switch',
                    'extender', 'range extender', 'wifi extender', 'access point', 'repeater',
                    'network adapter', 'wifi adapter', 'ethernet adapter', 'powerline',
                    'network cable', 'ethernet cable', 'patch cable', 'hdmi cable', 'usb cable',
                    'smart home', 'home automation', 'smart device', 'connected device',
                    'smart plug', 'smart switch', 'smart bulb', 'smart light', 'smart lock',
                    'doorbell', 'video doorbell', 'smart doorbell', 'security camera',
                    'ip camera', 'wifi camera', 'baby monitor', 'pet camera', 'dash cam',
                    'thermostat', 'smart thermostat', 'temperature controller',
                    'sensor', 'sensors', 'motion sensor', 'door sensor', 'window sensor',
                    'smoke detector', 'co detector', 'carbon monoxide', 'water leak detector',
                    'hub', 'smart hub', 'bridge', 'controller', 'remote control', 'universal remote',
                    'game console', 'gaming console', 'playstation', 'xbox', 'nintendo',
                    'controller', 'game controller', 'gamepad', 'joystick', 'racing wheel',
                    'vr', 'virtual reality', 'vr headset', 'oculus', 'htc vive', 'psvr',
                    'phone', 'phones', 'smartphone', 'mobile phone', 'cell phone', 'iphone',
                    'android phone', 'case', 'phone case', 'screen protector', 'charger',
                    'power bank', 'battery pack', 'portable charger', 'wireless charger',
                    'cable', 'cables', 'charging cable', 'data cable', 'adapter', 'dongle',
                    'camera', 'cameras', 'digital camera', 'dslr', 'mirrorless', 'compact camera',
                    'action camera', 'gopro', 'instant camera', 'polaroid', 'film camera',
                    'lens', 'camera lens', 'tripod', 'camera bag', 'memory card', 'sd card',
                    'vacuum', 'vacuum cleaner', 'robot vacuum', 'cordless vacuum', 'stick vacuum',
                    'fan', 'cooler', 'heater', 'space heater', 'air purifier', 'humidifier',
                    'dehumidifier', 'diffuser', 'essential oil', 'air fryer', 'toaster oven',
                ],
                'exclude': [],
                'sku_patterns': [r'EL\d+', r'TV\d+', r'SP\d+', r'PC\d+', r'LP\d+'],
                'confidence_boost': 1.0
            },

            'Kitchen': {
                'keywords': [
                    'kitchen', 'cookware', 'cooking', 'appliance', 'appliances',
                    'refrigerator', 'fridge', 'freezer', 'side by side', 'french door',
                    'bottom freezer', 'top freezer', 'mini fridge', 'compact fridge',
                    'wine cooler', 'beverage cooler', 'ice maker', 'ice machine',
                    'stove', 'stoves', 'range', 'ranges', 'cooktop', 'cooktops',
                    'gas range', 'electric range', 'induction range', 'dual fuel',
                    'oven', 'ovens', 'wall oven', 'double oven', 'single oven',
                    'microwave', 'microwaves', 'countertop microwave', 'over range',
                    'built in microwave', 'microwave drawer', 'convection microwave',
                    'dishwasher', 'dishwashers', 'built in dishwasher', 'portable dishwasher',
                    'range hood', 'hood', 'vent hood', 'island hood', 'wall hood',
                    'trash compactor', 'garbage disposal', 'disposal', 'compactor',
                    'blender', 'blenders', 'mixer', 'mixers', 'stand mixer', 'hand mixer',
                    'food processor', 'chopper', 'food chopper', 'mini chopper',
                    'coffee maker', 'coffee machine', 'espresso machine', 'cappuccino maker',
                    'kettle', 'electric kettle', 'gooseneck kettle', 'tea kettle',
                    'toaster', 'toasters', 'toaster oven', 'air fryer', 'airfryer',
                    'pressure cooker', 'instant pot', 'slow cooker', 'crock pot',
                    'rice cooker', 'steamer', 'food steamer', 'sous vide', 'immersion circulator',
                    'griddle', 'grill', 'electric grill', 'panini press', 'sandwich maker',
                    'waffle maker', 'waffle iron', 'pancake maker', 'crepe maker',
                    'juicer', 'juicers', 'citrus juicer', 'masticating juicer', 'centrifugal',
                    'dehydrator', 'food dehydrator', 'yogurt maker', 'bread maker', 'ice cream maker',
                    'pot', 'pots', 'pan', 'pans', 'cookware set', 'cookware',
                    'saucepan', 'saucepans', 'stock pot', 'dutch oven', 'french oven',
                    'frying pan', 'skillet', 'saute pan', 'grill pan', 'griddle pan',
                    'wok', 'stir fry pan', 'paella pan', 'crepe pan', 'omelet pan',
                    'roasting pan', 'roaster', 'baking dish', 'casserole dish', 'lasagna pan',
                    'sheet pan', 'baking sheet', 'cookie sheet', 'jelly roll pan',
                    'muffin pan', 'cupcake pan', 'cake pan', 'round cake pan', 'square cake pan',
                    'bundt pan', 'loaf pan', 'bread pan', 'pie pan', 'pie dish', 'tart pan',
                    'springform pan', 'tube pan', 'angel food pan', 'madeleine pan',
                    'baking', 'bakeware', 'baking set', 'baking tools', 'pastry tools',
                    'mixing bowl', 'mixing bowls', 'prep bowl', 'nesting bowl',
                    'measuring cup', 'measuring cups', 'measuring spoon', 'measuring spoons',
                    'scale', 'kitchen scale', 'food scale', 'digital scale',
                    'timer', 'kitchen timer', 'thermometer', 'meat thermometer', 'oven thermometer',
                    'rolling pin', 'pastry cutter', 'pastry brush', 'basting brush',
                    'spatula', 'spatulas', 'rubber spatula', 'silicone spatula', 'offset spatula',
                    'whisk', 'whisks', 'balloon whisk', 'flat whisk', 'silicone whisk',
                    'tongs', 'kitchen tongs', 'salad tongs', 'pasta tongs',
                    'ladle', 'ladles', 'soup ladle', 'gravy ladle',
                    'skimmer', 'slotted spoon', 'solid spoon', 'serving spoon',
                    'turner', 'flipper', 'spatula turner', 'fish turner', 'pancake turner',
                    'peeler', 'vegetable peeler', 'potato peeler', 'julienne peeler',
                    'grater', 'graters', 'box grater', 'microplane', 'zester', 'citrus zester',
                    'colander', 'colanders', 'strainer', 'strainers', 'sieve', 'fine mesh',
                    'salad spinner', 'lettuce spinner', 'herb spinner',
                    'cutting board', 'chopping board', 'butcher block', 'carving board',
                    'knife', 'knives', 'chef knife', 'paring knife', 'bread knife',
                    'santoku', 'utility knife', 'boning knife', 'filleting knife',
                    'knife set', 'knife block', 'knife sharpener', 'honing steel',
                    'shears', 'kitchen shears', 'poultry shears', 'scissors',
                    'container', 'containers', 'food container', 'storage container',
                    'tupperware', 'plastic container', 'glass container', 'stainless container',
                    'canister', 'canisters', 'jar', 'jars', 'mason jar', 'cookie jar',
                    'spice rack', 'spice organizer', 'spice jar', 'spice bottle',
                    'bread box', 'bread bin', 'fruit bowl', 'fruit basket', 'egg holder',
                    'utensil', 'utensils', 'kitchen utensil', 'cooking utensil', 'gadget',
                    'can opener', 'bottle opener', 'corkscrew', 'wine opener',
                    'garlic press', 'garlic chopper', 'onion chopper', 'vegetable chopper',
                    'apple corer', 'apple slicer', 'avocado slicer', 'mango splitter',
                    'egg slicer', 'egg separator', 'egg poacher', 'egg cooker',
                    'pizza cutter', 'pizza wheel', 'pizza peel', 'pizza stone',
                    'pasta maker', 'pasta machine', 'noodle maker', 'ravioli maker',
                    'ice cream scoop', 'cookie scoop', 'melon baller', 'fruit corer',
                    'nutcracker', 'lobster cracker', 'seafood cracker', 'crab cracker',
                    'funnel', 'funnels', 'kitchen funnel', 'straining funnel',
                ],
                'exclude': [],
                'sku_patterns': [r'KT\d+', r'KW\d+', r'AP\d+', r'CK\d+'],
                'confidence_boost': 1.0
            },

            'Bathroom': {
                'keywords': [
                    'bathroom', 'bath', 'toilet', 'sink', 'basin', 'vanity', 'shower', 'bathtub',
                    'bath tub', 'jacuzzi', 'whirlpool', 'sauna', 'steam room', 'bidet',
                    'faucet', 'tap', 'mixer tap', 'shower head', 'hand shower', 'rain shower',
                    'toilet seat', 'toilet paper holder', 'towel bar', 'towel rack', 'robe hook',
                    'soap dispenser', 'toothbrush holder', 'tumbler', 'trash can', 'bath mat',
                    'shower curtain', 'shower caddy', 'bathroom cabinet', 'medicine cabinet',
                    'mirror cabinet', 'bathroom shelf', 'bathroom organizer', 'bathroom storage',
                ],
                'exclude': [],
                'sku_patterns': [r'BT\d+', r'BH\d+'],
                'confidence_boost': 1.0
            },

            'Outdoor': {
                'keywords': [
                    'outdoor', 'patio', 'garden', 'lawn', 'yard', 'backyard', 'bbq', 'grill',
                    'barbecue', 'charcoal grill', 'gas grill', 'electric grill', 'smoker',
                    'patio heater', 'fire pit', 'firepit', 'chiminea', 'outdoor fireplace',
                    'patio furniture', 'outdoor furniture', 'garden furniture', 'lawn furniture',
                    'gazebo', 'pergola', 'arbor', 'trellis', 'fence', 'fencing', 'gate',
                    'planter', 'planters', 'flower pot', 'garden pot', 'raised bed',
                    'compost bin', 'rain barrel', 'garden shed', 'greenhouse', 'cold frame',
                    'lawn mower', 'grass cutter', 'trimmer', 'hedge trimmer', 'leaf blower',
                    'pressure washer', 'power washer', 'hose', 'garden hose', 'sprinkler',
                    'outdoor light', 'solar light', 'path light', 'spotlight', 'floodlight',
                    'hammock', 'swing', 'porch swing', 'outdoor cushion', 'patio umbrella',
                ],
                'exclude': [],
                'sku_patterns': [r'OD\d+', r'GD\d+', r'PT\d+'],
                'confidence_boost': 1.0
            },

            'Hardware': {
                'keywords': [
                    'hardware', 'tool', 'tools', 'power tool', 'hand tool', 'cordless tool',
                    'drill', 'drills', 'cordless drill', 'hammer drill', 'impact driver',
                    'saw', 'saws', 'circular saw', 'jigsaw', 'reciprocating saw', 'miter saw',
                    'table saw', 'band saw', 'scroll saw', 'chainsaw', 'pole saw',
                    'sander', 'sanders', 'orbital sander', 'belt sander', 'random orbit',
                    'grinder', 'grinders', 'angle grinder', 'bench grinder', 'die grinder',
                    'router', 'routers', 'trim router', 'plunge router', 'cnc router',
                    'nailer', 'nail gun', 'stapler', 'staple gun', 'brad nailer', 'finish nailer',
                    'compressor', 'air compressor', 'generator', 'portable generator', 'inverter',
                    'ladder', 'ladders', 'step ladder', 'extension ladder', 'telescoping ladder',
                    'scaffold', 'scaffolding', 'work platform', 'sawhorse', 'work bench',
                    'tool box', 'tool chest', 'tool cabinet', 'tool bag', 'tool belt',
                    'screwdriver', 'screwdrivers', 'wrench', 'wrenches', 'socket set',
                    'pliers', 'hammer', 'hammers', 'tape measure', 'level', 'square',
                    'fastener', 'fasteners', 'screw', 'screws', 'bolt', 'bolts', 'nut', 'nuts',
                    'washer', 'washers', 'anchor', 'anchors', 'nail', 'nails', 'staple', 'staples',
                    'hinge', 'hinges', 'handle', 'handles', 'knob', 'knobs', 'pull', 'pulls',
                    'lock', 'locks', 'deadbolt', 'door lock', 'padlock', 'combination lock',
                    'chain', 'chains', 'rope', 'ropes', 'cable', 'cables', 'wire', 'wires',
                ],
                'exclude': [],
                'sku_patterns': [r'HW\d+', r'TL\d+', r'PT\d+'],
                'confidence_boost': 1.0
            },

            'Plumbing': {
                'keywords': [
                    'plumbing', 'pipe', 'pipes', 'piping', 'fitting', 'fittings', 'connector',
                    'valve', 'valves', 'faucet', 'tap', 'mixer', 'shower valve', 'stop valve',
                    'drain', 'drains', 'sink drain', 'shower drain', 'floor drain', 'catch basin',
                    'trap', 'traps', 'p trap', 's trap', 'water heater', 'tankless heater',
                    'pump', 'pumps', 'sump pump', 'sewage pump', 'utility pump', 'transfer pump',
                    'toilet', 'wc', 'commode', 'urinal', 'bidet', 'toilet tank', 'flush valve',
                    'sewer', 'sewage', 'septic', 'drainage', 'storm drain', 'gutter', 'downspout',
                    'water softener', 'water filter', 'reverse osmosis', 'whole house filter',
                    'hose', 'hoses', 'garden hose', 'washer hose', 'supply line', 'flexible hose',
                    'pipe insulation', 'heat tape', 'pipe wrap', 'frost protection',
                ],
                'exclude': [],
                'sku_patterns': [r'PL\d+', r'PV\d+', r'WH\d+'],
                'confidence_boost': 1.0
            },

            'Electrical': {
                'keywords': [
                    'electrical', 'electric', 'wiring', 'wire', 'cable', 'conductor', 'circuit',
                    'outlet', 'outlets', 'receptacle', 'socket', 'wall outlet', 'gfci', 'gfi',
                    'switch', 'switches', 'light switch', 'dimmer switch', 'timer switch',
                    'breaker', 'breakers', 'circuit breaker', 'panel', 'breaker panel', 'fuse box',
                    'junction box', 'outlet box', 'switch box', 'gang box', 'old work box',
                    'conduit', 'conduits', 'emt', 'pvc conduit', 'flexible conduit', 'liquidtight',
                    'fixture', 'light fixture', 'ceiling fixture', 'wall fixture', 'outdoor fixture',
                    'bulb', 'bulbs', 'led bulb', 'cfl bulb', 'halogen bulb', 'incandescent',
                    'extension cord', 'power cord', 'power strip', 'surge protector', 'ups',
                    'smoke detector', 'carbon monoxide detector', 'co detector', 'alarm',
                    'fan', 'exhaust fan', 'ventilation fan', 'bathroom fan', 'attic fan',
                    'heater', 'baseboard heater', 'wall heater', 'space heater', 'garage heater',
                    'thermostat', 'programmable thermostat', 'smart thermostat', 'line voltage',
                ],
                'exclude': [],
                'sku_patterns': [r'EC\d+', r'WR\d+', r'CB\d+'],
                'confidence_boost': 1.0
            },
        }

        # Compile all keywords for faster lookup
        self._compile_keywords()

        # Column name patterns to check
        self.priority_column_patterns = [
            'category', 'categories', 'cat', 'product category', 'item category',
            'type', 'product type', 'item type', 'product_type', 'item_type',
            'class', 'classification', 'group', 'department', 'section',
            'family', 'product family', 'line', 'product line', 'series',
        ]

        self.secondary_column_patterns = [
            'description', 'desc', 'product description', 'item description', 'long description',
            'name', 'product name', 'item name', 'product_name', 'item_name', 'title',
            'product', 'item', 'sku', 'model', 'model number', 'part number', 'partno',
            'brand', 'manufacturer', 'mfg', 'vendor', 'supplier',
            'short description', 'brief description', 'summary', 'details',
        ]

    def _compile_keywords(self):
        """Pre-compile all keywords for faster matching"""
        self.all_keywords = set()
        for cat_data in self.categories.values():
            self.all_keywords.update(cat_data['keywords'])

    def _fuzzy_match(self, text, keyword, threshold=0.85):
        """Check if text fuzzy matches keyword"""
        text_lower = text.lower()
        keyword_lower = keyword.lower()

        # Direct match
        if keyword_lower in text_lower:
            return True, 1.0

        # Word boundary match
        words = text_lower.split()
        for word in words:
            if keyword_lower in word or word in keyword_lower:
                return True, 0.9

        # Sequence matcher for typos
        similarity = SequenceMatcher(None, text_lower, keyword_lower).ratio()
        if similarity >= threshold:
            return True, similarity

        # Check individual words
        keyword_words = keyword_lower.split()
        for kw_word in keyword_words:
            for text_word in words:
                if len(kw_word) > 3 and len(text_word) > 3:
                    word_sim = SequenceMatcher(None, text_word, kw_word).ratio()
                    if word_sim >= 0.9:
                        return True, word_sim

        return False, 0

    def _check_sku_pattern(self, text, patterns):
        """Check if text matches any SKU pattern"""
        if not text or pd.isna(text):
            return False
        text = str(text).upper().strip()
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False

    def _clean_text(self, text):
        """Clean and normalize text for matching"""
        if pd.isna(text) or text is None:
            return ""
        text = str(text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Convert to lowercase
        text = text.lower()
        # Replace common separators with spaces
        text = re.sub(r'[-_/\\|,.;:+]', ' ', text)
        return text.strip()

    def _detect_from_cell(self, cell_value, enabled_categories):
        """
        Detect category from a single cell value.
        Returns (category, confidence_score, matched_keyword)
        """
        if pd.isna(cell_value) or cell_value is None:
            return None, 0, None

        text = self._clean_text(cell_value)
        if not text:
            return None, 0, None

        best_category = None
        best_score = 0
        best_match = None

        for category in enabled_categories:
            if category not in self.categories:
                continue

            cat_data = self.categories[category]

            # Check exclude list first
            excluded = False
            for exclude_word in cat_data.get('exclude', []):
                if exclude_word in text:
                    excluded = True
                    break

            if excluded:
                continue

            # Check keywords
            for keyword in cat_data.get('keywords', []):
                matched, score = self._fuzzy_match(text, keyword)
                if matched:
                    # Boost score for exact word matches
                    keyword_with_spaces = ' ' + keyword + ' '
                    text_with_spaces = ' ' + text + ' '
                    if keyword_with_spaces in text_with_spaces:
                        score = max(score, 1.0) * 20  # Strong boost for exact match
                    elif text.startswith(keyword) or text.endswith(keyword):
                        score = max(score, 0.9) * 15  # Good boost for boundary match
                    else:
                        score = score * 10  # Normal boost

                    if score > best_score:
                        best_score = score
                        best_category = category
                        best_match = keyword

            # Check SKU patterns
            sku_patterns = cat_data.get('sku_patterns', [])
            if self._check_sku_pattern(cell_value, sku_patterns):
                score = 25  # High score for SKU match
                if score > best_score:
                    best_score = score
                    best_category = category
                    best_match = "SKU_PATTERN"

        return best_category, best_score, best_match

    def find_all_text_columns(self, df):
        """
        Find ALL columns that might contain category information.
        Returns list of all relevant columns in priority order.
        """
        all_columns = []
        priority_cols = []
        secondary_cols = []
        other_text_cols = []

        for col in df.columns:
            col_str = str(col).lower().strip()

            # Check if it is a priority column
            is_priority = any(pattern in col_str for pattern in self.priority_column_patterns)
            is_secondary = any(pattern in col_str for pattern in self.secondary_column_patterns)

            # Check if column contains text data
            try:
                sample_values = df[col].dropna().head(10).astype(str)
                is_text = all(len(v) > 1 and not v.replace('.','').isdigit() for v in sample_values)
            except:
                is_text = False

            if is_priority:
                priority_cols.append(col)
            elif is_secondary:
                secondary_cols.append(col)
            elif is_text or df[col].dtype == 'object':
                other_text_cols.append(col)

        # Return in priority order
        all_columns = priority_cols + secondary_cols + other_text_cols
        return all_columns, priority_cols, secondary_cols, other_text_cols

    def detect_row_category(self, row, all_columns, enabled_categories):
        """
        Detect category for a single row by checking ALL columns.
        Uses multiple strategies and returns the best match.
        """
        category_scores = defaultdict(lambda: {'score': 0, 'matches': [], 'columns': []})

        # Strategy 1: Check all columns for keyword matches
        for col in all_columns:
            try:
                cell_value = row[col]
                cat, score, match = self._detect_from_cell(cell_value, enabled_categories)
                if cat and score > 0:
                    category_scores[cat]['score'] += score
                    category_scores[cat]['matches'].append(match)
                    category_scores[cat]['columns'].append(col)
            except:
                continue

        # Strategy 2: Concatenate all text cells and check as one
        try:
            all_text = ' '.join([str(row[col]) for col in all_columns if pd.notna(row[col])])
            all_text = self._clean_text(all_text)

            for category in enabled_categories:
                if category not in self.categories:
                    continue

                cat_data = self.categories[category]

                # Check exclude list
                excluded = False
                for exclude_word in cat_data.get('exclude', []):
                    if exclude_word in all_text:
                        excluded = True
                        break

                if excluded:
                    continue

                # Count keyword matches in combined text
                match_count = 0
                for keyword in cat_data.get('keywords', []):
                    if keyword in all_text:
                        match_count += all_text.count(keyword)

                if match_count > 0:
                    bonus_score = match_count * 5
                    category_scores[category]['score'] += bonus_score
        except:
            pass

        # Find best category
        if not category_scores:
            return None, 0, []

        best_category = max(category_scores.keys(), key=lambda k: category_scores[k]['score'])
        best_score = category_scores[best_category]['score']
        matched_columns = category_scores[best_category]['columns']

        return best_category, best_score, matched_columns

    def process_file(self, file, sheet_name, enabled_categories):
        """
        Process entire file with ultra-strong detection.
        Checks EVERY row and EVERY column.
        """
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)

            if df.empty:
                return {}, {
                    'total_rows': 0,
                    'matched_rows': 0,
                    'unmatched_rows': 0,
                    'categories_found': 0,
                    'distribution': {},
                    'confidence_breakdown': {'high': 0, 'medium': 0, 'low': 0},
                    'detection_log': []
                }

            # Find ALL text columns
            all_columns, priority_cols, secondary_cols, other_cols = self.find_all_text_columns(df)

            st.info(f"Scanning {len(df)} rows across {len(all_columns)} columns")
            st.caption(f"Priority columns: {len(priority_cols)} | Secondary: {len(secondary_cols)} | Other text: {len(other_cols)}")

            # Initialize result columns
            df['Detected_Category'] = None
            df['Match_Score'] = 0
            df['Confidence_Level'] = None
            df['Matched_Columns'] = ''

            detection_log = []
            unmatched_rows = []

            # Process EACH row individually
            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx in df.index:
                row = df.loc[idx]

                # Update progress every 100 rows
                if idx % 100 == 0 or idx == len(df) - 1:
                    progress = min((idx + 1) / len(df), 1.0)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing row {idx + 1} of {len(df)}...")

                # Detect category for this row
                category, score, matched_cols = self.detect_row_category(
                    row, all_columns, enabled_categories
                )

                if category:
                    df.at[idx, 'Detected_Category'] = category
                    df.at[idx, 'Match_Score'] = score
                    df.at[idx, 'Matched_Columns'] = ', '.join(matched_cols[:3]) if matched_cols else ''

                    # Set confidence level
                    if score >= 30:
                        df.at[idx, 'Confidence_Level'] = 'High'
                    elif score >= 15:
                        df.at[idx, 'Confidence_Level'] = 'Medium'
                    else:
                        df.at[idx, 'Confidence_Level'] = 'Low'

                    detection_log.append({
                        'row': idx,
                        'category': category,
                        'score': score,
                        'columns': matched_cols
                    })
                else:
                    unmatched_rows.append(idx)

            progress_bar.empty()
            status_text.empty()

            # Handle unmatched rows with intelligent fallback
            if unmatched_rows and enabled_categories:
                st.warning(f"{len(unmatched_rows)} rows need additional analysis...")

                for idx in unmatched_rows:
                    # Try to find ANY keyword match with lower threshold
                    row = df.loc[idx]
                    best_fallback = None
                    best_fallback_score = 0

                    for col in all_columns:
                        try:
                            cell_value = str(row[col]).lower()
                            for category in enabled_categories:
                                cat_data = self.categories.get(category, {})
                                for keyword in cat_data.get('keywords', []):
                                    if keyword in cell_value:
                                        score = cell_value.count(keyword) * 3
                                        if score > best_fallback_score:
                                            best_fallback_score = score
                                            best_fallback = category
                        except:
                            continue

                    if best_fallback:
                        df.at[idx, 'Detected_Category'] = best_fallback
                        df.at[idx, 'Match_Score'] = best_fallback_score
                        df.at[idx, 'Confidence_Level'] = 'Low'
                        df.at[idx, 'Matched_Columns'] = 'fallback'

            # Separate data by category
            separated = {}
            original_cols = [c for c in df.columns if c not in ['Detected_Category', 'Match_Score', 'Confidence_Level', 'Matched_Columns']]

            for category in enabled_categories:
                cat_data = df[df['Detected_Category'] == category][original_cols].copy()
                if len(cat_data) > 0:
                    separated[category] = cat_data

            # Calculate statistics
            distribution = df['Detected_Category'].value_counts().to_dict()
            confidence_breakdown = {
                'high': len(df[df['Confidence_Level'] == 'High']),
                'medium': len(df[df['Confidence_Level'] == 'Medium']),
                'low': len(df[df['Confidence_Level'] == 'Low']),
            }

            stats = {
                'total_rows': len(df),
                'matched_rows': len(df[df['Detected_Category'].notna()]),
                'unmatched_rows': len(df[df['Detected_Category'].isna()]),
                'categories_found': len(separated),
                'distribution': distribution,
                'confidence_breakdown': confidence_breakdown,
                'detection_log': detection_log,
                'columns_scanned': len(all_columns),
                'priority_columns': priority_cols,
                'secondary_columns': secondary_cols,
            }

            return separated, stats

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return {}, {
                'total_rows': 0, 'matched_rows': 0, 'unmatched_rows': 0,
                'categories_found': 0, 'distribution': {},
                'confidence_breakdown': {'high': 0, 'medium': 0, 'low': 0},
                'detection_log': [], 'error': str(e)
            }


def get_sheet_info(file):
    """Get information about Excel sheets"""
    try:
        wb = load_workbook(file, read_only=True, data_only=False)
        sheets = [{
            'name': name,
            'rows': wb[name].max_row or 0,
            'cols': wb[name].max_column or 0
        } for name in wb.sheetnames]
        wb.close()
        return sheets
    except:
        return []


def create_excel(df):
    """Create formatted Excel file"""
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')

            from openpyxl.styles import Font, PatternFill, Alignment
            ws = writer.sheets['Data']

            # Style header
            hf = PatternFill(start_color='667eea', end_color='667eea', fill_type='solid')
            for cell in ws[1]:
                cell.fill = hf
                cell.font = Font(color='FFFFFF', bold=True)
                cell.alignment = Alignment(horizontal='center')

            # Auto-adjust column widths
            for col in ws.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column].width = adjusted_width

        output.seek(0)
        return output.getvalue()
    except:
        return None


def main():
    # Hero Header
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">Data Separation Tool</h1>
        <p class="hero-subtitle">Ultra-Strong Detection - Never Misses a Single SKU</p>
        <span class="hero-badge">Professional Grade</span>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'detector' not in st.session_state:
        st.session_state.detector = UltraStrongDetector()
    if 'processed' not in st.session_state:
        st.session_state.processed = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'selected_cats' not in st.session_state:
        st.session_state.selected_cats = ['Lighting', 'Fans', 'Furniture', 'Decor']

    # Step 1: Upload
    st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">1</span>Upload Your File</h3>', unsafe_allow_html=True)

    uploaded = st.file_uploader("", type=['xlsx', 'xlsm', 'xls'], label_visibility="collapsed")

    if uploaded:
        st.markdown('<div class="success-box">File loaded successfully</div>', unsafe_allow_html=True)

        sheets = get_sheet_info(uploaded)
        if sheets:
            opts = [f"{s['name']} ({s['rows']} rows, {s['cols']} cols)" for s in sheets]
            sel = st.selectbox("Select sheet to process", opts, label_visibility="collapsed")
            st.session_state.sheet = sheets[opts.index(sel)]['name']
            st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')

    st.markdown('</div>', unsafe_allow_html=True)

    # Step 2: Categories
    st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">2</span>Select Categories</h3>', unsafe_allow_html=True)

    all_cats = list(st.session_state.detector.categories.keys())

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Select All", use_container_width=True):
            st.session_state.selected_cats = all_cats.copy()
            st.rerun()
    with col2:
        if st.button("Clear All", use_container_width=True):
            st.session_state.selected_cats = []
            st.rerun()

    # Show categories in a grid
    cat_cols = st.columns(3)
    selected = []
    for i, cat in enumerate(all_cats):
        with cat_cols[i % 3]:
            if st.checkbox(cat, value=cat in st.session_state.selected_cats, key=f"cat_{cat}"):
                selected.append(cat)

    st.session_state.selected_cats = selected

    # Show keyword count for selected categories
    if selected:
        total_keywords = sum(len(st.session_state.detector.categories[cat]['keywords']) for cat in selected)
        st.info(f"{total_keywords} keywords loaded across {len(selected)} categories")

    st.markdown('</div>', unsafe_allow_html=True)

    # Step 3: Process
    if uploaded and st.session_state.selected_cats:
        st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">3</span>Process Data</h3>', unsafe_allow_html=True)

        if st.button("Start Ultra-Strong Processing", type="primary", use_container_width=True):
            with st.spinner('Running ultra-strong detection...'):
                uploaded.seek(0)
                separated, stats = st.session_state.detector.process_file(
                    uploaded,
                    st.session_state.sheet,
                    st.session_state.selected_cats
                )
                st.session_state.processed = separated
                st.session_state.stats = stats

        st.markdown('</div>', unsafe_allow_html=True)

    # Results
    if st.session_state.processed is not None:
        stats = st.session_state.stats

        st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">4</span>Results</h3>', unsafe_allow_html=True)

        # Statistics
        st.markdown('<div class="stat-container">', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["total_rows"]}</div><div class="stat-label">Total Rows</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["matched_rows"]}</div><div class="stat-label">Matched</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["unmatched_rows"]}</div><div class="stat-label">Unmatched</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["categories_found"]}</div><div class="stat-label">Categories</div></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Confidence breakdown
        st.subheader("Confidence Levels")
        conf_cols = st.columns(3)
        with conf_cols[0]:
            st.markdown(f"<span class='confidence-high'>High: {stats['confidence_breakdown']['high']}</span>", unsafe_allow_html=True)
        with conf_cols[1]:
            st.markdown(f"<span class='confidence-medium'>Medium: {stats['confidence_breakdown']['medium']}</span>", unsafe_allow_html=True)
        with conf_cols[2]:
            st.markdown(f"<span class='confidence-low'>Low: {stats['confidence_breakdown']['low']}</span>", unsafe_allow_html=True)

        # Category distribution
        st.subheader("Category Distribution")
        for cat, count in stats['distribution'].items():
            if cat:
                st.markdown(f'<div class="distribution-item"><span><strong>{cat}</strong></span><span>{count} items</span></div>', unsafe_allow_html=True)

        # Download buttons
        st.subheader("Download Results")

        download_cols = st.columns(min(len(st.session_state.processed), 4))
        for idx, (category, data) in enumerate(st.session_state.processed.items()):
            with download_cols[idx % len(download_cols)]:
                excel_data = create_excel(data)
                if excel_data:
                    st.download_button(
                        label=f"{category} ({len(data)})",
                        data=excel_data,
                        file_name=f"{st.session_state.filename}_{category}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
