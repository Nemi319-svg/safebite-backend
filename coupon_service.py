import datetime
import logging
import threading
from collections import defaultdict, deque
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException, status
from models import Coupon, CouponRedemption, Subscription, User

logger = logging.getLogger("safebite.coupon")

# Rate limiting: max 5 redemption attempts per user per hour (3600 seconds)
RATE_LIMIT_WINDOW_SECONDS = 3600
MAX_ATTEMPTS_PER_WINDOW = 5

_rate_limit_lock = threading.Lock()
_user_attempts: Dict[int, deque] = defaultdict(deque)

_redeem_lock = threading.Lock()


def reset_rate_limits() -> None:
    """Resets rate limiting state (useful for test isolation)."""
    with _rate_limit_lock:
        _user_attempts.clear()


def check_and_record_attempt(user_id: int) -> bool:
    """
    Checks if a user is within the allowed 5 attempts/hour window.
    Returns True if allowed (and records attempt), False if rate-limited.
    """
    now = datetime.datetime.utcnow().timestamp()
    with _rate_limit_lock:
        attempts = _user_attempts[user_id]
        # Remove timestamps outside the sliding window
        while attempts and attempts[0] <= now - RATE_LIMIT_WINDOW_SECONDS:
            attempts.popleft()

        if len(attempts) >= MAX_ATTEMPTS_PER_WINDOW:
            return False

        attempts.append(now)
        return True


def normalize_code(code: Optional[str]) -> str:
    """Trims whitespace and converts code to uppercase."""
    return (code or "").strip().upper()


def redeem_coupon_for_user(
    raw_code: str,
    user: User,
    db: Any
) -> Dict[str, Any]:
    """
    Redeems a promo coupon for an authenticated, eligible user.

    Validations enforced:
    1. Authentication & user eligibility: guest users are rejected.
    2. Rate limiting: max 5 attempts/hour/user.
    3. User single-redemption constraint: one coupon per user across all codes.
    4. Code validation: code must exist, be active, and not expired.
    5. Redemption limit: code must not exceed max_redemptions.
    6. Concurrency safety: atomic execution prevents race conditions.

    Returns:
        dict: {"success": True, "premiumUntil": "<ISO-8601>", "premium_until": "<ISO-8601>", "message": "..."}
    """
    if not user or not user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "NOT_AUTHENTICATED", "message": "Authentication required to redeem coupons."}
        )

    # Check guest status
    username_lower = (user.username or "").lower()
    if getattr(user, "role", "user") == "guest" or username_lower.startswith("guest_") or username_lower == "demo_user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error_code": "NOT_AUTHENTICATED", "message": "Please sign in to your SafeBite account to redeem coupons."}
        )

    # Email verification check if configured
    if getattr(user, "email", None) and not (getattr(user, "is_verified", False) or getattr(user, "email_verified", False)):
        # If user has an unverified email
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error_code": "NOT_AUTHENTICATED", "message": "Please verify your email address before redeeming coupons."}
        )

    # Rate limiting check (5 attempts per user per hour)
    if not check_and_record_attempt(user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error_code": "LIMIT_REACHED",
                "message": "Too many coupon redemption attempts. Maximum 5 attempts per hour. Please try again later."
            }
        )

    code = normalize_code(raw_code)
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "INVALID_CODE", "message": "Please enter a valid coupon code."}
        )

    now = datetime.datetime.utcnow()

    with _redeem_lock:
        # Check single redemption per user constraint
        existing_redemption = db.find_one(CouponRedemption, {"user_id": user.id})
        if existing_redemption:
            logger.info("User %s attempted duplicate coupon redemption (already used %s)", user.id, existing_redemption.code)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error_code": "ALREADY_REDEEMED", "message": "You have already redeemed a coupon on this account."}
            )

        # Lookup coupon
        coupon = db.find_one(Coupon, {"code": code})
        if not coupon:
            logger.info("Coupon code not found: %s", code)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error_code": "INVALID_CODE", "message": "Invalid coupon code. Please check and try again."}
            )

        if not coupon.active:
            logger.info("Coupon code inactive: %s", code)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error_code": "INVALID_CODE", "message": "This coupon code is inactive."}
            )

        if coupon.expires_at and now > coupon.expires_at:
            logger.info("Coupon code expired: %s (expired at %s)", code, coupon.expires_at)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error_code": "EXPIRED", "message": "This coupon code has expired."}
            )

        if coupon.max_redemptions is not None and coupon.redeemed_count >= coupon.max_redemptions:
            logger.info("Coupon code %s limit reached: %s/%s", code, coupon.redeemed_count, coupon.max_redemptions)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error_code": "LIMIT_REACHED", "message": "This coupon has reached its maximum redemptions limit."}
            )

        # Calculate new premium expiry date: max(existing_premium_until, now + days_free * 86400)
        days_free = max(1, int(coupon.days_free or 30))
        grant_duration = datetime.timedelta(days=days_free)

        # Check existing subscription expiry if present
        existing_sub = db.find_one(Subscription, {"user_id": user.id})
        base_time = now
        if existing_sub and existing_sub.expiry_time and existing_sub.expiry_time > now:
            base_time = existing_sub.expiry_time

        new_premium_until = base_time + grant_duration

        # Increment redeemed count on coupon
        coupon.redeemed_count = int(coupon.redeemed_count or 0) + 1
        db.update(coupon)

        # Record redemption
        redemption = CouponRedemption(
            user_id=user.id,
            code=code,
            redeemed_at=now,
            premium_until=new_premium_until
        )
        db.insert(redemption)

        # Maintain backward-compatible Subscription entitlement record
        if existing_sub:
            if existing_sub.expiry_time is None or new_premium_until > existing_sub.expiry_time:
                existing_sub.expiry_time = new_premium_until
            existing_sub.status = "ACTIVE"
            existing_sub.last_checked_at = now
            db.update(existing_sub)
        else:
            new_sub = Subscription(
                user_id=user.id,
                product_id=f"safebite_coupon_{code.lower()}",
                purchase_token_hash=f"coupon_{user.id}_{code}_{int(now.timestamp())}",
                order_id=f"COUPON-{code}-{user.id}",
                status="ACTIVE",
                start_time=now,
                expiry_time=new_premium_until,
                auto_renewing=False,
                verified_at=now,
                last_checked_at=now
            )
            db.insert(new_sub)

        logger.info(
            "User %s successfully redeemed coupon %s (+%d days, active until %s)",
            user.id, code, days_free, new_premium_until.isoformat()
        )

        iso_expiry = new_premium_until.isoformat()
        return {
            "success": True,
            "premiumUntil": iso_expiry,
            "premium_until": iso_expiry,
            "days_added": days_free,
            "message": f"Coupon redeemed successfully! SafeBite Premium active for {days_free} days."
        }


def grant_premium_days(user_id: int, days: int, source: str, db: Any) -> datetime.datetime:
    """
    Grants premium days to a user, extending any existing subscription.
    Thread-safe and keeps Subscription table in sync.
    """
    now = datetime.datetime.utcnow()
    with _redeem_lock:
        existing_sub = db.find_one(Subscription, {"user_id": user_id})
        base_time = now
        if existing_sub and existing_sub.expiry_time and existing_sub.expiry_time > now:
            base_time = existing_sub.expiry_time

        new_expiry = base_time + datetime.timedelta(days=max(1, days))
        if existing_sub:
            if existing_sub.expiry_time is None or new_expiry > existing_sub.expiry_time:
                existing_sub.expiry_time = new_expiry
            existing_sub.status = "ACTIVE"
            existing_sub.last_checked_at = now
            db.update(existing_sub)
        else:
            new_sub = Subscription(
                user_id=user_id,
                product_id=f"safebite_{source}",
                purchase_token_hash=f"{source}_{user_id}_{int(now.timestamp())}",
                order_id=f"{source.upper()}-{user_id}",
                status="ACTIVE",
                start_time=now,
                expiry_time=new_expiry,
                auto_renewing=False,
                verified_at=now,
                last_checked_at=now
            )
            db.insert(new_sub)
        return new_expiry
