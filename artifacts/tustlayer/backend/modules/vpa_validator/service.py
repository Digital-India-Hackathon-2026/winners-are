"""
TrustLayer AI – VPA Validator v2.0
Validates UPI VPA handles using Razorpay's live lookup API.
Gracefully degrades to regex-only if Razorpay keys are not configured.
"""
import re
from typing import Optional
import httpx
from backend.core.config import settings
from backend.modules.vpa_validator.schemas import VPALookupResult


# PRD Section 12: 37 valid UPI bank suffixes
VALID_UPI_HANDLES = {
    "@ybl", "@ibl", "@axl",
    "@paytm",
    "@okaxis", "@okicici", "@oksbi", "@okhdfcbank",
    "@upi",
    "@apl", "@abfspay",
    "@naviaxis",
    "@waicici", "@waxis",
    "@yapl", "@rapl", "@pnb", "@sbi", "@hdfc", "@icici", "@axis",
    "@federal", "@indus", "@kotak", "@fbl",
    "@barodampay", "@mahb", "@sib", "@idbi",
    "@centralbank", "@csbpay", "@dcb", "@jkb",
    "@kvb", "@lvb", "@scb", "@unionbank",
    "@zoicici", "@freecharge", "@airtelpaymentsbank",
    # Paytm and Partner UPI handles
    "@pthdfc", "@ptaxis", "@ptsbi", "@ptyes", "@superyes",
    # WhatsApp UPI handles
    "@waaxis", "@wahdfc", "@wasbi",
}

UPI_VPA_REGEX = re.compile(r'^[\w.\-]{2,256}@[\w]{2,64}$')


def _validate_handle_format(upi_id: str) -> bool:
    """Regex + known-suffix check."""
    if not upi_id or not UPI_VPA_REGEX.match(upi_id):
        return False
    lower = upi_id.lower()
    return any(lower.endswith(h) for h in VALID_UPI_HANDLES)


def _name_match(registered_name: Optional[str], receiver_name: Optional[str]) -> Optional[bool]:
    """Fuzzy name match — returns True/False/None."""
    if not registered_name or not receiver_name:
        return None
    a = re.sub(r'[^a-z\s]', '', registered_name.lower()).strip()
    b = re.sub(r'[^a-z\s]', '', receiver_name.lower()).strip()
    if not a or not b:
        return None
    # Check word overlap
    words_a = set(a.split())
    words_b = set(b.split())
    overlap = words_a & words_b
    if not overlap:
        return False
    ratio = len(overlap) / max(len(words_a), len(words_b))
    return ratio >= 0.5


class VPAValidatorService:
    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.razorpay_available = bool(self.key_id and self.key_secret)
        print(f"[VPA-VALIDATOR] Init: key_id_present={bool(self.key_id)}, key_secret_present={bool(self.key_secret)}, available={self.razorpay_available}")

    async def validate(self, upi_id: str, receiver_name: Optional[str] = None) -> VPALookupResult:
        """
        Full VPA validation:
         1. Format + suffix regex check
         2. Razorpay live lookup (if keys configured)
         3. Name match check
        """
        handle_valid = _validate_handle_format(upi_id)

        if not self.razorpay_available:
            print(f"[VPA-VALIDATOR] Razorpay keys not set — regex-only for {upi_id}")
            return VPALookupResult(
                upi_id=upi_id,
                vpa_handle_valid=handle_valid,
                vpa_exists=None,
                error="Razorpay keys not configured — live lookup skipped"
            )

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.post(
                    "https://api.razorpay.com/v1/payments/validate/vpa",
                    json={"vpa": upi_id},
                    auth=(self.key_id, self.key_secret),
                    headers={"Content-Type": "application/json"},
                )

            if response.status_code == 200:
                data = response.json()
                vpa_exists = data.get("vpa") is not None or data.get("success") is True
                registered_name = data.get("name") or data.get("customer_name")
                match = _name_match(registered_name, receiver_name)
                print(f"[VPA-VALIDATOR] {upi_id} → exists={vpa_exists}, name='{registered_name}'")
                return VPALookupResult(
                    upi_id=upi_id,
                    vpa_handle_valid=handle_valid,
                    vpa_exists=vpa_exists,
                    registered_name=registered_name,
                    name_match=match,
                )
            elif response.status_code == 400:
                # Razorpay returns 400 for VPA not found, but also for unsupported institutional VPAs
                resp_body = response.json()
                if resp_body.get("error", {}).get("code") == "BAD_REQUEST_ERROR":
                    print(f"[VPA-VALIDATOR] {upi_id} → VPA unsupported or does not exist (400 bad request)")
                    return VPALookupResult(
                        upi_id=upi_id,
                        vpa_handle_valid=handle_valid,
                        vpa_exists=None,
                    )
                raise ValueError(f"Razorpay 400: {resp_body}")
            else:
                raise ValueError(f"Razorpay HTTP {response.status_code}")

        except Exception as e:
            print(f"[VPA-VALIDATOR] Razorpay lookup failed for {upi_id}: {e}")
            return VPALookupResult(
                upi_id=upi_id,
                vpa_handle_valid=handle_valid,
                vpa_exists=None,
                error=str(e),
            )


def get_vpa_validator_service() -> VPAValidatorService:
    return VPAValidatorService()
