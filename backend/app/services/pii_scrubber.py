import base64
import os
import re
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .context_manager import ContextManager


TOKEN_PATTERN = re.compile(r"\{\{([A-Z_]+)_([A-Za-z0-9_-]+)\}\}")


@dataclass(frozen=True)
class Detection:
    entity_type: str
    start: int
    end: int


class PIIScrubber:
    """
    Scrubs high-risk identifiers before they reach external models or storage.

    The original value is encrypted into the token itself using AES-GCM so
    the system can restore values later without storing a separate token vault.
    """

    PII_ENTITY_TYPES = {
        "PERSON",
        "PHONE_NUMBER",
        "EMAIL_ADDRESS",
        "LOCATION",
        "DATE_TIME",
        "CREDIT_CARD",
    }

    def __init__(self, industry: str = "fertility"):
        self.context_manager = ContextManager(industry=industry)
        self.medical_terms = {
            "pcos",
            "endometriosis",
            "ivf",
            "fsh",
            "amh",
            "iui",
            "ohss",
        }
        passphrase = os.environ.get("PII_ENCRYPTION_KEY")
        if not passphrase:
            raise RuntimeError("PII_ENCRYPTION_KEY is required for the PII scrubber.")
        self._aesgcm = AESGCM(self._build_key(passphrase))

    def _build_key(self, passphrase: str) -> bytes:
        salt = b"season_1_dt_pii_scrubber"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )
        return kdf.derive(passphrase.encode("utf-8"))

    def scrub(self, text: str) -> str:
        if not text:
            return text

        detections = self._detect_entities(text)
        if not detections:
            return text

        scrubbed = text
        for detection in sorted(detections, key=lambda item: item.start, reverse=True):
            if detection.entity_type not in self.PII_ENTITY_TYPES:
                continue

            raw_value = scrubbed[detection.start:detection.end]
            token = self._build_token(detection.entity_type, raw_value)
            scrubbed = scrubbed[:detection.start] + token + scrubbed[detection.end:]

        return scrubbed

    def restore(self, masked_text: str) -> str:
        if not masked_text:
            return masked_text

        def replace(match: re.Match[str]) -> str:
            entity_type = match.group(1)
            payload = match.group(2)
            try:
                return self._decrypt_payload(payload)
            except (InvalidTag, ValueError):
                return f"[REDACTED_{entity_type}]"

        return TOKEN_PATTERN.sub(replace, masked_text)

    def restore_object(self, value: Any) -> Any:
        if isinstance(value, str):
            return self.restore(value)
        if isinstance(value, list):
            return [self.restore_object(item) for item in value]
        if isinstance(value, dict):
            return {key: self.restore_object(item) for key, item in value.items()}
        return value

    def _build_token(self, entity_type: str, raw_value: str) -> str:
        nonce = os.urandom(12)
        ciphertext = self._aesgcm.encrypt(nonce, raw_value.encode("utf-8"), None)
        payload = base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii").rstrip("=")
        return f"{{{{{entity_type}_{payload}}}}}"

    def _decrypt_payload(self, payload: str) -> str:
        padding = "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        nonce = decoded[:12]
        ciphertext = decoded[12:]
        plaintext = self._aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")

    def _detect_entities(self, text: str) -> list[Detection]:
        detections: list[Detection] = []

        detections.extend(self._scan_regex(text, "EMAIL_ADDRESS", r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b"))
        detections.extend(self._scan_regex(text, "PHONE_NUMBER", r"(?<!\w)(?:\+?\d[\d\s-]{7,}\d)(?!\w)"))
        detections.extend(self._scan_regex(text, "CREDIT_CARD", r"(?<!\w)(?:\d[ -]?){13,19}(?!\w)"))
        detections.extend(self._scan_regex(text, "DATE_TIME", r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"))
        detections.extend(self._scan_regex(text, "PERSON", r"\b[A-Z][a-z]{1,30}(?='s\b)"))
        detections.extend(self._scan_regex(text, "PERSON", r"\b(?:Patient|Mr|Mrs|Ms|Dr)\.?\s+([A-Z][a-z]{1,30})\b", group=1))
        detections.extend(self._scan_regex(text, "PERSON", r"\b(?:Hello|Hi|Hey)\s+([A-Z][a-z]{1,30})\b", group=1))

        detections.extend(self._scan_medical_terms(text))
        return self._filter_overlaps(detections, text)

    def _scan_regex(self, text: str, entity_type: str, pattern: str, group: int = 0) -> list[Detection]:
        detections: list[Detection] = []
        for match in re.finditer(pattern, text):
            detections.append(Detection(entity_type=entity_type, start=match.start(group), end=match.end(group)))
        return detections

    def _scan_medical_terms(self, text: str) -> list[Detection]:
        detections: list[Detection] = []
        for term in sorted(self.medical_terms, key=len, reverse=True):
            for match in re.finditer(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE):
                detections.append(Detection(entity_type="MEDICAL_CONDITION", start=match.start(), end=match.end()))
        return detections

    def _filter_overlaps(self, detections: list[Detection], text: str) -> list[Detection]:
        accepted: list[Detection] = []

        for detection in sorted(detections, key=lambda item: (item.start, -(item.end - item.start))):
            if self._overlaps_existing(detection, accepted):
                continue
            if detection.entity_type == "PERSON":
                candidate = text[detection.start:detection.end]
                if candidate.lower() in self.medical_terms:
                    continue
            accepted.append(detection)

        return accepted

    def _overlaps_existing(self, candidate: Detection, accepted: list[Detection]) -> bool:
        for existing in accepted:
            if candidate.start < existing.end and candidate.end > existing.start:
                return True
        return False


def scrub_input(*field_names: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            scrubber = PIIScrubber()
            for field_name in field_names:
                if field_name in kwargs and isinstance(kwargs[field_name], str):
                    kwargs[field_name] = scrubber.scrub(kwargs[field_name])
            return func(*args, **kwargs)

        return wrapper

    return decorator
