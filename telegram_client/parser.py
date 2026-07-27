import re
from dataclasses import dataclass
from typing import Optional


URL_PATTERN = re.compile(
    r"https?://[^\s<>\"]+",
    re.IGNORECASE,
)

CODE_LABEL_PATTERN = re.compile(
    r"(?:promo(?:syon)?\s*kodu|bonus\s*kodu|kod)\s*[:\-]?\s*([A-Z0-9_-]{4,40})",
    re.IGNORECASE,
)

SITE_LABEL_PATTERN = re.compile(
    r"(?:site|marka)\s*[:\-]\s*([A-Z0-9ÇĞİÖŞÜ_-]{2,40})",
    re.IGNORECASE,
)

CODE_PATTERN = re.compile(
    r"\b[A-Z0-9][A-Z0-9_-]{4,39}\b",
    re.IGNORECASE,
)

IGNORED_WORDS = {
    "HTTPS",
    "HTTP",
    "TELEGRAM",
    "PROMOSYON",
    "PROMOSYONU",
    "PROMOSYONKODU",
    "BONUS",
    "BONUSKODU",
    "KAMPANYA",
    "YATIRIM",
    "ÜYELİK",
    "UYELIK",
    "CEVRİM",
    "ÇEVRİM",
    "KATILIM",
    "KULLANIM",
    "HEMEN",
    "TIKLA",
    "SITE",
    "MARKA",
    "KOD",
}


@dataclass
class ParsedPromoMessage:
    site_name: Optional[str]
    promo_code: Optional[str]
    url: Optional[str]
    raw_text: str
    is_valid: bool


def clean_url(url: str) -> str:
    return url.rstrip(".,);]}>\"'")


def extract_url(text: str) -> Optional[str]:
    match = URL_PATTERN.search(text)

    if not match:
        return None

    return clean_url(match.group(0))


def normalize_candidate(value: str) -> str:
    return value.strip(" \t\r\n:;-").upper()


def extract_promo_code(text: str) -> Optional[str]:
    labelled_match = CODE_LABEL_PATTERN.search(text)

    if labelled_match:
        return normalize_candidate(labelled_match.group(1))

    url = extract_url(text)
    text_without_url = text.replace(url, " ") if url else text

    lines = [
        normalize_candidate(line)
        for line in text_without_url.splitlines()
        if line.strip()
    ]

    # Önce tek başına duran satırlara bak.
    for line in lines:
        if line in IGNORED_WORDS:
            continue

        if not re.fullmatch(r"[A-Z0-9_-]{5,40}", line):
            continue

        if line.isdigit():
            continue

        # Kodlarda çoğunlukla büyük harf, rakam veya uzun birleşik yapı bulunur.
        has_digit = any(character.isdigit() for character in line)

        if has_digit or len(line) >= 7:
            return line

    # Son çare olarak metnin içindeki adaylara bak.
    candidates = CODE_PATTERN.findall(text_without_url)

    for candidate in candidates:
        normalized = normalize_candidate(candidate)

        if normalized in IGNORED_WORDS:
            continue

        if normalized.isdigit():
            continue

        has_digit = any(character.isdigit() for character in normalized)

        if has_digit or len(normalized) >= 7:
            return normalized

    return None


def extract_site_name(text: str, promo_code: Optional[str]) -> Optional[str]:
    labelled_match = SITE_LABEL_PATTERN.search(text)

    if labelled_match:
        return normalize_candidate(labelled_match.group(1))

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines:
        upper_line = normalize_candidate(line)

        if upper_line.startswith("HTTP"):
            continue

        if promo_code and upper_line == promo_code.upper():
            continue

        if re.search(
            r"\b(?:PROMOSYON|BONUS|KOD|YATIRIM|KAMPANYA)\b",
            upper_line,
            re.IGNORECASE,
        ):
            continue

        cleaned = re.sub(
            r"[^A-Za-z0-9ÇĞİÖŞÜçğıöşü_-]",
            "",
            line,
        )

        if 2 <= len(cleaned) <= 30:
            return cleaned.upper()

    return None


def parse_message(text: str) -> ParsedPromoMessage:
    normalized_text = text.strip()

    url = extract_url(normalized_text)
    promo_code = extract_promo_code(normalized_text)
    site_name = extract_site_name(normalized_text, promo_code)

    return ParsedPromoMessage(
        site_name=site_name,
        promo_code=promo_code,
        url=url,
        raw_text=normalized_text,
        is_valid=bool(promo_code and url),
    )