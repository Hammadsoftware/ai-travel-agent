
from datetime import datetime
import os
import re

import airportsdata
import certifi
import pycountry
import requests

from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
BASE_URL = "https://api.aviationstack.com/v1/flights"

AIRPORTS = airportsdata.load("IATA")

COUNTRY_ALIASES = {
    "usa":"US","us":"US","united states":"US","united states of america":"US",
    "uk":"GB","united kingdom":"GB","great britain":"GB","britain":"GB","england":"GB",
    "pakistan":"PK","pak":"PK","pk":"PK",
    "india":"IN","ind":"IN",
    "uae":"AE","united arab emirates":"AE","emirates":"AE",
}

def clean_text(text:str)->str:
    text=text.lower().strip()
    text=re.sub(r"[^a-z0-9\s]"," ",text)
    text=re.sub(r"\s+"," ",text)
    stop={"flight","flights","ticket","tickets","trip","travel","plan","planning","complete",
          "day","days","including","hotel","hotels","sightseeing","under","budget",
          "info","information","for","to","from","of","the","a","an"}
    return " ".join(w for w in text.split() if w not in stop)


def _parse_datetime(value: str | None):
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _estimate_price(duration_minutes: int | None) -> float | None:
    if duration_minutes is None:
        return None
    return round(120 + max(duration_minutes, 0) * 1.45, 2)

def country_name_to_code(text:str):
    text=text.lower().strip()
    try:
        return pycountry.countries.lookup(text).alpha_2
    except LookupError:
        pass
    for c in pycountry.countries:
        if c.name.lower() in text:
            return c.alpha_2
    for a,code in COUNTRY_ALIASES.items():
        if a in text:
            return code
    return None

def airport_country_matches(airport:dict,country_code:str)->bool:
    country=airport.get("country","")
    if country.upper()==country_code:
        return True
    obj=pycountry.countries.get(alpha_2=country_code)
    return bool(obj and country.lower()==obj.name.lower())

def get_best_airport_for_country(country_code:str):
    best=None
    score=-1
    for iata,airport in AIRPORTS.items():
        if airport_country_matches(airport,country_code):
            s=0
            name=airport.get("name","").lower()
            if "international" in name: s+=50
            if "intl" in name: s+=40
            if s>score:
                score=s
                best=iata
    return best

def resolve_location_to_iata(location:str):
    if not location:
        return None
    raw=location.strip()
    if re.fullmatch(r"[A-Za-z]{3}",raw):
        return raw.upper() if raw.upper() in AIRPORTS else None
    cc=country_name_to_code(raw)
    if cc:
        return get_best_airport_for_country(cc)
    target=clean_text(raw)
    for iata,a in AIRPORTS.items():
        if a.get("city","").lower()==target:
            return iata
    return None

def parse_route(query:str):
    m=re.search(r"from (.+?) to (.+)",query,re.I)
    if m:
        return resolve_location_to_iata(m.group(1)),resolve_location_to_iata(m.group(2))
    codes=re.findall(r"\b[A-Z]{3}\b",query)
    if len(codes)>=2:
        return codes[0],codes[1]
    return None,None

def format_flight(flight:dict)->str:
    record = parse_flight_record(flight)
    return f"""Airline: {record.get('airline')}
Flight: {record.get('flight_number')}
Status: {record.get('status')}

Departure: {record.get('origin')} at {record.get('departure_time')}
Arrival: {record.get('destination')} at {record.get('arrival_time')}
Duration: {record.get('duration_minutes')} minutes
Estimated price: {record.get('estimated_price')}
"""


def parse_flight_record(flight: dict) -> dict:
    dep = flight.get("departure", {})
    arr = flight.get("arrival", {})
    departure_time = dep.get("scheduled")
    arrival_time = arr.get("scheduled")
    departure_dt = _parse_datetime(departure_time)
    arrival_dt = _parse_datetime(arrival_time)
    duration_minutes = None
    if departure_dt and arrival_dt:
        duration = arrival_dt - departure_dt
        duration_minutes = max(int(duration.total_seconds() // 60), 0)

    airline = flight.get("airline", {}).get("name") or "Unknown airline"
    flight_number = flight.get("flight", {}).get("iata")

    return {
        "airline": airline,
        "flight_number": flight_number,
        "origin": dep.get("airport") or dep.get("iata") or dep.get("city"),
        "destination": arr.get("airport") or arr.get("iata") or arr.get("city"),
        "departure_time": departure_time,
        "arrival_time": arrival_time,
        "departure_hour": departure_dt.hour if departure_dt else None,
        "duration_minutes": duration_minutes,
        "estimated_price": _estimate_price(duration_minutes),
        "status": flight.get("flight_status"),
    }


def fetch_flights_data(query: str) -> list[dict]:
    dep, arr = parse_route(query)
    params = {"access_key": API_KEY}
    if dep:
        params["dep_iata"] = dep
    if arr:
        params["arr_iata"] = arr

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json().get("data", [])
        return [parse_flight_record(flight) for flight in data[:5]]
    except Exception:
        return []

@tool
def search_flights(query:str)->str:
    """Search flights by natural language route."""
    data = fetch_flights_data(query)
    if not data:
        return "No flights found."
    return "\n\n".join(format_flight(f) for f in data)