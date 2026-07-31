# Shared dataset — Contoso Travel Concierge

⚠️ **Fictional.** Companies, flights, hotels, and rentals in these CSVs are
entirely made up for educational purposes. Do not treat them as real.

Files:

| File | Schema | Used by |
|------|--------|---------|
| `flights.csv`      | [`specs/schemas/flights.schema.json`](../specs/schemas/flights.schema.json)         | Both Prompt Agent and Hosted Agent |
| `hotels.csv`       | [`specs/schemas/hotels.schema.json`](../specs/schemas/hotels.schema.json)           | Both Prompt Agent and Hosted Agent |
| `car_rentals.csv`  | [`specs/schemas/car_rentals.schema.json`](../specs/schemas/car_rentals.schema.json) | Both Prompt Agent and Hosted Agent |

`tests/test_data_schemas.py` validates each row against its schema on every PR.
