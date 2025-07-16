# backend/scripts/seed_stats_aggregated_channel.py

from seed_utils import get_db_session
from app.models.stats import StatsAggregatedChannel
from app.models.channel import Channel
from sqlalchemy.exc import IntegrityError
import random

def seed_stats_aggregated_channel():
    session = get_db_session()
    try:
        channels = session.query(Channel).all()
        if not channels:
            print("⚠️  No channels found. Please seed channels first.")
            return

        aggregates = []
        existing = session.query(StatsAggregatedChannel.channel_id).all()
        existing_ids = {row[0] for row in existing}

        new_channels = [c for c in channels if c.id not in existing_ids]
        if not new_channels:
            print("✅ All channels already have stats. Skipping.")
            return

        for channel in new_channels:
            base = random.randint(50, 150)
            day_1 = int(base * 0.9)
            day_2 = int(base * 0.8)
            day_3 = int(base * 0.7)
            day_4 = int(base * 0.6)
            day_5 = int(base * 0.5)
            day_6 = int(base * 0.4)
            day_7 = int(base * 0.3)
            day_8 = int(base * 0.2)

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

            agg = StatsAggregatedChannel(
                channel_id=channel.id,
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
                all_time_count=month_current + random.randint(1000, 10000)
            )
            aggregates.append(agg)

        session.add_all(aggregates)
        session.commit()

        print(f"✅ Seeded {len(aggregates)} new stats_aggregated_channel entries.")
        for a in aggregates[:3]:  # Preview first 3
            print(f" - Channel ID {a.channel_id} | Daily: {a.day_current_count}, Weekly: {a.week_current_count}, All-time: {a.all_time_count}")

    except IntegrityError as e:
        session.rollback()
        print("⚠️  Integrity error while inserting aggregated channel stats:", str(e))
    finally:
        session.close()

if __name__ == "__main__":
    seed_stats_aggregated_channel()
