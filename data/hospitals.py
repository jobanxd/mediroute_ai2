"""Mock hospital data for MediRoute AI hackathon."""

HOSPITALS = [
    {
        "id": "H001",
        "name": "St. Luke's Medical Center - BGC",
        "address": (
            "Rizal Drive cor. 32nd St. and 5th Ave, "
            "Bonifacio Global City, Taguig, Metro Manila"
        ),
        "lat": 14.5494,
        "lng": 121.0509,
        "contact": "+63 2 8789 7700",
        "emergency_contact": "+63 2 8789 7777",
        "capabilities": {
            "trauma_unit": True,
            "ct_scan": True,
            "mri": True,
            "icu": True,
            "cardiac_cath_lab": True,
            "burn_unit": False,
            "stroke_unit": True,
            "respiratory_unit": True,
            "emergency_room": True
        },
        "insurance_accepted": [
            "Maxicare",
            "AIA Philippines Life",
            "Insular Life Assurance Company",
        ],
        "emergency_types_supported": [
            "CARDIAC", "TRAUMA", "NEUROLOGICAL", "RESPIRATORY", "GENERAL"
        ]
    },
    {
        "id": "H002",
        "name": "Makati Medical Center",
        "address": "2 Amorsolo St, Legazpi Village, Makati, Metro Manila",
        "lat": 14.5567,
        "lng": 121.0150,
        "contact": "+63 2 8888 8999",
        "emergency_contact": "+63 2 8888 8911",
        "capabilities": {
            "trauma_unit": True,
            "ct_scan": True,
            "mri": True,
            "icu": True,
            "cardiac_cath_lab": True,
            "burn_unit": False,
            "stroke_unit": True,
            "respiratory_unit": True,
            "emergency_room": True
        },
        "insurance_accepted": [
            "Maxicare",
            "AIA Philippines Life",
        ],
        "emergency_types_supported": [
            "CARDIAC", "TRAUMA", "NEUROLOGICAL", "RESPIRATORY", "GENERAL"
        ]
    },
    {
        "id": "H003",
        "name": "Philippine General Hospital",
        "address": "Taft Ave, Ermita, Manila, Metro Manila",
        "lat": 14.5765,
        "lng": 120.9822,
        "contact": "+63 2 8554 8400",
        "emergency_contact": "+63 2 8554 8450",
        "capabilities": {
            "trauma_unit": True,
            "ct_scan": True,
            "mri": True,
            "icu": True,
            "cardiac_cath_lab": False,
            "burn_unit": True,
            "stroke_unit": True,
            "respiratory_unit": True,
            "emergency_room": True
        },
        "insurance_accepted": [
            "Insular Life Assurance Company",
            "Maxicare",
        ],
        "emergency_types_supported": [
            "CARDIAC", "TRAUMA", "NEUROLOGICAL", "RESPIRATORY", "BURNS", "GENERAL"
        ]
    },
    {
        "id": "H004",
        "name": "The Medical City - Ortigas",
        "address": "Ortigas Ave, Pasig, Metro Manila",
        "lat": 14.5872,
        "lng": 121.0674,
        "contact": "+63 2 8988 1000",
        "emergency_contact": "+63 2 8988 1911",
        "capabilities": {
            "trauma_unit": False,
            "ct_scan": True,
            "mri": True,
            "icu": True,
            "cardiac_cath_lab": True,
            "burn_unit": False,
            "stroke_unit": True,
            "respiratory_unit": True,
            "emergency_room": True
        },
        "insurance_accepted": [
            "Maxicare",
            "Insular Life Assurance Company",
        ],
        "emergency_types_supported": [
            "CARDIAC", "NEUROLOGICAL", "RESPIRATORY", "GENERAL"
        ]
    },
    {
        "id": "H005",
        "name": "Lung Center of the Philippines",
        "address": "Quezon Ave, Diliman, Quezon City, Metro Manila",
        "lat": 14.6488,
        "lng": 121.0498,
        "contact": "+63 2 8924 6101",
        "emergency_contact": "+63 2 8924 6199",
        "capabilities": {
            "trauma_unit": False,
            "ct_scan": True,
            "mri": False,
            "icu": True,
            "cardiac_cath_lab": False,
            "burn_unit": False,
            "stroke_unit": False,
            "respiratory_unit": True,
            "emergency_room": True
        },
        "insurance_accepted": [
            "AIA Philippines Life",
            "Insular Life Assurance Company",
        ],
        "emergency_types_supported": ["RESPIRATORY", "GENERAL"]
    },
    {
        "id": "H006",
        "name": "National Kidney and Transplant Institute",
        "address": "East Ave, Diliman, Quezon City, Metro Manila",
        "lat": 14.6476,
        "lng": 121.0436,
        "contact": "+63 2 8981 0300",
        "emergency_contact": "+63 2 8981 0399",
        "capabilities": {
            "trauma_unit": False,
            "ct_scan": True,
            "mri": True,
            "icu": True,
            "cardiac_cath_lab": False,
            "burn_unit": False,
            "stroke_unit": False,
            "respiratory_unit": False,
            "emergency_room": True
        },
        "insurance_accepted": ["Maxicare"],
        "emergency_types_supported": ["GENERAL"]
    },
    {
        "id": "H007",
        "name": "Quezon City General Hospital",
        "address": "Seminary Rd, Diliman, Quezon City, Metro Manila",
        "lat": 14.6412,
        "lng": 121.0551,
        "contact": "+63 2 8920 7931",
        "emergency_contact": "+63 2 8920 7999",
        "capabilities": {
            "trauma_unit": True,
            "ct_scan": True,
            "mri": False,
            "icu": True,
            "cardiac_cath_lab": False,
            "burn_unit": True,
            "stroke_unit": False,
            "respiratory_unit": True,
            "emergency_room": True
        },
        "insurance_accepted": [
            "AIA Philippines Life",
            "Insular Life Assurance Company",
            "Maxicare",
        ],
        "emergency_types_supported": ["TRAUMA", "BURNS", "RESPIRATORY", "GENERAL"]
    },
    {
        "id": "H008",
        "name": "Asian Hospital and Medical Center",
        "address": (
            "2205 Civic Drive, Filinvest Corporate City, "
            "Alabang, Muntinlupa"
        ),
        "lat": 14.4195,
        "lng": 121.0347,
        "contact": "+63 2 8771 9000",
        "emergency_contact": "+63 2 8771 9911",
        "capabilities": {
            "trauma_unit": True,
            "ct_scan": True,
            "mri": True,
            "icu": True,
            "cardiac_cath_lab": True,
            "burn_unit": False,
            "stroke_unit": True,
            "respiratory_unit": True,
            "emergency_room": True
        },
        "insurance_accepted": [
            "Maxicare",
            "AIA Philippines Life",
        ],
        "emergency_types_supported": [
            "CARDIAC", "TRAUMA", "NEUROLOGICAL", "RESPIRATORY", "GENERAL"
        ]
    },
    {
        "id": "H009",
        "name": "Ospital ng Maynila Medical Center",
        "address": "Roxas Blvd, Malate, Manila, Metro Manila",
        "lat": 14.5649,
        "lng": 120.9904,
        "contact": "+63 2 8523 5555",
        "emergency_contact": "+63 2 8523 5911",
        "capabilities": {
            "trauma_unit": True,
            "ct_scan": True,
            "mri": False,
            "icu": True,
            "cardiac_cath_lab": False,
            "burn_unit": True,
            "stroke_unit": False,
            "respiratory_unit": True,
            "emergency_room": True
        },
        "insurance_accepted": [
            "Insular Life Assurance Company",
        ],
        "emergency_types_supported": ["TRAUMA", "BURNS", "RESPIRATORY", "GENERAL"]
    },
    {
        "id": "H010",
        "name": "Cardinal Santos Medical Center",
        "address": "10 Wilson St, Greenhills, San Juan, Metro Manila",
        "lat": 14.5997,
        "lng": 121.0382,
        "contact": "+63 2 8727 0001",
        "emergency_contact": "+63 2 8727 0911",
        "capabilities": {
            "trauma_unit": False,
            "ct_scan": True,
            "mri": True,
            "icu": True,
            "cardiac_cath_lab": True,
            "burn_unit": False,
            "stroke_unit": True,
            "respiratory_unit": False,
            "emergency_room": True
        },
        "insurance_accepted": [
            "Maxicare",
            "AIA Philippines Life",
            "Insular Life Assurance Company",
        ],
        "emergency_types_supported": ["CARDIAC", "NEUROLOGICAL", "GENERAL"]
    }
]


# ── Capability requirements per emergency type ────────────────────────────────

# Maps LOA service text → the capability key it corresponds to
# If the hospital has the capability, include the service in the LOA
EMERGENCY_LOA_SERVICES_MAP = {
    "CARDIAC": {
        "services": [
            {"label": "Emergency cardiac evaluation and monitoring", "requires": None},
            {"label": "Cardiac catheterization (Cath Lab) procedures", "requires": "cardiac_cath_lab"},
            {"label": "ICU admission and continuous cardiac monitoring", "requires": "icu"},
            {"label": "12-lead ECG and cardiac enzyme testing", "requires": None},
            {"label": "CT scan for diagnostic imaging", "requires": "ct_scan"},
            {"label": "MRI for advanced cardiac imaging", "requires": "mri"},
            {"label": "Emergency coronary intervention if indicated", "requires": "cardiac_cath_lab"},
        ],
        "room_type": "ICU / Cardiac Care Unit",
        "typical_exclusions": [
            "Elective cosmetic procedures",
            "Pre-existing conditions not related to cardiac emergency",
            "Non-emergency dental procedures",
        ]
    },
    "TRAUMA": {
        "services": [
            {"label": "Emergency trauma assessment and stabilization", "requires": None},
            {"label": "Trauma unit admission", "requires": "trauma_unit"},
            {"label": "ICU admission if required", "requires": "icu"},
            {"label": "CT scan for injury assessment", "requires": "ct_scan"},
            {"label": "Surgical intervention for traumatic injuries if indicated", "requires": "trauma_unit"},
            {"label": "Blood transfusion and fluid resuscitation", "requires": None},
        ],
        "room_type": "ICU / Trauma Ward",
        "typical_exclusions": [
            "Elective reconstructive surgery unrelated to trauma",
            "Non-emergency rehabilitation",
        ]
    },
    "NEUROLOGICAL": {
        "services": [
            {"label": "Emergency neurological assessment", "requires": None},
            {"label": "CT scan for neurological evaluation", "requires": "ct_scan"},
            {"label": "MRI for advanced neurological imaging", "requires": "mri"},
            {"label": "ICU admission and neurological monitoring", "requires": "icu"},
            {"label": "Stroke unit admission if indicated", "requires": "stroke_unit"},
            {"label": "Thrombolytic therapy if eligible", "requires": "stroke_unit"},
            {"label": "Neurosurgical consultation", "requires": None},
        ],
        "room_type": "ICU / Stroke Unit / Neurology Ward",
        "typical_exclusions": [
            "Elective neurosurgical procedures",
            "Non-emergency psychiatric care",
        ]
    },
    "RESPIRATORY": {
        "services": [
            {"label": "Emergency respiratory assessment and management", "requires": None},
            {"label": "Supplemental oxygen and nebulization therapy", "requires": None},
            {"label": "Respiratory unit admission", "requires": "respiratory_unit"},
            {"label": "ICU admission and mechanical ventilation if required", "requires": "icu"},
            {"label": "CT scan for pulmonary assessment", "requires": "ct_scan"},
        ],
        "room_type": "ICU / Respiratory Care Unit",
        "typical_exclusions": [
            "Elective pulmonary procedures",
            "Non-emergency allergy treatments",
        ]
    },
    "BURNS": {
        "services": [
            {"label": "Emergency burn assessment and wound management", "requires": None},
            {"label": "Burn unit admission", "requires": "burn_unit"},
            {"label": "ICU admission for severe burns", "requires": "icu"},
            {"label": "Fluid resuscitation and pain management", "requires": None},
            {"label": "Surgical debridement and skin grafting if indicated", "requires": "burn_unit"},
            {"label": "CT scan for associated injury assessment", "requires": "ct_scan"},
        ],
        "room_type": "ICU / Burn Unit",
        "typical_exclusions": [
            "Elective reconstructive or cosmetic procedures",
            "Non-burn related skin conditions",
        ]
    },
    "GENERAL": {
        "services": [
            {"label": "Emergency room evaluation and treatment", "requires": None},
            {"label": "Diagnostic workup as clinically indicated", "requires": None},
            {"label": "ICU admission if required", "requires": "icu"},
            {"label": "CT scan if indicated", "requires": "ct_scan"},
            {"label": "Physician and specialist consultation", "requires": None},
            {"label": "Standard laboratory services", "requires": None},
        ],
        "room_type": "General Ward / ICU if required",
        "typical_exclusions": [
            "Elective procedures",
            "Pre-existing conditions outside current emergency",
            "Non-emergency specialist consultations",
        ]
    }
}