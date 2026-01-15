"""
NYC-specific mock data for evaluation scenarios.

This module provides geographically coherent mock data organized by
hierarchical regions (atomic and composite) for realistic evaluation.

All coordinates are real NYC locations.
"""

from typing import Any


# =============================================================================
# NYC WEATHER MOCK DATA (Independent of region - all NYC area)
# =============================================================================

MOCK_WEATHER_NYC: list[dict[str, Any]] = [
    {
        "id": "weather_sunny_warm",
        "location": "New York, NY",
        "temperature": 75,
        "feels_like": 73,
        "condition": "clear",
        "description": "sunny and pleasant",
        "humidity": 45,
        "wind_speed": 8.0,
        "precipitation": 0,
        "clouds": 5,
        "outdoor_suitable": True,
        "outdoor_recommendation": "Great weather for outdoor activities!",
    },
    {
        "id": "weather_sunny_hot",
        "location": "New York, NY",
        "temperature": 92,
        "feels_like": 98,
        "condition": "clear",
        "description": "hot and humid",
        "humidity": 70,
        "wind_speed": 5.0,
        "precipitation": 0,
        "clouds": 10,
        "outdoor_suitable": False,
        "outdoor_recommendation": "Very hot - consider indoor activities or water activities",
    },
    {
        "id": "weather_cloudy_mild",
        "location": "New York, NY",
        "temperature": 68,
        "feels_like": 66,
        "condition": "clouds",
        "description": "partly cloudy",
        "humidity": 55,
        "wind_speed": 12.0,
        "precipitation": 0,
        "clouds": 45,
        "outdoor_suitable": True,
        "outdoor_recommendation": "Good weather for outdoor activities",
    },
    {
        "id": "weather_overcast",
        "location": "New York, NY",
        "temperature": 58,
        "feels_like": 55,
        "condition": "clouds",
        "description": "overcast",
        "humidity": 65,
        "wind_speed": 10.0,
        "precipitation": 0,
        "clouds": 90,
        "outdoor_suitable": True,
        "outdoor_recommendation": "Cloudy but dry - outdoor activities okay",
    },
    {
        "id": "weather_rainy",
        "location": "New York, NY",
        "temperature": 52,
        "feels_like": 48,
        "condition": "rain",
        "description": "steady rain",
        "humidity": 85,
        "wind_speed": 15.0,
        "precipitation": 5.2,
        "clouds": 100,
        "outdoor_suitable": False,
        "outdoor_recommendation": "Rainy weather - indoor activities recommended",
    },
    {
        "id": "weather_drizzle",
        "location": "New York, NY",
        "temperature": 55,
        "feels_like": 52,
        "condition": "drizzle",
        "description": "light drizzle",
        "humidity": 78,
        "wind_speed": 8.0,
        "precipitation": 0.8,
        "clouds": 80,
        "outdoor_suitable": False,
        "outdoor_recommendation": "Light rain - consider indoor activities",
    },
    {
        "id": "weather_cold_clear",
        "location": "New York, NY",
        "temperature": 35,
        "feels_like": 28,
        "condition": "clear",
        "description": "cold and clear",
        "humidity": 40,
        "wind_speed": 18.0,
        "precipitation": 0,
        "clouds": 5,
        "outdoor_suitable": False,
        "outdoor_recommendation": "Very cold - dress warmly or choose indoor activities",
    },
    {
        "id": "weather_cold_cloudy",
        "location": "New York, NY",
        "temperature": 42,
        "feels_like": 36,
        "condition": "clouds",
        "description": "cold and overcast",
        "humidity": 55,
        "wind_speed": 12.0,
        "precipitation": 0,
        "clouds": 75,
        "outdoor_suitable": False,
        "outdoor_recommendation": "Cold weather - indoor activities recommended",
    },
    {
        "id": "weather_snow",
        "location": "New York, NY",
        "temperature": 28,
        "feels_like": 18,
        "condition": "snow",
        "description": "light snow",
        "humidity": 80,
        "wind_speed": 10.0,
        "precipitation": 2.0,
        "clouds": 100,
        "outdoor_suitable": False,
        "outdoor_recommendation": "Snowy - indoor activities recommended",
    },
    {
        "id": "weather_spring_perfect",
        "location": "New York, NY",
        "temperature": 65,
        "feels_like": 65,
        "condition": "clear",
        "description": "perfect spring day",
        "humidity": 50,
        "wind_speed": 6.0,
        "precipitation": 0,
        "clouds": 15,
        "outdoor_suitable": True,
        "outdoor_recommendation": "Perfect weather for any outdoor activity!",
    },
]


# =============================================================================
# NYC TRANSIT STOPS BY REGION
# =============================================================================

MOCK_TRANSIT_STOPS_NYC: dict[str, list[dict[str, Any]]] = {
    "greenpoint": [
        {"name": "Greenpoint Ave", "lat": 40.7312, "lng": -73.9544, "type": "SUBWAY", "line_name": "G"},
        {"name": "Nassau Ave", "lat": 40.7244, "lng": -73.9512, "type": "SUBWAY", "line_name": "G"},
    ],
    "williamsburg": [
        {"name": "Bedford Ave", "lat": 40.7172, "lng": -73.9567, "type": "SUBWAY", "line_name": "L"},
        {"name": "Lorimer St", "lat": 40.7140, "lng": -73.9500, "type": "SUBWAY", "line_name": "L"},
        {"name": "Metropolitan Ave", "lat": 40.7127, "lng": -73.9515, "type": "SUBWAY", "line_name": "G"},
        {"name": "Marcy Ave", "lat": 40.7083, "lng": -73.9579, "type": "SUBWAY", "line_name": "J/M/Z"},
    ],
    "dumbo": [
        {"name": "York St", "lat": 40.7014, "lng": -73.9867, "type": "SUBWAY", "line_name": "F"},
        {"name": "High St", "lat": 40.6994, "lng": -73.9907, "type": "SUBWAY", "line_name": "A/C"},
    ],
    "brooklyn_heights": [
        {"name": "Clark St", "lat": 40.6975, "lng": -73.9932, "type": "SUBWAY", "line_name": "2/3"},
        {"name": "Borough Hall", "lat": 40.6930, "lng": -73.9899, "type": "SUBWAY", "line_name": "2/3/4/5/R"},
    ],
    "fidi": [
        {"name": "Wall St", "lat": 40.7074, "lng": -74.0119, "type": "SUBWAY", "line_name": "2/3"},
        {"name": "Fulton St", "lat": 40.7102, "lng": -74.0074, "type": "SUBWAY", "line_name": "2/3/4/5/A/C/J/Z"},
        {"name": "Broad St", "lat": 40.7063, "lng": -74.0112, "type": "SUBWAY", "line_name": "J/Z"},
        {"name": "Bowling Green", "lat": 40.7044, "lng": -74.0143, "type": "SUBWAY", "line_name": "4/5"},
    ],
    "tribeca": [
        {"name": "Chambers St", "lat": 40.7150, "lng": -74.0087, "type": "SUBWAY", "line_name": "1/2/3"},
        {"name": "Franklin St", "lat": 40.7190, "lng": -74.0066, "type": "SUBWAY", "line_name": "1"},
    ],
    "soho": [
        {"name": "Spring St", "lat": 40.7223, "lng": -73.9973, "type": "SUBWAY", "line_name": "6"},
        {"name": "Prince St", "lat": 40.7243, "lng": -73.9977, "type": "SUBWAY", "line_name": "R/W"},
        {"name": "Canal St", "lat": 40.7200, "lng": -74.0012, "type": "SUBWAY", "line_name": "A/C/E"},
    ],
    "les": [
        {"name": "Delancey St", "lat": 40.7187, "lng": -73.9884, "type": "SUBWAY", "line_name": "F"},
        {"name": "Essex St", "lat": 40.7183, "lng": -73.9872, "type": "SUBWAY", "line_name": "J/M/Z"},
        {"name": "East Broadway", "lat": 40.7140, "lng": -73.9901, "type": "SUBWAY", "line_name": "F"},
    ],
    "east_village": [
        {"name": "Astor Place", "lat": 40.7304, "lng": -73.9909, "type": "SUBWAY", "line_name": "6"},
        {"name": "1st Ave", "lat": 40.7307, "lng": -73.9817, "type": "SUBWAY", "line_name": "L"},
        {"name": "2nd Ave", "lat": 40.7234, "lng": -73.9898, "type": "SUBWAY", "line_name": "F"},
    ],
    "chelsea": [
        {"name": "23rd St", "lat": 40.7459, "lng": -73.9979, "type": "SUBWAY", "line_name": "C/E"},
        {"name": "14th St", "lat": 40.7400, "lng": -74.0002, "type": "SUBWAY", "line_name": "A/C/E/L"},
        {"name": "18th St", "lat": 40.7411, "lng": -73.9979, "type": "SUBWAY", "line_name": "1"},
    ],
    "midtown_west": [
        {"name": "Times Sq-42 St", "lat": 40.7559, "lng": -73.9870, "type": "SUBWAY", "line_name": "N/Q/R/W/S/1/2/3/7"},
        {"name": "34th St-Penn Station", "lat": 40.7505, "lng": -73.9914, "type": "SUBWAY", "line_name": "1/2/3/A/C/E"},
        {"name": "42nd St-Port Authority", "lat": 40.7574, "lng": -73.9903, "type": "SUBWAY", "line_name": "A/C/E"},
    ],
    "midtown_east": [
        {"name": "Grand Central-42 St", "lat": 40.7527, "lng": -73.9772, "type": "SUBWAY", "line_name": "4/5/6/7/S"},
        {"name": "51st St", "lat": 40.7571, "lng": -73.9720, "type": "SUBWAY", "line_name": "6"},
        {"name": "Lexington Ave/53rd St", "lat": 40.7575, "lng": -73.9692, "type": "SUBWAY", "line_name": "E/M"},
    ],
    "lic": [
        {"name": "Court Sq", "lat": 40.7471, "lng": -73.9454, "type": "SUBWAY", "line_name": "E/M/G/7"},
        {"name": "Hunters Point Ave", "lat": 40.7423, "lng": -73.9487, "type": "SUBWAY", "line_name": "7"},
        {"name": "Vernon Blvd-Jackson Ave", "lat": 40.7426, "lng": -73.9535, "type": "SUBWAY", "line_name": "7"},
        {"name": "Queensboro Plaza", "lat": 40.7508, "lng": -73.9402, "type": "SUBWAY", "line_name": "N/W/7"},
    ],
    "southern_astoria": [
        {"name": "Astoria Blvd", "lat": 40.7701, "lng": -73.9180, "type": "SUBWAY", "line_name": "N/W"},
        {"name": "30th Ave", "lat": 40.7666, "lng": -73.9218, "type": "SUBWAY", "line_name": "N/W"},
        {"name": "Broadway", "lat": 40.7618, "lng": -73.9254, "type": "SUBWAY", "line_name": "N/W"},
    ],
    "northern_astoria": [
        {"name": "Astoria-Ditmars Blvd", "lat": 40.7750, "lng": -73.9121, "type": "SUBWAY", "line_name": "N/W"},
    ],
    "uws": [
        {"name": "72nd St", "lat": 40.7785, "lng": -73.9819, "type": "SUBWAY", "line_name": "1/2/3"},
        {"name": "86th St", "lat": 40.7889, "lng": -73.9769, "type": "SUBWAY", "line_name": "1"},
        {"name": "79th St", "lat": 40.7838, "lng": -73.9797, "type": "SUBWAY", "line_name": "1"},
        {"name": "96th St", "lat": 40.7937, "lng": -73.9722, "type": "SUBWAY", "line_name": "1/2/3"},
    ],
    "ues": [
        {"name": "77th St", "lat": 40.7736, "lng": -73.9598, "type": "SUBWAY", "line_name": "6"},
        {"name": "86th St", "lat": 40.7794, "lng": -73.9555, "type": "SUBWAY", "line_name": "4/5/6"},
        {"name": "96th St", "lat": 40.7854, "lng": -73.9510, "type": "SUBWAY", "line_name": "6"},
        {"name": "68th St-Hunter College", "lat": 40.7680, "lng": -73.9640, "type": "SUBWAY", "line_name": "6"},
    ],
    "prospect_heights": [
        {"name": "Bergen St", "lat": 40.6809, "lng": -73.9752, "type": "SUBWAY", "line_name": "2/3"},
        {"name": "Atlantic Ave-Barclays Ctr", "lat": 40.6846, "lng": -73.9780, "type": "SUBWAY", "line_name": "2/3/4/5/B/D/N/Q/R"},
    ],
}


# =============================================================================
# NYC PLACES BY ATOMIC REGION
# =============================================================================
# Each place follows the Google Maps Places API structure

def _make_place(
    name: str,
    address: str,
    lat: float,
    lng: float,
    category: str,
    rating: float,
    price_level: int,
    description: str,
    hours: str = "Mon-Sun: 10AM-10PM",
) -> dict[str, Any]:
    """Helper to create consistent place dicts."""
    price_map = {0: None, 1: "$", 2: "$$", 3: "$$$", 4: "$$$$"}
    return {
        "name": name,
        "location": address,
        "description": description,
        "price": price_map.get(price_level),
        "date": hours,
        "url": f"https://maps.google.com/?q={name.replace(' ', '+')}",
        "image_url": None,
        "category": category,
        "gmaps_place_id": f"ChIJ_{name.lower().replace(' ', '_')[:20]}",
        "gmaps_rating": rating,
        "gmaps_price_level": price_level,
        "gmaps_opening_hours": hours,
        "gmaps_review_summary": description,
        "coordinates": {"lat": lat, "lng": lng},
    }


ATOMIC_REGIONS: dict[str, list[dict[str, Any]]] = {
    # ==========================================================================
    # BROOKLYN
    # ==========================================================================
    "greenpoint": [
        _make_place("Cafe Grumpy", "193 Meserole Ave, Brooklyn, NY 11222", 40.7271, -73.9448, "Cafe", 4.5, 2, "Beloved local coffee roaster with industrial-chic vibes", "Mon-Sun: 7AM-7PM"),
        _make_place("Paulie Gee's", "60 Greenpoint Ave, Brooklyn, NY 11222", 40.7303, -73.9574, "Restaurant", 4.7, 2, "Famous wood-fired pizza with creative toppings", "Mon-Sun: 5PM-11PM"),
        _make_place("Transmitter Park", "Greenpoint Ave & West St, Brooklyn, NY 11222", 40.7295, -73.9610, "Park", 4.6, 0, "Waterfront park with Manhattan skyline views", "Open 24 hours"),
        _make_place("WNYC Transmitter Park", "2 Greenpoint Ave, Brooklyn, NY 11222", 40.7298, -73.9607, "Park", 4.5, 0, "Scenic waterfront with historic radio transmitter", "Open 6AM-10PM"),
        _make_place("Archestratus Books + Foods", "160 Huron St, Brooklyn, NY 11222", 40.7277, -73.9485, "Cafe", 4.8, 2, "Cookbook store with cafe serving Mediterranean fare", "Tue-Sun: 10AM-6PM"),
        _make_place("Oxomoco", "128 Greenpoint Ave, Brooklyn, NY 11222", 40.7302, -73.9564, "Restaurant", 4.6, 3, "Upscale Mexican with wood-fired dishes", "Tue-Sun: 5PM-10PM"),
        _make_place("The Habitat", "988 Manhattan Ave, Brooklyn, NY 11222", 40.7329, -73.9545, "Bar", 4.4, 2, "Cozy bar with craft cocktails and board games", "Mon-Sun: 4PM-2AM"),
        _make_place("McCarren Park", "McCarren Park, Brooklyn, NY 11222", 40.7207, -73.9513, "Park", 4.5, 0, "Large park with pool, track, and sports facilities", "Open 24 hours"),
        _make_place("Bakeri", "150 Wythe Ave, Brooklyn, NY 11249", 40.7197, -73.9583, "Bakery", 4.6, 2, "Norwegian-inspired bakery with pastries and coffee", "Wed-Sun: 8AM-5PM"),
        _make_place("Esme", "999 Manhattan Ave, Brooklyn, NY 11222", 40.7333, -73.9543, "Restaurant", 4.5, 3, "Seasonal American with cozy atmosphere", "Tue-Sun: 5:30PM-10PM"),
    ],
    
    "williamsburg": [
        _make_place("Devocion", "69 Grand St, Brooklyn, NY 11249", 40.7118, -73.9631, "Cafe", 4.6, 2, "Colombian coffee roaster in stunning greenhouse space", "Mon-Sun: 7AM-7PM"),
        _make_place("Domino Park", "15 River St, Brooklyn, NY 11249", 40.7147, -73.9683, "Park", 4.7, 0, "Waterfront park with city views on former sugar factory site", "Open 6AM-1AM"),
        _make_place("Smorgasburg", "90 Kent Ave, Brooklyn, NY 11249", 40.7213, -73.9615, "Food Market", 4.5, 2, "Massive outdoor food market with 100+ vendors", "Sat-Sun: 11AM-6PM"),
        _make_place("Peter Luger Steak House", "178 Broadway, Brooklyn, NY 11211", 40.7098, -73.9622, "Restaurant", 4.4, 4, "Legendary steakhouse since 1887", "Mon-Sun: 11:45AM-10PM"),
        _make_place("Brooklyn Brewery", "79 N 11th St, Brooklyn, NY 11249", 40.7217, -73.9575, "Brewery", 4.4, 2, "Iconic craft brewery with tours and tastings", "Mon-Thu: 5PM-11PM; Fri-Sun: 12PM-11PM"),
        _make_place("Marlow & Sons", "81 Broadway, Brooklyn, NY 11249", 40.7107, -73.9649, "Restaurant", 4.5, 3, "Farm-to-table pioneer with oyster bar", "Mon-Sun: 8AM-12AM"),
        _make_place("Artists & Fleas", "70 N 7th St, Brooklyn, NY 11249", 40.7189, -73.9593, "Market", 4.3, 2, "Curated indie market with local artisans", "Sat-Sun: 10AM-7PM"),
        _make_place("The Hoxton", "97 Wythe Ave, Brooklyn, NY 11249", 40.7210, -73.9576, "Hotel", 4.5, 3, "Trendy hotel with rooftop bar and great views", "Open 24 hours"),
        _make_place("Misi", "329 Kent Ave, Brooklyn, NY 11249", 40.7134, -73.9674, "Restaurant", 4.6, 3, "Handmade pasta in minimalist waterfront space", "Mon-Sun: 5:30PM-10PM"),
        _make_place("Berry Park", "4 Berry St, Brooklyn, NY 11249", 40.7153, -73.9628, "Bar", 4.4, 2, "Rooftop beer garden with skyline views", "Mon-Sun: 3PM-4AM"),
    ],
    
    "east_williamsburg": [
        _make_place("Roberta's", "261 Moore St, Brooklyn, NY 11206", 40.7050, -73.9335, "Restaurant", 4.4, 2, "Famous pizza spot with garden and radio station", "Mon-Sun: 11AM-12AM"),
        _make_place("House of Yes", "2 Wyckoff Ave, Brooklyn, NY 11237", 40.7054, -73.9234, "Nightclub", 4.6, 2, "Immersive circus-themed nightclub", "Fri-Sat: 10PM-4AM"),
        _make_place("Nowadays", "56-06 Cooper Ave, Queens, NY 11385", 40.7067, -73.9104, "Bar", 4.5, 2, "Outdoor bar and event space with DJ sets", "Thu-Sun: 2PM-12AM"),
        _make_place("Pine Box Rock Shop", "12 Grattan St, Brooklyn, NY 11206", 40.7063, -73.9370, "Bar", 4.4, 2, "Former casket factory turned dive bar with live music", "Mon-Sun: 4PM-4AM"),
        _make_place("Bunna Cafe", "1084 Flushing Ave, Brooklyn, NY 11237", 40.6995, -73.9276, "Restaurant", 4.7, 2, "Excellent Ethiopian vegan cuisine", "Mon-Sun: 11AM-10PM"),
    ],
    
    "south_williamsburg": [
        _make_place("Traif", "229 S 4th St, Brooklyn, NY 11211", 40.7096, -73.9631, "Restaurant", 4.5, 3, "Creative Asian-influenced small plates", "Tue-Sun: 6PM-11PM"),
        _make_place("Pies 'n' Thighs", "166 S 4th St, Brooklyn, NY 11211", 40.7094, -73.9614, "Restaurant", 4.4, 2, "Southern comfort food and fried chicken", "Mon-Sun: 9AM-11PM"),
        _make_place("Beco", "355 Roebling St, Brooklyn, NY 11211", 40.7082, -73.9569, "Restaurant", 4.5, 3, "Brazilian-inspired with great cocktails", "Tue-Sun: 5PM-11PM"),
    ],
    
    "dumbo": [
        _make_place("Brooklyn Bridge Park", "334 Furman St, Brooklyn, NY 11201", 40.7024, -73.9967, "Park", 4.8, 0, "Stunning waterfront park with playgrounds and piers", "Open 6AM-1AM"),
        _make_place("Juliana's Pizza", "19 Old Fulton St, Brooklyn, NY 11201", 40.7027, -73.9937, "Restaurant", 4.6, 2, "Coal-fired pizza from original Grimaldi's founder", "Mon-Sun: 11:30AM-10PM"),
        _make_place("Time Out Market", "55 Water St, Brooklyn, NY 11201", 40.7030, -73.9902, "Food Hall", 4.4, 2, "Curated food hall with top NYC restaurants", "Mon-Sun: 11AM-10PM"),
        _make_place("Jane's Carousel", "Dock St, Brooklyn, NY 11201", 40.7044, -73.9932, "Attraction", 4.7, 1, "Restored 1922 carousel in glass pavilion", "Wed-Mon: 11AM-7PM"),
        _make_place("Westlight", "111 N 12th St, Brooklyn, NY 11249", 40.7220, -73.9572, "Bar", 4.5, 3, "Rooftop bar with panoramic NYC views", "Mon-Sun: 4PM-2AM"),
        _make_place("One Girl Cookies", "33 Main St, Brooklyn, NY 11201", 40.7025, -73.9906, "Bakery", 4.5, 2, "Charming bakery with handcrafted treats", "Mon-Sun: 8AM-7PM"),
        _make_place("St. Ann's Warehouse", "45 Water St, Brooklyn, NY 11201", 40.7032, -73.9895, "Theater", 4.6, 3, "Innovative theater in tobacco warehouse", "Varies by show"),
        _make_place("Empire Stores", "55 Water St, Brooklyn, NY 11201", 40.7030, -73.9902, "Shopping", 4.4, 2, "Historic warehouse with shops and dining", "Mon-Sun: 10AM-9PM"),
        _make_place("Pebble Beach", "Plymouth St, Brooklyn, NY 11201", 40.7024, -73.9936, "Beach", 4.5, 0, "Small rocky beach with Brooklyn Bridge views", "Open 24 hours"),
        _make_place("Almondine Bakery", "85 Water St, Brooklyn, NY 11201", 40.7034, -73.9893, "Bakery", 4.6, 2, "Authentic French bakery with croissants", "Mon-Sat: 7AM-7PM; Sun: 8AM-6PM"),
    ],
    
    "brooklyn_heights": [
        _make_place("Brooklyn Heights Promenade", "Pierrepont Pl, Brooklyn, NY 11201", 40.6969, -73.9979, "Park", 4.8, 0, "Scenic esplanade with Manhattan skyline views", "Open 24 hours"),
        _make_place("Henry's End", "44 Henry St, Brooklyn, NY 11201", 40.6962, -73.9956, "Restaurant", 4.5, 3, "Classic American with wild game menu", "Tue-Sun: 5PM-10PM"),
        _make_place("Jack the Horse Tavern", "66 Hicks St, Brooklyn, NY 11201", 40.6968, -73.9968, "Restaurant", 4.4, 3, "Cozy tavern with New American cuisine", "Mon-Sun: 10AM-10PM"),
        _make_place("Montague Street", "Montague St, Brooklyn, NY 11201", 40.6943, -73.9945, "Shopping", 4.3, 2, "Main shopping and dining street", "Varies by store"),
        _make_place("Brooklyn Historical Society", "128 Pierrepont St, Brooklyn, NY 11201", 40.6946, -73.9936, "Museum", 4.5, 2, "Brooklyn history in landmark building", "Wed-Sun: 12PM-5PM"),
    ],
    
    "prospect_heights": [
        _make_place("Brooklyn Museum", "200 Eastern Pkwy, Brooklyn, NY 11238", 40.6712, -73.9636, "Museum", 4.7, 2, "World-class art museum with vast collections", "Wed-Sun: 10AM-5PM"),
        _make_place("Brooklyn Botanic Garden", "990 Washington Ave, Brooklyn, NY 11225", 40.6694, -73.9639, "Garden", 4.8, 2, "Beautiful gardens with Japanese hill-and-pond", "Tue-Sun: 8AM-6PM"),
        _make_place("Prospect Park", "Prospect Park, Brooklyn, NY 11225", 40.6602, -73.9690, "Park", 4.8, 0, "526-acre park designed by Olmsted and Vaux", "Open 5AM-1AM"),
        _make_place("Olmsted", "659 Vanderbilt Ave, Brooklyn, NY 11238", 40.6788, -73.9687, "Restaurant", 4.6, 3, "Garden-to-table dining with backyard farm", "Tue-Sun: 5:30PM-10PM"),
        _make_place("Bergen Bagels", "754 Washington Ave, Brooklyn, NY 11238", 40.6732, -73.9648, "Bakery", 4.4, 1, "Classic NY bagels and breakfast", "Mon-Sun: 6AM-4PM"),
        _make_place("The Meat Hook", "495 Lorimer St, Brooklyn, NY 11211", 40.7141, -73.9505, "Shop", 4.5, 2, "Whole-animal butcher with sandwiches", "Mon-Sat: 10AM-8PM"),
    ],
    
    # ==========================================================================
    # MANHATTAN - LOWER
    # ==========================================================================
    "fidi": [
        _make_place("The Oculus", "50 Church St, New York, NY 10007", 40.7117, -74.0117, "Landmark", 4.5, 0, "Stunning transit hub and shopping center", "Mon-Sun: 7AM-9PM"),
        _make_place("Stone Street", "Stone St, New York, NY 10004", 40.7040, -74.0091, "Street", 4.5, 2, "Historic cobblestone street with outdoor dining", "Varies by venue"),
        _make_place("Fraunces Tavern", "54 Pearl St, New York, NY 10004", 40.7034, -74.0110, "Restaurant", 4.3, 3, "Historic tavern where Washington bid farewell", "Mon-Sun: 11AM-2AM"),
        _make_place("One World Observatory", "285 Fulton St, New York, NY 10007", 40.7127, -74.0134, "Attraction", 4.6, 3, "Observation deck with 360-degree views", "Mon-Sun: 9AM-9PM"),
        _make_place("9/11 Memorial & Museum", "180 Greenwich St, New York, NY 10007", 40.7115, -74.0134, "Museum", 4.8, 2, "Moving tribute to September 11 victims", "Wed-Mon: 9AM-8PM"),
        _make_place("Battery Park", "Battery Park, New York, NY 10004", 40.7033, -74.0170, "Park", 4.6, 0, "Waterfront park with Statue of Liberty views", "Open 6AM-1AM"),
        _make_place("Dead Rabbit", "30 Water St, New York, NY 10004", 40.7031, -74.0098, "Bar", 4.5, 3, "Award-winning Irish pub and cocktail bar", "Mon-Sun: 11AM-4AM"),
        _make_place("Blue Smoke", "255 Vesey St, New York, NY 10282", 40.7143, -74.0161, "Restaurant", 4.3, 2, "NYC BBQ institution with waterfront views", "Mon-Sun: 11:30AM-10PM"),
    ],
    
    "tribeca": [
        _make_place("Bubby's", "120 Hudson St, New York, NY 10013", 40.7191, -74.0082, "Restaurant", 4.3, 2, "Classic American comfort food and pies", "Mon-Sun: 8AM-10PM"),
        _make_place("Locanda Verde", "377 Greenwich St, New York, NY 10013", 40.7209, -74.0101, "Restaurant", 4.5, 3, "Italian taverna in Greenwich Hotel", "Mon-Sun: 7AM-11PM"),
        _make_place("The Odeon", "145 W Broadway, New York, NY 10013", 40.7169, -74.0076, "Restaurant", 4.3, 3, "Iconic 80s bistro still going strong", "Mon-Sun: 8AM-12AM"),
        _make_place("Washington Market Park", "Greenwich St & Chambers St, New York, NY 10013", 40.7175, -74.0114, "Park", 4.5, 0, "Family-friendly park with playground", "Open 6AM-12AM"),
        _make_place("Mysterious Bookshop", "58 Warren St, New York, NY 10007", 40.7143, -74.0086, "Shop", 4.7, 2, "World's oldest mystery bookstore", "Mon-Sat: 11AM-7PM"),
        _make_place("Tribeca Film Center", "375 Greenwich St, New York, NY 10013", 40.7208, -74.0101, "Cinema", 4.5, 3, "De Niro's film center and screening venue", "Varies by screening"),
    ],
    
    "soho": [
        _make_place("McNally Jackson", "52 Prince St, New York, NY 10012", 40.7234, -73.9953, "Bookstore", 4.6, 2, "Independent bookstore with cafe", "Mon-Sun: 10AM-9PM"),
        _make_place("Balthazar", "80 Spring St, New York, NY 10012", 40.7227, -73.9976, "Restaurant", 4.4, 3, "Iconic French brasserie and bakery", "Mon-Sun: 7:30AM-12AM"),
        _make_place("The Drawing Center", "35 Wooster St, New York, NY 10013", 40.7217, -74.0012, "Gallery", 4.5, 0, "Non-profit focused on drawing as art", "Wed-Sun: 12PM-6PM"),
        _make_place("Housing Works Bookstore", "126 Crosby St, New York, NY 10012", 40.7244, -73.9981, "Bookstore", 4.7, 2, "Used bookstore supporting AIDS charity", "Mon-Sun: 10AM-9PM"),
        _make_place("Dominique Ansel Bakery", "189 Spring St, New York, NY 10012", 40.7237, -74.0025, "Bakery", 4.4, 2, "Home of the Cronut", "Mon-Sun: 8AM-7PM"),
        _make_place("New York Earth Room", "141 Wooster St, New York, NY 10012", 40.7271, -73.9999, "Art", 4.4, 0, "250 cubic yards of earth in a SoHo loft", "Wed-Sun: 12PM-6PM"),
        _make_place("Fanelli Cafe", "94 Prince St, New York, NY 10012", 40.7252, -73.9989, "Bar", 4.3, 2, "One of NYC's oldest bars since 1847", "Mon-Sun: 10AM-2AM"),
        _make_place("Artists Space", "11 Cortlandt Alley, New York, NY 10013", 40.7171, -74.0014, "Gallery", 4.4, 0, "Alternative contemporary art space", "Wed-Sun: 11AM-6PM"),
    ],
    
    "les": [
        _make_place("Katz's Delicatessen", "205 E Houston St, New York, NY 10002", 40.7223, -73.9874, "Restaurant", 4.5, 2, "Legendary pastrami since 1888", "Mon-Sun: 8AM-10:45PM"),
        _make_place("Russ & Daughters", "179 E Houston St, New York, NY 10002", 40.7222, -73.9883, "Shop", 4.7, 2, "Appetizing store since 1914 with bagels and lox", "Mon-Sun: 8AM-6PM"),
        _make_place("Economy Candy", "108 Rivington St, New York, NY 10002", 40.7197, -73.9873, "Shop", 4.6, 1, "Old-school candy emporium since 1937", "Mon-Sun: 9AM-6PM"),
        _make_place("Metrograph", "7 Ludlow St, New York, NY 10002", 40.7147, -73.9908, "Cinema", 4.7, 2, "Boutique cinema with bar and restaurant", "Varies by screening"),
        _make_place("Essex Market", "88 Essex St, New York, NY 10002", 40.7181, -73.9867, "Market", 4.5, 2, "Historic market with diverse vendors", "Mon-Sat: 8AM-8PM; Sun: 10AM-6PM"),
        _make_place("Tenement Museum", "103 Orchard St, New York, NY 10002", 40.7186, -73.9899, "Museum", 4.7, 2, "Immigration history in preserved tenement", "Fri-Wed: 10AM-6:30PM"),
        _make_place("Attaboy", "134 Eldridge St, New York, NY 10002", 40.7187, -73.9921, "Bar", 4.6, 3, "Speakeasy-style cocktail bar", "Mon-Sun: 6PM-4AM"),
        _make_place("Dimes", "49 Canal St, New York, NY 10002", 40.7152, -73.9919, "Restaurant", 4.4, 2, "Health-focused California-style cafe", "Mon-Sun: 8AM-11PM"),
    ],
    
    "east_village": [
        _make_place("Tompkins Square Park", "E 7th St & Avenue A, New York, NY 10009", 40.7265, -73.9817, "Park", 4.4, 0, "Historic park with dog runs and events", "Open 6AM-12AM"),
        _make_place("Veselka", "144 2nd Ave, New York, NY 10003", 40.7290, -73.9873, "Restaurant", 4.5, 2, "24-hour Ukrainian diner since 1954", "Open 24 hours"),
        _make_place("McSorley's Old Ale House", "15 E 7th St, New York, NY 10003", 40.7283, -73.9899, "Bar", 4.4, 1, "NYC's oldest Irish pub since 1854", "Mon-Sat: 11AM-1AM; Sun: 1PM-1AM"),
        _make_place("B&H Dairy", "127 2nd Ave, New York, NY 10003", 40.7285, -73.9878, "Restaurant", 4.5, 1, "Tiny kosher vegetarian counter", "Mon-Fri: 7AM-10PM; Sat-Sun: 8AM-10PM"),
        _make_place("Anthology Film Archives", "32 2nd Ave, New York, NY 10003", 40.7257, -73.9898, "Cinema", 4.6, 2, "Essential cinema for avant-garde film", "Varies by screening"),
        _make_place("Momofuku Noodle Bar", "171 1st Ave, New York, NY 10003", 40.7295, -73.9841, "Restaurant", 4.4, 2, "David Chang's famous ramen spot", "Mon-Sun: 12PM-11PM"),
        _make_place("Death & Company", "433 E 6th St, New York, NY 10009", 40.7260, -73.9819, "Bar", 4.6, 3, "Award-winning cocktail bar", "Mon-Sun: 6PM-2AM"),
        _make_place("Strand Book Store", "828 Broadway, New York, NY 10003", 40.7333, -73.9912, "Bookstore", 4.6, 2, "18 miles of books since 1927", "Mon-Sun: 10AM-10PM"),
    ],
    
    # ==========================================================================
    # MANHATTAN - MIDTOWN
    # ==========================================================================
    "chelsea": [
        _make_place("The High Line", "Gansevoort St to 34th St, New York, NY 10011", 40.7480, -74.0048, "Park", 4.7, 0, "Elevated park on former rail line", "Open 7AM-10PM"),
        _make_place("Chelsea Market", "75 9th Ave, New York, NY 10011", 40.7424, -74.0061, "Market", 4.5, 2, "Food hall in former Nabisco factory", "Mon-Sun: 7AM-9PM"),
        _make_place("Whitney Museum", "99 Gansevoort St, New York, NY 10014", 40.7396, -74.0089, "Museum", 4.6, 3, "American art museum by Renzo Piano", "Mon/Wed-Sun: 10:30AM-6PM"),
        _make_place("The Rubin Museum", "150 W 17th St, New York, NY 10011", 40.7400, -73.9975, "Museum", 4.6, 2, "Himalayan art and culture", "Thu-Mon: 11AM-5PM"),
        _make_place("192 Books", "192 10th Ave, New York, NY 10011", 40.7464, -74.0068, "Bookstore", 4.7, 2, "Curated independent bookstore", "Tue-Sun: 11AM-7PM"),
        _make_place("Printed Matter", "231 11th Ave, New York, NY 10001", 40.7489, -74.0062, "Bookstore", 4.6, 2, "Artists' books and publications", "Tue-Sat: 11AM-6PM"),
        _make_place("Cookshop", "156 10th Ave, New York, NY 10011", 40.7453, -74.0059, "Restaurant", 4.4, 3, "Farm-to-table with great brunch", "Mon-Sun: 8AM-10PM"),
        _make_place("David Zwirner Gallery", "537 W 20th St, New York, NY 10011", 40.7466, -74.0056, "Gallery", 4.6, 0, "Major contemporary art gallery", "Tue-Sat: 10AM-6PM"),
        _make_place("Little Island", "Pier 55, Hudson River Park, New York, NY 10014", 40.7418, -74.0103, "Park", 4.6, 0, "Floating park with performances", "Open 6AM-12AM"),
    ],
    
    "midtown_west": [
        _make_place("Times Square", "Times Square, New York, NY 10036", 40.7580, -73.9855, "Landmark", 4.3, 0, "The crossroads of the world", "Open 24 hours"),
        _make_place("Bryant Park", "Bryant Park, New York, NY 10018", 40.7536, -73.9832, "Park", 4.6, 0, "Midtown oasis with events and dining", "Open 7AM-11PM"),
        _make_place("The Museum of Modern Art", "11 W 53rd St, New York, NY 10019", 40.7614, -73.9776, "Museum", 4.7, 3, "World's premier modern art museum", "Sun-Fri: 10:30AM-5:30PM; Sat: 10:30AM-7PM"),
        _make_place("Radio City Music Hall", "1260 6th Ave, New York, NY 10020", 40.7600, -73.9799, "Venue", 4.7, 3, "Art Deco landmark and entertainment venue", "Varies by event"),
        _make_place("Rockefeller Center", "45 Rockefeller Plaza, New York, NY 10111", 40.7587, -73.9787, "Landmark", 4.6, 0, "Historic complex with Top of the Rock", "Open 24 hours"),
        _make_place("St. Patrick's Cathedral", "5th Ave & 50th St, New York, NY 10022", 40.7585, -73.9762, "Landmark", 4.7, 0, "Neo-Gothic cathedral landmark", "Open 6:30AM-8:45PM"),
        _make_place("Ippudo", "321 W 51st St, New York, NY 10019", 40.7623, -73.9872, "Restaurant", 4.5, 2, "Legendary Japanese ramen chain", "Mon-Sun: 11AM-11PM"),
        _make_place("The Smith", "1900 Broadway, New York, NY 10023", 40.7699, -73.9829, "Restaurant", 4.3, 2, "American brasserie with lively atmosphere", "Mon-Sun: 8AM-12AM"),
    ],
    
    "midtown_east": [
        _make_place("Grand Central Terminal", "89 E 42nd St, New York, NY 10017", 40.7527, -73.9772, "Landmark", 4.7, 0, "Beaux-Arts masterpiece and transit hub", "Open 5:15AM-2AM"),
        _make_place("The Morgan Library", "225 Madison Ave, New York, NY 10016", 40.7493, -73.9812, "Museum", 4.7, 2, "Rare books and manuscripts in Pierpont's library", "Tue-Sun: 10:30AM-5PM"),
        _make_place("Chrysler Building", "405 Lexington Ave, New York, NY 10174", 40.7516, -73.9755, "Landmark", 4.6, 0, "Art Deco skyscraper icon", "Lobby: Mon-Fri: 8AM-6PM"),
        _make_place("United Nations", "405 E 42nd St, New York, NY 10017", 40.7489, -73.9680, "Landmark", 4.5, 2, "UN headquarters with tours", "Mon-Fri: 9AM-4:30PM"),
        _make_place("Tudor City", "Tudor City Place, New York, NY 10017", 40.7491, -73.9714, "Landmark", 4.4, 0, "Historic residential enclave with parks", "Open 24 hours"),
        _make_place("Sushi Yasuda", "204 E 43rd St, New York, NY 10017", 40.7517, -73.9742, "Restaurant", 4.6, 4, "Traditional omakase experience", "Mon-Sat: 12PM-2:15PM, 6PM-10:15PM"),
        _make_place("The Campbell", "15 Vanderbilt Ave, New York, NY 10017", 40.7524, -73.9777, "Bar", 4.5, 3, "Opulent bar in Grand Central", "Mon-Sat: 12PM-1AM; Sun: 12PM-10PM"),
    ],
    
    # ==========================================================================
    # MANHATTAN - UPPER
    # ==========================================================================
    "uws": [
        _make_place("Central Park West", "Central Park West, New York, NY 10024", 40.7812, -73.9713, "Park", 4.8, 0, "Western edge of Central Park", "Open 6AM-1AM"),
        _make_place("American Museum of Natural History", "Central Park West & 79th St, New York, NY 10024", 40.7813, -73.9740, "Museum", 4.7, 2, "World's largest natural history museum", "Wed-Sun: 10AM-5:30PM"),
        _make_place("Lincoln Center", "10 Lincoln Center Plaza, New York, NY 10023", 40.7725, -73.9835, "Venue", 4.7, 3, "Performing arts complex", "Varies by performance"),
        _make_place("Zabar's", "2245 Broadway, New York, NY 10024", 40.7848, -73.9787, "Shop", 4.6, 2, "Iconic gourmet food emporium since 1934", "Mon-Sat: 8AM-7:30PM; Sun: 9AM-6PM"),
        _make_place("Barney Greengrass", "541 Amsterdam Ave, New York, NY 10024", 40.7859, -73.9756, "Restaurant", 4.5, 2, "Sturgeon King since 1908", "Tue-Sun: 8AM-4PM"),
        _make_place("Riverside Park", "Riverside Dr, New York, NY 10024", 40.7870, -73.9798, "Park", 4.6, 0, "4-mile waterfront park", "Open 6AM-1AM"),
        _make_place("The Beacon Theatre", "2124 Broadway, New York, NY 10023", 40.7781, -73.9814, "Venue", 4.7, 3, "Historic concert venue", "Varies by show"),
        _make_place("Jacob's Pickles", "509 Amsterdam Ave, New York, NY 10024", 40.7855, -73.9754, "Restaurant", 4.4, 2, "Southern comfort with craft beer", "Mon-Sun: 10AM-2AM"),
    ],
    
    "ues": [
        _make_place("The Metropolitan Museum of Art", "1000 5th Ave, New York, NY 10028", 40.7794, -73.9632, "Museum", 4.8, 3, "2 million works spanning 5,000 years", "Sun-Tue/Thu: 10AM-5PM; Fri-Sat: 10AM-9PM"),
        _make_place("Solomon R. Guggenheim Museum", "1071 5th Ave, New York, NY 10128", 40.7830, -73.9590, "Museum", 4.6, 3, "Frank Lloyd Wright's spiral masterpiece", "Sun-Wed/Fri: 10AM-5:30PM; Sat: 10AM-8PM"),
        _make_place("Central Park Zoo", "64th St & 5th Ave, New York, NY 10065", 40.7676, -73.9719, "Zoo", 4.5, 2, "Intimate zoo in Central Park", "Mon-Sun: 10AM-5PM"),
        _make_place("Neue Galerie", "1048 5th Ave, New York, NY 10028", 40.7812, -73.9607, "Museum", 4.7, 3, "German and Austrian art, home of Klimt's Adele", "Thu-Mon: 11AM-5PM"),
        _make_place("Cafe Sabarsky", "1048 5th Ave, New York, NY 10028", 40.7812, -73.9607, "Cafe", 4.5, 3, "Viennese cafe in Neue Galerie", "Thu-Mon: 9AM-6PM"),
        _make_place("The Frick Collection", "1 E 70th St, New York, NY 10021", 40.7711, -73.9671, "Museum", 4.7, 3, "Old Masters in Gilded Age mansion", "Thu-Sun: 10AM-6PM"),
        _make_place("Lexington Candy Shop", "1226 Lexington Ave, New York, NY 10028", 40.7800, -73.9573, "Restaurant", 4.5, 1, "1925 luncheonette with classic diner fare", "Mon-Sat: 7AM-7PM; Sun: 8AM-6PM"),
        _make_place("Bemelmans Bar", "35 E 76th St, New York, NY 10021", 40.7738, -73.9639, "Bar", 4.6, 4, "Legendary bar with Madeline murals", "Mon-Sun: 5PM-1AM"),
    ],
    
    # ==========================================================================
    # QUEENS
    # ==========================================================================
    "lic": [
        _make_place("Gantry Plaza State Park", "4-09 47th Rd, Long Island City, NY 11101", 40.7461, -73.9590, "Park", 4.7, 0, "Waterfront park with iconic gantries and views", "Open 24 hours"),
        _make_place("MoMA PS1", "22-25 Jackson Ave, Long Island City, NY 11101", 40.7456, -73.9470, "Museum", 4.5, 2, "Contemporary art in former school", "Thu-Mon: 12PM-6PM"),
        _make_place("LIC Landing", "52-10 Center Blvd, Long Island City, NY 11101", 40.7472, -73.9582, "Restaurant", 4.4, 2, "Waterfront dining with kayak rentals", "Mon-Sun: 11AM-10PM"),
        _make_place("Hunters Point South Park", "Center Blvd, Long Island City, NY 11101", 40.7420, -73.9575, "Park", 4.6, 0, "Modern waterfront park with great views", "Open 6AM-10PM"),
        _make_place("Sweetleaf Coffee", "10-93 Jackson Ave, Long Island City, NY 11101", 40.7473, -73.9495, "Cafe", 4.5, 2, "Beloved local coffee roaster", "Mon-Sun: 7AM-7PM"),
        _make_place("Dutch Kills", "27-24 Jackson Ave, Long Island City, NY 11101", 40.7507, -73.9409, "Bar", 4.5, 2, "Speakeasy-style craft cocktails", "Mon-Sun: 5PM-2AM"),
        _make_place("Court Square Diner", "45-30 23rd St, Long Island City, NY 11101", 40.7476, -73.9455, "Restaurant", 4.4, 1, "Classic 24-hour diner", "Open 24 hours"),
        _make_place("The Noguchi Museum", "9-01 33rd Rd, Long Island City, NY 11106", 40.7670, -73.9371, "Museum", 4.7, 2, "Isamu Noguchi's sculpture garden", "Wed-Sun: 11AM-6PM"),
        _make_place("SculptureCenter", "44-19 Purves St, Long Island City, NY 11101", 40.7478, -73.9425, "Museum", 4.5, 1, "Experimental sculpture in trolley repair shop", "Thu-Mon: 11AM-6PM"),
    ],
    
    "southern_astoria": [
        _make_place("Astoria Park", "19th St & 23rd Dr, Astoria, NY 11105", 40.7785, -73.9230, "Park", 4.6, 0, "Large park with pool and Hell Gate Bridge views", "Open 6AM-9PM"),
        _make_place("Bohemian Hall & Beer Garden", "29-19 24th Ave, Astoria, NY 11102", 40.7647, -73.9261, "Bar", 4.5, 2, "NYC's oldest beer garden since 1910", "Mon-Sun: 12PM-11PM"),
        _make_place("Taverna Kyclades", "33-07 Ditmars Blvd, Astoria, NY 11105", 40.7717, -73.9115, "Restaurant", 4.6, 2, "Legendary Greek seafood", "Mon-Sun: 12PM-11PM"),
        _make_place("Socrates Sculpture Park", "32-01 Vernon Blvd, Long Island City, NY 11106", 40.7692, -73.9373, "Park", 4.6, 0, "Outdoor sculpture exhibitions on the waterfront", "Open 9AM-sunset"),
        _make_place("Museum of the Moving Image", "36-01 35th Ave, Astoria, NY 11106", 40.7564, -73.9237, "Museum", 4.6, 2, "Film, TV, and digital media museum", "Wed-Sun: 10:30AM-5PM"),
        _make_place("SingleCut Beersmiths", "19-33 37th St, Astoria, NY 11105", 40.7603, -73.9256, "Brewery", 4.5, 2, "Craft brewery with rock music theme", "Mon-Thu: 4PM-10PM; Fri-Sun: 12PM-10PM"),
    ],
    
    "northern_astoria": [
        _make_place("Astoria Seafood", "37-10 33rd St, Astoria, NY 11101", 40.7578, -73.9180, "Restaurant", 4.4, 2, "Pick your own fish from the market", "Mon-Sun: 11AM-10PM"),
        _make_place("Ditmars area cafes", "Ditmars Blvd, Astoria, NY 11105", 40.7750, -73.9121, "Neighborhood", 4.4, 2, "Walkable strip with cafes and shops", "Varies"),
        _make_place("Ralph's Famous Italian Ices", "35-12 Ditmars Blvd, Astoria, NY 11105", 40.7718, -73.9097, "Dessert", 4.6, 1, "Classic NYC Italian ice shop", "Mon-Sun: 12PM-11PM"),
    ],
}


# =============================================================================
# COMPOSITE REGIONS (Unions of Atomic Regions)
# =============================================================================

COMPOSITE_REGIONS: dict[str, list[str]] = {
    # Cross-river corridors
    "lic_midtown_east": ["lic", "midtown_east"],
    "fidi_dumbo": ["fidi", "dumbo", "brooklyn_heights"],
    "lic_greenpoint": ["lic", "greenpoint"],
    "les_williamsburg": ["les", "williamsburg"],
    
    # Neighborhood combinations
    "greenpoint_williamsburg": ["greenpoint", "williamsburg"],
    "chelsea_midtown_west": ["chelsea", "midtown_west"],
    "astoria": ["southern_astoria", "northern_astoria"],
    "queens_near_manhattan": ["lic", "southern_astoria", "northern_astoria"],
    "williamsburg_all": ["williamsburg", "east_williamsburg", "south_williamsburg"],
    
    # Broad areas
    "lower_manhattan": ["fidi", "tribeca", "soho", "les", "east_village"],
    "southern_manhattan": ["fidi", "tribeca", "soho", "les"],
    "midtown": ["midtown_west", "midtown_east", "chelsea"],
    "north_brooklyn": ["greenpoint", "williamsburg", "east_williamsburg"],
    "downtown_brooklyn": ["dumbo", "brooklyn_heights", "prospect_heights"],
    
    # Borough-level
    "brooklyn": [
        "greenpoint", "williamsburg", "east_williamsburg", "south_williamsburg",
        "dumbo", "brooklyn_heights", "prospect_heights"
    ],
    "manhattan": [
        "fidi", "tribeca", "soho", "les", "east_village", "chelsea",
        "midtown_west", "midtown_east", "uws", "ues"
    ],
    "queens": ["lic", "southern_astoria", "northern_astoria"],
    
    # Upper Manhattan
    "upper_manhattan": ["uws", "ues"],
    "central_park_area": ["uws", "ues", "midtown_east"],
}


# =============================================================================
# REGION BOUNDS (for validation)
# =============================================================================
# Approximate bounding boxes: (min_lat, max_lat, min_lng, max_lng)

REGION_BOUNDS: dict[str, tuple[float, float, float, float]] = {
    "greenpoint": (40.720, 40.740, -73.965, -73.940),
    "williamsburg": (40.700, 40.725, -73.970, -73.945),
    "east_williamsburg": (40.700, 40.715, -73.940, -73.905),
    "south_williamsburg": (40.700, 40.715, -73.970, -73.950),
    "dumbo": (40.695, 40.710, -74.000, -73.980),
    "brooklyn_heights": (40.690, 40.705, -74.000, -73.985),
    "prospect_heights": (40.665, 40.685, -73.980, -73.960),
    "fidi": (40.700, 40.715, -74.020, -74.000),
    "tribeca": (40.710, 40.725, -74.015, -74.000),
    "soho": (40.718, 40.730, -74.010, -73.990),
    "les": (40.710, 40.725, -73.995, -73.975),
    "east_village": (40.720, 40.735, -73.995, -73.975),
    "chelsea": (40.735, 40.755, -74.010, -73.990),
    "midtown_west": (40.750, 40.770, -74.000, -73.980),
    "midtown_east": (40.745, 40.765, -73.985, -73.965),
    "uws": (40.770, 40.800, -73.990, -73.970),
    "ues": (40.760, 40.790, -73.975, -73.950),
    "lic": (40.735, 40.755, -73.960, -73.935),
    "southern_astoria": (40.755, 40.780, -73.935, -73.910),
    "northern_astoria": (40.770, 40.785, -73.925, -73.905),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_places_for_region(region_id: str) -> list[dict[str, Any]]:
    """
    Get all places for a region (atomic or composite).
    
    Args:
        region_id: Region identifier (e.g., 'williamsburg' or 'north_brooklyn')
        
    Returns:
        List of place dicts for the region
        
    Raises:
        ValueError: If region_id is not found
    """
    # Check atomic regions first
    if region_id in ATOMIC_REGIONS:
        return ATOMIC_REGIONS[region_id]
    
    # Check composite regions
    if region_id in COMPOSITE_REGIONS:
        places = []
        for atomic_region in COMPOSITE_REGIONS[region_id]:
            if atomic_region in ATOMIC_REGIONS:
                places.extend(ATOMIC_REGIONS[atomic_region])
            elif atomic_region in COMPOSITE_REGIONS:
                # Handle nested composite (like "astoria" containing atomics)
                for nested_region in COMPOSITE_REGIONS[atomic_region]:
                    if nested_region in ATOMIC_REGIONS:
                        places.extend(ATOMIC_REGIONS[nested_region])
        return places
    
    raise ValueError(f"Unknown region: {region_id}")


def get_transit_stops_for_region(region_id: str) -> list[dict[str, Any]]:
    """
    Get all transit stops for a region (atomic or composite).
    
    Args:
        region_id: Region identifier
        
    Returns:
        List of transit stop dicts for the region
    """
    if region_id in MOCK_TRANSIT_STOPS_NYC:
        return MOCK_TRANSIT_STOPS_NYC[region_id]
    
    if region_id in COMPOSITE_REGIONS:
        stops = []
        for atomic_region in COMPOSITE_REGIONS[region_id]:
            if atomic_region in MOCK_TRANSIT_STOPS_NYC:
                stops.extend(MOCK_TRANSIT_STOPS_NYC[atomic_region])
        return stops
    
    return []


def get_all_region_ids() -> list[str]:
    """Get all available region IDs (atomic and composite)."""
    return list(ATOMIC_REGIONS.keys()) + list(COMPOSITE_REGIONS.keys())


def validate_place_in_region(
    place: dict[str, Any], region_id: str
) -> bool:
    """
    Validate that a place's coordinates fall within a region's bounds.
    
    Args:
        place: Place dict with coordinates
        region_id: Region to check against
        
    Returns:
        True if place is within region bounds
    """
    coords = place.get("coordinates", {})
    lat = coords.get("lat")
    lng = coords.get("lng")
    
    if lat is None or lng is None:
        return False
    
    # Get bounds for atomic region
    if region_id in REGION_BOUNDS:
        min_lat, max_lat, min_lng, max_lng = REGION_BOUNDS[region_id]
        return min_lat <= lat <= max_lat and min_lng <= lng <= max_lng
    
    # For composite regions, check if place is in any component region
    if region_id in COMPOSITE_REGIONS:
        for atomic_region in COMPOSITE_REGIONS[region_id]:
            if atomic_region in REGION_BOUNDS:
                min_lat, max_lat, min_lng, max_lng = REGION_BOUNDS[atomic_region]
                if min_lat <= lat <= max_lat and min_lng <= lng <= max_lng:
                    return True
    
    return False
