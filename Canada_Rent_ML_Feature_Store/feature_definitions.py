from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float64
from datetime import timedelta

# Entity: postal code (unique region identifier)
postal_code = Entity(name="postal_code", value_type="STRING", description="Canadian postal code")

# Data source (offline store)
rental_source = FileSource(
    path="data/rental_market.csv",
    event_timestamp_column="event_timestamp",
)

# Feature View (rental stats)
rental_features = FeatureView(
    name="rental_market_stats",
    entities=["postal_code"],
    ttl=timedelta(days=30),
    schema=[
        Field(name="avg_rent_1br", dtype=Float64),
        Field(name="avg_rent_2br", dtype=Float64),
        Field(name="avg_rent_3br", dtype=Float64),
        Field(name="vacancy_rate", dtype=Float64),
    ],
    source=rental_source,
)
