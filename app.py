import streamlit as st
import pandas as pd
from openpyxl import load_workbook
import io
import re
from collections import defaultdict

st.set_page_config(page_title="Data Separation Tool", layout="wide", initial_sidebar_state="collapsed")

# CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main > div { background: #f8fafc; min-height: 100vh; padding: 2rem; }
    .hero-header {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
        padding: 3rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
    }
    .hero-title { color: #ffffff; font-size: 2.5rem; font-weight: 800; margin: 0; }
    .hero-subtitle { color: rgba(255, 255, 255, 0.9); font-size: 1.1rem; margin-top: 0.5rem; }
    .premium-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 1.5rem;
        border: 1px solid #e5e7eb;
    }
    .card-title { color: #1e293b; font-size: 1.3rem; font-weight: 700; margin-bottom: 1.2rem; display: flex; align-items: center; gap: 0.5rem; }
    .card-number {
        display: inline-flex; align-items: center; justify-content: center;
        width: 32px; height: 32px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border-radius: 8px; font-size: 1rem; font-weight: 700;
    }
    .success-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 4px solid #10b981;
        color: #065f46; padding: 1rem 1.2rem; border-radius: 10px; margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        color: #92400e; padding: 1rem 1.2rem; border-radius: 10px; margin: 1rem 0;
    }
    .stat-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.2rem; margin: 1.5rem 0;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.8rem; border-radius: 16px;
        color: white; text-align: center;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    }
    .stat-number { font-size: 2.5rem; font-weight: 800; margin-bottom: 0.3rem; }
    .stat-label { font-size: 0.9rem; opacity: 0.95; font-weight: 500; text-transform: uppercase; }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; padding: 0.9rem 2rem;
        border-radius: 12px; font-weight: 600; font-size: 1rem; width: 100%;
    }
    .stDownloadButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white; border: none; padding: 1rem 1.5rem;
        border-radius: 12px; font-weight: 600; width: 100%;
    }
    .distribution-item {
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
        padding: 1rem 1.5rem; border-radius: 12px; margin: 0.5rem 0;
        display: flex; justify-content: space-between; align-items: center;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)


class DataSeparator:
    """Fixed and working data separator - checks all columns properly"""

    def __init__(self):
        # COMPREHENSIVE KEYWORDS - organized by category
        self.categories = {
            'Fans': {
                'keywords': [
                    'fan', 'fans', 'ceiling fan', 'table fan', 'wall fan', 'floor fan', 'exhaust fan',
                    'ventilator', 'blower', 'cooling fan', 'pedestal fan', 'tower fan', 'stand fan',
                    'desk fan', 'box fan', 'window fan', 'attic fan', 'bathroom fan', 'kitchen fan',
                    'range hood fan', 'inline fan', 'centrifugal fan', 'axial fan', 'ventilation fan',
                    'air circulator', 'air mover', 'extractor fan', 'intake fan', 'circulation fan',
                    'oscillating fan', 'industrial fan', 'portable fan', 'rechargeable fan',
                    'solar fan', 'battery fan', 'usb fan', 'mini fan', 'personal fan', 'neck fan',
                    'handheld fan', 'clip fan', 'bracket fan', 'duct fan', 'inline duct fan',
                    'booster fan', 'pressure fan', 'suction fan', 'supply fan', 'return fan',
                    'makeup air fan', 'spot cooler', 'portable cooler', 'swamp cooler',
                    'fan blade', 'fan motor', 'fan guard', 'fan cage', 'fan grill',
                    'fan controller', 'fan speed', 'fan switch', 'fan timer', 'fan remote',
                    'fan light kit', 'fan downrod', 'fan canopy', 'fan mounting bracket',
                    'ventilation grille', 'air vent', 'air register', 'air diffuser',
                    'vent cover', 'vent cap', 'vent hood', 'range hood', 'cooker hood',
                    'extractor hood', 'fume hood', 'laboratory hood', 'louvre', 'louver',
                ],
                'exclude': ['light', 'lamp', 'bulb', 'led', 'chandelier', 'pendant']
            },

            'Lighting': {
                'keywords': [
                    'light', 'lights', 'lamp', 'lamps', 'bulb', 'bulbs', 'lighting', 'led', 'fixture',
                    'chandelier', 'chandeliers', 'pendant', 'pendants', 'pendant light', 'downlight',
                    'downlights', 'spotlight', 'spotlights', 'track light', 'track lighting',
                    'ceiling light', 'wall light', 'floor lamp', 'table lamp', 'desk lamp',
                    'reading lamp', 'bedside lamp', 'night light', 'accent light', 'ambient light',
                    'task light', 'decorative light', 'crystal chandelier', 'modern chandelier',
                    'mini chandelier', 'island pendant', 'flush mount', 'semi flush',
                    'close to ceiling', 'recessed light', 'can light', 'pot light', 'gimbal light',
                    'eyeball light', 'adjustable downlight', 'baffle trim', 'reflector trim',
                    'wall sconce', 'vanity light', 'bathroom light', 'mirror light',
                    'picture light', 'art light', 'wall washer', 'uplight', 'torchiere',
                    'arc lamp', 'tripod lamp', 'tree lamp', 'pharmacy lamp', 'banker lamp',
                    'touch lamp', 'clip lamp', 'led strip', 'led tape', 'led ribbon',
                    'under cabinet light', 'puck light', 'rope light', 'neon light',
                    'flexible light', 'tape light', 'outdoor light', 'exterior light',
                    'landscape light', 'path light', 'flood light', 'floodlight',
                    'security light', 'motion light', 'dusk to dawn', 'solar light',
                    'garden light', 'deck light', 'step light', 'post light', 'bollard light',
                    'well light', 'inground light', 'underwater light', 'pool light',
                    'spa light', 'fountain light', 'pond light', 'street light', 'area light',
                    'parking lot light', 'shoebox light', 'wall pack', 'canopy light',
                    'soffit light', 'eave light', 'high bay', 'low bay', 'warehouse light',
                    'industrial light', 'shop light', 'garage light', 'workshop light',
                    'utility light', 'emergency light', 'exit sign', 'egress light',
                    'safety light', 'grow light', 'plant light', 'aquarium light',
                    'terrarium light', 'black light', 'uv light', 'germicidal light',
                    'therapy light', 'sad light', 'daylight lamp', 'full spectrum',
                    'smart light', 'wifi light', 'bluetooth light', 'color changing',
                    'rgb light', 'rgbw', 'tunable white', 'dim to warm', 'dimmable',
                    'dimmable led', 'three way', 'touch dimmer', 'remote dimmer',
                    'edison bulb', 'filament bulb', 'vintage bulb', 'antique bulb',
                    'halogen', 'incandescent', 'cfl', 'compact fluorescent', 'hid',
                    'metal halide', 'high pressure sodium', 'mercury vapor',
                    'tube light', 'fluorescent tube', 't5', 't8', 't12', 'led tube',
                    'candle bulb', 'globe bulb', 'par bulb', 'mr bulb', 'br bulb',
                    'gu10', 'mr16', 'e26', 'e27', 'e12', 'e14', 'b22', 'g4', 'g9',
                    'light switch', 'dimmer switch', 'timer switch', 'motion sensor',
                    'daylight sensor', 'occupancy sensor', 'photocell',
                    'light fixture', 'light fitting', 'light housing', 'light trim',
                    'light shade', 'lamp shade', 'diffuser', 'lens', 'reflector', 'baffle',
                    'ballast', 'driver', 'transformer', 'power supply', 'led driver',
                    'light socket', 'lamp holder', 'bulb holder',
                ],
                'exclude': ['fan', 'ventilator', 'blower', 'exhaust', 'cooling']
            },

            'Furniture': {
                'keywords': [
                    'chair', 'chairs', 'seat', 'seating', 'stool', 'stools', 'bench', 'benches',
                    'ottoman', 'ottomans', 'armchair', 'armchairs', 'accent chair',
                    'side chair', 'dining chair', 'kitchen chair', 'office chair',
                    'desk chair', 'computer chair', 'task chair', 'executive chair',
                    'ergonomic chair', 'gaming chair', 'recliner', 'recliners',
                    'reclining chair', 'lift chair', 'rocking chair', 'rocker',
                    'glider', 'swivel chair', 'barrel chair', 'wingback chair',
                    'club chair', 'slipper chair', 'parsons chair', 'folding chair',
                    'stackable chair', 'banquet chair', 'chiavari chair', 'bar stool',
                    'counter stool', 'backless stool', 'saddle stool', 'sofa', 'sofas',
                    'couch', 'couches', 'settee', 'loveseat', 'sectional', 'sectionals',
                    'modular sofa', 'sleeper sofa', 'sofa bed', 'futon', 'daybed',
                    'chaise', 'chaise lounge', 'footstool', 'footrest', 'pouf', 'pouffe',
                    'hassock', 'bean bag', 'gaming seat', 'massage chair', 'zero gravity chair',
                    'table', 'tables', 'desk', 'desks', 'workstation', 'workbench',
                    'dining table', 'kitchen table', 'breakfast table', 'nook table',
                    'coffee table', 'cocktail table', 'accent table', 'side table',
                    'end table', 'console table', 'sofa table', 'hallway table',
                    'entryway table', 'nightstand', 'nightstands', 'night table',
                    'bedside table', 'bedside cabinet', 'dresser', 'dressers',
                    'chest of drawers', 'bureau', 'highboy', 'lowboy', 'wardrobe',
                    'armoire', 'chiffonier', 'gentlemans chest', 'tv stand',
                    'tv console', 'media console', 'entertainment center', 'bookcase',
                    'bookshelf', 'shelving unit', 'etagere', 'bakers rack',
                    'filing cabinet', 'file cabinet', 'lateral file', 'vertical file',
                    'credenza', 'sideboard', 'buffet', 'hutch', 'china cabinet',
                    'curio', 'office desk', 'computer desk', 'writing desk',
                    'secretary desk', 'standing desk', 'adjustable desk', 'sit stand desk',
                    'converter', 'drafting table', 'drawing table', 'art table',
                    'hobby table', 'conference table', 'meeting table', 'boardroom table',
                    'training table', 'folding table', 'banquet table', 'picnic table',
                    'patio table', 'bar table', 'pub table', 'bistro table', 'high top table',
                    'nesting table', 'nest of tables', 'bed', 'beds', 'bed frame',
                    'platform bed', 'panel bed', 'sleigh bed', 'canopy bed',
                    'four poster bed', 'poster bed', 'storage bed', 'captains bed',
                    'mate bed', 'murphy bed', 'wall bed', 'bunk bed', 'loft bed',
                    'trundle bed', 'futon bed', 'headboard', 'footboard', 'bed rails',
                    'bed slats', 'box spring', 'mattress foundation', 'bed base',
                    'adjustable base', 'bed legs', 'cabinet', 'cabinets', 'cupboard',
                    'closet', 'storage', 'organizer', 'shelf', 'shelves', 'shelving',
                    'rack', 'stand', 'holder', 'storage bin', 'storage box',
                    'storage basket', 'storage crate', 'drawer', 'drawers', 'drawer unit',
                    'cart', 'trolley', 'island', 'pantry', 'larder', 'wine rack',
                    'shoe rack', 'coat rack', 'hat stand', 'jewelry armoire',
                    'jewelry cabinet', 'mirror cabinet', 'medicine cabinet',
                    'patio furniture', 'outdoor furniture', 'garden furniture',
                    'lawn furniture', 'deck furniture', 'balcony furniture',
                    'porch furniture', 'adirondack chair', 'lawn chair', 'beach chair',
                    'folding lawn chair', 'garden bench', 'park bench', 'porch swing',
                    'swing seat', 'hammock', 'outdoor sofa', 'patio sofa',
                    'sectional outdoor', 'outdoor sectional', 'outdoor dining set',
                    'patio dining set', 'garden dining set', 'umbrella', 'parasol',
                    'shade sail', 'pergola', 'gazebo', 'arbor', 'crib', 'cot',
                    'bassinet', 'cradle', 'changing table', 'nursery furniture',
                    'kids bed', 'toddler bed', 'twin bed', 'kids desk', 'study desk',
                    'activity table', 'play table', 'train table', 'toy box',
                    'toy chest', 'toy storage', 'book sling', 'kids bookshelf',
                ],
                'exclude': []
            },

            'Decor': {
                'keywords': [
                    'decor', 'decoration', 'decorative', 'wall decor', 'wall art', 'artwork',
                    'painting', 'canvas art', 'framed art', 'print', 'prints', 'poster',
                    'wall hanging', 'tapestry', 'wall tapestry', 'macrame', 'wall macrame',
                    'woven wall art', 'metal wall art', 'wood wall art', 'canvas print',
                    'photo print', 'mirror', 'mirrors', 'wall mirror', 'floor mirror',
                    'full length mirror', 'vanity mirror', 'decorative mirror',
                    'accent mirror', 'sunburst mirror', 'round mirror', 'oval mirror',
                    'rectangular mirror', 'square mirror', 'framed mirror',
                    'frameless mirror', 'beveled mirror', 'led mirror', 'clock', 'clocks',
                    'wall clock', 'mantel clock', 'table clock', 'alarm clock',
                    'floating shelf', 'ledge shelf', 'picture ledge', 'display shelf',
                    'wall shelf', 'corner shelf', 'cube shelf', 'hexagon shelf',
                    'geometric shelf', 'vase', 'vases', 'flower vase', 'bud vase',
                    'floor vase', 'ceramic vase', 'glass vase', 'crystal vase',
                    'metal vase', 'wood vase', 'basket', 'baskets', 'bowl', 'bowls',
                    'decorative bowl', 'centerpiece bowl', 'fruit bowl', 'planter',
                    'planters', 'flower pot', 'plant pot', 'cachepot', 'urn', 'urns',
                    'jar', 'jars', 'canister', 'canisters', 'bottle', 'bottles',
                    'decanter', 'pitcher', 'ewer', 'amphora', 'terracotta', 'clay pot',
                    'concrete pot', 'sculpture', 'sculptures', 'statue', 'statues',
                    'figurine', 'figurines', 'bust', 'busts', 'art object', 'curio',
                    'collectible', 'ornament', 'ornaments', 'keepsake', 'memento',
                    'souvenir', 'bookend', 'bookends', 'paperweight', 'desk accessory',
                    'trinket', 'pillow', 'pillows', 'cushion', 'cushions', 'throw pillow',
                    'accent pillow', 'decorative pillow', 'lumbar pillow', 'euro sham',
                    'pillow sham', 'pillow cover', 'cushion cover', 'pillow insert',
                    'cushion insert', 'blanket', 'blankets', 'throw', 'throws',
                    'afghan', 'quilt', 'quilts', 'coverlet', 'bedspread', 'comforter',
                    'duvet', 'duvet cover', 'bed skirt', 'dust ruffle', 'rug', 'rugs',
                    'area rug', 'throw rug', 'accent rug', 'runner', 'runners', 'carpet',
                    'mat', 'mats', 'doormat', 'bath mat', 'kitchen mat', 'accent mat',
                    'curtain', 'curtains', 'drape', 'drapes', 'window panel',
                    'sheer curtain', 'valance', 'cornice', 'swag', 'tier curtain',
                    'cafe curtain', 'panel pair', 'candle', 'candles', 'pillar candle',
                    'taper candle', 'votive candle', 'tea light', 'led candle',
                    'flameless candle', 'scented candle', 'candle holder', 'candleholder',
                    'candlestick', 'candelabra', 'votive holder', 'tea light holder',
                    'pillar holder', 'taper holder', 'hurricane candle', 'lantern',
                    'lanterns', 'candle lantern', 'metal lantern', 'wood lantern',
                    'frame', 'frames', 'picture frame', 'photo frame', 'collage frame',
                    'gallery frame', 'float frame', 'shadow box', 'document frame',
                    'diploma frame', 'album', 'albums', 'photo album', 'scrapbook',
                    'memory book', 'guest book', 'wreath', 'wreaths', 'door wreath',
                    'seasonal decor', 'holiday decor', 'christmas decor', 'halloween decor',
                    'easter decor', 'fall decor', 'spring decor', 'summer decor',
                    'winter decor', 'harvest decor', 'garland', 'garlands', 'topiary',
                    'topiaries', 'faux plant', 'artificial plant', 'silk plant',
                    'plastic plant', 'faux flower', 'artificial flower', 'silk flower',
                    'dried flower', 'preserved flower', 'flower arrangement',
                    'floral arrangement', 'bouquet', 'succulent', 'succulents',
                    'air plant', 'cactus', 'cacti', 'bonsai', 'fiddle leaf', 'monstera',
                    'palm', 'fern', 'ferns', 'greenery', 'foliage', 'stem', 'stems',
                    'branch', 'branches', 'twig', 'dried botanical', 'pampas grass',
                    'eucalyptus', 'lavender', 'wheat', 'tray', 'trays', 'serving tray',
                    'decorative tray', 'ottoman tray', 'jewelry box', 'keepsake box',
                    'memory box', 'treasure box', 'trinket box', 'watch box',
                    'cufflink box', 'tie box', 'valet tray', 'catchall tray',
                    'screen', 'screens', 'room divider', 'folding screen',
                    'privacy screen', 'divider', 'dividers', 'panel screen',
                    'shoji screen', 'rattan screen', 'fireplace screen', 'spark guard',
                    'fire screen', 'andiron', 'fire tool', 'wall panel', '3d panel',
                    'acoustic panel', 'slat panel',
                ],
                'exclude': []
            },

            'Electronics': {
                'keywords': [
                    'tv', 'television', 'televisions', 'smart tv', 'led tv', 'oled tv',
                    'qled tv', '4k tv', '8k tv', 'ultra hd', 'full hd', 'flat screen',
                    'curved tv', 'monitor', 'monitors', 'computer monitor', 'gaming monitor',
                    'ultrawide', 'display', 'displays', 'screen', 'screens',
                    'digital display', 'signage', 'projector', 'projectors',
                    'home projector', 'portable projector', 'speaker', 'speakers',
                    'audio', 'sound', 'soundbar', 'sound bar', 'bluetooth speaker',
                    'wireless speaker', 'portable speaker', 'smart speaker',
                    'bookshelf speaker', 'floor speaker', 'tower speaker', 'center speaker',
                    'subwoofer', 'sub', 'woofer', 'bass speaker', 'surround speaker',
                    'home theater', 'home theatre', 'hifi', 'hi fi', 'stereo',
                    'stereo system', 'amplifier', 'amp', 'receiver', 'av receiver',
                    'audio receiver', 'turntable', 'record player', 'vinyl player',
                    'dj equipment', 'mixer', 'headphone', 'headphones', 'earphone',
                    'earphones', 'earbud', 'earbuds', 'headset', 'gaming headset',
                    'wireless headphone', 'noise cancelling', 'microphone', 'mic',
                    'condenser mic', 'dynamic mic', 'usb mic', 'computer', 'computers',
                    'desktop', 'laptop', 'laptops', 'notebook', 'netbook', 'tablet',
                    'tablets', 'ipad', 'android tablet', '2 in 1', 'convertible',
                    'chromebook', 'gaming pc', 'workstation', 'all in one', 'mini pc',
                    'nuc', 'barebone', 'keyboard', 'keyboards', 'mechanical keyboard',
                    'gaming keyboard', 'mouse', 'mice', 'gaming mouse', 'wireless mouse',
                    'trackball', 'trackpad', 'webcam', 'web camera', 'document camera',
                    'visual presenter', 'printer', 'printers', 'inkjet', 'laser printer',
                    'all in one printer', 'scanner', 'scanners', 'flatbed scanner',
                    'document scanner', 'photo scanner', '3d printer', 'label printer',
                    'receipt printer', 'thermal printer', 'cartridge', 'ink cartridge',
                    'toner', 'toner cartridge', 'drum unit', 'router', 'routers',
                    'wifi router', 'wireless router', 'mesh router', 'modem',
                    'cable modem', 'dsl modem', 'gateway', 'network switch',
                    'extender', 'range extender', 'wifi extender', 'access point',
                    'repeater', 'network adapter', 'wifi adapter', 'ethernet adapter',
                    'powerline', 'network cable', 'ethernet cable', 'patch cable',
                    'hdmi cable', 'usb cable', 'smart home', 'home automation',
                    'smart device', 'connected device', 'smart plug', 'smart switch',
                    'smart bulb', 'smart light', 'smart lock', 'doorbell',
                    'video doorbell', 'smart doorbell', 'security camera', 'ip camera',
                    'wifi camera', 'baby monitor', 'pet camera', 'dash cam',
                    'thermostat', 'smart thermostat', 'temperature controller',
                    'sensor', 'sensors', 'motion sensor', 'door sensor', 'window sensor',
                    'smoke detector', 'co detector', 'carbon monoxide', 'water leak detector',
                    'hub', 'smart hub', 'bridge', 'controller', 'remote control',
                    'universal remote', 'game console', 'gaming console', 'playstation',
                    'xbox', 'nintendo', 'game controller', 'gamepad', 'joystick',
                    'racing wheel', 'vr', 'virtual reality', 'vr headset', 'oculus',
                    'htc vive', 'psvr', 'phone', 'phones', 'smartphone', 'mobile phone',
                    'cell phone', 'iphone', 'android phone', 'case', 'phone case',
                    'screen protector', 'charger', 'power bank', 'battery pack',
                    'portable charger', 'wireless charger', 'cable', 'cables',
                    'charging cable', 'data cable', 'adapter', 'dongle', 'camera',
                    'cameras', 'digital camera', 'dslr', 'mirrorless', 'compact camera',
                    'action camera', 'gopro', 'instant camera', 'polaroid', 'film camera',
                    'lens', 'camera lens', 'tripod', 'camera bag', 'memory card', 'sd card',
                    'vacuum', 'vacuum cleaner', 'robot vacuum', 'cordless vacuum',
                    'stick vacuum', 'cooler', 'heater', 'space heater', 'air purifier',
                    'humidifier', 'dehumidifier', 'diffuser', 'essential oil',
                    'air fryer', 'toaster oven',
                ],
                'exclude': []
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
                    'dishwasher', 'dishwashers', 'built in dishwasher',
                    'portable dishwasher', 'range hood', 'hood', 'vent hood',
                    'island hood', 'wall hood', 'trash compactor', 'garbage disposal',
                    'disposal', 'compactor', 'blender', 'blenders', 'mixer', 'mixers',
                    'stand mixer', 'hand mixer', 'food processor', 'chopper',
                    'food chopper', 'mini chopper', 'coffee maker', 'coffee machine',
                    'espresso machine', 'cappuccino maker', 'kettle', 'electric kettle',
                    'gooseneck kettle', 'tea kettle', 'toaster', 'toasters',
                    'toaster oven', 'air fryer', 'airfryer', 'pressure cooker',
                    'instant pot', 'slow cooker', 'crock pot', 'rice cooker',
                    'steamer', 'food steamer', 'sous vide', 'immersion circulator',
                    'griddle', 'grill', 'electric grill', 'panini press',
                    'sandwich maker', 'waffle maker', 'waffle iron', 'pancake maker',
                    'crepe maker', 'juicer', 'juicers', 'citrus juicer',
                    'masticating juicer', 'centrifugal', 'dehydrator', 'food dehydrator',
                    'yogurt maker', 'bread maker', 'ice cream maker', 'pot', 'pots',
                    'pan', 'pans', 'cookware set', 'saucepan', 'saucepans',
                    'stock pot', 'dutch oven', 'french oven', 'frying pan', 'skillet',
                    'saute pan', 'grill pan', 'griddle pan', 'wok', 'stir fry pan',
                    'paella pan', 'crepe pan', 'omelet pan', 'roasting pan', 'roaster',
                    'baking dish', 'casserole dish', 'lasagna pan', 'sheet pan',
                    'baking sheet', 'cookie sheet', 'jelly roll pan', 'muffin pan',
                    'cupcake pan', 'cake pan', 'round cake pan', 'square cake pan',
                    'bundt pan', 'loaf pan', 'bread pan', 'pie pan', 'pie dish',
                    'tart pan', 'springform pan', 'tube pan', 'angel food pan',
                    'madeleine pan', 'baking', 'bakeware', 'baking set', 'baking tools',
                    'pastry tools', 'mixing bowl', 'mixing bowls', 'prep bowl',
                    'nesting bowl', 'measuring cup', 'measuring cups', 'measuring spoon',
                    'measuring spoons', 'scale', 'kitchen scale', 'food scale',
                    'digital scale', 'timer', 'kitchen timer', 'thermometer',
                    'meat thermometer', 'oven thermometer', 'rolling pin', 'pastry cutter',
                    'pastry brush', 'basting brush', 'spatula', 'spatulas',
                    'rubber spatula', 'silicone spatula', 'offset spatula', 'whisk',
                    'whisks', 'balloon whisk', 'flat whisk', 'silicone whisk', 'tongs',
                    'kitchen tongs', 'salad tongs', 'pasta tongs', 'ladle', 'ladles',
                    'soup ladle', 'gravy ladle', 'skimmer', 'slotted spoon',
                    'solid spoon', 'serving spoon', 'turner', 'flipper', 'spatula turner',
                    'fish turner', 'pancake turner', 'peeler', 'vegetable peeler',
                    'potato peeler', 'julienne peeler', 'grater', 'graters',
                    'box grater', 'microplane', 'zester', 'citrus zester', 'colander',
                    'colanders', 'strainer', 'strainers', 'sieve', 'fine mesh',
                    'salad spinner', 'lettuce spinner', 'herb spinner', 'cutting board',
                    'chopping board', 'butcher block', 'carving board', 'knife', 'knives',
                    'chef knife', 'paring knife', 'bread knife', 'santoku', 'utility knife',
                    'boning knife', 'filleting knife', 'knife set', 'knife block',
                    'knife sharpener', 'honing steel', 'shears', 'kitchen shears',
                    'poultry shears', 'scissors', 'container', 'containers',
                    'food container', 'storage container', 'tupperware', 'plastic container',
                    'glass container', 'stainless container', 'canister', 'canisters',
                    'jar', 'jars', 'mason jar', 'cookie jar', 'spice rack',
                    'spice organizer', 'spice jar', 'spice bottle', 'bread box',
                    'bread bin', 'fruit bowl', 'fruit basket', 'egg holder', 'utensil',
                    'utensils', 'kitchen utensil', 'cooking utensil', 'gadget',
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
                'exclude': []
            },

            'Bathroom': {
                'keywords': [
                    'bathroom', 'bath', 'toilet', 'toilets', 'sink', 'sinks', 'basin',
                    'basins', 'vanity', 'vanities', 'shower', 'showers', 'bathtub',
                    'bathtubs', 'bath tub', 'jacuzzi', 'whirlpool', 'sauna', 'steam room',
                    'bidet', 'faucet', 'faucets', 'tap', 'taps', 'mixer tap', 'shower head',
                    'hand shower', 'rain shower', 'toilet seat', 'toilet paper holder',
                    'towel bar', 'towel rack', 'towel ring', 'robe hook', 'soap dispenser',
                    'toothbrush holder', 'tumbler', 'trash can', 'bath mat', 'bath rug',
                    'shower curtain', 'shower caddy', 'shower organizer', 'bathroom cabinet',
                    'medicine cabinet', 'mirror cabinet', 'bathroom shelf', 'bathroom organizer',
                    'bathroom storage', 'bathroom accessory', 'bathroom set', 'bath towel',
                    'hand towel', 'washcloth', 'bathrobe', 'shower door', 'shower enclosure',
                    'tub surround', 'bathroom mirror', 'vanity mirror', 'vanity light',
                    'bathroom fan', 'exhaust fan', 'ventilation fan',
                ],
                'exclude': []
            },

            'Outdoor': {
                'keywords': [
                    'outdoor', 'patio', 'garden', 'lawn', 'yard', 'backyard', 'bbq', 'grill',
                    'barbecue', 'charcoal grill', 'gas grill', 'electric grill', 'smoker',
                    'patio heater', 'fire pit', 'firepit', 'chiminea', 'outdoor fireplace',
                    'patio furniture', 'outdoor furniture', 'garden furniture', 'lawn furniture',
                    'deck furniture', 'balcony furniture', 'porch furniture', 'gazebo',
                    'pergola', 'arbor', 'trellis', 'fence', 'fencing', 'gate', 'planter',
                    'planters', 'flower pot', 'garden pot', 'raised bed', 'garden bed',
                    'compost bin', 'rain barrel', 'garden shed', 'greenhouse', 'cold frame',
                    'lawn mower', 'grass cutter', 'trimmer', 'hedge trimmer', 'leaf blower',
                    'pressure washer', 'power washer', 'hose', 'garden hose', 'sprinkler',
                    'irrigation', 'outdoor light', 'solar light', 'path light', 'spotlight',
                    'floodlight', 'hammock', 'swing', 'porch swing', 'outdoor cushion',
                    'patio umbrella', 'market umbrella', 'cantilever umbrella', 'shade sail',
                    'patio cover', 'awning', 'canopy', 'deck box', 'storage bench',
                    'potting bench', 'garden tool', 'shovel', 'rake', 'hoe', 'trowel',
                    'pruner', 'shears', 'lopper', 'wheelbarrow', 'garden cart',
                ],
                'exclude': []
            },

            'Hardware': {
                'keywords': [
                    'hardware', 'tool', 'tools', 'power tool', 'hand tool', 'cordless tool',
                    'drill', 'drills', 'cordless drill', 'hammer drill', 'impact driver',
                    'impact wrench', 'saw', 'saws', 'circular saw', 'jigsaw', 'reciprocating saw',
                    'miter saw', 'chop saw', 'table saw', 'band saw', 'scroll saw',
                    'chainsaw', 'pole saw', 'sander', 'sanders', 'orbital sander',
                    'belt sander', 'random orbit', 'sheet sander', 'detail sander',
                    'grinder', 'grinders', 'angle grinder', 'bench grinder', 'die grinder',
                    'router', 'routers', 'trim router', 'plunge router', 'cnc router',
                    'nailer', 'nail gun', 'stapler', 'staple gun', 'brad nailer',
                    'finish nailer', 'framing nailer', 'roofing nailer', 'floor nailer',
                    'compressor', 'air compressor', 'generator', 'portable generator',
                    'inverter generator', 'ladder', 'ladders', 'step ladder', 'extension ladder',
                    'telescoping ladder', 'multi ladder', 'platform ladder', 'scaffold',
                    'scaffolding', 'work platform', 'sawhorse', 'work bench', 'tool box',
                    'tool chest', 'tool cabinet', 'tool bag', 'tool belt', 'tool organizer',
                    'screwdriver', 'screwdrivers', 'wrench', 'wrenches', 'socket set',
                    'socket wrench', 'ratchet', 'pliers', 'hammer', 'hammers', 'mallet',
                    'tape measure', 'level', 'laser level', 'square', 'speed square',
                    'combination square', 'chalk line', 'stud finder', 'fastener', 'fasteners',
                    'screw', 'screws', 'bolt', 'bolts', 'nut', 'nuts', 'washer', 'washers',
                    'anchor', 'anchors', 'nail', 'nails', 'staple', 'staples', 'brad',
                    'hinge', 'hinges', 'door hinge', 'cabinet hinge', 'handle', 'handles',
                    'door handle', 'cabinet handle', 'drawer handle', 'knob', 'knobs',
                    'door knob', 'cabinet knob', 'drawer knob', 'pull', 'pulls', 'drawer pull',
                    'lock', 'locks', 'deadbolt', 'door lock', 'padlock', 'combination lock',
                    'key lock', 'smart lock', 'chain', 'chains', 'rope', 'ropes', 'twine',
                    'cable', 'cables', 'wire', 'wires', 'bungee', 'strap', 'straps',
                ],
                'exclude': []
            },

            'Plumbing': {
                'keywords': [
                    'plumbing', 'pipe', 'pipes', 'piping', 'fitting', 'fittings', 'connector',
                    'coupling', 'union', 'adapter', 'valve', 'valves', 'ball valve',
                    'gate valve', 'globe valve', 'check valve', 'faucet', 'faucets',
                    'tap', 'taps', 'mixer tap', 'shower valve', 'stop valve', 'shutoff valve',
                    'drain', 'drains', 'sink drain', 'shower drain', 'floor drain',
                    'catch basin', 'floor sink', 'trap', 'traps', 'p trap', 's trap',
                    'bottle trap', 'water heater', 'tankless heater', 'instant water heater',
                    'pump', 'pumps', 'sump pump', 'sewage pump', 'utility pump',
                    'transfer pump', 'circulating pump', 'booster pump', 'toilet', 'toilets',
                    'wc', 'water closet', 'commode', 'urinal', 'bidet', 'toilet tank',
                    'flush valve', 'fill valve', 'flapper', 'sewer', 'sewage', 'septic',
                    'drainage', 'storm drain', 'gutter', 'gutters', 'downspout',
                    'water softener', 'water filter', 'reverse osmosis', 'ro system',
                    'whole house filter', 'under sink filter', 'faucet filter',
                    'hose', 'hoses', 'garden hose', 'washer hose', 'supply line',
                    'flexible hose', 'braided hose', 'pipe insulation', 'heat tape',
                    'pipe wrap', 'frost protection', 'pipe clamp', 'pipe hanger',
                    'pipe support', 'pipe bracket',
                ],
                'exclude': []
            },

            'Electrical': {
                'keywords': [
                    'electrical', 'electric', 'wiring', 'wire', 'wires', 'cable', 'cables',
                    'conductor', 'circuit', 'outlet', 'outlets', 'receptacle', 'receptacles',
                    'socket', 'sockets', 'wall outlet', 'gfci', 'gfi', 'ground fault',
                    'switch', 'switches', 'light switch', 'dimmer switch', 'timer switch',
                    'motion switch', 'smart switch', 'three way switch', 'four way switch',
                    'breaker', 'breakers', 'circuit breaker', 'breaker panel', 'panel',
                    'electrical panel', 'load center', 'fuse box', 'fuse', 'fuses',
                    'junction box', 'outlet box', 'switch box', 'gang box', 'old work box',
                    'new work box', 'ceiling box', 'conduit', 'conduits', 'emt',
                    'pvc conduit', 'flexible conduit', 'liquidtight', 'flex pipe',
                    'fixture', 'fixtures', 'light fixture', 'ceiling fixture',
                    'wall fixture', 'outdoor fixture', 'security light fixture',
                    'bulb', 'bulbs', 'led bulb', 'cfl bulb', 'halogen bulb',
                    'incandescent bulb', 'fluorescent', 'extension cord', 'power cord',
                    'power strip', 'surge protector', 'ups', 'uninterruptible power supply',
                    'smoke detector', 'smoke alarm', 'carbon monoxide detector',
                    'co detector', 'alarm', 'fire alarm', 'heat detector',
                    'fan', 'exhaust fan', 'ventilation fan', 'bathroom fan',
                    'attic fan', 'whole house fan', 'heater', 'baseboard heater',
                    'wall heater', 'space heater', 'garage heater', 'thermostat',
                    'programmable thermostat', 'smart thermostat', 'line voltage thermostat',
                    'low voltage thermostat', 'transformer', 'doorbell transformer',
                    'low voltage transformer', 'landscape transformer',
                ],
                'exclude': []
            },
        }

        # Column patterns to check
        self.priority_patterns = [
            'category', 'categories', 'cat', 'product category', 'item category',
            'type', 'product type', 'item type', 'product_type', 'item_type',
            'class', 'classification', 'group', 'department', 'section',
            'family', 'product family', 'line', 'product line', 'series',
        ]

        self.secondary_patterns = [
            'description', 'desc', 'product description', 'item description',
            'name', 'product name', 'item name', 'product_name', 'item_name', 'title',
            'product', 'item', 'sku', 'model', 'model number', 'part number', 'partno',
            'brand', 'manufacturer', 'mfg', 'vendor', 'supplier',
            'short description', 'brief description', 'summary', 'details',
        ]

    def clean_text(self, text):
        """Clean text for matching"""
        if pd.isna(text) or text is None:
            return ""
        text = str(text).lower().strip()
        # Replace separators with spaces
        for char in '-_/\\|,.;:+=':
            text = text.replace(char, ' ')
        # Remove extra spaces
        text = ' '.join(text.split())
        return text

    def detect_category(self, text, enabled_categories):
        """
        Detect category from text.
        Returns (category, score, matched_keyword)
        """
        if not text:
            return None, 0, None

        text_clean = self.clean_text(text)
        if not text_clean:
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
                if exclude_word in text_clean:
                    excluded = True
                    break

            if excluded:
                continue

            # Check each keyword
            for keyword in cat_data.get('keywords', []):
                keyword_lower = keyword.lower()

                # Check if keyword is in text
                if keyword_lower in text_clean:
                    # Calculate score based on match quality
                    score = 10  # Base score

                    # Bonus for exact word match (surrounded by spaces or at start/end)
                    if f' {keyword_lower} ' in f' {text_clean} ':
                        score += 10  # Exact word match
                    elif text_clean.startswith(keyword_lower + ' ') or text_clean.endswith(' ' + keyword_lower):
                        score += 8  # Word at boundary
                    elif f'{keyword_lower} ' in text_clean or f' {keyword_lower}' in text_clean:
                        score += 5  # Partial word match

                    # Bonus for longer keywords (more specific)
                    score += len(keyword_lower) * 0.1

                    if score > best_score:
                        best_score = score
                        best_category = category
                        best_match = keyword

        return best_category, best_score, best_match

    def find_columns(self, df):
        """Find all relevant columns"""
        priority = []
        secondary = []
        other = []

        for col in df.columns:
            col_str = str(col).lower().strip()

            is_priority = any(p in col_str for p in self.priority_patterns)
            is_secondary = any(p in col_str for p in self.secondary_patterns)

            if is_priority:
                priority.append(col)
            elif is_secondary:
                secondary.append(col)
            elif df[col].dtype == 'object':
                other.append(col)

        return priority, secondary, other

    def process_row(self, row, priority_cols, secondary_cols, other_cols, enabled_categories):
        """Process a single row and return best category"""
        category_scores = defaultdict(float)
        category_matches = defaultdict(list)

        all_cols = priority_cols + secondary_cols + other_cols

        # Check each column
        for col in all_cols:
            try:
                value = row[col]
                if pd.notna(value):
                    cat, score, match = self.detect_category(str(value), enabled_categories)
                    if cat and score > 0:
                        # Boost priority columns
                        if col in priority_cols:
                            score *= 2
                        elif col in secondary_cols:
                            score *= 1.5

                        category_scores[cat] += score
                        category_matches[cat].append((col, match, score))
            except:
                continue

        if not category_scores:
            return None, 0, []

        # Get best category
        best_cat = max(category_scores.keys(), key=lambda k: category_scores[k])
        best_score = category_scores[best_cat]
        matches = category_matches[best_cat]

        return best_cat, best_score, matches

    def process_file(self, file, sheet_name, enabled_categories):
        """Process entire file"""
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)

            if df.empty:
                return {}, {'total_rows': 0, 'matched_rows': 0, 'unmatched_rows': 0,
                           'categories_found': 0, 'distribution': {}}

            # Find columns
            priority_cols, secondary_cols, other_cols = self.find_columns(df)
            all_cols = priority_cols + secondary_cols + other_cols

            st.info(f"Scanning {len(df)} rows across {len(all_cols)} columns")
            st.caption(f"Priority: {len(priority_cols)} | Secondary: {len(secondary_cols)} | Other: {len(other_cols)}")

            # Add result columns
            df['Detected_Category'] = None
            df['Match_Score'] = 0

            # Process with progress bar
            progress_bar = st.progress(0)
            status = st.empty()

            unmatched = []

            for idx in df.index:
                if idx % 50 == 0 or idx == len(df) - 1:
                    progress = (idx + 1) / len(df)
                    progress_bar.progress(min(progress, 1.0))
                    status.text(f"Processing row {idx + 1} of {len(df)}...")

                row = df.loc[idx]
                cat, score, matches = self.process_row(
                    row, priority_cols, secondary_cols, other_cols, enabled_categories
                )

                if cat:
                    df.at[idx, 'Detected_Category'] = cat
                    df.at[idx, 'Match_Score'] = score
                else:
                    unmatched.append(idx)

            progress_bar.empty()
            status.empty()

            # Handle unmatched with simple fallback
            if unmatched and enabled_categories:
                st.warning(f"{len(unmatched)} rows need fallback matching...")

                for idx in unmatched:
                    row = df.loc[idx]
                    best_cat = None
                    best_count = 0

                    # Simple keyword count fallback
                    for col in all_cols:
                        try:
                            text = str(row[col]).lower()
                            for cat in enabled_categories:
                                count = 0
                                for kw in self.categories[cat]['keywords']:
                                    count += text.count(kw.lower())
                                if count > best_count:
                                    best_count = count
                                    best_cat = cat
                        except:
                            continue

                    if best_cat and best_count > 0:
                        df.at[idx, 'Detected_Category'] = best_cat
                        df.at[idx, 'Match_Score'] = best_count

            # Separate by category
            separated = {}
            original_cols = [c for c in df.columns if c not in ['Detected_Category', 'Match_Score']]

            for cat in enabled_categories:
                cat_data = df[df['Detected_Category'] == cat][original_cols].copy()
                if len(cat_data) > 0:
                    separated[cat] = cat_data

            # Stats
            stats = {
                'total_rows': len(df),
                'matched_rows': len(df[df['Detected_Category'].notna()]),
                'unmatched_rows': len(df[df['Detected_Category'].isna()]),
                'categories_found': len(separated),
                'distribution': df['Detected_Category'].value_counts().to_dict(),
            }

            return separated, stats

        except Exception as e:
            st.error(f"Error: {str(e)}")
            return {}, {'total_rows': 0, 'matched_rows': 0, 'unmatched_rows': 0,
                       'categories_found': 0, 'distribution': {}, 'error': str(e)}


def get_sheet_info(file):
    try:
        wb = load_workbook(file, read_only=True, data_only=False)
        sheets = [{'name': name, 'rows': wb[name].max_row or 0, 'cols': wb[name].max_column or 0}
                  for name in wb.sheetnames]
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
                max_len = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value:
                            max_len = max(max_len, len(str(cell.value)))
                    except:
                        pass
                ws.column_dimensions[column].width = min(max_len + 2, 50)

        output.seek(0)
        return output.getvalue()
    except:
        return None


def main():
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">Data Separation Tool</h1>
        <p class="hero-subtitle">Fixed Version - Accurate Category Detection</p>
    </div>
    """, unsafe_allow_html=True)

    if 'detector' not in st.session_state:
        st.session_state.detector = DataSeparator()
    if 'processed' not in st.session_state:
        st.session_state.processed = None
    if 'stats' not in st.session_state:
        st.session_state.stats = None
    if 'selected_cats' not in st.session_state:
        st.session_state.selected_cats = ['Lighting', 'Fans', 'Furniture', 'Decor']

    # Upload
    st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">1</span>Upload Your File</h3>', unsafe_allow_html=True)

    uploaded = st.file_uploader("", type=['xlsx', 'xlsm', 'xls'], label_visibility="collapsed")

    if uploaded:
        st.markdown('<div class="success-box">File loaded successfully</div>', unsafe_allow_html=True)

        sheets = get_sheet_info(uploaded)
        if sheets:
            opts = [f"{s['name']} ({s['rows']} rows, {s['cols']} cols)" for s in sheets]
            sel = st.selectbox("Select sheet", opts, label_visibility="collapsed")
            st.session_state.sheet = sheets[opts.index(sel)]['name']
            st.session_state.filename = uploaded.name.replace('.xlsx', '').replace('.xlsm', '').replace('.xls', '')

    st.markdown('</div>', unsafe_allow_html=True)

    # Categories
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

    cat_cols = st.columns(3)
    selected = []
    for i, cat in enumerate(all_cats):
        with cat_cols[i % 3]:
            if st.checkbox(cat, value=cat in st.session_state.selected_cats, key=f"cat_{cat}"):
                selected.append(cat)

    st.session_state.selected_cats = selected

    if selected:
        total_kw = sum(len(st.session_state.detector.categories[cat]['keywords']) for cat in selected)
        st.info(f"{total_kw} keywords loaded across {len(selected)} categories")

    st.markdown('</div>', unsafe_allow_html=True)

    # Process
    if uploaded and st.session_state.selected_cats:
        st.markdown('<div class="premium-card"><h3 class="card-title"><span class="card-number">3</span>Process Data</h3>', unsafe_allow_html=True)

        if st.button("Start Processing", type="primary", use_container_width=True):
            with st.spinner('Processing...'):
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

        st.markdown('<div class="stat-container">', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["total_rows"]}</div><div class="stat-label">Total Rows</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["matched_rows"]}</div><div class="stat-label">Matched</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["unmatched_rows"]}</div><div class="stat-label">Unmatched</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["categories_found"]}</div><div class="stat-label">Categories</div></div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.subheader("Category Distribution")
        for cat, count in stats['distribution'].items():
            if cat:
                pct = (count / stats['total_rows']) * 100
                st.markdown(f'<div class="distribution-item"><span><strong>{cat}</strong></span><span>{count} items ({pct:.1f}%)</span></div>', unsafe_allow_html=True)

        st.subheader("Download Results")

        dl_cols = st.columns(min(len(st.session_state.processed), 4))
        for idx, (category, data) in enumerate(st.session_state.processed.items()):
            with dl_cols[idx % len(dl_cols)]:
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
