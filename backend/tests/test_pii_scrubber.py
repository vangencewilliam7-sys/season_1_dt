import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.pii_scrubber import PIIScrubber


os.environ["PII_ENCRYPTION_KEY"] = "test_passphrase_for_pii_scrubber"


@pytest.fixture
def scrubber():
    return PIIScrubber()


def test_scrub_person_name(scrubber):
    text = "Is Anu's blood pressure safe?"
    scrubbed = scrubber.scrub(text)
    assert "Anu" not in scrubbed
    assert "{{PERSON_" in scrubbed
    assert scrubbed.startswith("Is {{PERSON_")


def test_scrub_phone_number(scrubber):
    text = "Call me at 9876543210"
    scrubbed = scrubber.scrub(text)
    assert "9876543210" not in scrubbed
    assert "{{PHONE_NUMBER_" in scrubbed


def test_scrub_email(scrubber):
    text = "Email john@hospital.com"
    scrubbed = scrubber.scrub(text)
    assert "john@hospital.com" not in scrubbed
    assert "{{EMAIL_ADDRESS_" in scrubbed


def test_roundtrip(scrubber):
    text = "Patient Anu, age 32, call 9876543210"
    scrubbed = scrubber.scrub(text)
    assert "Anu" not in scrubbed
    assert "9876543210" not in scrubbed

    restored = scrubber.restore(scrubbed)
    assert restored == text


def test_medical_terms_preserved(scrubber):
    text = "Patient has PCOS and low AMH"
    scrubbed = scrubber.scrub(text)
    assert "PCOS" in scrubbed
    assert "AMH" in scrubbed
    assert "MEDICAL_CONDITION" not in scrubbed


def test_no_pii_passthrough(scrubber):
    text = "What is the IVF process?"
    scrubbed = scrubber.scrub(text)
    assert scrubbed == text


def test_key_mismatch():
    scrubber_a = PIIScrubber()
    scrubber_a._aesgcm = scrubber_a._aesgcm.__class__(scrubber_a._build_key("key_A_password"))

    scrubber_b = PIIScrubber()
    scrubber_b._aesgcm = scrubber_b._aesgcm.__class__(scrubber_b._build_key("key_B_password"))

    text = "Hello Anu"
    scrubbed_a = scrubber_a.scrub(text)

    restored_b = scrubber_b.restore(scrubbed_a)

    assert "Anu" not in restored_b
    assert "[REDACTED_PERSON]" in restored_b
