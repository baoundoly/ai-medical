"""
AI Service: Bangla medical NLP, transcription, summarisation, and drug-interaction checks.
All AI inference is stubbed for portability — replace with real model calls as needed.
"""

import re
from typing import Optional

# ---------------------------------------------------------------------------
# Bangla → English medical term mapping
# ---------------------------------------------------------------------------
BANGLA_MEDICAL_TERMS: dict[str, str] = {
    "মাথাব্যথা": "Headache",
    "মাথা ঘোরা": "Dizziness",
    "বুক ব্যথা": "Chest pain",
    "বুক ধড়ফড়": "Palpitation",
    "শ্বাসকষ্ট": "Shortness of breath",
    "কাশি": "Cough",
    "জ্বর": "Fever",
    "পেট ব্যথা": "Abdominal pain",
    "বমি": "Vomiting",
    "বমি বমি ভাব": "Nausea",
    "ডায়রিয়া": "Diarrhoea",
    "কোষ্ঠকাঠিন্য": "Constipation",
    "ক্লান্তি": "Fatigue",
    "দুর্বলতা": "Weakness",
    "ঘুমের সমস্যা": "Insomnia",
    "পিঠ ব্যথা": "Back pain",
    "হাঁটু ব্যথা": "Knee pain",
    "গলা ব্যথা": "Sore throat",
    "কানে ব্যথা": "Earache",
    "চোখ লাল": "Red eye",
    "প্রস্রাবে জ্বালা": "Dysuria",
    "ঘন ঘন প্রস্রাব": "Frequent urination",
    "রক্তক্ষরণ": "Bleeding",
    "ফোলা": "Swelling",
    "চুলকানি": "Itching",
    "র‍্যাশ": "Rash",
    "ওজন কমা": "Weight loss",
    "ওজন বাড়া": "Weight gain",
    "ক্ষুধামন্দা": "Loss of appetite",
    "অতিরিক্ত তৃষ্ণা": "Polydipsia",
    "অতিরিক্ত ক্ষুধা": "Polyphagia",
}

# ---------------------------------------------------------------------------
# Drug interaction database (simplified)
# ---------------------------------------------------------------------------
DRUG_INTERACTIONS: dict[tuple[str, str], dict] = {
    ("warfarin", "aspirin"): {
        "severity": "high",
        "message": "Increased bleeding risk with warfarin + aspirin combination.",
    },
    ("warfarin", "ibuprofen"): {
        "severity": "high",
        "message": "NSAIDs can potentiate warfarin anticoagulation.",
    },
    ("metformin", "contrast"): {
        "severity": "high",
        "message": "Metformin should be withheld before iodinated contrast (lactic acidosis risk).",
    },
    ("ssri", "tramadol"): {
        "severity": "high",
        "message": "Serotonin syndrome risk with SSRI + tramadol.",
    },
    ("ace inhibitor", "potassium"): {
        "severity": "moderate",
        "message": "Hyperkalaemia risk with ACE inhibitor + potassium supplements.",
    },
    ("digoxin", "amiodarone"): {
        "severity": "high",
        "message": "Amiodarone significantly increases digoxin levels.",
    },
    ("sildenafil", "nitrate"): {
        "severity": "high",
        "message": "Severe hypotension risk with PDE5 inhibitor + nitrates.",
    },
    ("ciprofloxacin", "theophylline"): {
        "severity": "moderate",
        "message": "Ciprofloxacin raises theophylline levels.",
    },
}

PREGNANCY_CONTRAINDICATED = {
    "warfarin", "methotrexate", "thalidomide", "isotretinoin",
    "valproate", "carbamazepine", "lithium", "ace inhibitor", "nsaid",
}

PEDIATRIC_RESTRICTED = {
    "aspirin",   # Reye syndrome
    "tetracycline",
    "fluoroquinolone",
    "ciprofloxacin",
}

# Simple red-flag symptom patterns
RED_FLAG_PATTERNS = [
    (r"\bchest pain\b", "Possible cardiac event — urgent assessment"),
    (r"\bsevere headache\b", "Rule out meningitis or subarachnoid haemorrhage"),
    (r"\bshortness of breath\b", "Assess for respiratory or cardiac emergency"),
    (r"\bblood in (stool|urine|sputum)\b", "Bleeding — urgent investigation required"),
    (r"\bsuicidal\b|\bself.harm\b", "Mental health emergency — escalate immediately"),
    (r"\bhigh fever\b|\bfever.*days\b", "Possible systemic infection"),
    (r"\bparalysis\b|\bweakness.*one side\b", "Possible stroke — FAST assessment"),
]


def translate_bangla_symptoms(text: str) -> str:
    """Replace known Bangla medical terms in text with English equivalents."""
    for bangla, english in BANGLA_MEDICAL_TERMS.items():
        text = text.replace(bangla, english)
    return text


def extract_clinical_history(text: str) -> dict:
    """
    Extract structured clinical data from free-form transcribed text.
    Returns dict with keys: chief_complaint, symptoms, duration, severity.
    (Stub implementation — replace with NLP model.)
    """
    translated = translate_bangla_symptoms(text)
    symptoms = []
    for bangla, english in BANGLA_MEDICAL_TERMS.items():
        if bangla in text or english.lower() in translated.lower():
            symptoms.append(english)

    # Very simple heuristic for chief complaint (first sentence)
    sentences = translated.strip().split(".")
    chief_complaint = sentences[0].strip() if sentences else translated[:100]

    return {
        "chief_complaint": chief_complaint,
        "symptoms": symptoms,
        "raw_translated": translated,
    }


def suggest_diagnosis(symptoms: list[str]) -> list[dict]:
    """
    Rule-based diagnosis suggestions.  Returns up to 3 candidates with confidence.
    (Stub — replace with ML model.)
    """
    rules = {
        "Chest pain": [
            {"diagnosis": "Unstable Angina", "confidence": 0.6, "icd10": "I20.0"},
            {"diagnosis": "GERD", "confidence": 0.3, "icd10": "K21.0"},
        ],
        "Headache": [
            {"diagnosis": "Tension Headache", "confidence": 0.5, "icd10": "G44.2"},
            {"diagnosis": "Migraine", "confidence": 0.4, "icd10": "G43.9"},
        ],
        "Fever": [
            {"diagnosis": "Viral URI", "confidence": 0.5, "icd10": "J06.9"},
            {"diagnosis": "Dengue Fever", "confidence": 0.3, "icd10": "A90"},
        ],
        "Shortness of breath": [
            {"diagnosis": "Asthma", "confidence": 0.5, "icd10": "J45.9"},
            {"diagnosis": "Pneumonia", "confidence": 0.4, "icd10": "J18.9"},
        ],
    }
    diagnoses: list[dict] = []
    seen: set[str] = set()
    for symptom in symptoms:
        for candidate in rules.get(symptom, []):
            if candidate["diagnosis"] not in seen:
                diagnoses.append(candidate)
                seen.add(candidate["diagnosis"])
    return diagnoses[:3]


def detect_red_flags(text: str) -> list[str]:
    """Scan text for clinical red-flag patterns. Returns list of alert messages."""
    text_lower = text.lower()
    alerts = []
    for pattern, message in RED_FLAG_PATTERNS:
        if re.search(pattern, text_lower):
            alerts.append(message)
    return alerts


def parse_voice_prescription(text: str) -> list[dict]:
    """
    Parse a voice dictation string into structured prescription items.
    e.g. "tab paracetamol 500mg twice daily for 5 days"
    (Stub — returns simple regex-based extraction.)
    """
    items = []
    # Very simple pattern: (form) (name) (strength) (frequency) for (duration)
    pattern = re.compile(
        r"(?P<form>tab|cap|syp|inj|drop|oint)\.?\s+"
        r"(?P<name>[a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s+"
        r"(?P<strength>[\d.]+\s*(?:mg|ml|mcg|g))?\s*"
        r"(?P<frequency>once|twice|thrice|[\d]+\s*times?)?\s*"
        r"(?:daily|a\s*day)?\s*"
        r"(?:for\s+(?P<duration>[\d]+\s*(?:day|week|month)s?))?",
        re.IGNORECASE,
    )
    for m in pattern.finditer(text):
        items.append({
            "form": m.group("form"),
            "medicine_name": m.group("name"),
            "dosage": m.group("strength") or "",
            "frequency": m.group("frequency") or "",
            "duration": m.group("duration") or "",
        })
    return items


def check_drug_interactions(drug_names: list[str]) -> list[dict]:
    """
    Check a list of drug names for known interactions.
    Returns list of interaction dicts with severity and message.
    """
    normalised = [d.lower().strip() for d in drug_names]
    alerts = []
    checked: set[frozenset] = set()

    for i, d1 in enumerate(normalised):
        for d2 in normalised[i + 1 :]:
            pair = frozenset([d1, d2])
            if pair in checked:
                continue
            checked.add(pair)
            for (k1, k2), info in DRUG_INTERACTIONS.items():
                if (k1 in d1 or k1 in d2) and (k2 in d1 or k2 in d2):
                    alerts.append({"drug1": d1, "drug2": d2, **info})
                    break
    return alerts


def calculate_confidence(
    symptoms: list[str],
    diagnoses: list[dict],
    transcript_confidence: Optional[float] = None,
) -> float:
    """Return an overall AI confidence score 0-1 for the session summary."""
    base = 0.5
    if symptoms:
        base += min(len(symptoms) * 0.05, 0.2)
    if diagnoses:
        top_confidence = max(d.get("confidence", 0) for d in diagnoses)
        base = (base + top_confidence) / 2
    if transcript_confidence is not None:
        base = (base + transcript_confidence) / 2
    return round(min(base, 1.0), 3)


def transcribe_audio(file_path: str, language: str = "bn") -> dict:
    """
    Stub for audio transcription.  Replace with Whisper / Google STT call.
    Returns dict with keys: text, confidence, segments.
    """
    return {
        "text": f"[Transcription placeholder for {file_path}]",
        "confidence": 0.0,
        "segments": [],
        "language": language,
    }
