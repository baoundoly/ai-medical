"""Tests for patient endpoints."""
import pytest


def _create_patient(client, headers, tenant_id):
    return client.post("/api/v1/patients/", json={
        "name": "Rahim Uddin",
        "mobile": "01711000001",
        "gender": "male",
        "tenant_id": tenant_id,
    }, headers=headers)


def test_create_patient(client, doctor_user, doctor_headers):
    resp = _create_patient(client, doctor_headers, doctor_user.tenant_id)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Rahim Uddin"
    assert "patient_uid" in data
    assert data["patient_uid"].startswith("TST-DHK-")


def test_patient_uid_format(client, doctor_user, doctor_headers):
    resp = _create_patient(client, doctor_headers, doctor_user.tenant_id)
    uid = resp.json()["patient_uid"]
    parts = uid.split("-")
    assert len(parts) == 4
    assert parts[0] == "TST"
    assert parts[1] == "DHK"
    assert len(parts[3]) == 6  # 6-digit sequence


def test_list_patients(client, doctor_user, doctor_headers):
    _create_patient(client, doctor_headers, doctor_user.tenant_id)
    _create_patient(client, doctor_headers, doctor_user.tenant_id)
    resp = client.get("/api/v1/patients/", headers=doctor_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2


def test_get_patient_not_found(client, doctor_headers):
    resp = client.get("/api/v1/patients/99999", headers=doctor_headers)
    assert resp.status_code == 404


def test_update_patient(client, doctor_user, doctor_headers):
    create_resp = _create_patient(client, doctor_headers, doctor_user.tenant_id)
    patient_id = create_resp.json()["id"]
    resp = client.patch(
        f"/api/v1/patients/{patient_id}",
        json={"mobile": "01722000002"},
        headers=doctor_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["mobile"] == "01722000002"


def test_check_duplicates(client, doctor_user, doctor_headers):
    _create_patient(client, doctor_headers, doctor_user.tenant_id)
    resp = client.post(
        "/api/v1/patients/check-duplicates",
        json={"name": "Rahim Uddin", "mobile": "01711000001"},
        headers=doctor_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["count"] >= 1


def test_add_allergy(client, doctor_user, doctor_headers):
    create_resp = _create_patient(client, doctor_headers, doctor_user.tenant_id)
    patient_id = create_resp.json()["id"]
    resp = client.post(
        f"/api/v1/patients/{patient_id}/allergies",
        json={"allergen": "Penicillin", "severity": "high", "reaction": "Anaphylaxis"},
        headers=doctor_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["allergen"] == "Penicillin"


def test_assistant_cannot_access_without_role(client, assistant_user, assistant_headers):
    """Assistants can create patients but not list all users."""
    resp = client.get("/api/v1/users/", headers=assistant_headers)
    assert resp.status_code == 403
