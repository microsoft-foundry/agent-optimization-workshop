# Copyright (c) Microsoft. All rights reserved.
"""Contoso Travel Concierge — multi-agent orchestration with the Microsoft Agent Framework.

A single user-facing **Concierge** agent orchestrates three specialist sub-agents
(Flight, Hotel, Car Rental) by calling them as tools. Each specialist owns one
CSV data source and exposes a small set of typed Python tools to query it.
"""

import csv
import os
from pathlib import Path
from typing import Any

from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from pydantic import Field
from typing_extensions import Annotated

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
INSTRUCTIONS_DIR = Path(__file__).parent / "instructions"
DEFAULT_INSTRUCTIONS_FILE = INSTRUCTIONS_DIR / "concierge.md"


# ---------------------------------------------------------------------------
# Data loaders (read once at import)
# ---------------------------------------------------------------------------

def _load_csv(name: str) -> list[dict[str, str]]:
    with (DATA_DIR / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


_FLIGHTS = _load_csv("flights.csv")
_HOTELS = _load_csv("hotels.csv")
_CARS = _load_csv("car_rentals.csv")


def _matches(value: str, query: str | None) -> bool:
    return query is None or query.strip().lower() in value.strip().lower()


def _format_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No matching records found."
    return "\n".join(f"- {row}" for row in rows)


# ---------------------------------------------------------------------------
# Flight Agent tools
# ---------------------------------------------------------------------------

@tool(approval_mode="never_require")
def search_flights(
    origin: Annotated[str | None, Field(description="Origin city, e.g. 'Chicago'. Optional.")] = None,
    destination: Annotated[str | None, Field(description="Destination city, e.g. 'Rome'. Optional.")] = None,
    cabin_class: Annotated[str | None, Field(description="Cabin class: Economy, Business, or First. Optional.")] = None,
    max_price_usd: Annotated[float | None, Field(description="Maximum price in USD. Optional.")] = None,
) -> str:
    """Search the Contoso flights catalog. Returns matching flights with id, airline, route, dates, cabin, and price."""
    results = []
    for f in _FLIGHTS:
        if not _matches(f["origin"], origin):
            continue
        if not _matches(f["destination"], destination):
            continue
        if not _matches(f["cabin_class"], cabin_class):
            continue
        if max_price_usd is not None and float(f["price_usd"]) > max_price_usd:
            continue
        results.append(f)
    return _format_rows(results)


# ---------------------------------------------------------------------------
# Hotel Agent tools
# ---------------------------------------------------------------------------

@tool(approval_mode="never_require")
def search_hotels(
    city: Annotated[str | None, Field(description="City name, e.g. 'Paris'. Optional.")] = None,
    min_star_rating: Annotated[int | None, Field(description="Minimum star rating 1-5. Optional.")] = None,
    max_price_per_night_usd: Annotated[float | None, Field(description="Maximum nightly price in USD. Optional.")] = None,
    required_amenity: Annotated[str | None, Field(description="A single amenity that must be present, e.g. 'Pool'. Optional.")] = None,
) -> str:
    """Search the Contoso hotels catalog. Returns properties with id, name, city, star rating, nightly price, and amenities."""
    results = []
    for h in _HOTELS:
        if not _matches(h["city"], city):
            continue
        if min_star_rating is not None and int(h["star_rating"]) < min_star_rating:
            continue
        if max_price_per_night_usd is not None and float(h["price_per_night_usd"]) > max_price_per_night_usd:
            continue
        if required_amenity is not None and required_amenity.strip().lower() not in h["amenities"].lower():
            continue
        results.append(h)
    return _format_rows(results)


# ---------------------------------------------------------------------------
# Car Rental Agent tools
# ---------------------------------------------------------------------------

@tool(approval_mode="never_require")
def search_car_rentals(
    city: Annotated[str | None, Field(description="Pickup city, e.g. 'Rome'. Optional.")] = None,
    car_type: Annotated[str | None, Field(description="Vehicle type: Economy, SUV, Luxury, or Minivan. Optional.")] = None,
    max_price_per_day_usd: Annotated[float | None, Field(description="Maximum daily price in USD. Optional.")] = None,
    available_only: Annotated[bool, Field(description="If true, only return vehicles currently available.")] = True,
) -> str:
    """Search the Contoso car rental catalog. Returns vehicles with id, company, city, type, daily price, and availability."""
    results = []
    for c in _CARS:
        if not _matches(c["city"], city):
            continue
        if not _matches(c["car_type"], car_type):
            continue
        if max_price_per_day_usd is not None and float(c["price_per_day_usd"]) > max_price_per_day_usd:
            continue
        if available_only and c["available"].lower() != "true":
            continue
        results.append(c)
    return _format_rows(results)


# ---------------------------------------------------------------------------
# Build the multi-agent system
# ---------------------------------------------------------------------------

def _make_client() -> FoundryChatClient:
    # FOUNDRY_PROJECT_ENDPOINT is auto-injected by the Foundry hosting runtime.
    # When running locally (azd ai agent run / direct python) we accept the
    # AZURE_AI_PROJECT_ENDPOINT name used in `.env` / Bicep outputs.
    project_endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT") or os.environ[
        "AZURE_AI_PROJECT_ENDPOINT"
    ]
    return FoundryChatClient(
        project_endpoint=project_endpoint,
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )


# ============================================================================
# WORKSHOP NOTE — THE CONCIERGE PROMPT LIVES IN A VERSIONED FILE
# ============================================================================
# The concierge system prompt is loaded from instructions/concierge.md so it
# can be iterated and version-controlled independently of this code. In Lab 3
# you edit that file, snapshot it (scripts/snapshot-instructions.sh), and
# redeploy with `azd deploy` to evaluate the change.
#
# The repo ships with the intentionally-basic baseline seed
# (instructions/versions/instructions-0.md). It passes simple playground
# checks but underperforms on the evaluation set — that gap is what you close
# during the optimization labs. Set CONCIERGE_INSTRUCTIONS_FILE to load a
# different version without editing the active file.
# ============================================================================


def _load_concierge_instructions() -> str:
    """Load the concierge system prompt from the active instructions file.

    Resolution order:
    1. CONCIERGE_INSTRUCTIONS_FILE env var (absolute, or relative to this file).
    2. instructions/concierge.md (the active prompt shipped in the image).
    """
    override = os.environ.get("CONCIERGE_INSTRUCTIONS_FILE")
    path = Path(override) if override else DEFAULT_INSTRUCTIONS_FILE
    if not path.is_absolute():
        path = Path(__file__).parent / path
    return path.read_text(encoding="utf-8").strip()


def _build_concierge() -> Agent:
    flight_agent = Agent(
        client=_make_client(),
        name="flight_agent",
        description="Searches the Contoso flights catalog and recommends flights by route, cabin class, and price.",
        instructions=(
            "You are the Contoso Flight Specialist. Use `search_flights` to answer "
            "every question. Return concise results with flight ID, airline, "
            "route, dates, cabin class, and price. Never invent flights."
        ),
        tools=[search_flights],
    )

    hotel_agent = Agent(
        client=_make_client(),
        name="hotel_agent",
        description="Searches the Contoso hotels catalog and recommends properties by city, star rating, amenities, and budget.",
        instructions=(
            "You are the Contoso Hotel Specialist. Use `search_hotels` to answer "
            "every question. Return concise results with hotel ID, name, city, "
            "star rating, nightly price, and key amenities. Never invent hotels."
        ),
        tools=[search_hotels],
    )

    car_rental_agent = Agent(
        client=_make_client(),
        name="car_rental_agent",
        description="Searches the Contoso car rental catalog and recommends vehicles by city, type, and daily price.",
        instructions=(
            "You are the Contoso Car Rental Specialist. Use `search_car_rentals` "
            "to answer every question. Return concise results with rental ID, "
            "company, city, vehicle type, daily price, and availability. "
            "Never invent vehicles."
        ),
        tools=[search_car_rentals],
    )

    concierge = Agent(
        client=_make_client(),
        name="contoso-concierge",
        description="Contoso Travel Concierge — orchestrates flight, hotel, and car rental specialists to plan complete itineraries.",
        instructions=_load_concierge_instructions(),
        tools=[
            flight_agent.as_tool(arg_description="Question to delegate to the flight specialist."),
            hotel_agent.as_tool(arg_description="Question to delegate to the hotel specialist."),
            car_rental_agent.as_tool(arg_description="Question to delegate to the car rental specialist."),
        ],
        # History is managed by the hosting infrastructure.
        default_options={"store": False},
    )
    return concierge


def main() -> None:
    server = ResponsesHostServer(_build_concierge())
    server.run()


if __name__ == "__main__":
    main()
