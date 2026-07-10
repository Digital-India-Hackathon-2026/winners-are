from PIL import Image
import io
from typing import List, Optional
from backend.modules.fraud_intelligence.schemas import FraudFingerprint, SimilarityScore

class FraudIntelligenceEngine:
    def __init__(self, exact_match_threshold: int = 5):
        """
        exact_match_threshold: Maximum Hamming distance to be considered a 'near-exact' match.
        For a hackathon MVP, a distance of <= 5 usually handles minor compression artifacts well.
        """
        self.exact_match_threshold = exact_match_threshold

    def generate_phash(self, image_bytes: bytes) -> str:
        """Generates a robust Difference Hash (dHash) to capture structural layout and borders."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Resize to 9x8 and convert to grayscale. 
            # We resize to 9 width so we can compare adjacent horizontal pixels (giving 8 differences per row).
            image = image.convert('L').resize((9, 8), Image.Resampling.LANCZOS)
            pixels = list(image.getdata())
            
            # Calculate horizontal differences between adjacent pixels:
            # 8 rows of 9 pixels -> 8 rows of 8 differences = 64 bits.
            bits = []
            for row in range(8):
                for col in range(8):
                    pixel_left = pixels[row * 9 + col]
                    pixel_right = pixels[row * 9 + col + 1]
                    bits.append('1' if pixel_left > pixel_right else '0')
                    
            bit_str = ''.join(bits)
            hex_str = f"{int(bit_str, 2):016x}"
            return hex_str
        except Exception as e:
            raise ValueError(f"Failed to process image for dHash: {e}")

    def calculate_distance(self, hash1: str, hash2: str) -> int:
        """Calculates Hamming distance between two hex hash strings in pure Python."""
        try:
            val1 = int(hash1, 16)
            val2 = int(hash2, 16)
            return bin(val1 ^ val2).count('1')
        except Exception:
            # Fallback character-wise distance in case of mismatched formats
            return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))

    def confidence_from_distance(self, distance: int, max_distance: int = 64) -> float:
        """
        Converts a Hamming distance into a normalized confidence percentage [0.0 - 1.0].
        0 distance = 1.0 confidence.
        """
        confidence = max(0.0, 1.0 - (distance / max_distance))
        return round(confidence, 3)

    def find_matches(self, input_hash: str, known_fingerprints: List[FraudFingerprint]) -> List[SimilarityScore]:
        """
        Scans a list of known fraud fingerprints and returns matches below the threshold.
        """
        matches = []
        for fingerprint in known_fingerprints:
            distance = self.calculate_distance(input_hash, fingerprint.phash)
            if distance <= self.exact_match_threshold:
                confidence = self.confidence_from_distance(distance)
                matches.append(SimilarityScore(
                    fingerprint_id=fingerprint.id,
                    hamming_distance=distance,
                    match_confidence=confidence,
                    fraud_type=fingerprint.fraud_type
                ))
        
        # Sort by best match (lowest distance / highest confidence)
        matches.sort(key=lambda x: x.hamming_distance)
        return matches
