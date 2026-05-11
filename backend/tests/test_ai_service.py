"""Tests for the AI service module (no DB required)."""
import pytest

from app.services.ai_service import (
    BANGLA_MEDICAL_TERMS,
    calculate_confidence,
    check_drug_interactions,
    detect_red_flags,
    extract_clinical_history,
    parse_voice_prescription,
    suggest_diagnosis,
    translate_bangla_symptoms,
)


def test_bangla_translation_known_term():
    result = translate_bangla_symptoms("রোগীর বুক ধড়ফড় হচ্ছে")
    assert "Palpitation" in result


def test_bangla_translation_multiple_terms():
    text = "মাথাব্যথা এবং জ্বর"
    result = translate_bangla_symptoms(text)
    assert "Headache" in result
    assert "Fever" in result


def test_extract_clinical_history_bangla():
    result = extract_clinical_history("রোগীর মাথাব্যথা এবং জ্বর আছে")
    assert "symptoms" in result
    assert len(result["symptoms"]) >= 1


def test_suggest_diagnosis_chest_pain():
    diagnoses = suggest_diagnosis(["Chest pain"])
    assert len(diagnoses) > 0
    names = [d["diagnosis"] for d in diagnoses]
    assert "Unstable Angina" in names or "GERD" in names


def test_suggest_diagnosis_unknown_symptom():
    diagnoses = suggest_diagnosis(["Unknown symptom XYZ"])
    assert diagnoses == []


def test_detect_red_flags_chest_pain():
    alerts = detect_red_flags("Patient has chest pain and shortness of breath")
    assert len(alerts) >= 1


def test_detect_red_flags_clean():
    alerts = detect_red_flags("Patient has mild cold")
    assert alerts == []


def test_drug_interaction_warfarin_aspirin():
    interactions = check_drug_interactions(["warfarin", "aspirin"])
    assert len(interactions) == 1
    assert interactions[0]["severity"] == "high"


def test_drug_interaction_no_interaction():
    interactions = check_drug_interactions(["paracetamol", "amoxicillin"])
    assert interactions == []


def test_drug_interaction_multiple():
    interactions = check_drug_interactions(["warfarin", "aspirin", "ibuprofen"])
    assert len(interactions) >= 2


def test_parse_voice_prescription():
    items = parse_voice_prescription("tab paracetamol 500mg twice daily for 5 days")
    assert len(items) >= 1
    assert items[0]["medicine_name"].lower() == "paracetamol"


def test_calculate_confidence_with_symptoms_and_diagnoses():
    symptoms = ["Fever", "Headache"]
    diagnoses = [{"diagnosis": "Viral URI", "confidence": 0.5}]
    score = calculate_confidence(symptoms, diagnoses, transcript_confidence=0.8)
    assert 0.0 <= score <= 1.0


def test_bangla_terms_dict_not_empty():
    assert len(BANGLA_MEDICAL_TERMS) > 10
