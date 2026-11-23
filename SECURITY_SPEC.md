# SafeBite Backend Security Specification & Deployment Guide

## 1. Executive Summary
This document establishes the authoritative security architecture, threat model, authorization controls, cryptographic standards, and production operational guidelines for SafeBite's FastAPI backend and Google Play integration.

---

## 2. Threat Model & Countermeasures

| Threat Vector | Attack Scenario | Countermeasure Applied | HTTP Response |
|---|---|---|---|
| **IDOR / Resource Enumeration** | Attacker probes `/history/{id}` or `/saved-foods/{id}` using sequential integers | Strict `user_id` query filtering on all data queries; non-owned resources return 404 Not Found (never 403) to prevent ID existence leakage | `404 Not Found` |
| **Account / Email Enumeration** | Attacker calls `/send-verification` or `/resend-verification` to discover registered users | Generic idempotent responses returned ("If associated with a pending account, a code was sent"); timing-safe execution | `200 OK` (generic) |
| **OTP Brute-Force** | Attacker attempts to cycle through 6-digit verification codes (100,000–999,999) | Cryptographic hash comparison (`secrets.compare_digest`), 10-minute code expiry, max 5 failed attempts per code, after which the code and hash are permanently deleted/invalidated | `429 Too Many Requests` |
| **Credential Stuffing / DoS** | Automated bot submits rapid login or OTP requests | `SecurityRateLimiter` sliding window limiter: Max 3 OTP requests/10 min per email/IP; Max 10 failed logins/10 min per IP | `429 Too Many Requests` |
| **Admin Privilege Escalation** | Attacker discovers or brute-forces `ADMIN_SECRET` | Secret query parameters eliminated; rate limited to 5 attempts/15 min; structured audit logs (`ADMIN_AUDIT`); masked emails (`u***@domain.com`) in admin views | `401 Unauthorized` |
| **Malicious Payload / Shell Injection** | Attacker uploads bash/PHP/EXE scripts disguised with `image/jpeg` MIME header | Magic bytes verification (enforces JPEG `FF D8 FF`, PNG `89 50 4E 47`, WEBP `RIFF....WEBP`); 10MB ceiling; Pillow bitmap re-encoding | `400 Bad Request` |
| **Billing Token Replay / Fraud** | Attacker copies another user's Google Play `purchase_token` | Token hashed with SHA-256 (`purchase_token_hash`); unique ownership enforced; cross-user token reuse rejected with HTTP 409 Conflict | `409 Conflict` |
| **AI Resource Exhaustion** | Scrapers overwhelm Gemini Vision AI or NutriCoach chat | Per-user and per-IP daily quotas (Free: 15/day; Premium: 200/day) and 10 req/min burst limits | `429 Too Many Requests` |

---

## 3. Authorization & IDOR Architecture
1. **Rule of Ownership:**
   - Every read, update, and delete operation on `Scan`, `SavedFood`, `Conversation`, `ChatMessage`, `Subscription`, and `UserProfile` MUST join against `user_id == current_user.id`.
   - If no record exists with both `id == resource_id` and `user_id == current_user.id`, the server immediately returns:
     ```json
     { "detail": "Requested item or user not found." }
     ```
   - Returning `404` instead of `403` ensures attackers cannot distinguish between "id does not exist" and "id belongs to someone else".

---

## 4. Authentication, Verification & Cryptographic Standards
1. **Password Hashing:**
   - Salted `bcrypt` hashing with auto-generated salts (`bcrypt.gensalt()`).
2. **OTP Generation & Verification:**
   - 6-digit cryptographically random integer (`secrets.randbelow(900000) + 100000`).
   - Stored in database as salted SHA-256 hash (`hash_verification_code`), never in plaintext.
   - Compared using `secrets.compare_digest(computed, stored_hash)` to prevent timing side-channel attacks.
   - Expiration: exactly 10 minutes from dispatch.
   - Brute-force threshold: exactly 5 attempts before complete invalidation.
3. **Session Tokens:**
   - Signed HMAC-SHA256 JWT-equivalent bearer tokens with mandatory expiry (`exp`) claim.
   - Verified via `hmac.compare_digest` on signature segment.

---

## 5. Google Play Billing & Real-Time Developer Notifications (RTDN)
### Endpoints:
- `POST /api/subscription/verify`: Client submits `{ purchase_token, product_id, package_name, order_id }`.
  - Verifies package name (`com.safebite.app`).
  - Verifies product ID (`safebite_premium_monthly`, `safebite_premium_yearly`).
  - Queries Google Play Developer API (`purchases.subscriptions.get`).
  - Acknowledges purchase (`purchases.subscriptions.acknowledge`).
  - Stores SHA-256 hash of purchase token in `Subscription` table.
- `POST /api/subscriptions/rtdn`: Webhook for Google Cloud Pub/Sub push notifications.
  - Decodes base64 payload.
  - Handles `notificationType`:
    - `1 (RECOVERED)`, `2 (RENEWED)`, `4 (PURCHASED)`: Extends entitlement, status = `ACTIVE`.
    - `3 (CANCELED)`: Disables auto-renew; active until end of current billing period.
    - `12 (REVOKED)`, `13 (EXPIRED)`: Deactivates entitlement; status = `EXPIRED`.

---

## 6. HTTP Security Headers & Middleware
All responses include:
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (Enforces HTTPS)
- `X-Content-Type-Options: nosniff` (Prevents MIME confusion)
- `X-Frame-Options: DENY` (Clickjacking prevention)
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- Request size limit: Maximum 12MB total body size (`HTTP 413 Payload Too Large`).

---

## 7. Manual Configuration Checklist for Operator

1. **Google Cloud Console (Gemini API & OAuth):**
   - In Google Cloud Console -> APIs & Services -> Credentials:
   - Restrict the Gemini API key to **Android apps only**, specifying:
     - Package Name: `com.safebite.app`
     - SHA-1 Certificate Fingerprint: Release keystore SHA-1.
2. **Google Play Console (RTDN Setup):**
   - Go to Google Play Console -> Monetization setup.
   - Under Real-time developer notifications:
     - Topic name: `projects/<your-gcp-project>/topics/play-billing-rtdn`
   - In Google Cloud Pub/Sub:
     - Create a push subscription pointing to: `https://<your-server-domain>/api/subscriptions/rtdn`
3. **Google Play Service Account JSON:**
   - Create a Service Account in GCP with `Google Play Android Developer` role.
   - Link the Service Account in Google Play Console -> API access.
   - Grant `View financial data, orders, and cancellation survey responses` and `Manage orders and subscriptions`.
   - Provide the key in Render environment variable: `GOOGLE_PLAY_SERVICE_ACCOUNT_JSON`.
4. **Environment Variables on Render:**
   - `SECRET_KEY`: High-entropy 64-character secret for JWT/OTP signing.
   - `ADMIN_SECRET`: High-entropy secret for administrative maintenance.
   - `GEMINI_API_KEY`: Server-side Gemini API key.
   - `ENVIRONMENT`: Set to `production` (enables strict CORS origins).
