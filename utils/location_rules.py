"""
location_rules.py
=================
Geographic and Agro-Climatic Suitability Knowledge Base for Indian Agriculture.

This module acts as a rule-based agro-climatic decision layer that evaluates
whether a crop is regionally, geographically, and topographically suitable
for a given farmer's location (city, state, or region in India).

NOTE: This is an AI-assisted decision-support knowledge base representing broad
agro-ecological guidelines. It is not an absolute agricultural prescription.
"""

import re

# ─────────────────────────────────────────────────────────────────────────────
# 1. REGIONAL TAXONOMY & NORMALIZATION DICTIONARIES
# ─────────────────────────────────────────────────────────────────────────────

# Standard Indian Agricultural Zones
REGIONS = {
    "Central India": {
        "description": "Black cotton soil (Regur), semi-arid to sub-humid tropical climate, plateau terrain.",
        "states": ["maharashtra", "madhya pradesh", "chhattisgarh"],
    },
    "Western India": {
        "description": "Arid to semi-arid climate, alluvial and sandy-loam tracts.",
        "states": ["gujarat", "rajasthan", "goa"],
    },
    "Northern India": {
        "description": "Indo-Gangetic alluvial plains, distinct winter (Rabi) season.",
        "states": ["punjab", "haryana", "uttar pradesh", "delhi", "chandigarh"],
    },
    "Southern India": {
        "description": "Tropical Deccan plateau, red and laterite soils, coastal plains.",
        "states": ["karnataka", "tamil nadu", "kerala", "andhra pradesh", "telangana", "puducherry"],
    },
    "Eastern India": {
        "description": "Humid alluvial delta tracts, high monsoon rainfall, floodplains.",
        "states": ["west bengal", "bihar", "odisha", "jharkhand"],
    },
    "Northeast India": {
        "description": "Subtropical humid hills, heavy monsoons, acidic forest soils.",
        "states": ["assam", "meghalaya", "tripura", "manipur", "mizoram", "nagaland", "arunachal pradesh", "sikkim"],
    },
    "Northern Highland": {
        "description": "Temperate sub-alpine valleys, cold chilling climate, mountain topography.",
        "states": ["himachal pradesh", "jammu and kashmir", "ladakh", "uttarakhand"],
    },
}

# Known Highland / Plantation tracts suitable for specialized crops like Coffee / Tea
HIGHLAND_PLANTATION_ZONES = [
    "coorg", "kodagu", "chikmagalur", "chikkamagaluru", "hassan", "baba budan",
    "wayanad", "idukki", "munnar", "travancore", "nelliyampathy",
    "nilgiris", "ooty", "shevaroys", "kodaikanal", "yercaud", "valparai", "anamalai",
    "araku", "araku valley", "chintapalli", "visakhapatnam hills",
    "koraput", "rayagada", "kandhamal",
    "darjeeling", "kalimpong", "shillong", "karbi anglong", "dima hasao"
]

# Known Temperate Mountain Valleys suitable for Apple / Temperate Fruits
TEMPERATE_FRUIT_ZONES = [
    "shimla", "kullu", "kinnaur", "mandi", "solan", "chamba",
    "srinagar", "baramulla", "shopian", "anantnag", "pulwama", "kashmir",
    "nainital", "almora", "chamoli", "uttarkashi", "mukteshwar", "tehri"
]

# Coastal Zones suitable for Coconut / Coastal agriculture
COASTAL_DISTRICTS = [
    "mumbai", "ratnagiri", "sindhudurg", "raigad", "thane", "palghar",
    "goa", "north goa", "south goa",
    "mangalore", "dakshina kannada", "udupi", "uttara kannada",
    "kochi", "cochin", "alappuzha", "kollam", "thiruvananthapuram", "kozhikode", "kannur",
    "chennai", "cuddalore", "nagapattinam", "kanchipuram", "ramanathapuram", "kanyakumari",
    "visakhapatnam", "vizag", "east godavari", "west godavari", "srikakulam", "machilipatnam",
    "puri", "cuttack", "balasore", "bhadrak", "ganjam", "paradip",
    "kolkata", "south 24 parganas", "north 24 parganas", "digha"
]

# Common City to State / Region Mapping
CITY_LOOKUP = {
    # Maharashtra
    "nagpur": ("Nagpur", "Maharashtra", "Central India", False, False),
    "vidarbha": ("Vidarbha", "Maharashtra", "Central India", False, False),
    "pune": ("Pune", "Maharashtra", "Western India", False, False),
    "mumbai": ("Mumbai", "Maharashtra", "Western India", False, True),
    "nashik": ("Nashik", "Maharashtra", "Western India", False, False),
    "aurangabad": ("Chhatrapati Sambhajinagar", "Maharashtra", "Central India", False, False),
    "sambhajinagar": ("Chhatrapati Sambhajinagar", "Maharashtra", "Central India", False, False),
    "amravati": ("Amravati", "Maharashtra", "Central India", False, False),
    "solapur": ("Solapur", "Maharashtra", "Central India", False, False),
    "kolhapur": ("Kolhapur", "Maharashtra", "Western India", False, False),
    "jalgaon": ("Jalgaon", "Maharashtra", "Central India", False, False),
    "akola": ("Akola", "Maharashtra", "Central India", False, False),
    "nanded": ("Nanded", "Maharashtra", "Central India", False, False),
    "thane": ("Thane", "Maharashtra", "Western India", False, True),
    "wardha": ("Wardha", "Maharashtra", "Central India", False, False),
    "chandrapur": ("Chandrapur", "Maharashtra", "Central India", False, False),
    "yavatmal": ("Yavatmal", "Maharashtra", "Central India", False, False),

    # Karnataka
    "bengaluru": ("Bengaluru", "Karnataka", "Southern India", False, False),
    "bangalore": ("Bengaluru", "Karnataka", "Southern India", False, False),
    "mysore": ("Mysuru", "Karnataka", "Southern India", False, False),
    "mysuru": ("Mysuru", "Karnataka", "Southern India", False, False),
    "coorg": ("Coorg (Kodagu)", "Karnataka", "Southern India", True, False),
    "kodagu": ("Kodagu", "Karnataka", "Southern India", True, False),
    "chikmagalur": ("Chikmagalur", "Karnataka", "Southern India", True, False),
    "chikkamagaluru": ("Chikkamagaluru", "Karnataka", "Southern India", True, False),
    "hassan": ("Hassan", "Karnataka", "Southern India", True, False),
    "mangalore": ("Mangaluru", "Karnataka", "Southern India", False, True),
    "belagavi": ("Belagavi", "Karnataka", "Southern India", False, False),
    "belgaum": ("Belagavi", "Karnataka", "Southern India", False, False),
    "hubli": ("Hubballi", "Karnataka", "Southern India", False, False),
    "dharwad": ("Dharwad", "Karnataka", "Southern India", False, False),

    # Kerala
    "kochi": ("Kochi", "Kerala", "Southern India", False, True),
    "thiruvananthapuram": ("Thiruvananthapuram", "Kerala", "Southern India", False, True),
    "wayanad": ("Wayanad", "Kerala", "Southern India", True, False),
    "idukki": ("Idukki", "Kerala", "Southern India", True, False),
    "palakkad": ("Palakkad", "Kerala", "Southern India", False, False),
    "kozhikode": ("Kozhikode", "Kerala", "Southern India", False, True),

    # Tamil Nadu
    "chennai": ("Chennai", "Tamil Nadu", "Southern India", False, True),
    "coimbatore": ("Coimbatore", "Tamil Nadu", "Southern India", False, False),
    "madurai": ("Madurai", "Tamil Nadu", "Southern India", False, False),
    "salem": ("Salem", "Tamil Nadu", "Southern India", False, False),
    "ooty": ("Ooty (Nilgiris)", "Tamil Nadu", "Southern India", True, False),
    "nilgiris": ("Nilgiris", "Tamil Nadu", "Southern India", True, False),

    # Andhra Pradesh & Telangana
    "hyderabad": ("Hyderabad", "Telangana", "Southern India", False, False),
    "warangal": ("Warangal", "Telangana", "Southern India", False, False),
    "visakhapatnam": ("Visakhapatnam", "Andhra Pradesh", "Southern India", False, True),
    "vijayawada": ("Vijayawada", "Andhra Pradesh", "Southern India", False, False),
    "guntur": ("Guntur", "Andhra Pradesh", "Southern India", False, False),
    "araku": ("Araku Valley", "Andhra Pradesh", "Southern India", True, False),

    # Northern Plains
    "delhi": ("Delhi", "Delhi", "Northern India", False, False),
    "ludhiana": ("Ludhiana", "Punjab", "Northern India", False, False),
    "amritsar": ("Amritsar", "Punjab", "Northern India", False, False),
    "jalandhar": ("Jalandhar", "Punjab", "Northern India", False, False),
    "karnal": ("Karnal", "Haryana", "Northern India", False, False),
    "hisar": ("Hisar", "Haryana", "Northern India", False, False),
    "lucknow": ("Lucknow", "Uttar Pradesh", "Northern India", False, False),
    "kanpur": ("Kanpur", "Uttar Pradesh", "Northern India", False, False),
    "varanasi": ("Varanasi", "Uttar Pradesh", "Northern India", False, False),
    "agra": ("Agra", "Uttar Pradesh", "Northern India", False, False),
    "meerut": ("Meerut", "Uttar Pradesh", "Northern India", False, False),

    # Madhya Pradesh
    "bhopal": ("Bhopal", "Madhya Pradesh", "Central India", False, False),
    "indore": ("Indore", "Madhya Pradesh", "Central India", False, False),
    "jabalpur": ("Jabalpur", "Madhya Pradesh", "Central India", False, False),
    "gwalior": ("Gwalior", "Madhya Pradesh", "Central India", False, False),
    "ujjain": ("Ujjain", "Madhya Pradesh", "Central India", False, False),

    # Rajasthan & Gujarat
    "jaipur": ("Jaipur", "Rajasthan", "Western India", False, False),
    "jodhpur": ("Jodhpur", "Rajasthan", "Western India", False, False),
    "kota": ("Kota", "Rajasthan", "Western India", False, False),
    "ahmedabad": ("Ahmedabad", "Gujarat", "Western India", False, False),
    "surat": ("Surat", "Gujarat", "Western India", False, True),
    "rajkot": ("Rajkot", "Gujarat", "Western India", False, False),
    "vadodara": ("Vadodara", "Gujarat", "Western India", False, False),

    # Eastern & Northeastern
    "kolkata": ("Kolkata", "West Bengal", "Eastern India", False, True),
    "siliguri": ("Siliguri", "West Bengal", "Eastern India", False, False),
    "patna": ("Patna", "Bihar", "Eastern India", False, False),
    "gaya": ("Gaya", "Bihar", "Eastern India", False, False),
    "bhubaneswar": ("Bhubaneswar", "Odisha", "Eastern India", False, False),
    "cuttack": ("Cuttack", "Odisha", "Eastern India", False, False),
    "koraput": ("Koraput", "Odisha", "Eastern India", True, False),
    "ranchi": ("Ranchi", "Jharkhand", "Eastern India", False, False),
    "guwahati": ("Guwahati", "Assam", "Northeast India", False, False),

    # Northern Highlands
    "shimla": ("Shimla", "Himachal Pradesh", "Northern Highland", True, False),
    "kullu": ("Kullu", "Himachal Pradesh", "Northern Highland", True, False),
    "srinagar": ("Srinagar", "Jammu and Kashmir", "Northern Highland", True, False),
    "jammu": ("Jammu", "Jammu and Kashmir", "Northern Highland", False, False),
    "dehradun": ("Dehradun", "Uttarakhand", "Northern Highland", True, False),
}

STATE_LOOKUP = {
    "maharashtra": ("Maharashtra", "Central India", False, False),
    "madhya pradesh": ("Madhya Pradesh", "Central India", False, False),
    "chhattisgarh": ("Chhattisgarh", "Central India", False, False),
    "punjab": ("Punjab", "Northern India", False, False),
    "haryana": ("Haryana", "Northern India", False, False),
    "uttar pradesh": ("Uttar Pradesh", "Northern India", False, False),
    "delhi": ("Delhi", "Northern India", False, False),
    "gujarat": ("Gujarat", "Western India", False, True),
    "rajasthan": ("Rajasthan", "Western India", False, False),
    "karnataka": ("Karnataka", "Southern India", False, False),
    "tamil nadu": ("Tamil Nadu", "Southern India", False, True),
    "kerala": ("Kerala", "Southern India", True, True),
    "andhra pradesh": ("Andhra Pradesh", "Southern India", False, True),
    "telangana": ("Telangana", "Southern India", False, False),
    "west bengal": ("West Bengal", "Eastern India", False, True),
    "bihar": ("Bihar", "Eastern India", False, False),
    "odisha": ("Odisha", "Eastern India", False, True),
    "jharkhand": ("Jharkhand", "Eastern India", False, False),
    "assam": ("Assam", "Northeast India", False, False),
    "himachal pradesh": ("Himachal Pradesh", "Northern Highland", True, False),
    "jammu and kashmir": ("Jammu and Kashmir", "Northern Highland", True, False),
    "uttarakhand": ("Uttarakhand", "Northern Highland", True, False),
}


# ─────────────────────────────────────────────────────────────────────────────
# 2. LOCATION NORMALIZATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def normalize_location(location_str: str) -> dict:
    """
    Parse, normalize, and classify a user-supplied location string.

    Handles inputs like:
      - 'Nagpur'
      - 'Nagpur, Maharashtra'
      - 'Nagpur Maharashtra'
      - 'Pune, Maharashtra'
      - 'Karnataka'
      - 'Coorg, Karnataka'
      - 'All India' or blank

    Returns a dict with:
      - 'raw': original string
      - 'city': matched city name or None
      - 'state': matched state name or None
      - 'region': major agricultural zone (e.g. 'Central India')
      - 'is_highland': boolean indicating hilly/plantation terrain
      - 'is_coastal': boolean indicating coastal humid zone
      - 'display': human-readable location tag
    """
    raw = (location_str or "").strip()
    if not raw:
        return {
            "raw": "",
            "city": None,
            "state": None,
            "region": "All India / General",
            "is_highland": False,
            "is_coastal": False,
            "display": "All India (General Agro-Climatic Zone)",
        }

    loc_lower = raw.lower()
    # Remove punctuation for token matching
    cleaned = re.sub(r"[^\w\s]", " ", loc_lower)
    tokens = [t.strip() for t in cleaned.split() if t.strip()]

    matched_city = None
    matched_state = None
    matched_region = "Central India"  # sensible default for India central geography
    is_highland = False
    is_coastal = False

    # Check highland keywords
    for hz in HIGHLAND_PLANTATION_ZONES:
        if hz in loc_lower:
            is_highland = True
            break
    for tz in TEMPERATE_FRUIT_ZONES:
        if tz in loc_lower:
            is_highland = True
            break

    # Check coastal keywords
    for cd in COASTAL_DISTRICTS:
        if cd in loc_lower:
            is_coastal = True
            break

    # 1. Match specific city
    for city_key, (c_name, s_name, reg_name, c_highland, c_coastal) in CITY_LOOKUP.items():
        if city_key in loc_lower or city_key in tokens:
            matched_city = c_name
            matched_state = s_name
            matched_region = reg_name
            is_highland = is_highland or c_highland
            is_coastal = is_coastal or c_coastal
            break

    # 2. Match state if not yet matched or state explicitly specified
    for state_key, (s_name, reg_name, s_highland, s_coastal) in STATE_LOOKUP.items():
        if state_key in loc_lower:
            matched_state = s_name
            if not matched_city:
                matched_region = reg_name
                is_highland = is_highland or s_highland
                is_coastal = is_coastal or s_coastal
            break

    # 3. If neither matched directly, check regional names
    if not matched_state and not matched_city:
        for reg_key in REGIONS.keys():
            if reg_key.lower() in loc_lower:
                matched_region = reg_key
                break

    # Build clean display string
    parts = []
    if matched_city:
        parts.append(matched_city)
    if matched_state and matched_state != matched_city:
        parts.append(matched_state)
    if parts:
        display = f"{', '.join(parts)} ({matched_region})"
    else:
        display = f"{raw.title()} ({matched_region})"

    return {
        "raw": raw,
        "city": matched_city,
        "state": matched_state,
        "region": matched_region,
        "is_highland": is_highland,
        "is_coastal": is_coastal,
        "display": display,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. AGRO-CLIMATIC CROP LOCATION KNOWLEDGE BASE
# ─────────────────────────────────────────────────────────────────────────────

CROP_LOCATION_PROFILES = {
    "coffee": {
        "crop_name": "Coffee",
        "category": "Highland Plantation Crop",
        "primary_states": ["karnataka", "kerala", "tamil nadu", "andhra pradesh", "odisha"],
        "primary_districts": [
            "coorg", "kodagu", "chikmagalur", "chikkamagaluru", "hassan",
            "wayanad", "idukki", "nilgiris", "araku", "koraput"
        ],
        "strictly_requires_highland": True,
        "unsuitable_terrain": ["plains", "lowland", "arid", "semi-arid continental plains", "nagpur", "vidarbha", "punjab", "haryana", "rajasthan", "up"],
        "highland_score": 92,
        "secondary_score": 60,
        "unsuitable_score": 10,
        "description": "Requires tropical highland elevation (600–1600m), shade trees, and acidic forest loam; unsuited for lowland/inland plains."
    },
    "apple": {
        "crop_name": "Apple",
        "category": "Temperate Highland Fruit",
        "primary_states": ["himachal pradesh", "jammu and kashmir", "uttarakhand", "arunachal pradesh"],
        "strictly_requires_highland": True,
        "unsuitable_terrain": ["tropical plains", "subtropical plains", "peninsular india", "nagpur", "maharashtra", "punjab", "rajasthan", "tamil nadu"],
        "highland_score": 95,
        "secondary_score": 40,
        "unsuitable_score": 5,
        "description": "Requires temperate mountain valleys with 800–1200 winter chilling hours (<7°C); completely unsuited for peninsular/central plains."
    },
    "cotton": {
        "crop_name": "Cotton",
        "category": "Commercial Fiber (Black Soil Tracts)",
        "primary_states": ["maharashtra", "gujarat", "telangana", "andhra pradesh", "karnataka", "madhya pradesh", "punjab", "haryana", "rajasthan"],
        "primary_districts": ["nagpur", "vidarbha", "amravati", "akola", "yavatmal", "wardha", "aurangabad", "jalgaon", "rajkot", "surendranagar"],
        "highland_score": 35,
        "suitable_score": 95,
        "secondary_score": 75,
        "unsuitable_score": 20,
        "description": "Thrives in warm, semi-arid to sub-humid black cotton soils (Regur) across Maharashtra (Vidarbha), Gujarat, and Deccan plateau."
    },
    "wheat": {
        "crop_name": "Wheat",
        "category": "Core Rabi Cereal",
        "primary_states": ["punjab", "haryana", "uttar pradesh", "madhya pradesh", "rajasthan", "bihar", "gujarat", "maharashtra", "west bengal"],
        "suitable_score": 90,
        "secondary_score": 75,
        "unsuitable_score": 25,
        "description": "Widely adapted Rabi staple cereal across Northern, Central, and Western Indian plains with cool winter temperatures."
    },
    "chickpea": {
        "crop_name": "Chickpea",
        "category": "Major Rabi Pulse (Gram)",
        "primary_states": ["madhya pradesh", "maharashtra", "rajasthan", "uttar pradesh", "karnataka", "andhra pradesh", "gujarat"],
        "primary_districts": ["nagpur", "vidarbha", "amravati", "bhopal", "indore", "jabalpur"],
        "suitable_score": 95,
        "secondary_score": 80,
        "unsuitable_score": 30,
        "description": "Major post-monsoon pulse extensively grown across Central and Western India, especially Maharashtra (Vidarbha) and MP."
    },
    "rice": {
        "crop_name": "Rice",
        "category": "Core Kharif Cereal",
        "primary_states": ["west bengal", "uttar pradesh", "punjab", "odisha", "andhra pradesh", "tamil nadu", "bihar", "assam", "chhattisgarh", "haryana", "kerala", "karnataka", "maharashtra"],
        "suitable_score": 90,
        "secondary_score": 80,
        "unsuitable_score": 40,
        "description": "Extensively cultivated staple across alluvial river basins, coastal plains, and canal-irrigated tracts throughout India."
    },
    "maize": {
        "crop_name": "Maize",
        "category": "Versatile Coarse Cereal",
        "primary_states": ["karnataka", "madhya pradesh", "maharashtra", "bihar", "rajasthan", "uttar pradesh", "telangana", "andhra pradesh", "gujarat", "punjab"],
        "suitable_score": 88,
        "secondary_score": 80,
        "unsuitable_score": 40,
        "description": "Highly adaptable crop grown in warm seasons across diverse soils throughout Central, Southern, and Northern India."
    },
    "orange": {
        "crop_name": "Orange",
        "category": "Subtropical Citrus Fruit",
        "primary_states": ["maharashtra", "madhya pradesh", "punjab", "rajasthan", "assam"],
        "primary_districts": ["nagpur", "amravati", "wardha", "vidarbha"],
        "special_district_score": 98,
        "suitable_score": 85,
        "secondary_score": 65,
        "unsuitable_score": 25,
        "description": "World-famous in the Vidarbha mandarin belt centered at Nagpur ('Orange City'); well-adapted to well-drained loams of Central India."
    },
    "pigeonpeas": {
        "crop_name": "Pigeonpeas",
        "category": "Kharif Pulse (Tur / Arhar)",
        "primary_states": ["maharashtra", "madhya pradesh", "karnataka", "uttar pradesh", "gujarat", "telangana", "andhra pradesh"],
        "primary_districts": ["nagpur", "vidarbha", "amravati", "akola", "latur", "gulbarga", "kalaburagi"],
        "suitable_score": 95,
        "secondary_score": 80,
        "unsuitable_score": 30,
        "description": "Leading Kharif pulse across Central and Peninsular India; Maharashtra is India's largest producer."
    },
    "blackgram": {
        "crop_name": "Blackgram",
        "category": "Pulse (Urad)",
        "primary_states": ["madhya pradesh", "maharashtra", "andhra pradesh", "tamil nadu", "uttar pradesh", "rajasthan"],
        "suitable_score": 90,
        "secondary_score": 80,
        "unsuitable_score": 35,
        "description": "Short-duration pulse widely cultivated across warm plains and plateau tracts of Central and Southern India."
    },
    "mungbean": {
        "crop_name": "Mungbean",
        "category": "Short Duration Pulse (Moong)",
        "primary_states": ["rajasthan", "maharashtra", "madhya pradesh", "karnataka", "bihar", "gujarat", "andhra pradesh", "tamil nadu"],
        "suitable_score": 90,
        "secondary_score": 80,
        "unsuitable_score": 35,
        "description": "Quick-maturing pulse suited for catch-cropping and rotation across semi-arid and sub-humid plains."
    },
    "mothbeans": {
        "crop_name": "Mothbeans",
        "category": "Drought-Hardy Arid Pulse",
        "primary_states": ["rajasthan", "gujarat", "haryana", "maharashtra", "punjab"],
        "suitable_score": 85,
        "secondary_score": 75,
        "unsuitable_score": 30,
        "description": "Drought-resilient arid/semi-arid legume thriving in sandy loams and dry tracts of Western and Central India."
    },
    "lentil": {
        "crop_name": "Lentil",
        "category": "Rabi Pulse (Masoor)",
        "primary_states": ["madhya pradesh", "uttar pradesh", "bihar", "west bengal", "rajasthan", "maharashtra"],
        "suitable_score": 85,
        "secondary_score": 75,
        "unsuitable_score": 30,
        "description": "Cool-season Rabi pulse grown across fertile loams of Central, Northern, and Eastern India."
    },
    "kidneybeans": {
        "crop_name": "Kidneybeans",
        "category": "Specialized Pulse (Rajma)",
        "primary_states": ["jammu and kashmir", "himachal pradesh", "uttarakhand", "maharashtra", "karnataka"],
        "primary_districts": ["bhaderwah", "kishtwar", "shimla", "solan", "pune", "satara"],
        "suitable_score": 78,
        "secondary_score": 65,
        "unsuitable_score": 30,
        "description": "Best suited to temperate hills of Northern India and mild winter pockets in Peninsular plateau."
    },
    "jute": {
        "crop_name": "Jute",
        "category": "Humid Deltaic Fiber",
        "primary_states": ["west bengal", "assam", "bihar", "odisha", "meghalaya"],
        "strictly_requires_humid_east": True,
        "suitable_score": 95,
        "secondary_score": 45,
        "unsuitable_score": 18,
        "description": "Strongly associated with humid, swampy alluvial tracts of the Eastern delta (West Bengal/Assam); unsuited to dry inland plains."
    },
    "coconut": {
        "crop_name": "Coconut",
        "category": "Tropical Coastal Plantation",
        "primary_states": ["kerala", "tamil nadu", "karnataka", "andhra pradesh", "odisha", "goa", "west bengal", "maharashtra"],
        "requires_coastal_or_humid": True,
        "suitable_score": 92,
        "secondary_score": 50,
        "unsuitable_score": 15,
        "description": "Tropical perennial palm requiring high humidity, warm climate, and coastal or well-watered alluvial belts."
    },
    "banana": {
        "crop_name": "Banana",
        "category": "Tropical Fruit",
        "primary_states": ["maharashtra", "gujarat", "tamil nadu", "andhra pradesh", "karnataka", "kerala", "uttar pradesh", "bihar"],
        "primary_districts": ["jalgaon", "solapur", "pune", "theanur", "trichy"],
        "suitable_score": 90,
        "secondary_score": 80,
        "unsuitable_score": 35,
        "description": "Widely grown tropical and subtropical fruit; Maharashtra (Jalgaon) is India's leading producer."
    },
    "mango": {
        "crop_name": "Mango",
        "category": "Tropical & Subtropical Fruit",
        "primary_states": ["uttar pradesh", "andhra pradesh", "karnataka", "bihar", "gujarat", "tamil nadu", "maharashtra", "odisha", "west bengal"],
        "suitable_score": 90,
        "secondary_score": 80,
        "unsuitable_score": 35,
        "description": "National fruit of India with widespread adaptation across diverse tropical and subtropical plains."
    },
    "grapes": {
        "crop_name": "Grapes",
        "category": "Commercial Subtropical Vine",
        "primary_states": ["maharashtra", "karnataka", "tamil nadu", "andhra pradesh", "telangana", "punjab"],
        "primary_districts": ["nashik", "sangli", "solapur", "pune", "vijayapura", "bijapur"],
        "suitable_score": 90,
        "secondary_score": 75,
        "unsuitable_score": 30,
        "description": "Premier commercial horticultural crop centered in Maharashtra (Nashik, Sangli) and Karnataka."
    },
    "pomegranate": {
        "crop_name": "Pomegranate",
        "category": "Semi-Arid Commercial Fruit",
        "primary_states": ["maharashtra", "gujarat", "karnataka", "rajasthan", "andhra pradesh", "madhya pradesh"],
        "primary_districts": ["solapur", "nashik", "sangli", "ahmednagar", "pune"],
        "suitable_score": 92,
        "secondary_score": 78,
        "unsuitable_score": 30,
        "description": "Thrives in dry, warm semi-arid climates; Maharashtra (Solapur) is India's largest pomegranate hub."
    },
    "watermelon": {
        "crop_name": "Watermelon",
        "category": "Summer Cucurbit",
        "primary_states": ["uttar pradesh", "karnataka", "andhra pradesh", "tamil nadu", "rajasthan", "maharashtra", "madhya pradesh", "punjab", "haryana"],
        "suitable_score": 85,
        "secondary_score": 75,
        "unsuitable_score": 35,
        "description": "Warm-season riverbed and irrigated field crop widely cultivated across Indian river basins."
    },
    "muskmelon": {
        "crop_name": "Muskmelon",
        "category": "Summer Cucurbit",
        "primary_states": ["uttar pradesh", "punjab", "haryana", "rajasthan", "madhya pradesh", "andhra pradesh", "maharashtra"],
        "suitable_score": 85,
        "secondary_score": 75,
        "unsuitable_score": 35,
        "description": "Heat-loving cucurbit thriving in warm, dry weather and sandy loams during summer (Zaid) months."
    },
    "papaya": {
        "crop_name": "Papaya",
        "category": "Tropical Fruit",
        "primary_states": ["gujarat", "andhra pradesh", "karnataka", "madhya pradesh", "maharashtra", "west bengal", "tamil nadu"],
        "suitable_score": 88,
        "secondary_score": 78,
        "unsuitable_score": 35,
        "description": "Fast-growing tropical fruit cultivated in frost-free plains across Central, Western, and Southern India."
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# 4. LOCATION SUITABILITY EVALUATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def get_location_suitability(crop: str, location_str: str,
                             temperature: float = None,
                             rainfall: float = None) -> dict:
    """
    Calculate geographic and agro-climatic suitability of a crop for a given location.

    Returns:
      {
          "score": int (0 to 100),
          "status": "Compatible" | "Check" | "Unsuitable",
          "status_display": "✓ Compatible" | "⚠ Check" | "✕ Unsuitable",
          "reason": str,
          "region": str,
          "city": str or None,
          "state": str or None,
          "exclude_from_ranking": bool  # True if score < 25 (hard exclusion)
      }
    """
    crop_lower = crop.strip().lower()
    norm = normalize_location(location_str)

    city = norm["city"]
    state = norm["state"]
    region = norm["region"]
    is_highland = norm["is_highland"]
    is_coastal = norm["is_coastal"]
    raw_lower = norm["raw"].lower()

    # If crop profile not configured, return neutral compatible score
    profile = CROP_LOCATION_PROFILES.get(crop_lower)
    if not profile:
        return {
            "score": 75,
            "status": "Compatible",
            "status_display": "✓ Compatible",
            "reason": f"{crop.capitalize()} has general adaptability across diverse Indian agricultural tracts.",
            "region": region,
            "city": city,
            "state": state,
            "exclude_from_ranking": False,
        }

    crop_name = profile["crop_name"]
    score = 75
    status = "Compatible"
    reason = ""

    # ── SPECIAL HANDLING: COFFEE ──
    if crop_lower == "coffee":
        # Coffee specifically needs highland tropical plantation tracts
        if is_highland or any(d in raw_lower for d in profile["primary_districts"]):
            score = 92
            status = "Compatible"
            reason = f"Excellent match: {norm['display']} is located in a recognized tropical highland coffee plantation belt."
        elif state and state.lower() in ["karnataka", "kerala", "tamil nadu"]:
            # State has coffee belts, but specific city may not be highland
            if city and city.lower() in ["bengaluru", "bangalore", "mysore", "mysuru", "mangalore"]:
                score = 55
                status = "Check"
                reason = f"Karnataka has premier coffee tracts (Kodagu, Chikmagalur), but {city} plains require verification of microclimate."
            else:
                score = 65
                status = "Check"
                reason = f"{state} is a premier coffee-growing state, but commercial coffee requires hilly highland terrain (600–1600m)."
        else:
            # Clearly in plains / central / northern / western agricultural plains
            score = 10
            status = "Unsuitable"
            loc_label = norm['city'] or norm['state'] or norm['region']
            reason = (
                f"Coffee is generally associated with specific highland/hilly growing regions (Karnataka, Kerala, Tamil Nadu hills); "
                f"the supplied location ({loc_label}) is a lowland/plain agricultural tract and does not match the configured regional suitability profile."
            )

    # ── SPECIAL HANDLING: APPLE ──
    elif crop_lower == "apple":
        if region == "Northern Highland" or is_highland and state and state.lower() in profile["primary_states"]:
            score = 95
            status = "Compatible"
            reason = f"Ideal match: {norm['display']} provides the temperate climate and winter chilling hours required for apple cultivation."
        else:
            score = 5
            status = "Unsuitable"
            loc_label = norm['city'] or norm['state'] or norm['region']
            reason = (
                f"Apples require temperate highland climates with 800–1200 winter chilling hours (<7°C); "
                f"the supplied location ({loc_label}) is a warm plain and is agronomically unsuitable."
            )

    # ── SPECIAL HANDLING: JUTE ──
    elif crop_lower == "jute":
        if state and state.lower() in profile["primary_states"] or region == "Eastern India":
            score = 95
            status = "Compatible"
            reason = f"{norm['display']} lies in the humid eastern deltaic belt ideal for jute cultivation."
        else:
            score = 18
            status = "Unsuitable"
            loc_label = norm['city'] or norm['state'] or norm['region']
            reason = (
                f"Jute is particularly associated with humid eastern/northeastern tracts (West Bengal, Assam, Bihar); "
                f"it receives low regional suitability in {loc_label} due to lack of prolonged humid delta conditions."
            )

    # ── SPECIAL HANDLING: COCONUT ──
    elif crop_lower == "coconut":
        if is_coastal or (state and state.lower() in ["kerala", "goa"]):
            score = 95
            status = "Compatible"
            reason = f"{norm['display']} provides the warm coastal humid environment ideal for coconut palms."
        elif state and state.lower() in ["tamil nadu", "karnataka", "andhra pradesh", "odisha", "maharashtra"]:
            if city and city.lower() in ["nagpur", "amravati", "akola", "solapur", "pune", "nashik"]:
                score = 15
                status = "Unsuitable"
                reason = f"Coconut requires coastal or high-humidity tropical conditions; unsuitable for inland semi-arid plains of {city}."
            else:
                score = 50
                status = "Check"
                reason = f"Coconut is cultivated in parts of {state}, but requires perennial moisture and high humidity."
        else:
            score = 15
            status = "Unsuitable"
            loc_label = norm['city'] or norm['state'] or norm['region']
            reason = f"Inland semi-arid/continental climate of {loc_label} does not meet coconut's humid coastal habitat requirements."

    # ── SPECIAL HANDLING: ORANGE (MANDARIN) ──
    elif crop_lower == "orange":
        if city and city.lower() in ["nagpur", "amravati", "wardha"] or "nagpur" in raw_lower or "vidarbha" in raw_lower:
            score = 98
            status = "Compatible"
            reason = "Nagpur is India's renowned 'Orange City' (Vidarbha mandarin hub); regional agro-climatic conditions are historically optimal."
        elif state and state.lower() in profile["primary_states"]:
            score = 88
            status = "Compatible"
            reason = f"Well-suited to citrus tracts across {state} and Central India."
        else:
            score = 65
            status = "Check"
            reason = f"Citrus can be cultivated in {norm['region']}, but local drainage and sub-tropical winter variation must be checked."

    # ── SPECIAL HANDLING: COTTON ──
    elif crop_lower == "cotton":
        if city and city.lower() in ["nagpur", "amravati", "wardha", "akola", "yavatmal"] or "vidarbha" in raw_lower:
            score = 96
            status = "Compatible"
            reason = "Nagpur and Vidarbha represent the heart of India's premier black cotton soil (Regur) belt, exceptionally compatible with cotton."
        elif state and state.lower() in profile["primary_states"]:
            score = 92
            status = "Compatible"
            reason = f"{state} is a leading commercial cotton production state with favorable warm climate and black soils."
        elif region in ["Central India", "Western India", "Southern India"]:
            score = 80
            status = "Compatible"
            reason = f"Compatible with the warm sub-humid and semi-arid conditions of {region}."
        else:
            score = 40
            status = "Check"
            reason = f"Cotton requires warm long growing seasons; cooler or high-rainfall tracts in {region} may affect fiber quality."

    # ── SPECIAL HANDLING: CHICKPEA (GRAM) ──
    elif crop_lower == "chickpea":
        if state and state.lower() in profile["primary_states"] or region in ["Central India", "Northern India", "Western India"]:
            score = 95
            status = "Compatible"
            loc_label = norm['city'] or norm['state'] or norm['region']
            reason = f"Central and Northern India (including {loc_label}) are India's premier chickpea producing zones, highly compatible with local winter climate."
        else:
            score = 60
            status = "Check"
            reason = f"Chickpea requires dry cool winter conditions; high humidity or heavy rainfall in {norm['region']} increases fungal risk."

    # ── SPECIAL HANDLING: WHEAT ──
    elif crop_lower == "wheat":
        if state and state.lower() in profile["primary_states"] or region in ["Northern India", "Central India", "Western India"]:
            score = 88
            status = "Compatible"
            loc_label = norm['city'] or norm['state'] or norm['region']
            reason = f"Wheat is a widely adapted core Rabi cereal across {loc_label}, compatible with winter irrigated cropping."
        else:
            score = 45
            status = "Check"
            reason = f"Wheat requires cool winter temperatures; tropical Southern coastal regions often lack sufficient winter chilling."

    # ── GENERAL CROPS (RICE, MAIZE, PULSES, VEGETABLES, FRUITS) ──
    else:
        # Check if state is in primary states
        if state and state.lower() in profile.get("primary_states", []):
            score = profile.get("suitable_score", 88)
            status = "Compatible"
            reason = f"{crop_name} is widely and successfully cultivated across {state}."
        elif region in ["Central India", "Northern India", "Western India", "Southern India", "Eastern India"]:
            score = profile.get("secondary_score", 80)
            status = "Compatible"
            reason = f"{crop_name} exhibits broad regional compatibility within {region}."
        else:
            score = profile.get("unsuitable_score", 45)
            status = "Check"
            reason = f"Agro-climatic conditions for {crop_name} in {norm['display']} should be verified against local soil depth and water resources."

    # Determine status & exclusion from score
    if score < 25:
        status = "Unsuitable"
        status_display = "✕ Unsuitable"
        exclude = True
    elif score < 60:
        status = "Check"
        status_display = "⚠ Check"
        exclude = False
    else:
        status = "Compatible"
        status_display = "✓ Compatible"
        exclude = False

    return {
        "score": score,
        "status": status,
        "status_display": status_display,
        "reason": reason,
        "region": region,
        "city": city,
        "state": state,
        "exclude_from_ranking": exclude,
    }
