"""
Seed Script for SafeBite Promotional Coupons.
Seeds NEMI100 and GUDDU100 (30 days free Premium) into SQLite or MongoDB store.
Can be executed safely and repeatedly on Render or locally.
"""
import datetime
import logging
from database import get_db, init_db, store
from models import Coupon

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("safebite.seed")

DEFAULT_COUPONS = [
    {
        "code": "NEMI100",
        "days_free": 30,
        "max_redemptions": None,
        "expires_at": None,
        "active": True
    },
    {
        "code": "GUDDU100",
        "days_free": 30,
        "max_redemptions": None,
        "expires_at": None,
        "active": True
    }
]

def seed():
    init_db()
    now = datetime.datetime.utcnow()
    for item in DEFAULT_COUPONS:
        existing = store.find_one(Coupon, {"code": item["code"]})
        if not existing:
            coupon = Coupon(
                code=item["code"],
                days_free=item["days_free"],
                max_redemptions=item["max_redemptions"],
                expires_at=item["expires_at"],
                active=item["active"],
                redeemed_count=0,
                created_at=now
            )
            store.insert(coupon)
            logger.info("Successfully created coupon: %s (days_free=%d)", item["code"], item["days_free"])
        else:
            logger.info("Coupon %s already exists in database (redeemed_count=%d)", item["code"], existing.redeemed_count)

if __name__ == "__main__":
    seed()
