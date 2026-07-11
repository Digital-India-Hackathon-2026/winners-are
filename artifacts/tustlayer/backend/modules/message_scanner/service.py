import re
import json
import httpx
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

from backend.core.config import settings
from backend.modules.message_scanner.schemas import MessageInspectionResult, URLScanDetail
from backend.integrations.safe_browsing_client import check_urls
from backend.modules.qr_inspector.engine import VALID_UPI_HANDLES

# 1. Class for Message Scanner Service
class MessageScannerService:
    def __init__(self):
        self.groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.groq_api_key = settings.GROQ_API_KEY
        self.groq_model = settings.GROQ_MODEL or "llama3-8b-8192"

    async def scan_message(self, message_text: str) -> MessageInspectionResult:
        try:
            if not message_text or not message_text.strip():
                return MessageInspectionResult(
                    success=False,
                    message_text=message_text,
                    verdict="Needs Verification",
                    summary="Empty message text provided.",
                    error="Message text is empty"
                )

            # 1. Forwarded Detection
            is_forwarded = False
            forwarded_many_times = False
            lower_msg = message_text.lower()
            if "forwarded many times" in lower_msg:
                is_forwarded = True
                forwarded_many_times = True
            elif "forwarded" in lower_msg:
                is_forwarded = True

            # Clean forwarding headers for cleaner parsing if present
            cleaned_text = message_text
            # Remove "Forwarded" prefix lines if they clutter
            cleaned_text = re.sub(r'^(forwarded\s*many\s*times|forwarded)\s*\n?', '', cleaned_text, flags=re.I)

            # 2. Extract URLs
            # Supports http, https, and standalone shortener URLs
            url_regex = r'(https?://[^\s<>"]+|[a-zA-Z0-9.-]+\.(?:com|org|net|in|co|us|info|biz|xyz|top|click|club|online|site|live|vip|download|work|fit|gdn|icu|loan|ly|gl|co|me)/[^\s<>"]*)'
            raw_urls = re.findall(url_regex, cleaned_text, re.I)
            # Remove trailing punctuation from extracted URLs
            urls = []
            for u in raw_urls:
                cleaned_u = u.rstrip('.,:;!?)"\'')
                if cleaned_u not in urls:
                    urls.append(cleaned_u)

            # 3. Extract Phone Numbers
            # Indian numbers: +91, 91, or 10-digit starting with 6-9
            # International numbers: starting with + and 7-15 digits
            indian_phone_regex = r'(?:\+?91[-.\s]?)?[6-9]\d{9}'
            intl_phone_regex = r'\+\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
            
            raw_phones = re.findall(indian_phone_regex, cleaned_text) + re.findall(intl_phone_regex, cleaned_text)
            phone_numbers = list(set([p.strip() for p in raw_phones if p]))

            # 4. Extract UPI IDs & Validate Suffixes
            upi_regex = r'[a-zA-Z0-9.\-_]+@[a-zA-Z0-9.\-_]+'
            raw_upis = re.findall(upi_regex, cleaned_text)
            upi_ids = list(set([u.strip() for u in raw_upis if u]))

            # 5. Extract Emails
            email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            raw_emails = re.findall(email_regex, cleaned_text)
            emails = list(set([e.strip() for e in raw_emails if e]))

            # 6. Keyword Detection
            scam_keywords = [
                "KYC", "PAN Update", "Account Blocked", "Click Immediately", "Limited Time",
                "Lottery", "Prize", "Refund", "Courier Held", "Income Tax Refund",
                "Bank Verification", "Electricity Bill", "Suspended Account", "Police Notice",
                "Income Tax", "Investment", "Crypto", "APK", "Remote Access", "Screen Sharing"
            ]
            detected_keywords = []
            for kw in scam_keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', cleaned_text, re.I):
                    detected_keywords.append(kw)

            # 7. URL Safety & Domain Reputation Analysis
            url_analyses: List[URLScanDetail] = []
            google_safe_browsing_threat = False
            
            if urls:
                # Run Safe Browsing
                try:
                    sb_results = await check_urls(urls)
                except Exception as e:
                    print(f"[MESSAGE-SCANNER] Safe Browsing check error: {e}")
                    sb_results = {}

                for u in urls:
                    status = "Safe"
                    reasons = []
                    
                    # Safe Browsing API check
                    sb_match = sb_results.get(u)
                    if sb_match and sb_match.get("is_threat"):
                        status = "Likely Fraud"
                        google_safe_browsing_threat = True
                        reasons.append(f"Flagged by Google Safe Browsing as {sb_match.get('threat_type')}")
                    
                    # Domain checks
                    try:
                        parsed_u = urlparse(u if "://" in u else f"http://{u}")
                        domain = parsed_u.netloc.lower()
                        
                        # Shorteners
                        shorteners = {
                            "bit.ly", "tinyurl.com", "t.co", "goo.gl", "rebrand.ly",
                            "is.gd", "buff.ly", "ow.ly", "bit.do", "lnkd.in"
                        }
                        if any(domain == s or domain.endswith("." + s) for s in shorteners):
                            if status != "Likely Fraud":
                                status = "Needs Verification"
                            reasons.append(f"Uses a URL shortener service: {domain}")
                            
                        # Suspicious TLDs
                        suspicious_tlds = {"xyz", "top", "click", "club", "info", "online", "cc", "ws", "biz"}
                        tld = domain.split(".")[-1]
                        if tld in suspicious_tlds:
                            if status != "Likely Fraud":
                                status = "Needs Verification"
                            reasons.append(f"Suspicious top-level TLD: .{tld}")
                            
                        # Non-HTTPS
                        if u.lower().startswith("http://"):
                            if status != "Likely Fraud":
                                status = "Needs Verification"
                            reasons.append("Unencrypted connection (HTTP instead of HTTPS)")
                    except Exception:
                        pass
                        
                    if not reasons:
                        reasons.append("No obvious threat indicators detected.")
                        
                    url_analyses.append(URLScanDetail(
                        url=u,
                        status=status,
                        reason="; ".join(reasons)
                    ))

            # 8. Rule Engine Scoring (Evidence Combination)
            score = 100.0

            # Shorteners or suspicious TLDs
            for ua in url_analyses:
                if ua.status == "Likely Fraud":
                    score -= 80
                elif ua.status == "Needs Verification":
                    score -= 25

            # Phishing keywords
            score -= len(detected_keywords) * 10
            
            # Forwarded / Forwarded many times
            if forwarded_many_times:
                score -= 15
            elif is_forwarded:
                score -= 5

            # UPI ID malformed validation
            malformed_upis = False
            for upi in upi_ids:
                suffix_match = False
                for suffix in VALID_UPI_HANDLES:
                    if upi.lower().endswith(suffix):
                        suffix_match = True
                        break
                if not suffix_match:
                    malformed_upis = True
                    score -= 25

            # Intent Spoofing: Check if text mentions "receive" or "refund" alongside payment triggers
            receive_keywords = ["receive", "refund", "cashback", "claim", "credit", "earn", "reward"]
            if any(kw in lower_msg for kw in receive_keywords) and (upi_ids or urls):
                score -= 30

            # Cap score
            score = max(0.0, min(100.0, score))

            if score >= 80:
                verdict = "Verified"
            elif score >= 40:
                verdict = "Needs Verification"
            else:
                verdict = "Likely Fraud"

            # 9. LLM Explanation Generation via Groq API
            summary = ""
            concerns = []
            action_steps = []
            
            if self.groq_api_key:
                try:
                    payload = {
                        "model": self.groq_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are a cybersecurity expert scanner. "
                                    "Analyze the provided message text and its extracted threat indicators. "
                                    "Provide the output strictly in valid JSON format. "
                                    "Do NOT include any markdown block ticks (like ```json), conversation, or extra text. "
                                    "JSON template:\n"
                                    "{\n"
                                    "  \"summary\": \"1-2 sentence description of the message's main request.\",\n"
                                    "  \"concerns\": [\"Reason for concern 1\", \"Reason for concern 2\", ...],\n"
                                    "  \"action_steps\": [\"Action step 1\", \"Action step 2\", ...]\n"
                                    "}"
                                )
                            },
                            {
                                "role": "user",
                                "content": f"Message text:\n\"{message_text}\"\n\nIndicators:\n- URLs: {urls}\n- Phones: {phone_numbers}\n- UPI IDs: {upi_ids}\n- Keywords: {detected_keywords}\n- Malformed UPI ID: {malformed_upis}\n- Verdict: {verdict}\n- Score: {score}"
                            }
                        ],
                        "temperature": 0.2,
                        "max_tokens": 512,
                        "response_format": {"type": "json_object"}
                    }
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        headers = {"Authorization": f"Bearer {self.groq_api_key}", "Content-Type": "application/json"}
                        resp = await client.post(self.groq_api_url, json=payload, headers=headers)
                        if resp.status_code == 200:
                            llm_data = resp.json()["choices"][0]["message"]["content"]
                            parsed_llm = json.loads(llm_data)
                            summary = parsed_llm.get("summary", "")
                            concerns = parsed_llm.get("concerns", [])
                            action_steps = parsed_llm.get("action_steps", [])
                except Exception as llm_err:
                    print(f"[MESSAGE-SCANNER] Groq AI reasoning failed: {llm_err}")

            # Fallback reasoning if Groq fails or is not configured
            if not summary:
                summary = f"This message appears to be a potential communication asking for immediate action."
                if verdict == "Likely Fraud":
                    concerns = [
                        "The message matches multiple known phishing keywords or malicious indicators.",
                        "It directs you to click on links or verify details urgently."
                    ]
                    action_steps = [
                        "Do not click on any links in the message.",
                        "Verify with the official customer support number of the company directly.",
                        "Delete the message immediately."
                    ]
                else:
                    concerns = ["No verified details match this message, creating potential security doubts."]
                    action_steps = ["Confirm the sender's identity using official channels before taking action."]

            # 10. WhatsApp Formatted Response (Spec format)
            verdict_emoji = "🟢" if verdict == "Verified" else "🟡" if verdict == "Needs Verification" else "🔴"
            
            # Format Found list
            found_bullets = []
            if urls:
                found_bullets.append(f"• {len(urls)} website link(s)")
            if phone_numbers:
                found_bullets.append(f"• {len(phone_numbers)} phone number(s)")
            if upi_ids:
                found_bullets.append(f"• {len(upi_ids)} UPI ID(s)")
            if detected_keywords:
                found_bullets.append(f"• Scam-related language detected ({', '.join(detected_keywords[:3])})")
            if is_forwarded:
                found_bullets.append("• Forwarded message flags")
                
            found_text = "\n".join(found_bullets) if found_bullets else "• No obviously malicious entities found"

            whatsapp_response = (
                f"🛡 *TrustLayer Message Analysis*\n\n"
                f"{verdict_emoji} *{verdict}*\n\n"
                f"*Message Summary*\n"
                f"{summary}\n\n"
                f"*We found*\n"
                f"{found_text}\n\n"
                f"*Why we're concerned*\n"
                f"{chr(10).join(['• ' + c for c in concerns])}\n\n"
                f"*What you should do*\n"
                f"{chr(10).join(['✓ ' + a for a in action_steps])}"
            )

            return MessageInspectionResult(
                success=True,
                message_text=message_text,
                urls_found=urls,
                url_analysis=url_analyses,
                phone_numbers_found=phone_numbers,
                upi_ids_found=upi_ids,
                emails_found=emails,
                keywords_detected=detected_keywords,
                is_forwarded=is_forwarded,
                forwarded_many_times=forwarded_many_times,
                score=score,
                verdict=verdict,
                summary=summary,
                concerns=concerns,
                action_steps=action_steps,
                whatsapp_response=whatsapp_response
            )

        except Exception as e:
            print(f"[MESSAGE-SCANNER] Service critical error: {e}")
            import traceback
            traceback.print_exc()
            return MessageInspectionResult(
                success=False,
                message_text=message_text,
                verdict="Needs Verification",
                summary="Analysis failed due to internal error.",
                error=str(e)
            )

# Factory function
_service_instance = None
def get_message_scanner_service() -> MessageScannerService:
    global _service_instance
    if _service_instance is None:
        _service_instance = MessageScannerService()
    return _service_instance
