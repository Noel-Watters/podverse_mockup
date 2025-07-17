# backend/scripts/seed_stats_aggregated_item.py

from seed_utils import get_db_session
from app.models.item import Item, StatsAggregatedItem
from sqlalchemy.exc import IntegrityError
import random

def seed_stats_aggregated_item():
    session = get_db_session()
    try:
        items = session.query(Item).all()
        if not items:
            print("⚠️  No items found. Please seed items first.")
            return

        # Check for already-seeded items to avoid duplication
        existing = session.query(StatsAggregatedItem.item_id).all()
        existing_ids = {row[0] for row in existing}
        new_items = [item for item in items if item.id not in existing_ids]

        if not new_items:
            print("✅ All items already have stats. Skipping.")
            return

        aggregates = []
        for item in new_items:
            base = random.randint(20, 120)
            day_1 = int(base * 0.95)
            day_2 = int(base * 0.85)
            day_3 = int(base * 0.75)
            day_4 = int(base * 0.65)
            day_5 = int(base * 0.55)
            day_6 = int(base * 0.45)
            day_7 = int(base * 0.35)
            day_8 = int(base * 0.25)

            # Week and Month Calcs
            week_current = int(
                base + day_1 + day_2 + day_3 + day_4 + day_5 + day_6 + day_7
            )
            week_1 = int(week_current * 0.6)
            week_2 = int(week_current * 0.5)
            week_3 = int(week_current * 0.4)
            week_4 = int(week_current * 0.3)

            month_current = int(
                week_current + week_1 + week_2 + week_3
            )

            month_1 = int(
                week_1 + week_2 + week_3 + week_4
            )

            agg = StatsAggregatedItem(
                item_id=item.id,
                day_current_count=base,
                day_1_count=day_1,
                day_2_count=day_2,
                day_3_count=day_3,
                day_4_count=day_4,
                day_5_count=day_5,
                day_6_count=day_6,
                day_7_count=day_7,
                day_8_count=day_8,
                week_current_count=week_current,
                week_1_count=week_1,
                week_2_count=week_2,
                week_3_count=week_3,
                week_4_count=week_4,
                month_current_count=month_current,
                month_1_count=month_1,
                all_time_count=month_current + random.randint(200, 2000)
            )
            aggregates.append(agg)

        session.add_all(aggregates)
        session.commit()

        print(f"✅ Seeded {len(aggregates)} new stats_aggregated_item entries.")
        for a in aggregates[:3]:  # Preview first 3
            print(f" - Item ID {a.item_id} | Daily: {a.day_current_count}, Weekly: {a.week_current_count}, All-time: {a.all_time_count}")

    except IntegrityError as e:
        session.rollback()
        print("⚠️  Integrity error while inserting aggregated item stats:", str(e))
    finally:
        session.close()

if __name__ == "__main__":
    seed_stats_aggregated_item()
