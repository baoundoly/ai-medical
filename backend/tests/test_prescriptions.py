"""Tests for prescription creation, signing, and drug interaction detection."""
import pytest


def _setup_patient_and_visit(client, doctor_user, doctor_headers):
    """Helper: create a patient and visit, return (patient_id, visit_id)."""
    p = client.post("/api/v1/patients/", json={
        "name": "Test Patient",
        "mobile": "01700000000",
        "tenant_id": doctor_user.tenant_id,
    }, headers=doctor_headers)
    patient_id = p.json()["id"]

    v = client.post("/api/v1/visits/", json={
        "patient_id": patient_id,
        "doctor_id": doctor_user.id,
        "tenant_id": doctor_user.tenant_id,
        "chief_complaint": "Chest pain",
    }, headers=doctor_headers)
    visit_id = v.json()["id"]
    return patient_id, visit_id


def test_create_prescription(client, doctor_user, doctor_headers):
    patient_id, visit_id = _setup_patient_and_visit(client, doctor_user, doctor_headers)
    resp = client.post("/api/v1/prescriptions/", json={
        "visit_id": visit_id,
        "patient_id": patient_id,
        "doctor_id": doctor_user.id,
        "items": [
            {"medicine_name": "Paracetamol", "dosage": "500mg", "frequency": "twice", "duration": "5 days"},
        ],
    }, headers=doctor_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "draft"
    assert len(data["items"]) == 1


def test_drug_interaction_detected(client, doctor_user, doctor_headers):
    patient_id, visit_id = _setup_patient_and_visit(client, doctor_user, doctor_headers)
    resp = client.post("/api/v1/prescriptions/", json={
        "visit_id": visit_id,
        "patient_id": patient_id,
        "doctor_id": doctor_user.id,
        "items": [
            {"medicine_name": "warfarin", "dosage": "5mg"},
            {"medicine_name": "aspirin", "dosage": "100mg"},
        ],
    }, headers=doctor_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["drug_interactions"]) > 0
    interaction = data["drug_interactions"][0]
    assert interaction["severity"] == "high"


def test_sign_prescription(client, doctor_user, doctor_headers):
    patient_id, visit_id = _setup_patient_and_visit(client, doctor_user, doctor_headers)
    create_resp = client.post("/api/v1/prescriptions/", json={
        "visit_id": visit_id,
        "patient_id": patient_id,
        "doctor_id": doctor_user.id,
        "items": [{"medicine_name": "Metformin", "dosage": "500mg"}],
    }, headers=doctor_headers)
    presc_id = create_resp.json()["id"]

    sign_resp = client.post(
        f"/api/v1/prescriptions/{presc_id}/sign",
        json={"signature_method": "password", "credential": "Test@1234"},
        headers=doctor_headers,
    )
    assert sign_resp.status_code == 200
    assert sign_resp.json()["status"] == "approved"
    assert sign_resp.json()["signature_method"] == "password"


def test_double_sign_blocked(client, doctor_user, doctor_headers):
    patient_id, visit_id = _setup_patient_and_visit(client, doctor_user, doctor_headers)
    create_resp = client.post("/api/v1/prescriptions/", json={
        "visit_id": visit_id,
        "patient_id": patient_id,
        "doctor_id": doctor_user.id,
        "items": [{"medicine_name": "Atorvastatin", "dosage": "10mg"}],
    }, headers=doctor_headers)
    presc_id = create_resp.json()["id"]

    sign_resp1 = client.post(f"/api/v1/prescriptions/{presc_id}/sign",
                             json={"signature_method": "password", "credential": "x"},
                             headers=doctor_headers)
    assert sign_resp1.status_code == 200, "First sign should succeed"
    # Second sign should fail
    resp2 = client.post(f"/api/v1/prescriptions/{presc_id}/sign",
                        json={"signature_method": "password", "credential": "x"},
                        headers=doctor_headers)
    assert resp2.status_code == 400


def test_voice_parse(client, doctor_headers):
    resp = client.post("/api/v1/prescriptions/voice-parse", json={
        "text": "tab paracetamol 500mg twice daily for 5 days",
        "language": "en",
    }, headers=doctor_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
