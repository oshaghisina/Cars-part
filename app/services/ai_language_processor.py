"""
AI Language Processor - Advanced Multi-language Support

This module provides enhanced language detection, processing, and translation
capabilities for Persian and English text in the AI Gateway.
"""

import logging
import re
from enum import Enum
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages."""

    PERSIAN = "persian"
    ENGLISH = "english"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class LanguageProcessor:
    """
    Advanced language processing for Persian and English text.
    """

    def __init__(self):
        self.persian_patterns = self._load_persian_patterns()
        self.english_patterns = self._load_english_patterns()
        self.car_terms_mapping = self._load_car_terms_mapping()
        self.language_confidence_threshold = 0.7

    def _load_persian_patterns(self) -> Dict[str, re.Pattern]:
        """Load Persian language detection patterns."""
        return {
            "persian_chars": re.compile(
                r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
            ),
            "persian_numbers": re.compile(r"[\u06F0-\u06F9]"),
            "persian_words": re.compile(r"\b[\u0600-\u06FF]+\b"),
            "persian_car_brands": re.compile(
                r"\b(چری|جک|بریلیانس|بید|جیلی|گریت وال|ام جی|هیوندای|کیا|"
                r"نیسان|تویوتا|هوندا|میتسوبیشی|سوزوکی|مزدا|سوبارو|ایسوزو|"
                r"داچیا|رنو|پژو|سیتروئن|فیات|آلفا رومئو|لانچیا|مازراتی|"
                r"فراری|لامبورگینی|مکلارن|آستون مارتین|بنتلی|رولز رویس|"
                r"بامو|مرسدس|آئودی|پورشه|فولکس واگن|اسکودا|سیات|آلفا رومئو)\b",
                re.IGNORECASE,
            ),
            "persian_part_types": re.compile(
                r"\b(لنت|فیلتر|موتور|تعلیق|گیربکس|کلاچ|دifferential|کمک فنر|"
                r"فنر|کمربند|تسمه|شمع|سیم|کابل|باطری|آلترناتور|استارت|پمپ|"
                r"رادیاتور|ترموستات|سنسور|شیر|شلنگ|لوله|میل|شفت|یاتاقان|"
                r"بوش|واشر|پیچ|مهره|پولک|رینگ|تایر|لاستیک|چرخ|فرمان|دستی|"
                r"اتومات|کامپیوتر|ای سی یو|مپ)\b",
                re.IGNORECASE,
            ),
        }

    def _load_english_patterns(self) -> Dict[str, re.Pattern]:
        """Load English language detection patterns."""
        return {
            "english_chars": re.compile(r"[a-zA-Z]"),
            "english_numbers": re.compile(r"[0-9]"),
            "english_words": re.compile(r"\b[a-zA-Z]+\b"),
            "english_car_brands": re.compile(
                r"\b(Chery|JAC|Brilliance|BYD|Geely|Great Wall|MG|Hyundai|Kia|"
                r"Nissan|Toyota|Honda|Mitsubishi|Suzuki|Mazda|Subaru|Isuzu|Dacia|"
                r"Renault|Peugeot|Citroen|Fiat|Alfa Romeo|Lancia|Maserati|Ferrari|"
                r"Lamborghini|McLaren|Aston Martin|Bentley|Rolls Royce|BMW|Mercedes|"
                r"Audi|Porsche|Volkswagen|Skoda|Seat)\b",
                re.IGNORECASE,
            ),
            "english_part_types": re.compile(
                r"\b(brake|filter|engine|suspension|transmission|clutch|differential|"
                r"shock|spring|belt|spark|wire|cable|battery|alternator|starter|pump|"
                r"radiator|thermostat|sensor|valve|hose|pipe|shaft|bearing|bush|"
                r"gasket|screw|nut|washer|ring|tire|wheel|steering|manual|automatic|"
                r"computer|ECU|MAP)\b",
                re.IGNORECASE,
            ),
        }

    def _load_car_terms_mapping(self) -> Dict[str, Dict[str, str]]:
        """Load car terms translation mapping."""
        return {
            "brands": {
                "چری": "Chery",
                "جک": "JAC",
                "بریلیانس": "Brilliance",
                "بید": "BYD",
                "جیلی": "Geely",
                "گریت وال": "Great Wall",
                "ام جی": "MG",
                "Chery": "چری",
                "JAC": "جک",
                "Brilliance": "بریلیانس",
                "BYD": "بید",
                "Geely": "جیلی",
                "Great Wall": "گریت وال",
                "MG": "ام جی",
            },
            "part_types": {
                "لنت": "brake pad",
                "فیلتر": "filter",
                "موتور": "engine",
                "تعلیق": "suspension",
                "گیربکس": "transmission",
                "کلاچ": "clutch",
                "کمک فنر": "shock absorber",
                "فنر": "spring",
                "کمربند": "belt",
                "شمع": "spark plug",
                "باطری": "battery",
                "رادیاتور": "radiator",
                "brake pad": "لنت",
                "filter": "فیلتر",
                "engine": "موتور",
                "suspension": "تعلیق",
                "transmission": "گیربکس",
                "clutch": "کلاچ",
                "shock absorber": "کمک فنر",
                "spring": "فنر",
                "belt": "کمربند",
                "spark plug": "شمع",
                "battery": "باطری",
                "radiator": "رادیاتور",
            },
            "positions": {
                "جلو": "front",
                "عقب": "rear",
                "چپ": "left",
                "راست": "right",
                "front": "جلو",
                "rear": "عقب",
                "left": "چپ",
                "right": "راست",
            },
        }

    def detect_language(self, text: str) -> Tuple[Language, float]:
        """
        Detect the primary language of the text with confidence score.

        Args:
            text: Input text to analyze

        Returns:
            Tuple of (detected_language, confidence_score)
        """
        if not text or not text.strip():
            return Language.UNKNOWN, 0.0

        text = text.strip()
        persian_score = self._calculate_persian_score(text)
        english_score = self._calculate_english_score(text)

        total_score = persian_score + english_score

        if total_score == 0:
            return Language.UNKNOWN, 0.0

        persian_confidence = persian_score / total_score
        english_confidence = english_score / total_score

        if persian_confidence >= self.language_confidence_threshold:
            return Language.PERSIAN, persian_confidence
        elif english_confidence >= self.language_confidence_threshold:
            return Language.ENGLISH, english_confidence
        elif persian_confidence > 0.3 and english_confidence > 0.3:
            return Language.MIXED, max(persian_confidence, english_confidence)
        else:
            return Language.UNKNOWN, max(persian_confidence, english_confidence)

    def _calculate_persian_score(self, text: str) -> float:
        """Calculate Persian language confidence score."""
        score = 0.0

        # Character-based scoring
        persian_chars = len(self.persian_patterns["persian_chars"].findall(text))
        total_chars = len([c for c in text if c.isalpha()])

        if total_chars > 0:
            score += (persian_chars / total_chars) * 0.4

        # Word-based scoring
        persian_words = len(self.persian_patterns["persian_words"].findall(text))
        total_words = len(text.split())

        if total_words > 0:
            score += (persian_words / total_words) * 0.3

        # Car-specific terms scoring
        persian_car_terms = len(self.persian_patterns["persian_car_brands"].findall(text))
        persian_part_terms = len(self.persian_patterns["persian_part_types"].findall(text))

        if total_words > 0:
            score += (persian_car_terms / total_words) * 0.2
            score += (persian_part_terms / total_words) * 0.1

        return min(score, 1.0)

    def _calculate_english_score(self, text: str) -> float:
        """Calculate English language confidence score."""
        score = 0.0

        # Character-based scoring
        english_chars = len(self.english_patterns["english_chars"].findall(text))
        total_chars = len([c for c in text if c.isalpha()])

        if total_chars > 0:
            score += (english_chars / total_chars) * 0.4

        # Word-based scoring
        english_words = len(self.english_patterns["english_words"].findall(text))
        total_words = len(text.split())

        if total_words > 0:
            score += (english_words / total_words) * 0.3

        # Car-specific terms scoring
        english_car_terms = len(self.english_patterns["english_car_brands"].findall(text))
        english_part_terms = len(self.english_patterns["english_part_types"].findall(text))

        if total_words > 0:
            score += (english_car_terms / total_words) * 0.2
            score += (english_part_terms / total_words) * 0.1

        return min(score, 1.0)

    def extract_car_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract car-related entities from text.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary with extracted entities
        """
        entities = {
            "brands": [],
            "part_types": [],
            "positions": [],
            "models": [],
            "years": [],
            "numbers": [],
        }

        # Extract brands
        persian_brands = self.persian_patterns["persian_car_brands"].findall(text)
        english_brands = self.english_patterns["english_car_brands"].findall(text)
        entities["brands"] = list(set(persian_brands + english_brands))

        # Extract part types
        persian_parts = self.persian_patterns["persian_part_types"].findall(text)
        english_parts = self.english_patterns["english_part_types"].findall(text)
        entities["part_types"] = list(set(persian_parts + english_parts))

        # Extract positions
        for pos_persian, pos_english in self.car_terms_mapping["positions"].items():
            if pos_persian in text.lower():
                entities["positions"].append(pos_persian)
            if pos_english in text.lower():
                entities["positions"].append(pos_english)

        # Extract model numbers (e.g., Tiggo 8, X5, etc.)
        model_pattern = re.compile(r"\b([A-Za-z\u0600-\u06FF]+\s*\d+)\b")
        entities["models"] = model_pattern.findall(text)

        # Extract years
        year_pattern = re.compile(r"\b(19|20)\d{2}\b")
        entities["years"] = year_pattern.findall(text)

        # Extract numbers
        number_pattern = re.compile(r"\b\d+\b")
        entities["numbers"] = number_pattern.findall(text)

        return entities

    def translate_terms(self, text: str, target_language: Language) -> str:
        """
        Translate car-related terms in the text.

        Args:
            text: Input text
            target_language: Target language for translation

        Returns:
            Text with translated terms
        """
        if target_language == Language.UNKNOWN:
            return text

        translated_text = text

        # Translate brands
        for source, target in self.car_terms_mapping["brands"].items():
            if target_language == Language.PERSIAN and source.isascii():
                translated_text = re.sub(
                    r"\b" + re.escape(source) + r"\b", target, translated_text, flags=re.IGNORECASE
                )
            elif target_language == Language.ENGLISH and not source.isascii():
                translated_text = re.sub(
                    r"\b" + re.escape(source) + r"\b", target, translated_text, flags=re.IGNORECASE
                )

        # Translate part types
        for source, target in self.car_terms_mapping["part_types"].items():
            if target_language == Language.PERSIAN and source.isascii():
                translated_text = re.sub(
                    r"\b" + re.escape(source) + r"\b", target, translated_text, flags=re.IGNORECASE
                )
            elif target_language == Language.ENGLISH and not source.isascii():
                translated_text = re.sub(
                    r"\b" + re.escape(source) + r"\b", target, translated_text, flags=re.IGNORECASE
                )

        # Translate positions
        for source, target in self.car_terms_mapping["positions"].items():
            if target_language == Language.PERSIAN and source.isascii():
                translated_text = re.sub(
                    r"\b" + re.escape(source) + r"\b", target, translated_text, flags=re.IGNORECASE
                )
            elif target_language == Language.ENGLISH and not source.isascii():
                translated_text = re.sub(
                    r"\b" + re.escape(source) + r"\b", target, translated_text, flags=re.IGNORECASE
                )

        return translated_text

    def normalize_text(self, text: str) -> str:
        """
        Normalize text for better processing.

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Normalize Persian numbers to English
        persian_to_english_numbers = {
            "۰": "0",
            "۱": "1",
            "۲": "2",
            "۳": "3",
            "۴": "4",
            "۵": "5",
            "۶": "6",
            "۷": "7",
            "۸": "8",
            "۹": "9",
        }

        for persian, english in persian_to_english_numbers.items():
            text = text.replace(persian, english)

        # Normalize common variations
        text = re.sub(r"\b(تیگو|tiggo)\b", "Tiggo", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(چری|chery)\b", "Chery", text, flags=re.IGNORECASE)

        return text

    def create_search_variants(self, text: str) -> List[str]:
        """
        Create search variants for better matching.

        Args:
            text: Input text

        Returns:
            List of search variants
        """
        variants = [text]

        # Add normalized version
        normalized = self.normalize_text(text)
        if normalized != text:
            variants.append(normalized)

        # Add translated versions
        language, confidence = self.detect_language(text)

        if language == Language.PERSIAN:
            english_variant = self.translate_terms(text, Language.ENGLISH)
            if english_variant != text:
                variants.append(english_variant)
        elif language == Language.ENGLISH:
            persian_variant = self.translate_terms(text, Language.PERSIAN)
            if persian_variant != text:
                variants.append(persian_variant)

        # Add case variations
        variants.append(text.lower())
        variants.append(text.upper())
        variants.append(text.title())

        # Remove duplicates while preserving order
        seen = set()
        unique_variants = []
        for variant in variants:
            if variant not in seen:
                seen.add(variant)
                unique_variants.append(variant)

        return unique_variants

    def analyze_query_intent(self, text: str) -> Dict[str, Any]:
        """
        Analyze query intent and extract structured information.

        Args:
            text: Input query text

        Returns:
            Dictionary with analysis results
        """
        language, confidence = self.detect_language(text)
        entities = self.extract_car_entities(text)
        variants = self.create_search_variants(text)

        # Determine intent
        intent = "search"
        if any(word in text.lower() for word in ["قیمت", "price", "هزینه", "cost"]):
            intent = "price_inquiry"
        elif any(word in text.lower() for word in ["موجود", "available", "stock", "inventory"]):
            intent = "availability_check"
        elif any(word in text.lower() for word in ["مشابه", "similar", "جایگزین", "alternative"]):
            intent = "similar_parts"
        elif any(word in text.lower() for word in ["توصیه", "recommend", "پیشنهاد", "suggest"]):
            intent = "recommendation"

        return {
            "original_text": text,
            "language": language.value,
            "language_confidence": confidence,
            "intent": intent,
            "entities": entities,
            "search_variants": variants,
            "normalized_text": self.normalize_text(text),
        }
