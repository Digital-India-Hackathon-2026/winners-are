"""
TrustLayer AI – Metadata Forensics v2.0
Enhanced EXIF, XMP, ICC, file-size, and timestamp anomaly detection.
Returns both an anomaly count AND a structured ExifForensicsResult.
"""
from PIL import Image, ExifTags
import io
import re
from typing import Optional, Tuple
from dataclasses import dataclass


EDITING_SOFTWARE = [
    "photoshop", "canva", "lightroom", "gimp", "picsart",
    "pixelmator", "snapseed", "figma", "sketch", "photoroom",
    "inshot", "pixlr", "meitu", "befunky", "fotor",
    "gd-jpeg", "paint.net", "canvas", "filmora", "capcut",
    "adobe", "affinity", "luminar", "darktable",
]

CAPTURE_APPS = [
    "screenshot", "android", "ios", "samsung", "oneplus", "xiaomi",
    "miui", "poco", "realme", "oppo", "vivo", "motorola",
]


@dataclass
class ExifForensicsResult:
    anomaly_count: int = 0
    editing_software_found: bool = False
    editing_software_name: Optional[str] = None
    exif_present: bool = False
    software_tag: Optional[str] = None
    gps_present: bool = False
    icc_mismatch: bool = False
    creation_modification_mismatch: bool = False
    details: list = None

    def __post_init__(self):
        if self.details is None:
            self.details = []


class MetadataService:
    def __init__(self):
        self.suspicious_software = EDITING_SOFTWARE

    def _check_tag_for_editor(self, value_str: str) -> Tuple[bool, Optional[str]]:
        """Check if a tag value contains known editing software."""
        for sw in self.suspicious_software:
            if sw in value_str:
                return True, sw
        return False, None

    def _is_capture_only(self, value_str: str) -> bool:
        """True if the software value is a native capture app, not an editor."""
        return any(cap in value_str for cap in CAPTURE_APPS)

    def extract_anomalies(self, image_bytes: bytes) -> int:
        """Backward-compat: returns anomaly count only."""
        result = self.analyze(image_bytes)
        return result.anomaly_count

    def analyze(self, image_bytes: bytes) -> ExifForensicsResult:
        """
        Full forensic analysis. Returns ExifForensicsResult with all signals.
        """
        result = ExifForensicsResult()
        try:
            image = Image.open(io.BytesIO(image_bytes))

            exif_data = image.getexif() if hasattr(image, "getexif") else None
            if exif_data:
                result.exif_present = True
                software_found = None
                datetime_original = None
                datetime_digitized = None

                for tag_id, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    tag_lower = str(tag_name).lower()
                    value_lower = str(value).lower()

                    # Software tag
                    if "software" in tag_lower:
                        result.software_tag = str(value).strip()
                        if not self._is_capture_only(value_lower):
                            found, sw_name = self._check_tag_for_editor(value_lower)
                            if found:
                                result.editing_software_found = True
                                result.editing_software_name = sw_name
                                result.anomaly_count += 2
                                result.details.append(f"Editing software in EXIF: {value.strip()}")
                                software_found = str(value).strip()

                    # Comment / Artist / Copyright / Description
                    elif any(t in tag_lower for t in ["comment", "artist", "copyright", "description", "imagedescription"]):
                        found, sw_name = self._check_tag_for_editor(value_lower)
                        if found:
                            result.editing_software_found = True
                            if not result.editing_software_name:
                                result.editing_software_name = sw_name
                            result.anomaly_count += 1
                            result.details.append(f"Editor reference in {tag_name}: {str(value)[:60]}")

                    # GPS presence (real screenshots never have GPS)
                    elif "gps" in tag_lower and value:
                        result.gps_present = True
                        result.anomaly_count += 1
                        result.details.append("GPS data present in screenshot (highly suspicious)")

                    # Datetime tracking
                    elif tag_lower == "datetimeoriginal":
                        datetime_original = str(value)
                    elif tag_lower == "datetimedigitized":
                        datetime_digitized = str(value)

                # Check if original != digitized (editing artifact)
                if datetime_original and datetime_digitized and datetime_original != datetime_digitized:
                    result.creation_modification_mismatch = True
                    result.anomaly_count += 1
                    result.details.append(f"DateTimeOriginal ≠ DateTimeDigitized (possible editing)")

            # ── 2. PIL info blocks (PNG text chunks, JPEG APP0/APP1) ─────────
            info = image.info or {}
            for key, val in info.items():
                key_str = str(key).lower()
                val_str = str(val).lower()

                # Skip thumbnail/raw binary data
                if len(val_str) > 2000:
                    continue

                if any(k in key_str for k in ["software", "comment", "description", "source", "author", "creator", "producer"]):
                    if not self._is_capture_only(val_str):
                        found, sw_name = self._check_tag_for_editor(val_str)
                        if found:
                            result.editing_software_found = True
                            if not result.editing_software_name:
                                result.editing_software_name = sw_name
                            result.anomaly_count += 2
                            result.details.append(f"Editor in info block [{key}]: {str(val)[:60]}")

                # XMP metadata check
                elif "xmp" in key_str or "xml" in key_str:
                    found, sw_name = self._check_tag_for_editor(val_str)
                    if found:
                        result.editing_software_found = True
                        if not result.editing_software_name:
                            result.editing_software_name = sw_name
                        result.anomaly_count += 2
                        result.details.append(f"Editor reference in XMP metadata")

                # Direct scan of any text value for editing tool names
                elif any(susp in val_str for susp in self.suspicious_software):
                    if not self._is_capture_only(val_str):
                        result.anomaly_count += 1
                        result.details.append(f"Editor name in metadata block: {str(val)[:40]}")

            # ── 3. ICC Profile check ──────────────────────────────────────────
            icc = info.get("icc_profile")
            if icc:
                icc_str = str(icc).lower()
                if any(sw in icc_str for sw in ["photoshop", "adobe", "lightroom"]):
                    result.icc_mismatch = True
                    result.anomaly_count += 1
                    result.details.append("ICC profile generated by Adobe/Photoshop")

            # ── 4. File-size sanity check (tiny files = compressed/fake) ──────
            file_size_kb = len(image_bytes) / 1024
            w, h = image.size
            pixel_count = w * h
            expected_min_kb = (pixel_count / 1_000_000) * 50  # ~50KB per MP minimum
            if file_size_kb < 10 and pixel_count > 100_000:
                result.anomaly_count += 1
                result.details.append(f"Suspiciously small file ({file_size_kb:.0f}KB) for {w}×{h} px image")

        except Exception as e:
            print(f"[METADATA-FORENSICS] Warning: {e}")

        # Clamp anomaly count
        result.anomaly_count = min(result.anomaly_count, 10)
        return result
