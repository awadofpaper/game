import random

# Weather types and rare events
WEATHER_TYPES = [
    "clear", "light_rain", "heavy_rain", "storm", "thunder", "snow", "fog", "heatwave"
]
RARE_WEATHER_TYPES = [
    "tornado", "tsunami", "meteor_shower", "aurora", "blood_moon"
]

# Map months to default seasonal weather weights (example, tweak as you like)
SEASONAL_WEATHER_WEIGHTS = {
    "Spring": {"clear": 30, "light_rain": 30, "heavy_rain": 10, "storm": 5, "thunder": 5, "snow": 0, "fog": 10, "heatwave": 0},
    "Summer": {"clear": 40, "light_rain": 10, "heavy_rain": 5, "storm": 10, "thunder": 10, "snow": 0, "fog": 5, "heatwave": 20},
    "Autumn": {"clear": 25, "light_rain": 25, "heavy_rain": 15, "storm": 10, "thunder": 5, "snow": 5, "fog": 10, "heatwave": 5},
    "Winter": {"clear": 10, "light_rain": 5, "heavy_rain": 5, "storm": 5, "thunder": 0, "snow": 40, "fog": 10, "heatwave": 0},
}

# Rare weather chances - FIXED: Was 0.00005 (1 in 20,000 days = 791 real days!)
# Now 0.005 (0.5% = 1 in 200 days = ~190 hours of gameplay)
RARE_WEATHER_CHANCE = 0.005  # 0.5% chance per day (1 in 200 days)

class WeatherSystem:
    def __init__(self, game_time, seed=None):
        self.game_time = game_time
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.random = random.Random(self.seed)
        self.current_weather = "clear"
        self.current_intensity = 1.0
        self.weather_history = {}  # (year, month, day): (weather, intensity)
        self.forecast = []  # List of (weather, intensity) for next 7 days

    # More methods will be added in the next steps
    
    def generate_weather_for_day(self, year, month, day):
        """Deterministically generate weather for a given date."""
        # Use a tuple of (year, month, day, seed) to get a repeatable random state
        day_seed = hash((self.seed, year, month, day))
        rng = random.Random(day_seed)

        # Check for rare weather first
        if rng.random() < RARE_WEATHER_CHANCE:
            weather = rng.choice(RARE_WEATHER_TYPES)
            intensity = rng.uniform(1.0, 2.0)
            return weather, intensity

        # Get season from game_time logic
        season = self.game_time.seasons[(month - 1) // 3]
        weights = SEASONAL_WEATHER_WEIGHTS[season]
        weather_choices = []
        for wtype, weight in weights.items():
            weather_choices.extend([wtype] * weight)
        weather = rng.choice(weather_choices)
        # Intensity: 1.0 for normal, 1.5 for heavy, 0.5 for light, etc.
        intensity = rng.uniform(0.7, 1.3)
        return weather, intensity
    
    def advance_weather(self):
        """Advance weather to the next day, update history and forecast."""
        year = self.game_time.year_count
        month = self.game_time.month_count
        day = self.game_time.day_count

        # Generate today's weather
        weather, intensity = self.generate_weather_for_day(year, month, day)
        self.current_weather = weather
        self.current_intensity = intensity
        self.weather_history[(year, month, day)] = (weather, intensity)

        # Update forecast for next 7 days
        self.forecast = []
        for i in range(1, 8):
            # Calculate future date
            f_day = day + i
            f_month = month
            f_year = year
            if f_day > self.game_time.days_per_month:
                f_day -= self.game_time.days_per_month
                f_month += 1
                if f_month > self.game_time.months_per_year:
                    f_month = 1
                    f_year += 1
            f_weather, f_intensity = self.generate_weather_for_day(f_year, f_month, f_day)
            self.forecast.append((f_weather, f_intensity))
            
    def get_current_weather(self):
        """Return the current weather and intensity."""
        return self.current_weather, self.current_intensity

    def get_weather_for_day(self, year, month, day):
        """Return the weather for a specific day (from history or generated)."""
        key = (year, month, day)
        if key in self.weather_history:
            return self.weather_history[key]
        return self.generate_weather_for_day(year, month, day)

    def get_forecast(self):
        """Return the forecast for the next 7 days, with 13% accuracy.
        
        Rare events now show as 'severe_weather_warning' to alert players without spoiling the surprise.
        """
        forecast = []
        for i, (w, intensity) in enumerate(self.forecast):
            # 13% chance of being correct, otherwise random
            if i == 0 or self.random.random() < 0.13:
                # Rare events show as generic warning (not specific event)
                if w in RARE_WEATHER_TYPES:
                    # Show warning for rare events within 3 days
                    if i < 3:
                        forecast.append(("severe_weather_warning", 2.0))
                    else:
                        # Too far out - just show normal weather
                        forecast.append(("clear", 1.0))
                else:
                    forecast.append((w, intensity))
            else:
                # Pick a non-rare weather type for the "wrong" forecast
                possible = [wt for wt in WEATHER_TYPES if wt != w]
                w_wrong = self.random.choice(possible)
                forecast.append((w_wrong, 1.0))
        return forecast
    
    def save_state(self):
        """Return a dict representing the weather system state."""
        return {
            "current_weather": self.current_weather,
            "current_intensity": self.current_intensity,
            "weather_history": self.weather_history,
            "forecast": self.forecast,
            "seed": self.seed,
        }

    def load_state(self, state):
        """Load the weather system state from a dict."""
        self.current_weather = state.get("current_weather", "clear")
        self.current_intensity = state.get("current_intensity", 1.0)
        self.weather_history = state.get("weather_history", {})
        self.forecast = state.get("forecast", [])
        self.seed = state.get("seed", self.seed)
        self.random = random.Random(self.seed)
