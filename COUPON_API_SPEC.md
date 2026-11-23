# SafeBite Promo Coupon Architecture & API Specification

Authoritative server specification for SafeBite's promotional coupon redemption, entitlement management, and database schema on Render.

---

## 1. Overview & Business Rules

1. **Promotional Value:** Valid coupons grant **30 days of SafeBite Premium** free of charge.
2. **Confidentiality:** Active promo codes (`NEMI100`, `GUDDU100`) are stored and evaluated **exclusively on the backend database**. They must never appear anywhere in the Android APK, strings, dex, or git client code.
3. **Single Redemption Per Account:** Each authenticated user account is permitted to redeem at most **one coupon** across the lifetime of the account.
4. **Multi-User Sharing:** The same promotional code can be redeemed by multiple distinct accounts up to its configured `max_redemptions` limit.
5. **Dual Entitlement (Google Play + Coupon):**
   - Play subscriptions and promo coupons coexist seamlessly.
   - If a user holds both an active Google Play subscription and a redeemed coupon, entitlement is granted until the **later** expiration date (`max(play_expiry, coupon_expiry)`).
   - Once a coupon expires and no active Play subscription exists, the user automatically falls back to the Free Tier with zero disruption, crashes, or locked states.
6. **Authentication & Eligibility:** Redeeming requires an authenticated, non-guest account with a verified email address.
7. **Rate Limiting:** Maximum **5 redemption attempts per user per hour** to prevent brute-force attacks.

---

## 2. Database Schema

SafeBite uses a unified abstraction layer supporting both **SQLite** and **MongoDB**.

### `coupons` Table / Collection

| Field | Type | Modifiers | Description |
|---|---|---|---|
| `id` | INTEGER / ObjectId | PRIMARY KEY | Unique identifier |
| `code` | TEXT / String | UNIQUE, NOT NULL | Uppercase normalized code (e.g., `NEMI100`) |
| `days_free` | INTEGER | DEFAULT 30 | Duration in days to extend premium |
| `max_redemptions` | INTEGER | NULLABLE | Total global redemption cap (NULL = unlimited) |
| `expires_at` | TEXT / DateTime | NULLABLE | Expiration timestamp in UTC ISO-8601 |
| `active` | INTEGER / Boolean | DEFAULT 1 (True) | Active flag (1 = active, 0 = disabled) |
| `redeemed_count` | INTEGER | DEFAULT 0 | Counter incremented on each successful claim |
| `created_at` | TEXT / DateTime | UTC ISO-8601 | Creation timestamp |

#### SQLite Definition
```sql
CREATE TABLE IF NOT EXISTS coupons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    days_free INTEGER DEFAULT 30,
    max_redemptions INTEGER,
    expires_at TEXT,
    active INTEGER DEFAULT 1,
    redeemed_count INTEGER DEFAULT 0,
    created_at TEXT
);
CREATE INDEX IF NOT EXISTS ix_coupons_code ON coupons(code);
```

### `coupon_redemptions` Table / Collection

| Field | Type | Modifiers | Description |
|---|---|---|---|
| `id` | INTEGER / ObjectId | PRIMARY KEY | Unique identifier |
| `user_id` | INTEGER | UNIQUE, NOT NULL | Foreign key referencing `users(id)` |
| `code` | TEXT / String | NOT NULL | Coupon code redeemed |
| `redeemed_at` | TEXT / DateTime | UTC ISO-8601 | Timestamp of redemption |
| `premium_until` | TEXT / DateTime | UTC ISO-8601 | Computed expiration date |

#### SQLite Definition
```sql
CREATE TABLE IF NOT EXISTS coupon_redemptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    code TEXT NOT NULL,
    redeemed_at TEXT,
    premium_until TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_redemptions_user_id ON coupon_redemptions(user_id);
```

---

## 3. Endpoints

### 3.1 `POST /api/coupons/redeem`

Redeems a coupon code for the authenticated user.

- **Headers:** `Authorization: Bearer <JWT_ACCESS_TOKEN>`
- **Content-Type:** `application/json`

#### Request Body
```json
{
  "code": "NEMI100"
}
```
*(Code is trimmed and compared case-insensitively)*

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "premiumUntil": "2026-12-22T19:30:00.000000",
  "premium_until": "2026-12-22T19:30:00.000000",
  "days_added": 30,
  "message": "Coupon redeemed successfully! SafeBite Premium active for 30 days."
}
```

#### Error Responses

| HTTP Status | `errorCode` | Description / Cause |
|---|---|---|
| `400 Bad Request` | `INVALID_CODE` | Code does not exist, is empty, or is inactive |
| `400 Bad Request` | `EXPIRED` | Coupon has reached its `expires_at` date |
| `400 Bad Request` | `LIMIT_REACHED` | Coupon has reached `max_redemptions` |
| `401 Unauthorized` | `NOT_AUTHENTICATED` | Bearer token is missing, expired, or invalid |
| `403 Forbidden` | `NOT_AUTHENTICATED` | User is a guest or has unverified email |
| `409 Conflict` | `ALREADY_REDEEMED` | Account has already redeemed a coupon |
| `429 Too Many Requests` | `LIMIT_REACHED` | Exceeded 5 redemption attempts in 1 hour |

#### Error Response Payload Format
```json
{
  "success": false,
  "errorCode": "INVALID_CODE",
  "error_code": "INVALID_CODE",
  "message": "Invalid coupon code. Please check and try again.",
  "detail": "Invalid coupon code. Please check and try again."
}
```

---

### 3.2 `GET /api/subscription/status`

Returns verified subscription and entitlement information.

- **Headers:** `Authorization: Bearer <JWT_ACCESS_TOKEN>`

#### Active via Coupon (`200 OK`)
```json
{
  "is_premium": true,
  "status": "ACTIVE",
  "product_id": "safebite_coupon_nemi100",
  "order_id": "COUPON-NEMI100-42",
  "expiry_time": "2026-12-22T19:30:00.000000",
  "auto_renewing": false,
  "source": "coupon",
  "premium_until": "2026-12-22T19:30:00.000000",
  "message": "SafeBite Premium is active via coupon."
}
```

#### Active via Google Play (`200 OK`)
```json
{
  "is_premium": true,
  "status": "ACTIVE",
  "product_id": "safebite_premium_monthly",
  "order_id": "GPA.3312-4451-9981",
  "expiry_time": "2026-12-22T19:30:00.000000",
  "auto_renewing": true,
  "source": "play",
  "premium_until": "2026-12-22T19:30:00.000000",
  "message": "SafeBite Premium is active via Google Play."
}
```

#### Inactive / Expired / Free Tier (`200 OK`)
```json
{
  "is_premium": false,
  "status": "NONE",
  "product_id": null,
  "order_id": null,
  "expiry_time": null,
  "auto_renewing": false,
  "source": null,
  "premium_until": null,
  "message": "No active subscription found for this account."
}
```

---

## 4. Operational Guide: Managing Coupons Without Redeploying

### 4.1 Using the Seed CLI Script
To seed or re-verify default coupons on Render:
```bash
python backend/seed_coupons.py
```

### 4.2 Adding a New Coupon via SQL (Render Shell / SQLite)
```sql
-- Add a 30-day coupon limited to 500 redemptions expiring on Dec 31, 2026
INSERT INTO coupons (code, days_free, max_redemptions, expires_at, active, redeemed_count, created_at)
VALUES ('NEWYEAR2027', 30, 500, '2026-12-31T23:59:59', 1, 0, datetime('now'));
```

### 4.3 Disabling a Compromised or Deprecated Coupon
```sql
UPDATE coupons SET active = 0 WHERE code = 'OLDCODE';
```

### 4.4 Modifying Limits or Expiration
```sql
-- Extend limit to 1000 redemptions
UPDATE coupons SET max_redemptions = 1000 WHERE code = 'NEMI100';

-- Set an expiration date
UPDATE coupons SET expires_at = '2027-06-30T23:59:59' WHERE code = 'GUDDU100';
```

---

## 5. cURL Test Examples

### Redeem a Coupon
```bash
curl -X POST "https://safebite-g3fc.onrender.com/api/coupons/redeem" \
     -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"code": "NEMI100"}'
```

### Check Subscription Status
```bash
curl -X GET "https://safebite-g3fc.onrender.com/api/subscription/status" \
     -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```
