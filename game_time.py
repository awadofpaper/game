class GameTime:
    def __init__(self, cycle_minutes=57):
        self.cycle_minutes = cycle_minutes  # Total minutes for a full day-night cycle
        self.seconds_per_cycle = cycle_minutes * 60
        self.current_seconds = 0.0  # Seconds elapsed in current cycle
        self.day_count = 1  # Start at day 1
        
        self.month_count = 1  # Start at month 1
        self.year_count = 1   # Start at year 1
        self.days_per_month = 30
        self.months_per_year = 12
        self.days_of_week = [
            "Solisday", "Lunaday", "Terraday", "Aquaday", "Aerisday", "Pyreday", "Starend"
        ]
        self.month_names = [
            "Auroramyst", "Emberveil", "Starspire", "Verdantia", "Luminaris", "Solstice",
            "Zephyros", "Pyraeli", "Umbrafall", "Frosthallow", "Duskryn", "Nivale"
        ]
        self.seasons = ["Spring", "Summer", "Autumn", "Winter"]
        
        # Day/night cycle properties
        self.is_night = False
        self.is_day = True
        self.time_period = "day"
        self.ambient_light = 1.0
        self.light_color = (1.0, 1.0, 1.0)

    # More methods will be added in the next steps
    def advance_time(self, delta_seconds):
        self.current_seconds += delta_seconds
        day_changed = False
        
        if self.current_seconds >= self.seconds_per_cycle:
            self.current_seconds -= self.seconds_per_cycle
            self.day_count += 1
            day_changed = True

            # Handle month and year rollover
            if self.day_count > self.days_per_month:
                self.day_count = 1
                self.month_count += 1
                if self.month_count > self.months_per_year:
                    self.month_count = 1
                    self.year_count += 1
        
        # Update day/night properties
        self.time_period = self.get_phase()
        self.is_night = self.time_period in ["night", "dusk"]
        self.is_day = self.time_period in ["day", "dawn"]
        self.ambient_light = self._calculate_ambient_light()
        self.light_color = self._calculate_light_color()
        
        return day_changed 
                        
    def get_month_name(self):
        """Returns the current month name."""
        return self.month_names[self.month_count - 1]

    def get_day_of_week(self):
        """Returns the current day of the week name."""
        # Day 1 of year is always index 0 (Solisday)
        total_days = (self.month_count - 1) * self.days_per_month + (self.day_count - 1)
        return self.days_of_week[total_days % len(self.days_of_week)]

    def get_season(self):
        """Returns the current season name."""
        # Each season is 3 months
        season_index = (self.month_count - 1) // 3
        return self.seasons[season_index]
            
    def get_time_hm(self):
        """Returns current time as (hour, minute) tuple."""
        total_minutes = (self.current_seconds / self.seconds_per_cycle) * 24 * 60
        hour = int(total_minutes // 60)
        minute = int(total_minutes % 60)
        return hour, minute

    def get_phase(self):
        """Returns the current phase: 'dawn', 'day', 'dusk', or 'night'."""
        # Define durations in minutes (customize as needed)
        dawn_duration = 4
        day_duration = 35
        dusk_duration = 4
        night_duration = 22

        # Calculate current minute in cycle
        minute_in_cycle = (self.current_seconds / self.seconds_per_cycle) * (dawn_duration + day_duration + dusk_duration + night_duration)
        
        if minute_in_cycle < dawn_duration:
            return "dawn"
        elif minute_in_cycle < dawn_duration + day_duration:
            return "day"
        elif minute_in_cycle < dawn_duration + day_duration + dusk_duration:
            return "dusk"
        else:
            return "night" 
        
    def get_time_str(self):
        """Returns the current time as a formatted string, e.g., '14:05'."""
        hour, minute = self.get_time_hm()
        return f"{hour:02d}:{minute:02d}"

    def get_day(self):
        """Returns the current day number."""
        return self.day_count   


    def get_total_minutes(self):
        """Return the total in-game minutes elapsed in the current day."""
        # Use the same calculation as get_time_hm
        total_minutes = (self.current_seconds / self.seconds_per_cycle) * 24 * 60
        return int(total_minutes)
        
    def get_time_of_day_fraction(self):
        """Return fraction of day passed (0.0 = start of day, 1.0 = end of day)."""
        return self.current_seconds / self.seconds_per_cycle
    
    def _calculate_ambient_light(self):
        """Calculate ambient light level (0.3 - 1.0)"""
        phase = self.get_phase()
        hour, minute = self.get_time_hm()
        time_fraction = hour + (minute / 60.0)
        
        if phase == "day":
            # Full daylight (between 10am-4pm peak, otherwise slight reduction)
            if 10 <= time_fraction <= 16:
                return 1.0
            else:
                return 0.95
        elif phase == "night":
            # Dark night (minimum 0.3 for gameplay visibility)
            return 0.35
        elif phase == "dawn":
            # Gradual brightening (0.35 -> 1.0)
            # Dawn is ~4 minutes, estimate progress
            dawn_progress = (time_fraction - 5) / 2  # Rough estimate 5-7am
            dawn_progress = max(0, min(1, dawn_progress))
            return 0.35 + (0.65 * dawn_progress)
        elif phase == "dusk":
            # Gradual darkening (1.0 -> 0.35)
            dusk_progress = (time_fraction - 18) / 2  # Rough estimate 18-20
            dusk_progress = max(0, min(1, dusk_progress))
            return 1.0 - (0.65 * dusk_progress)
        
        return 0.7
    
    def _calculate_light_color(self):
        """Calculate light color tint (R, G, B) as tuple of 0.0-1.0 values"""
        phase = self.get_phase()
        
        if phase == "day":
            # Neutral white light
            return (1.0, 1.0, 1.0)
        elif phase == "night":
            # Cool blue tint
            return (0.65, 0.75, 1.0)
        elif phase == "dawn":
            # Warm orange/pink tint
            return (1.0, 0.85, 0.75)
        elif phase == "dusk":
            # Warm orange/red tint
            return (1.0, 0.75, 0.6)
        
        return (1.0, 1.0, 1.0)
    
    def get_darkness_overlay_alpha(self):
        """Get alpha value for darkness overlay (0-255)"""
        # Convert ambient light (0.35-1.0) to darkness alpha
        # 1.0 light = 0 darkness, 0.35 light = ~165 darkness
        darkness = 1.0 - self.ambient_light
        return int(darkness * 220)  # Max 220 alpha for darkness
    
    def is_weekday(self):
        """Check if current day is a weekday (Solisday-Aerisday)"""
        day_name = self.get_day_of_week()
        weekdays = ["Solisday", "Lunaday", "Terraday", "Aquaday", "Aerisday"]
        return day_name in weekdays
    
    def is_weekend(self):
        """Check if current day is a weekend (Pyreday, Starend)"""
        return not self.is_weekday()
    
    def is_shop_open(self, open_hour=6, close_hour=20):
        """Check if shops should be open"""
        hour, _ = self.get_time_hm()
        return open_hour <= hour < close_hour
    
    def is_business_open(self, business_type, open_hour=9, close_hour=17, weekdays_only=True, 
                         weekend_open_hour=None, weekend_close_hour=None):
        """
        Check if a business should be open based on day and time.
        
        Args:
            business_type: Type of business (for future custom schedules)
            open_hour: Opening hour on weekdays
            close_hour: Closing hour on weekdays
            weekdays_only: If True, closed on weekends
            weekend_open_hour: Opening hour on weekends (None = closed)
            weekend_close_hour: Closing hour on weekends (None = closed)
        """
        hour, _ = self.get_time_hm()
        
        if self.is_weekday():
            return open_hour <= hour < close_hour
        else:  # Weekend
            if weekdays_only or weekend_open_hour is None:
                return False
            return weekend_open_hour <= hour < weekend_close_hour
    
    def is_npc_sleeping(self, sleep_hour=22, wake_hour=6):
        """Check if NPCs should be sleeping"""
        hour, _ = self.get_time_hm()
        if sleep_hour < wake_hour:
            # Normal case (e.g., 22 to 6)
            return hour >= sleep_hour or hour < wake_hour
        else:
            # Edge case
            return sleep_hour <= hour < wake_hour
    
    def skip_to_time(self, target_hour, target_minute=0):
        """Skip forward to a specific time (e.g., for inn rest)"""
        current_hour, current_minute = self.get_time_hm()
        current_total_minutes = current_hour * 60 + current_minute
        target_total_minutes = target_hour * 60 + target_minute
        
        # If target is earlier in the day, it means next day
        if target_total_minutes <= current_total_minutes:
            target_total_minutes += 24 * 60
            self.day_count += 1
        
        minutes_to_skip = target_total_minutes - current_total_minutes
        seconds_to_skip = minutes_to_skip * 60
        
        # Convert game minutes to cycle seconds
        seconds_to_skip_in_cycle = (seconds_to_skip / (24 * 60 * 60)) * self.seconds_per_cycle
        self.current_seconds += seconds_to_skip_in_cycle
        
        # Handle day rollover
        if self.current_seconds >= self.seconds_per_cycle:
            self.current_seconds -= self.seconds_per_cycle
        
        # Update derived values
        self.time_period = self.get_phase()
        self.is_night = self.time_period in ["night", "dusk"]
        self.is_day = self.time_period in ["day", "dawn"]
        self.ambient_light = self._calculate_ambient_light()
        self.light_color = self._calculate_light_color()
