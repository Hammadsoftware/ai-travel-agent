
import os
import re
import certifi
import requests
import airportsdata
import pycountry

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
    dep=flight.get("departure",{})
    arr=flight.get("arrival",{})
    return f"""Airline: {flight.get('airline',{}).get('name')}
Flight: {flight.get('flight',{}).get('iata')}
Status: {flight.get('flight_status')}

Departure: {dep.get('airport')} ({dep.get('iata')})
Scheduled: {dep.get('scheduled')}

Arrival: {arr.get('airport')} ({arr.get('iata')})
Scheduled: {arr.get('scheduled')}
"""

@tool
def search_flights(query:str)->str:
    """Search flights by natural language route."""
    dep,arr=parse_route(query)
    params={"access_key":API_KEY}
    if dep: params["dep_iata"]=dep
    if arr: params["arr_iata"]=arr
    r=requests.get(BASE_URL,params=params,timeout=30)
    r.raise_for_status()
    data=r.json().get("data",[])
    if not data:
        return "No flights found."
    return "\n\n".join(format_flight(f) for f in data[:5])