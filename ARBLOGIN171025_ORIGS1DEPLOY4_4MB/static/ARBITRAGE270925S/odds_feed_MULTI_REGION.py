from typing import List, Dict, Tuple, Optional
import requests, datetime

class OddsError(Exception): pass

class OddsFeed:
    def __init__(self, api_key_getter):
        self._get_key = api_key_getter
        self.last_quota: Dict[str, str] = {}
        self.last_error: Optional[str] = None

    def fetch_demo(self) -> Tuple[List[Dict[str, str]], Dict[str, str]]:
        base=[("soccer","EPL","Arsenal vs Nottingham Forest","Parions Sport (FR)","1.35","2025-09-06 10:21"),
              ("soccer","EPL","Arsenal vs Nottingham Forest","Unibet (FR)","7.05","2025-09-06 10:21"),
              ("soccer","EPL","Arsenal vs Nottingham Forest","Paddy Power","1.36","2025-09-06 10:21")]
        rows=[]
        for _ in range(12):
            for t in base:
                rows.append({"Sport":t[0],"League":t[1],"Match":t[2],"Book":t[3],"Price":t[4],"Time":t[5]})
        self.last_quota={"source":"demo"}
        self.last_error=None
        return rows, self.last_quota

    # Extended sport keys (The Odds API)
    SPORT_KEYS = {
        # Soccer
        "EPL":"soccer_epl",
        "LaLiga":"soccer_spain_la_liga",
        "Serie A":"soccer_italy_serie_a",
        "Bundesliga":"soccer_germany_bundesliga",
        "Ligue 1":"soccer_france_ligue_one",
        "Eredivisie":"soccer_netherlands_eredivisie",
        "Primeira Liga":"soccer_portugal_primeira_liga",
        "UCL":"soccer_uefa_champions_league",
        "UEL":"soccer_uefa_europa_league",
        "MLS":"soccer_usa_mls",
        "A-League":"soccer_australia_aleague",
        "J1 League":"soccer_japan_j_league",
        "K League":"soccer_south_korea_k_league1",
        "India (ISL)":"soccer_india_super_league",
        # Cricket
        "IPL":"cricket_ipl",
    }

    def fetch_live(self, league: str):
        key = (self._get_key() or "").strip()
        if not key:
            raise OddsError("API key is empty. Click Key… and save your The Odds API key first.")
        sport = self.SPORT_KEYS.get(league)
        if not sport:
            raise OddsError(f"Unsupported league '{league}'.")
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
        params = {"apiKey": key, "regions": "eu,uk,us", "markets":"h2h", "oddsFormat":"decimal", "dateFormat":"iso"}
        try:
            r = requests.get(url, params=params, timeout=15)
        except Exception as e:
            raise OddsError(f"Network error: {e!s}")
        self.last_quota = {k.lower(): v for k,v in r.headers.items() if any(w in k.lower() for w in ["quota","remaining","used","requests","limit"])}
        if r.status_code != 200:
            msg = None
            try: msg = r.json().get("message")
            except Exception: pass
            raise OddsError(msg or f"HTTP {r.status_code}")
        data = r.json()
        rows: List[Dict[str,str]] = []
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        for event in data:
            match = event.get("home_team","?")+" vs "+event.get("away_team","?")
            for book in event.get("bookmakers", []):
                book_title = book.get("title") or book.get("key","?")
                for market in book.get("markets", []):
                    if market.get("key") != "h2h":
                        continue
                    for outcome in market.get("outcomes", []):
                        price = outcome.get("price") or outcome.get("odds")
                        if price is None:
                            continue
                        rows.append({"Sport": "soccer" if sport.startswith("soccer") else "cricket",
                                     "League": league, "Match": match, "Book": book_title,
                                     "Price": f"{price}", "Time": now})
        if not rows:
            raise OddsError("No odds found for this league/regions/markets.")
        self.last_error=None
        return rows, self.last_quota
