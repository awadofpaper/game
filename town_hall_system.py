"""
Town Hall System with Bulletin Board
Provides town information, weather forecast, quest postings, and news
"""

import pygame
import logging

logger = logging.getLogger(__name__)


class BulletinPost:
    """A post on the bulletin board"""
    def __init__(self, title, content, post_type, priority=0):
        self.title = title
        self.content = content
        self.post_type = post_type  # weather, quest, bounty, news, wanted, job
        self.priority = priority  # Higher priority posts appear first


class TownHall:
    """Represents a town hall with bulletin board and services"""
    def __init__(self, building, town_name, town):
        self.building = building
        self.town_name = town_name
        self.town = town
        self.name = building.name


class TownHallManager:
    """Manages all town halls in the game world"""
    def __init__(self, weather_system, game_time, quest_manager=None):
        self.town_halls = []
        self.weather_system = weather_system
        self.game_time = game_time
        self.quest_manager = quest_manager
    
    def register_town_hall(self, building, town_name, town):
        """Register a building as a town hall"""
        town_hall = TownHall(building, town_name, town)
        self.town_halls.append(town_hall)
        logger.info(f"[TOWN HALL] Registered: {town_hall.name}")
        return town_hall
    
    def get_nearby_town_hall(self, player_x, player_y, max_distance=80):
        """Find the nearest town hall within interaction range"""
        nearest = None
        nearest_distance = max_distance
        
        for town_hall in self.town_halls:
            door_x = town_hall.building.x + town_hall.building.width // 2
            door_y = town_hall.building.y + town_hall.building.height
            
            dx = player_x - door_x
            dy = player_y - door_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < nearest_distance:
                nearest_distance = distance
                nearest = town_hall
        
        return nearest
    
    def generate_bulletin_posts(self, town_hall, player=None):
        """Generate bulletin board posts for a town hall"""
        posts = []
        
        # 1. Weather Forecast (14 days)
        posts.append(self._generate_weather_forecast())
        
        # 2. Town Information
        posts.append(self._generate_town_info(town_hall))
        
        # 3. Available Quests
        if self.quest_manager and player:
            quest_posts = self._generate_quest_posts(player)
            posts.extend(quest_posts)
        
        # 4. Regional News
        posts.extend(self._generate_regional_news())
        
        # 5. Wanted Posters
        posts.extend(self._generate_wanted_posters())
        
        # 6. Job Listings
        posts.extend(self._generate_job_listings())
        
        # Sort by priority
        posts.sort(key=lambda p: p.priority, reverse=True)
        
        return posts
    
    def _generate_weather_forecast(self):
        """Generate 14-day weather forecast post"""
        content_lines = ["═══ 14-Day Weather Outlook ═══", ""]
        
        # Current weather
        current_weather, current_intensity = self.weather_system.get_current_weather()
        content_lines.append(f"TODAY: {current_weather.replace('_', ' ').title()}")
        content_lines.append("")
        
        # Get current date
        year = self.game_time.year_count
        month = self.game_time.month_count
        day = self.game_time.day_count
        
        # Generate 14-day forecast
        content_lines.append("Upcoming Days:")
        for i in range(1, 15):
            # Calculate future date
            f_day = day + i
            f_month = month
            f_year = year
            
            while f_day > self.game_time.days_per_month:
                f_day -= self.game_time.days_per_month
                f_month += 1
                if f_month > self.game_time.months_per_year:
                    f_month = 1
                    f_year += 1
            
            # Get weather for that day
            f_weather, f_intensity = self.weather_system.generate_weather_for_day(f_year, f_month, f_day)
            
            # Format weather name
            weather_name = f_weather.replace('_', ' ').title()
            
            # Add intensity indicator
            if f_intensity > 1.2:
                intensity_marker = " [Heavy]"
            elif f_intensity < 0.8:
                intensity_marker = " [Light]"
            else:
                intensity_marker = ""
            
            # Add to forecast
            day_name = f"Day {i}"
            content_lines.append(f"  {day_name}: {weather_name}{intensity_marker}")
        
        content_lines.append("")
        content_lines.append("Note: Forecasts are estimates and may change.")
        
        return BulletinPost(
            "Weather Forecast",
            "\n".join(content_lines),
            "weather",
            priority=100  # Highest priority
        )
    
    def _generate_town_info(self, town_hall):
        """Generate town information post"""
        town = town_hall.town
        
        content_lines = [
            f"═══ Welcome to {town.name} ═══",
            "",
            f"Town Size: {town.size.title()}",
            f"Buildings: {len(town.buildings)}",
            "",
            "Available Services:",
        ]
        
        # List building types in town
        building_types = {}
        for building in town.buildings:
            building_type = building.type.name if hasattr(building.type, 'name') else str(building.type)
            building_types[building_type] = building_types.get(building_type, 0) + 1
        
        for building_type, count in sorted(building_types.items()):
            if count > 1:
                content_lines.append(f"  • {building_type.replace('_', ' ').title()} ({count})")
            else:
                content_lines.append(f"  • {building_type.replace('_', ' ').title()}")
        
        content_lines.append("")
        content_lines.append("The Mayor welcomes all travelers!")
        
        return BulletinPost(
            f"{town.name} Information",
            "\n".join(content_lines),
            "info",
            priority=90
        )
    
    def _generate_quest_posts(self, player):
        """Generate posts for available quests"""
        posts = []
        
        if not self.quest_manager:
            return posts
        
        available_quests = self.quest_manager.get_available_quests(player)
        
        for quest in available_quests[:5]:  # Show up to 5 quests
            content_lines = [
                f"Quest: {quest.name}",
                "",
                quest.description,
                "",
                f"Difficulty: {quest.category.name if hasattr(quest.category, 'name') else str(quest.category)}",
            ]
            
            if quest.rewards.get('gold', 0) > 0:
                content_lines.append(f"Reward: {quest.rewards['gold']}g")
            
            if quest.rewards.get('xp', 0) > 0:
                content_lines.append(f"Experience: {quest.rewards['xp']} XP")
            
            if quest.giver_npc_id:
                content_lines.append("")
                content_lines.append(f"Speak to: {quest.giver_npc_id}")
            
            posts.append(BulletinPost(
                f"Quest Available: {quest.name[:30]}",
                "\n".join(content_lines),
                "quest",
                priority=80
            ))
        
        return posts
    
    def _generate_regional_news(self):
        """Generate regional news posts"""
        import random
        
        news_items = [
            ("Trade Routes Secure", "Merchants report safe passage\nalong major trade routes.\nCommerce is thriving!", 60),
            ("Harvest Season", "Farmers celebrate a bountiful\nharvest this season.\nFood prices stable.", 55),
            ("Travelers Advisory", "The roads are busy with travelers.\nWatch for strangers and\nkeep valuables safe.", 50),
            ("Festival Coming", "The annual town festival\napproaches! Preparations\nare underway.", 65),
            ("Guard Patrol", "Town guards increase patrols\nafter dark. Citizens report\nfeeling safer.", 45),
        ]
        
        # Randomly select 1-2 news items
        selected = random.sample(news_items, min(2, len(news_items)))
        
        posts = []
        for title, content, priority in selected:
            posts.append(BulletinPost(
                title,
                content,
                "news",
                priority=priority
            ))
        
        return posts
    
    def _generate_wanted_posters(self):
        """Generate wanted posters for enemies"""
        import random
        
        wanted_creatures = [
            ("Bandit Leader", "Dangerous outlaw terrorizing\ntraders. Armed and hostile.\nReward: 500g", 70),
            ("Rogue Mage", "Wanted for dark magic practices.\nExtremely dangerous.\nReward: 1000g", 75),
            ("Giant Spider", "Massive arachnid spotted\nnear town. Threat to travelers.\nReward: 300g", 60),
            ("Wolf Pack Alpha", "Leading aggressive pack.\nMultiple attacks reported.\nReward: 400g", 65),
        ]
        
        # Select 1-2 wanted posters
        selected = random.sample(wanted_creatures, min(2, len(wanted_creatures)))
        
        posts = []
        for name, description, priority in selected:
            posts.append(BulletinPost(
                f"WANTED: {name}",
                description,
                "wanted",
                priority=priority
            ))
        
        return posts
    
    def _generate_job_listings(self):
        """Generate job listing posts"""
        import random
        
        jobs = [
            ("Guard Duty", "Town guard seeks volunteers\nfor night watch duty.\nPay: 50g per shift", 40),
            ("Herb Gathering", "Alchemist needs rare herbs.\nWill pay for fresh ingredients.\nPay: Varies", 35),
            ("Message Delivery", "Courier needed for deliveries\nto neighboring towns.\nPay: 100g per delivery", 45),
            ("Monster Hunting", "Bounty on dangerous creatures.\nExperience required.\nPay: By contract", 50),
        ]
        
        # Select 1-2 job listings
        selected = random.sample(jobs, min(2, len(jobs)))
        
        posts = []
        for title, description, priority in selected:
            posts.append(BulletinPost(
                title,
                description,
                "job",
                priority=priority
            ))
        
        return posts


class TownHallUI:
    """UI for town hall bulletin board"""
    def __init__(self, config):
        self.config = config
        self.active = False
        self.current_town_hall = None
        self.town_hall_manager = None
        self.bulletin_posts = []
        self.selected_post_index = 0
        self.scroll_offset = 0
        self.viewing_detail = False
        
        # Voting mode
        self.voting_mode = False
        self.ballot_box = None
        self.election_timeline = None
        self.selected_candidate_idx = 0
        
        # Services mode
        self.services_mode = True  # Start with services menu
        self.selected_service_idx = 0
        self.property_tax_system = None
        self.showing_tax_payment = False
    
    def open(self, town_hall, town_hall_manager, player=None, ballot_box=None, election_timeline=None, property_tax_system=None):
        """Open the town hall bulletin board, voting interface, or services"""
        self.active = True
        self.current_town_hall = town_hall
        self.town_hall_manager = town_hall_manager
        self.selected_post_index = 0
        self.scroll_offset = 0
        self.viewing_detail = False
        self.ballot_box = ballot_box
        self.election_timeline = election_timeline
        self.selected_candidate_idx = 0
        self.property_tax_system = property_tax_system
        self.selected_service_idx = 0
        self.showing_tax_payment = False
        
        # Check if voting mode should be active
        if election_timeline and ballot_box and election_timeline.state == "voting":
            self.voting_mode = True
            self.services_mode = False
            logger.info(f"[TOWN HALL UI] Opened in VOTING MODE")
        else:
            self.voting_mode = False
            self.services_mode = True  # Start with services menu
            # Don't generate bulletin posts yet - wait for user to select "View Bulletin Board"
        
        logger.info(f"[TOWN HALL UI] Opened {town_hall.name}")
    
    def close(self):
        """Close the town hall"""
        self.active = False
        self.current_town_hall = None
        self.viewing_detail = False
        self.voting_mode = False
        self.services_mode = True  # Reset to services mode
        self.showing_tax_payment = False
        logger.info("[TOWN HALL UI] Closed")
    
    def handle_input(self, event, player=None):
        """Handle keyboard input for town hall"""
        if not self.active or not self.current_town_hall:
            return
        
        if event.type == pygame.KEYDOWN:
            # Voting mode input handling
            if self.voting_mode:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                elif event.key == pygame.K_UP:
                    self.selected_candidate_idx = max(0, self.selected_candidate_idx - 1)
                elif event.key == pygame.K_DOWN:
                    num_candidates = len(self.ballot_box.candidates)
                    self.selected_candidate_idx = min(num_candidates - 1, self.selected_candidate_idx + 1)
                elif event.key == pygame.K_RETURN:
                    # Cast vote
                    if player and self.ballot_box:
                        if not player.can_vote:
                            logger.warning("[VOTING] Player is not eligible to vote")
                            return "not_eligible"
                        
                        if player.voted_this_election:
                            logger.warning("[VOTING] Player has already voted")
                            return "already_voted"
                        
                        candidate_name = self.ballot_box.candidates[self.selected_candidate_idx]
                        voter_id = "player"
                        success, message = self.ballot_box.cast_vote(candidate_name, voter_id)
                        
                        if success:
                            player.voted_this_election = True
                            logger.info(f"[VOTING] Player voted for {candidate_name}")
                            self.close()
                            return f"voted:{candidate_name}"
                        else:
                            logger.warning(f"[VOTING] Vote failed: {message}")
                            return "vote_failed"
            
            # Tax payment confirmation mode
            elif self.showing_tax_payment:
                if event.key == pygame.K_ESCAPE:
                    self.showing_tax_payment = False
                    self.services_mode = True
                elif event.key == pygame.K_y:
                    # Confirm payment
                    if player and self.property_tax_system:
                        success, message, amount = self.property_tax_system.pay_back_taxes(player)
                        if success:
                            logger.info(f"[TAX PAYMENT] Player paid {amount}g in back taxes")
                            self.showing_tax_payment = False
                            self.services_mode = True
                            return f"tax_paid:{amount}"
                        else:
                            logger.warning(f"[TAX PAYMENT] Payment failed: {message}")
                            return f"tax_failed:{message}"
                elif event.key == pygame.K_n:
                    # Cancel payment
                    self.showing_tax_payment = False
                    self.services_mode = True
            
            # Services menu mode
            elif self.services_mode:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                elif event.key == pygame.K_UP:
                    self.selected_service_idx = max(0, self.selected_service_idx - 1)
                elif event.key == pygame.K_DOWN:
                    # 2 services: Pay Back Taxes, View Bulletin Board
                    self.selected_service_idx = min(1, self.selected_service_idx + 1)
                elif event.key == pygame.K_RETURN:
                    if self.selected_service_idx == 0:
                        # Pay Back Taxes
                        if player and self.property_tax_system:
                            player_id = id(player)
                            unpaid = self.property_tax_system.unpaid_taxes.get(player_id, 0)
                            if unpaid > 0:
                                self.showing_tax_payment = True
                                self.services_mode = False
                            else:
                                return "no_taxes"
                    elif self.selected_service_idx == 1:
                        # View Bulletin Board
                        self.services_mode = False
                        # Generate bulletin posts now
                        self.bulletin_posts = self.town_hall_manager.generate_bulletin_posts(self.current_town_hall, player)
            
            # Bulletin board mode input handling
            else:
                if event.key == pygame.K_ESCAPE:
                    if self.viewing_detail:
                        self.viewing_detail = False
                    else:
                        # Go back to services menu
                        self.services_mode = True
                
                elif event.key == pygame.K_UP:
                    if not self.viewing_detail:
                        self.selected_post_index = max(0, self.selected_post_index - 1)
                        # Adjust scroll
                        if self.selected_post_index < self.scroll_offset:
                            self.scroll_offset = self.selected_post_index
                
                elif event.key == pygame.K_DOWN:
                    if not self.viewing_detail:
                        self.selected_post_index = min(len(self.bulletin_posts) - 1, self.selected_post_index + 1)
                        # Adjust scroll
                        max_visible = 8
                        if self.selected_post_index >= self.scroll_offset + max_visible:
                            self.scroll_offset = self.selected_post_index - max_visible + 1
                
                elif event.key == pygame.K_RETURN:
                    if not self.viewing_detail:
                        self.viewing_detail = True
    
    def draw(self, screen, player):
        """Draw the town hall UI"""
        if not self.active or not self.current_town_hall:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Draw voting UI if in voting mode
        if self.voting_mode:
            self._draw_voting_ui(screen, player)
        elif self.showing_tax_payment:
            self._draw_tax_payment_confirmation(screen, player)
        elif self.services_mode:
            self._draw_services_menu(screen, player)
        elif self.viewing_detail:
            self._draw_post_detail(screen)
        else:
            self._draw_bulletin_board(screen)
    
    def _draw_bulletin_board(self, screen):
        """Draw the bulletin board list view"""
        board_width = 800
        board_height = 650
        board_x = (self.config.SCREEN_WIDTH - board_width) // 2
        board_y = (self.config.SCREEN_HEIGHT - board_height) // 2
        
        # Board background - wood/notice board style
        board_bg = pygame.Surface((board_width, board_height), pygame.SRCALPHA)
        board_bg.fill((60, 45, 30, 245))
        pygame.draw.rect(board_bg, (120, 90, 60), (0, 0, board_width, board_height), 6)
        screen.blit(board_bg, (board_x, board_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("Town Hall Bulletin Board", True, (240, 220, 180))
        screen.blit(title, (board_x + board_width // 2 - title.get_width() // 2, board_y + 20))
        
        # Subtitle
        subtitle_font = pygame.font.SysFont(None, 24)
        subtitle = subtitle_font.render(f"{self.current_town_hall.town_name}", True, (200, 180, 140))
        screen.blit(subtitle, (board_x + board_width // 2 - subtitle.get_width() // 2, board_y + 70))
        
        # Posts list
        post_y = board_y + 110
        post_font = pygame.font.SysFont(None, 28)
        type_font = pygame.font.SysFont(None, 20)
        
        max_visible = 8
        visible_posts = self.bulletin_posts[self.scroll_offset:self.scroll_offset + max_visible]
        
        for i, post in enumerate(visible_posts):
            actual_index = i + self.scroll_offset
            is_selected = (actual_index == self.selected_post_index)
            
            # Post background - like pinned paper
            post_height = 55
            post_bg_color = (230, 220, 180, 230) if is_selected else (200, 190, 160, 200)
            post_bg = pygame.Surface((board_width - 60, post_height), pygame.SRCALPHA)
            post_bg.fill(post_bg_color)
            
            if is_selected:
                pygame.draw.rect(post_bg, (180, 140, 80), (0, 0, board_width - 60, post_height), 3)
            else:
                pygame.draw.rect(post_bg, (120, 100, 70), (0, 0, board_width - 60, post_height), 1)
            
            screen.blit(post_bg, (board_x + 30, post_y))
            
            # Post type icon/label
            type_colors = {
                "weather": (100, 150, 255),
                "info": (100, 200, 100),
                "quest": (255, 200, 50),
                "bounty": (255, 100, 100),
                "news": (150, 150, 200),
                "wanted": (200, 50, 50),
                "job": (200, 150, 100),
            }
            
            type_color = type_colors.get(post.post_type, (150, 150, 150))
            type_label = post.post_type.upper()
            type_text = type_font.render(type_label, True, type_color)
            screen.blit(type_text, (board_x + 40, post_y + 5))
            
            # Post title
            title_color = (40, 30, 20) if is_selected else (60, 50, 40)
            title_text = post_font.render(post.title[:60], True, title_color)
            screen.blit(title_text, (board_x + 40, post_y + 25))
            
            # Pin/tack visual
            pin_color = (180, 50, 50)
            pygame.draw.circle(screen, pin_color, (board_x + 35, post_y + 10), 4)
            pygame.draw.circle(screen, (150, 40, 40), (board_x + 35, post_y + 10), 4, 1)
            
            post_y += post_height + 8
        
        # Scroll indicator
        if len(self.bulletin_posts) > max_visible:
            indicator_font = pygame.font.SysFont(None, 20)
            indicator = indicator_font.render(f"Showing {self.scroll_offset + 1}-{min(self.scroll_offset + max_visible, len(self.bulletin_posts))} of {len(self.bulletin_posts)}", True, (180, 160, 120))
            screen.blit(indicator, (board_x + board_width // 2 - indicator.get_width() // 2, board_y + board_height - 80))
        
        # Instructions
        instruction_y = board_y + board_height - 50
        instruction_font = pygame.font.SysFont(None, 24)
        instructions = ["↑↓: Select", "ENTER: Read", "ESC: Exit"]
        
        instruction_x = board_x + 40
        for instruction in instructions:
            instr_text = instruction_font.render(instruction, True, (220, 200, 160))
            screen.blit(instr_text, (instruction_x, instruction_y))
            instruction_x += 240
    
    def _draw_post_detail(self, screen):
        """Draw detailed view of selected post"""
        if self.selected_post_index >= len(self.bulletin_posts):
            return
        
        post = self.bulletin_posts[self.selected_post_index]
        
        detail_width = 700
        detail_height = 600
        detail_x = (self.config.SCREEN_WIDTH - detail_width) // 2
        detail_y = (self.config.SCREEN_HEIGHT - detail_height) // 2
        
        # Detail background - paper style
        detail_bg = pygame.Surface((detail_width, detail_height), pygame.SRCALPHA)
        detail_bg.fill((240, 230, 200, 250))
        pygame.draw.rect(detail_bg, (100, 80, 50), (0, 0, detail_width, detail_height), 4)
        screen.blit(detail_bg, (detail_x, detail_y))
        
        # Type badge
        type_colors = {
            "weather": (100, 150, 255),
            "info": (100, 200, 100),
            "quest": (255, 200, 50),
            "bounty": (255, 100, 100),
            "news": (150, 150, 200),
            "wanted": (200, 50, 50),
            "job": (200, 150, 100),
        }
        
        type_color = type_colors.get(post.post_type, (150, 150, 150))
        type_font = pygame.font.SysFont(None, 22)
        type_text = type_font.render(post.post_type.upper(), True, (255, 255, 255))
        
        badge_width = type_text.get_width() + 20
        badge_bg = pygame.Surface((badge_width, 30), pygame.SRCALPHA)
        badge_bg.fill(type_color)
        pygame.draw.rect(badge_bg, (0, 0, 0, 100), (0, 0, badge_width, 30), 2)
        
        screen.blit(badge_bg, (detail_x + 20, detail_y + 15))
        screen.blit(type_text, (detail_x + 30, detail_y + 20))
        
        # Title
        title_font = pygame.font.SysFont(None, 36)
        title = title_font.render(post.title, True, (40, 30, 20))
        screen.blit(title, (detail_x + 30, detail_y + 60))
        
        # Divider
        pygame.draw.line(screen, (100, 80, 50), (detail_x + 30, detail_y + 100), (detail_x + detail_width - 30, detail_y + 100), 2)
        
        # Content
        content_font = pygame.font.SysFont(None, 24)
        content_y = detail_y + 120
        
        for line in post.content.split('\n'):
            line_text = content_font.render(line, True, (50, 40, 30))
            screen.blit(line_text, (detail_x + 40, content_y))
            content_y += 30
        
        # Instructions
        instruction_font = pygame.font.SysFont(None, 22)
        instruction = instruction_font.render("Press ESC to return to board", True, (100, 80, 60))
        screen.blit(instruction, (detail_x + detail_width // 2 - instruction.get_width() // 2, detail_y + detail_height - 40))

    def _draw_voting_ui(self, screen, player):
        """Draw the voting interface during election voting period"""
        # Main voting panel
        panel_width = 700
        panel_height = 600
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        # Panel background
        panel_surf = pygame.Surface((panel_width, panel_height))
        panel_surf.fill((40, 40, 60))
        pygame.draw.rect(panel_surf, (100, 150, 255), (0, 0, panel_width, panel_height), 4)
        screen.blit(panel_surf, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        title = title_font.render("🗳️ BALLOT BOX", True, (255, 255, 100))
        screen.blit(title, (self.config.SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 20))
        
        # Subtitle
        subtitle_font = pygame.font.SysFont(None, 24)
        subtitle = subtitle_font.render("Cast your vote for the next mayor", True, (200, 200, 200))
        screen.blit(subtitle, (self.config.SCREEN_WIDTH // 2 - subtitle.get_width() // 2, panel_y + 75))
        
        # Check voting eligibility
        if player and player.voted_this_election:
            # Already voted message
            message_font = pygame.font.SysFont(None, 32)
            message = message_font.render("✅ You have already voted in this election", True, (100, 255, 100))
            screen.blit(message, (self.config.SCREEN_WIDTH // 2 - message.get_width() // 2, panel_y + 250))
            
            thanks_font = pygame.font.SysFont(None, 24)
            thanks = thanks_font.render("Thank you for your civic participation!", True, (180, 180, 180))
            screen.blit(thanks, (self.config.SCREEN_WIDTH // 2 - thanks.get_width() // 2, panel_y + 300))
            
            instruction_font = pygame.font.SysFont(None, 22)
            instruction = instruction_font.render("Press ESC to exit", True, (150, 150, 150))
            screen.blit(instruction, (self.config.SCREEN_WIDTH // 2 - instruction.get_width() // 2, panel_y + panel_height - 60))
            return
        
        if player and not player.can_vote:
            # Not eligible message
            message_font = pygame.font.SysFont(None, 32)
            message = message_font.render("❌ You are not eligible to vote", True, (255, 100, 100))
            screen.blit(message, (self.config.SCREEN_WIDTH // 2 - message.get_width() // 2, panel_y + 250))
            
            reason_font = pygame.font.SysFont(None, 20)
            reason = reason_font.render("(Voting rights may have been revoked due to crimes)", True, (180, 180, 180))
            screen.blit(reason, (self.config.SCREEN_WIDTH // 2 - reason.get_width() // 2, panel_y + 290))
            
            instruction_font = pygame.font.SysFont(None, 22)
            instruction = instruction_font.render("Press ESC to exit", True, (150, 150, 150))
            screen.blit(instruction, (self.config.SCREEN_WIDTH // 2 - instruction.get_width() // 2, panel_y + panel_height - 60))
            return
        
        # Draw candidate list
        if not self.ballot_box or not self.ballot_box.candidates:
            # No candidates registered
            message_font = pygame.font.SysFont(None, 28)
            message = message_font.render("No candidates registered for this election", True, (255, 200, 100))
            screen.blit(message, (self.config.SCREEN_WIDTH // 2 - message.get_width() // 2, panel_y + 250))
            return
        
        candidate_font = pygame.font.SysFont(None, 28)
        list_y = panel_y + 130
        list_x = panel_x + 80
        
        for i, candidate_name in enumerate(self.ballot_box.candidates):
            is_selected = i == self.selected_candidate_idx
            
            # Background highlight for selected candidate
            if is_selected:
                highlight_surf = pygame.Surface((panel_width - 160, 45))
                highlight_surf.fill((80, 100, 150))
                screen.blit(highlight_surf, (list_x - 10, list_y - 5))
            
            # Candidate name
            if is_selected:
                candidate_color = (255, 255, 100)
                prefix = "►"
            else:
                candidate_color = (220, 220, 220)
                prefix = " "
            
            candidate_text = candidate_font.render(f"{prefix} {candidate_name}", True, candidate_color)
            screen.blit(candidate_text, (list_x + 20, list_y))
            
            list_y += 60
        
        # Vote count info (if available)
        info_y = panel_y + panel_height - 150
        info_font = pygame.font.SysFont(None, 20)
        
        if self.ballot_box:
            total_votes = len(self.ballot_box.ballots)
            info_text = f"Total votes cast so far: {total_votes}"
            info_surf = info_font.render(info_text, True, (180, 180, 200))
            screen.blit(info_surf, (self.config.SCREEN_WIDTH // 2 - info_surf.get_width() // 2, info_y))
        
        # Instructions
        instruction_y = panel_y + panel_height - 100
        instruction_font = pygame.font.SysFont(None, 24)
        
        instructions = [
            "↑↓: Select candidate",
            "ENTER: Cast vote",
            "ESC: Exit"
        ]
        
        instruction_x = panel_x + 60
        for instruction in instructions:
            instr_text = instruction_font.render(instruction, True, (200, 200, 220))
            screen.blit(instr_text, (instruction_x, instruction_y))
            instruction_x += 230
        
        # Warning message
        warning_y = panel_y + panel_height - 60
        warning_font = pygame.font.SysFont(None, 20)
        warning = warning_font.render("⚠️ Your vote is final and cannot be changed", True, (255, 200, 100))
        screen.blit(warning, (self.config.SCREEN_WIDTH // 2 - warning.get_width() // 2, warning_y))

    def _draw_services_menu(self, screen, player):
        """Draw the town hall services menu"""
        # Main panel
        panel_width = 600
        panel_height = 400
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        # Panel background
        panel_surf = pygame.Surface((panel_width, panel_height))
        panel_surf.fill((50, 45, 40))
        pygame.draw.rect(panel_surf, (120, 100, 80), (0, 0, panel_width, panel_height), 4)
        screen.blit(panel_surf, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 42)
        title = title_font.render("🏛️ TOWN HALL SERVICES", True, (240, 220, 180))
        screen.blit(title, (self.config.SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 25))
        
        # Services list
        services = ["Pay Back Taxes", "View Bulletin Board"]
        service_font = pygame.font.SysFont(None, 32)
        
        list_y = panel_y + 110
        list_x = panel_x + 80
        
        for i, service in enumerate(services):
            is_selected = i == self.selected_service_idx
            
            # Background highlight for selected service
            if is_selected:
                highlight_surf = pygame.Surface((panel_width - 160, 50))
                highlight_surf.fill((80, 70, 60))
                screen.blit(highlight_surf, (list_x - 10, list_y - 5))
            
            # Service text with arrow for selected
            if is_selected:
                service_color = (255, 240, 200)
                prefix = "►"
            else:
                service_color = (200, 180, 150)
                prefix = " "
            
            # Add tax debt indicator if viewing Pay Back Taxes
            if i == 0 and player and self.property_tax_system:
                player_id = id(player)
                unpaid = self.property_tax_system.unpaid_taxes.get(player_id, 0)
                if unpaid > 0:
                    service_text = f"{prefix} {service} ({unpaid}g)"
                    service_color = (255, 200, 100) if is_selected else (220, 180, 100)
                else:
                    service_text = f"{prefix} {service}"
            else:
                service_text = f"{prefix} {service}"
            
            text_surf = service_font.render(service_text, True, service_color)
            screen.blit(text_surf, (list_x + 20, list_y))
            
            list_y += 70
        
        # Instructions
        instruction_y = panel_y + panel_height - 70
        instruction_font = pygame.font.SysFont(None, 24)
        
        instructions = [
            "↑↓: Select",
            "ENTER: Confirm",
            "ESC: Exit"
        ]
        
        instruction_x = panel_x + 50
        for instruction in instructions:
            instr_text = instruction_font.render(instruction, True, (180, 160, 140))
            screen.blit(instr_text, (instruction_x, instruction_y))
            instruction_x += 190
    
    def _draw_tax_payment_confirmation(self, screen, player):
        """Draw tax payment confirmation screen"""
        # Main panel
        panel_width = 650
        panel_height = 450
        panel_x = (self.config.SCREEN_WIDTH - panel_width) // 2
        panel_y = (self.config.SCREEN_HEIGHT - panel_height) // 2
        
        # Panel background
        panel_surf = pygame.Surface((panel_width, panel_height))
        panel_surf.fill((50, 40, 40))
        pygame.draw.rect(panel_surf, (200, 100, 100), (0, 0, panel_width, panel_height), 4)
        screen.blit(panel_surf, (panel_x, panel_y))
        
        # Title
        title_font = pygame.font.SysFont(None, 40)
        title = title_font.render("💰 PAY BACK TAXES", True, (255, 200, 100))
        screen.blit(title, (self.config.SCREEN_WIDTH // 2 - title.get_width() // 2, panel_y + 30))
        
        if not player or not self.property_tax_system:
            return
        
        player_id = id(player)
        unpaid_amount = self.property_tax_system.unpaid_taxes.get(player_id, 0)
        
        # Tax debt info
        info_font = pygame.font.SysFont(None, 28)
        info_y = panel_y + 100
        
        info_lines = [
            f"Outstanding Tax Debt: {unpaid_amount}g",
            f"Your Balance: {player.dubloons}g"
        ]
        
        for line in info_lines:
            text_surf = info_font.render(line, True, (220, 220, 220))
            screen.blit(text_surf, (self.config.SCREEN_WIDTH // 2 - text_surf.get_width() // 2, info_y))
            info_y += 40
        
        # Check if can afford
        if player.dubloons >= unpaid_amount:
            # Can afford
            status_y = panel_y + 210
            status_font = pygame.font.SysFont(None, 26)
            status = status_font.render("✅ You have sufficient funds to pay this debt", True, (100, 255, 100))
            screen.blit(status, (self.config.SCREEN_WIDTH // 2 - status.get_width() // 2, status_y))
            
            # Remaining balance
            remaining = player.dubloons - unpaid_amount
            remaining_text = f"Remaining balance after payment: {remaining}g"
            remaining_surf = status_font.render(remaining_text, True, (200, 200, 200))
            screen.blit(remaining_surf, (self.config.SCREEN_WIDTH // 2 - remaining_surf.get_width() // 2, status_y + 35))
        else:
            # Cannot afford
            status_y = panel_y + 210
            status_font = pygame.font.SysFont(None, 26)
            needed = unpaid_amount - player.dubloons
            status = status_font.render(f"❌ Insufficient funds (Need {needed}g more)", True, (255, 100, 100))
            screen.blit(status, (self.config.SCREEN_WIDTH // 2 - status.get_width() // 2, status_y))
            
            warning_text = "You cannot pay this debt yet"
            warning_surf = status_font.render(warning_text, True, (220, 180, 100))
            screen.blit(warning_surf, (self.config.SCREEN_WIDTH // 2 - warning_surf.get_width() // 2, status_y + 35))
        
        # Confirmation prompt
        prompt_y = panel_y + panel_height - 130
        prompt_font = pygame.font.SysFont(None, 30)
        
        if player.dubloons >= unpaid_amount:
            prompt = prompt_font.render("Pay back taxes now?", True, (255, 255, 200))
        else:
            prompt = prompt_font.render("Cannot pay at this time", True, (200, 200, 200))
        
        screen.blit(prompt, (self.config.SCREEN_WIDTH // 2 - prompt.get_width() // 2, prompt_y))
        
        # Instructions
        instruction_y = panel_y + panel_height - 70
        instruction_font = pygame.font.SysFont(None, 24)
        
        if player.dubloons >= unpaid_amount:
            instructions = [
                "Y: Pay now",
                "N: Cancel",
                "ESC: Back"
            ]
        else:
            instructions = [
                "ESC: Back to menu"
            ]
        
        instruction_x = panel_x + (panel_width - 400) // 2
        for instruction in instructions:
            instr_text = instruction_font.render(instruction, True, (180, 180, 180))
            screen.blit(instr_text, (instruction_x, instruction_y))
            instruction_x += 140
