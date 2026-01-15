"""
Scenario generator for creating evaluation datasets.

Generates diverse scenarios by combining query templates with region-aware
mock data selection and independent weather variation.
"""

import json
import random
from pathlib import Path
from typing import Any

from eval.mock_data_nyc import (
    ATOMIC_REGIONS,
    COMPOSITE_REGIONS,
    MOCK_WEATHER_NYC,
    get_places_for_region,
    get_transit_stops_for_region,
    validate_place_in_region,
)
from eval.scenarios.models import Scenario


# =============================================================================
# QUERY TEMPLATES
# =============================================================================
# Templates are parameterized with {region}, {region1}, {region2}, {activity}, etc.

QUERY_TEMPLATES: dict[str, list[str]] = {
    # Single region queries
    "single_region_general": [
        "What are some fun things to do in {region}?",
        "Can you find activities in {region}?",
        "I'm looking for stuff to do in {region} this weekend",
        "What's happening in {region}?",
        "Find me some cool spots in {region}",
    ],
    "single_region_activity": [
        "Find me {activity} spots in {region}",
        "Where can I find good {activity} in {region}?",
        "I'm looking for {activity} places in {region}",
        "Best {activity} in {region}?",
        "Recommend some {activity} options in {region}",
    ],
    "single_region_date": [
        "Plan a date night in {region}",
        "What are some romantic spots in {region}?",
        "Date ideas for {region}?",
        "Looking for date activities in {region}",
        "Where should I take someone on a first date in {region}?",
    ],
    "single_region_budget": [
        "Find cheap things to do in {region}",
        "What's free in {region}?",
        "Budget-friendly activities in {region}",
        "Affordable date spots in {region}",
        "Low-cost fun in {region}",
    ],
    "single_region_food": [
        "Best restaurants in {region}",
        "Where should I eat in {region}?",
        "Good cafes in {region}",
        "Find me food spots in {region}",
        "Coffee shops in {region}?",
    ],
    "single_region_outdoor": [
        "Outdoor activities in {region}",
        "Parks near {region}",
        "Where can I go for a walk in {region}?",
        "Nature spots in {region}",
        "Best outdoor spots in {region}",
    ],
    
    # Two region queries (between locations)
    "between_regions_general": [
        "Find activities between {region1} and {region2}",
        "What's between {region1} and {region2}?",
        "Date spots between {region1} and {region2}",
        "We're meeting halfway between {region1} and {region2}, what's there?",
        "Activities along the way from {region1} to {region2}",
    ],
    "between_regions_specific": [
        "Find {activity} between {region1} and {region2}",
        "Coffee shops between {region1} and {region2}",
        "Restaurants between {region1} and {region2}",
        "Parks between {region1} and {region2}",
        "Bars between {region1} and {region2}",
    ],
    
    # Weather-dependent queries
    "weather_outdoor": [
        "What outdoor activities can I do in {region} today?",
        "Is it a good day for outdoor stuff in {region}?",
        "Should I plan outdoor activities in {region}?",
        "Good weather activities for {region}?",
    ],
    "weather_indoor": [
        "What indoor activities are there in {region}?",
        "Rainy day activities in {region}",
        "Indoor date ideas in {region}",
        "What to do inside in {region}?",
    ],
    
    # Multi-constraint queries
    "multi_constraint": [
        "Find a cheap {activity} spot in {region} for a date",
        "Budget-friendly {activity} in {region} with good vibes",
        "Romantic {activity} in {region} under $50",
        "Group-friendly {activity} in {region}",
        "Family-friendly things to do in {region}",
    ],
    
    # Context-specific
    "solo": [
        "Things to do alone in {region}",
        "Solo activities in {region}",
        "What can I do by myself in {region}?",
    ],
    "group": [
        "Group activities in {region}",
        "Fun things for a group in {region}",
        "Where can I take a group of friends in {region}?",
    ],
    "family": [
        "Family activities in {region}",
        "Kid-friendly spots in {region}",
        "What to do with kids in {region}?",
    ],
}

# Activity types for template substitution
ACTIVITY_TYPES = [
    "coffee", "food", "restaurants", "cafes", "bars", "parks",
    "museums", "galleries", "shopping", "entertainment", "games",
    "shows", "live music", "art", "outdoor", "nature", "nightlife",
]

# User preference templates
USER_PREFERENCE_TEMPLATES = [
    {"interests": ["coffee", "cafes"], "location": "Brooklyn", "budget_max": 30},
    {"interests": ["outdoor", "nature", "parks"], "location": "Manhattan", "budget_max": 20},
    {"interests": ["food", "restaurants"], "location": "Queens", "budget_max": 50},
    {"interests": ["art", "museums", "galleries"], "location": "Manhattan", "budget_max": 40},
    {"interests": ["nightlife", "bars"], "location": "Brooklyn", "budget_max": 60},
    {"interests": ["games", "entertainment"], "location": "Brooklyn", "budget_max": 35},
    {"interests": ["music", "shows"], "location": "Manhattan", "budget_max": 80},
    {"interests": ["coffee", "bookstores"], "location": "Manhattan", "budget_max": 25},
    {"interests": ["food", "outdoor"], "location": "Brooklyn", "budget_max": 40},
    {"interests": [], "location": None, "budget_max": None},  # Minimal preferences
]


class ScenarioGenerator:
    """
    Generates evaluation scenarios with geographically coherent mock data.
    
    Uses hierarchical regions (atomic and composite) to ensure mock data
    matches the query location.
    """
    
    def __init__(self, seed: int | None = None):
        """
        Initialize the generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
        
        # Pre-compute region lists for sampling
        self.atomic_region_ids = list(ATOMIC_REGIONS.keys())
        self.composite_region_ids = list(COMPOSITE_REGIONS.keys())
        self.all_region_ids = self.atomic_region_ids + self.composite_region_ids
    
    def _format_region_name(self, region_id: str) -> str:
        """Convert region ID to human-readable name."""
        name_map = {
            "greenpoint": "Greenpoint",
            "williamsburg": "Williamsburg",
            "east_williamsburg": "East Williamsburg",
            "south_williamsburg": "South Williamsburg",
            "dumbo": "DUMBO",
            "brooklyn_heights": "Brooklyn Heights",
            "prospect_heights": "Prospect Heights",
            "fidi": "the Financial District",
            "tribeca": "Tribeca",
            "soho": "SoHo",
            "les": "the Lower East Side",
            "east_village": "the East Village",
            "chelsea": "Chelsea",
            "midtown_west": "Midtown West",
            "midtown_east": "Midtown East",
            "uws": "the Upper West Side",
            "ues": "the Upper East Side",
            "lic": "Long Island City",
            "southern_astoria": "Astoria",
            "northern_astoria": "Astoria",
            "lic_midtown_east": "Long Island City and Midtown East",
            "fidi_dumbo": "FiDi and DUMBO",
            "lic_greenpoint": "Long Island City and Greenpoint",
            "les_williamsburg": "the Lower East Side and Williamsburg",
            "greenpoint_williamsburg": "Greenpoint and Williamsburg",
            "chelsea_midtown_west": "Chelsea and Midtown West",
            "astoria": "Astoria",
            "queens_near_manhattan": "Queens",
            "williamsburg_all": "Williamsburg",
            "lower_manhattan": "Lower Manhattan",
            "southern_manhattan": "Lower Manhattan",
            "midtown": "Midtown",
            "north_brooklyn": "North Brooklyn",
            "downtown_brooklyn": "Downtown Brooklyn",
            "brooklyn": "Brooklyn",
            "manhattan": "Manhattan",
            "queens": "Queens",
            "upper_manhattan": "the Upper East and West Sides",
            "central_park_area": "Central Park area",
        }
        return name_map.get(region_id, region_id.replace("_", " ").title())
    
    def _select_places_for_scenario(
        self, region_id: str, count: int = 5
    ) -> list[dict[str, Any]]:
        """Select a subset of places for a scenario."""
        all_places = get_places_for_region(region_id)
        if len(all_places) <= count:
            return all_places
        return random.sample(all_places, count)
    
    def _generate_single_region_scenario(
        self,
        scenario_id: str,
        category: str,
        template_key: str,
    ) -> Scenario:
        """Generate a scenario for a single region query."""
        # Select region
        region_id = random.choice(self.all_region_ids)
        region_name = self._format_region_name(region_id)
        
        # Select template and format
        templates = QUERY_TEMPLATES.get(template_key, QUERY_TEMPLATES["single_region_general"])
        template = random.choice(templates)
        
        # Handle activity substitution if needed
        if "{activity}" in template:
            activity = random.choice(ACTIVITY_TYPES)
            query = template.format(region=region_name, activity=activity)
        else:
            query = template.format(region=region_name)
        
        # Get mock data
        places = self._select_places_for_scenario(region_id)
        weather = random.choice(MOCK_WEATHER_NYC)
        preferences = random.choice(USER_PREFERENCE_TEMPLATES)
        
        # Determine expected tools based on category
        expected_tools = ["search_places_for_dates"]
        if category in ["weather_outdoor", "outdoor"]:
            expected_tools.append("get_weather_for_location")
        
        # Build ground truth
        ground_truth = {
            "min_places_mentioned": 1,
            "should_use_region": region_name.lower() in query.lower(),
        }
        if category == "weather_outdoor":
            ground_truth["should_mention_weather"] = True
        if category == "budget":
            ground_truth["should_mention_price"] = True
        
        return Scenario(
            id=scenario_id,
            category=category,
            query=query,
            region=region_id,
            user_preferences=preferences,
            mock_tool_responses={
                "search_places_for_dates": {"activities": places, "count": len(places)},
                "get_weather_for_location": weather,
            },
            expected_tools=expected_tools,
            ground_truth=ground_truth,
        )
    
    def _generate_between_regions_scenario(
        self,
        scenario_id: str,
        category: str,
    ) -> Scenario:
        """Generate a scenario for between-two-regions query."""
        # Select two different atomic regions
        region1_id = random.choice(self.atomic_region_ids)
        region2_id = random.choice([r for r in self.atomic_region_ids if r != region1_id])
        
        region1_name = self._format_region_name(region1_id)
        region2_name = self._format_region_name(region2_id)
        
        # Select template
        template_key = "between_regions_specific" if random.random() > 0.5 else "between_regions_general"
        templates = QUERY_TEMPLATES[template_key]
        template = random.choice(templates)
        
        if "{activity}" in template:
            activity = random.choice(ACTIVITY_TYPES)
            query = template.format(region1=region1_name, region2=region2_name, activity=activity)
        else:
            query = template.format(region1=region1_name, region2=region2_name)
        
        # Combine places from both regions
        places1 = self._select_places_for_scenario(region1_id, count=3)
        places2 = self._select_places_for_scenario(region2_id, count=3)
        places = places1 + places2
        random.shuffle(places)
        
        weather = random.choice(MOCK_WEATHER_NYC)
        preferences = random.choice(USER_PREFERENCE_TEMPLATES)
        
        # Create composite region ID for this scenario
        composite_region = f"{region1_id}_{region2_id}"
        
        return Scenario(
            id=scenario_id,
            category=category,
            query=query,
            region=composite_region,
            user_preferences=preferences,
            mock_tool_responses={
                "search_places_for_dates": {"activities": places, "count": len(places)},
                "get_weather_for_location": weather,
            },
            expected_tools=["search_places_for_dates"],
            ground_truth={
                "min_places_mentioned": 2,
                "should_mention_both_regions": True,
            },
        )
    
    def _generate_weather_scenario(
        self,
        scenario_id: str,
        outdoor: bool = True,
    ) -> Scenario:
        """Generate a weather-dependent scenario."""
        region_id = random.choice(self.all_region_ids)
        region_name = self._format_region_name(region_id)
        
        template_key = "weather_outdoor" if outdoor else "weather_indoor"
        template = random.choice(QUERY_TEMPLATES[template_key])
        query = template.format(region=region_name)
        
        places = self._select_places_for_scenario(region_id)
        
        # For outdoor queries, vary the weather impact
        if outdoor:
            # 50% good weather, 50% bad weather
            if random.random() > 0.5:
                weather_options = [w for w in MOCK_WEATHER_NYC if w["outdoor_suitable"]]
            else:
                weather_options = [w for w in MOCK_WEATHER_NYC if not w["outdoor_suitable"]]
            weather = random.choice(weather_options) if weather_options else random.choice(MOCK_WEATHER_NYC)
        else:
            # For indoor queries, use bad weather
            weather_options = [w for w in MOCK_WEATHER_NYC if not w["outdoor_suitable"]]
            weather = random.choice(weather_options) if weather_options else random.choice(MOCK_WEATHER_NYC)
        
        preferences = random.choice(USER_PREFERENCE_TEMPLATES)
        
        category = "outdoor" if outdoor else "indoor"
        
        return Scenario(
            id=scenario_id,
            category=category,
            query=query,
            region=region_id,
            user_preferences=preferences,
            mock_tool_responses={
                "search_places_for_dates": {"activities": places, "count": len(places)},
                "get_weather_for_location": weather,
            },
            expected_tools=["search_places_for_dates", "get_weather_for_location"],
            ground_truth={
                "should_mention_weather": True,
                "should_recommend_outdoor": weather["outdoor_suitable"] if outdoor else False,
                "min_places_mentioned": 1,
            },
        )
    
    def generate_scenario(self, scenario_id: str) -> Scenario:
        """
        Generate a single random scenario.
        
        Args:
            scenario_id: Unique ID for the scenario
            
        Returns:
            Generated Scenario object
        """
        # Randomly select scenario type
        scenario_type = random.choice([
            "single_general",
            "single_activity",
            "single_date",
            "single_budget",
            "single_food",
            "single_outdoor",
            "between_regions",
            "weather_outdoor",
            "weather_indoor",
            "multi_constraint",
            "context_solo",
            "context_group",
            "context_family",
        ])
        
        if scenario_type == "single_general":
            return self._generate_single_region_scenario(scenario_id, "general", "single_region_general")
        elif scenario_type == "single_activity":
            return self._generate_single_region_scenario(scenario_id, "activity", "single_region_activity")
        elif scenario_type == "single_date":
            return self._generate_single_region_scenario(scenario_id, "date", "single_region_date")
        elif scenario_type == "single_budget":
            return self._generate_single_region_scenario(scenario_id, "budget", "single_region_budget")
        elif scenario_type == "single_food":
            return self._generate_single_region_scenario(scenario_id, "food", "single_region_food")
        elif scenario_type == "single_outdoor":
            return self._generate_single_region_scenario(scenario_id, "outdoor", "single_region_outdoor")
        elif scenario_type == "between_regions":
            return self._generate_between_regions_scenario(scenario_id, "between_regions")
        elif scenario_type == "weather_outdoor":
            return self._generate_weather_scenario(scenario_id, outdoor=True)
        elif scenario_type == "weather_indoor":
            return self._generate_weather_scenario(scenario_id, outdoor=False)
        elif scenario_type == "multi_constraint":
            return self._generate_single_region_scenario(scenario_id, "multi_constraint", "multi_constraint")
        elif scenario_type == "context_solo":
            return self._generate_single_region_scenario(scenario_id, "solo", "solo")
        elif scenario_type == "context_group":
            return self._generate_single_region_scenario(scenario_id, "group", "group")
        elif scenario_type == "context_family":
            return self._generate_single_region_scenario(scenario_id, "family", "family")
        else:
            return self._generate_single_region_scenario(scenario_id, "general", "single_region_general")
    
    def generate(self, count: int = 100, seed: int | None = None) -> list[Scenario]:
        """
        Generate a set of evaluation scenarios.
        
        Args:
            count: Number of scenarios to generate
            seed: Random seed for reproducibility
            
        Returns:
            List of generated Scenario objects
        """
        if seed is not None:
            random.seed(seed)
        
        scenarios = []
        for i in range(count):
            scenario_id = f"scenario_{i:05d}"
            scenario = self.generate_scenario(scenario_id)
            scenarios.append(scenario)
        
        return scenarios
    
    def validate_scenario(self, scenario: Scenario) -> bool:
        """
        Validate that a scenario is coherent.
        
        Checks:
        - Mock place coordinates fall within expected region bounds
        
        Args:
            scenario: Scenario to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Get places from mock responses
        places_response = scenario.mock_tool_responses.get("search_places_for_dates", {})
        places = places_response.get("activities", [])
        
        if not places:
            return True  # No places to validate
        
        # Check that places are in the specified region
        region_id = scenario.region
        
        # Handle dynamic composite regions (like "region1_region2")
        if "_" in region_id and region_id not in COMPOSITE_REGIONS and region_id not in ATOMIC_REGIONS:
            # This is a dynamically created composite region
            parts = region_id.split("_")
            # For dynamic composites, we just check that places exist
            return len(places) > 0
        
        # Validate each place
        for place in places:
            if not validate_place_in_region(place, region_id):
                # Place is outside region bounds
                return False
        
        return True
    
    def save_dataset(self, scenarios: list[Scenario], path: str) -> None:
        """
        Save scenarios to a JSON file.
        
        Args:
            scenarios: List of scenarios to save
            path: Output file path
        """
        data = [s.to_dict() for s in scenarios]
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    def load_dataset(self, path: str) -> list[Scenario]:
        """
        Load scenarios from a JSON file.
        
        Args:
            path: Input file path
            
        Returns:
            List of Scenario objects
        """
        with open(path, "r") as f:
            data = json.load(f)
        return [Scenario.from_dict(d) for d in data]


def generate_eval_dataset(
    count: int = 1000,
    output_path: str | None = None,
    seed: int = 42,
) -> list[Scenario]:
    """
    Convenience function to generate and optionally save an evaluation dataset.
    
    Args:
        count: Number of scenarios to generate
        output_path: Optional path to save the dataset
        seed: Random seed for reproducibility
        
    Returns:
        List of generated scenarios
    """
    generator = ScenarioGenerator(seed=seed)
    scenarios = generator.generate(count=count)
    
    # Validate all scenarios
    valid_scenarios = []
    invalid_count = 0
    for scenario in scenarios:
        if generator.validate_scenario(scenario):
            valid_scenarios.append(scenario)
        else:
            invalid_count += 1
    
    if invalid_count > 0:
        print(f"Warning: {invalid_count} scenarios failed validation")
    
    if output_path:
        generator.save_dataset(valid_scenarios, output_path)
        print(f"Saved {len(valid_scenarios)} scenarios to {output_path}")
    
    return valid_scenarios
