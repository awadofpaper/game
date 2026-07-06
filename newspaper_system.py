"""
Newspaper System - Daily news publication tracking world events
Includes: Market prices, obituaries, mayor news, family events, world happenings
"""

import random
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class NewsArticle:
    """Represents a single news article"""
    
    def __init__(self, section: str, headline: str, content: str, date: int):
        self.section = section  # 'obituary', 'politics', 'society', 'market', 'world'
        self.headline = headline
        self.content = content
        self.date = date  # Game day when published
        self.importance = 1  # 1-5, affects placement

    def to_dict(self) -> dict:
        return {
            'section': self.section,
            'headline': self.headline,
            'content': self.content,
            'date': self.date,
            'importance': self.importance
        }


class Newspaper:
    """A single edition of the newspaper"""
    
    def __init__(self, date: int, edition_number: int):
        self.date = date
        self.edition_number = edition_number
        self.articles = []
        self.weather_report = ""
        self.price = 10  # Cost to purchase
        
        # Sections
        self.obituaries = []
        self.political_news = []
        self.society_news = []
        self.market_reports = []
        self.world_events = []
    
    def add_article(self, article: NewsArticle):
        """Add an article to the appropriate section"""
        self.articles.append(article)
        
        # Sort into sections
        if article.section == 'obituary':
            self.obituaries.append(article)
        elif article.section == 'politics':
            self.political_news.append(article)
        elif article.section == 'society':
            self.society_news.append(article)
        elif article.section == 'market':
            self.market_reports.append(article)
        elif article.section == 'world':
            self.world_events.append(article)
    
    def get_section_count(self, section: str) -> int:
        """Get number of articles in a section"""
        section_map = {
            'obituary': self.obituaries,
            'politics': self.political_news,
            'society': self.society_news,
            'market': self.market_reports,
            'world': self.world_events
        }
        return len(section_map.get(section, []))
    
    def to_dict(self) -> dict:
        return {
            'date': self.date,
            'edition_number': self.edition_number,
            'weather_report': self.weather_report,
            'articles': [a.to_dict() for a in self.articles],
            'price': self.price
        }


class NewspaperGenerator:
    """Generates daily newspaper content from game events"""
    
    def __init__(self):
        self.recent_deaths = []  # Track for obituaries
        self.recent_marriages = []  # Track for society section
        self.recent_births = []  # Track for society section
        self.recent_adoptions = []  # Track for society section
        self.mayor_actions = []  # Track for political section
        self.price_changes = []  # Track for market section
        
        # Newspaper names (randomized)
        self.newspaper_names = [
            "The Merchant's Digest",
            "Trading Post Times",
            "The Kingdom Chronicle",
            "Economic Herald",
            "The Daily Ledger"
        ]
        self.current_name = random.choice(self.newspaper_names)
    
    def record_death(self, npc_name: str, npc_type: str, town: str, cause: str, age: int = None):
        """Record a death for obituary section"""
        self.recent_deaths.append({
            'name': npc_name,
            'type': npc_type,
            'town': town,
            'cause': cause,
            'age': age or random.randint(25, 75),
            'recorded_time': datetime.now()
        })
        logger.info(f"[NEWSPAPER] Recorded death: {npc_name} ({cause})")
    
    def record_marriage(self, spouse1: str, spouse2: str, town: str):
        """Record a marriage for society section"""
        self.recent_marriages.append({
            'spouse1': spouse1,
            'spouse2': spouse2,
            'town': town,
            'recorded_time': datetime.now()
        })
    
    def record_birth(self, parent_names: List[str], child_name: str, town: str):
        """Record a birth for society section"""
        self.recent_births.append({
            'parents': parent_names,
            'child': child_name,
            'town': town,
            'recorded_time': datetime.now()
        })
    
    def record_adoption(self, adopter: str, child: str, town: str):
        """Record an adoption for society section"""
        self.recent_adoptions.append({
            'adopter': adopter,
            'child': child,
            'town': town,
            'recorded_time': datetime.now()
        })
    
    def record_mayor_action(self, town: str, action: str, approval_rating: float):
        """Record mayor action for political section"""
        self.mayor_actions.append({
            'town': town,
            'action': action,
            'approval': approval_rating,
            'recorded_time': datetime.now()
        })
    
    def record_price_change(self, commodity: str, town: str, old_price: float, new_price: float, reason: str):
        """Record significant price change for market section"""
        percent_change = ((new_price - old_price) / old_price) * 100
        if abs(percent_change) >= 20:  # Only record significant changes
            self.price_changes.append({
                'commodity': commodity,
                'town': town,
                'old_price': old_price,
                'new_price': new_price,
                'percent_change': percent_change,
                'reason': reason,
                'recorded_time': datetime.now()
            })
    
    def generate_daily_newspaper(self, game_time, market_manager=None, election_system=None, 
                                 family_system=None, weather_system=None, disease_manager=None) -> Newspaper:
        """Generate a newspaper for the current day"""
        current_day = game_time.day_count
        edition_number = current_day
        
        newspaper = Newspaper(current_day, edition_number)
        
        # Generate weather report
        if weather_system:
            newspaper.weather_report = self._generate_weather_report(weather_system)
        
        # Generate obituaries (from recent deaths)
        self._generate_obituaries(newspaper, current_day)
        
        # Generate political news (mayors, elections, policies)
        if election_system:
            self._generate_political_news(newspaper, election_system, current_day)
        
        # Generate society news (marriages, births, adoptions)
        if family_system:
            self._generate_society_news(newspaper, family_system, current_day)
        
        # Generate market reports (prices, arbitrage opportunities)
        if market_manager:
            self._generate_market_reports(newspaper, market_manager, current_day)
        
        # Generate disease outbreak news and health warnings
        if disease_manager:
            self._generate_disease_outbreak_news(newspaper, disease_manager, current_day)
        
        # Generate world events (random flavor)
        self._generate_world_events(newspaper, current_day)
        
        # Clear old recorded events (keep them for 1 day only)
        self._clear_old_events()
        
        logger.info(f"[NEWSPAPER] Generated edition #{edition_number} with {len(newspaper.articles)} articles")
        return newspaper
    
    def _generate_weather_report(self, weather_system) -> str:
        """Generate weather forecast section"""
        current = weather_system.current_weather if hasattr(weather_system, 'current_weather') else 'clear'
        
        weather_descriptions = {
            'clear': 'Clear skies expected. Perfect conditions for travel and trade.',
            'rain': 'Rainy conditions ahead. Travelers advised to prepare accordingly.',
            'storm': 'Severe storms forecasted. Sea travel highly discouraged.',
            'snow': 'Snowfall expected. Mountain passes may become treacherous.',
            'fog': 'Heavy fog rolling in. Visibility will be greatly reduced.'
        }
        
        return weather_descriptions.get(current, 'Weather conditions normal.')
    
    def _generate_obituaries(self, newspaper: Newspaper, current_day: int):
        """Generate obituary articles from recent deaths"""
        for death in self.recent_deaths[-10:]:  # Last 10 deaths
            cause_descriptions = {
                'combat_death': f"fell in combat near {death['town']}",
                'old_age': f"passed peacefully in {death['town']}",
                'disease': f"succumbed to illness in {death['town']}",
                'accident': f"died in an unfortunate accident near {death['town']}",
                'murder': f"was murdered in {death['town']}"
            }
            
            cause_text = cause_descriptions.get(death['cause'], f"died in {death['town']}")
            
            headline = f"{death['name']}, {death['type'].title()}"
            
            # Generate obituary content
            content = f"{death['name']}, a {death['type']} of {death['town']}, {cause_text}. "
            content += f"Age {death['age']}. "
            
            # Add flavor based on NPC type
            if death['type'] in ['miner', 'woodcutter', 'fisher', 'forager']:
                content += f"Known for their dedication to {death['type']} work, they will be missed by the community."
            elif 'merchant' in death['type']:
                content += "A respected trader whose deals were known throughout the region."
            elif death['type'] == 'guard':
                content += "Served honorably protecting the town from threats."
            else:
                content += "They lived a full life and contributed to the prosperity of the realm."
            
            article = NewsArticle('obituary', headline, content, current_day)
            article.importance = 2
            newspaper.add_article(article)
    
    def _generate_political_news(self, newspaper: Newspaper, election_system, current_day: int):
        """Generate political news articles"""
        # Mayor approval ratings
        if hasattr(election_system, 'get_all_mayors'):
            mayors = election_system.get_all_mayors()
            
            # Pick most newsworthy mayors (highest/lowest approval)
            mayor_list = list(mayors.items())
            random.shuffle(mayor_list)
            
            for town_name, mayor_info in mayor_list[:3]:  # Top 3 newsworthy
                if not mayor_info:
                    continue
                
                approval = mayor_info.get('approval_rating', 50)
                mayor_name = mayor_info.get('name', 'Unknown')
                
                # Generate headline based on approval
                if approval >= 80:
                    headline = f"{mayor_name}'s Policies Praised in {town_name}"
                    content = f"Mayor {mayor_name} of {town_name} continues to enjoy strong public support "
                    content += f"with an approval rating of {approval:.1f}%. Citizens cite effective governance "
                    content += "and economic prosperity as key factors."
                elif approval <= 30:
                    headline = f"Residents Question {mayor_name}'s Leadership"
                    content = f"Mayor {mayor_name} faces growing criticism in {town_name} "
                    content += f"as approval rating drops to {approval:.1f}%. "
                    content += "Some citizens are calling for new leadership in the next election."
                else:
                    headline = f"{town_name} Mayor Reports Mixed Results"
                    content = f"Mayor {mayor_name} maintains a moderate approval rating of {approval:.1f}%. "
                    content += "Supporters and critics remain divided on recent policy decisions."
                
                article = NewsArticle('politics', headline, content, current_day)
                article.importance = 3
                newspaper.add_article(article)
        
        # Election news
        if hasattr(election_system, 'state'):
            if election_system.state == 'campaigning':
                headline = "Election Campaign Heats Up"
                content = "Candidates across the realm are actively campaigning for public support. "
                content += "Citizens are encouraged to meet with candidates and make their voices heard."
                article = NewsArticle('politics', headline, content, current_day)
                article.importance = 5
                newspaper.add_article(article)
            elif election_system.state == 'voting':
                headline = "Polls Open for Elections"
                content = "Voting is now underway in towns across the kingdom. "
                content += "All eligible citizens should visit their local town hall to cast their ballots."
                article = NewsArticle('politics', headline, content, current_day)
                article.importance = 5
                newspaper.add_article(article)
        
        # Recent mayor actions
        for action in self.mayor_actions[-5:]:
            headline = f"Mayor Takes Action in {action['town']}"
            content = f"{action['action']} "
            content += f"Current approval rating: {action['approval']:.1f}%."
            
            article = NewsArticle('politics', headline, content, current_day)
            article.importance = 3
            newspaper.add_article(article)
    
    def _generate_society_news(self, newspaper: Newspaper, family_system, current_day: int):
        """Generate society news (marriages, births, adoptions)"""
        # Marriages
        for marriage in self.recent_marriages:
            headline = f"{marriage['spouse1']} Weds {marriage['spouse2']}"
            content = f"{marriage['spouse1']} and {marriage['spouse2']} were married in {marriage['town']}. "
            content += "Friends and family gathered to celebrate the joyous occasion. "
            content += "The couple plans to establish their household in the town."
            
            article = NewsArticle('society', headline, content, current_day)
            article.importance = 2
            newspaper.add_article(article)
        
        # Births
        for birth in self.recent_births:
            parent_names = " and ".join(birth['parents'])
            headline = f"New Arrival in {birth['town']}"
            content = f"{parent_names} are proud to announce the birth of {birth['child']}. "
            content += f"The family resides in {birth['town']} and report mother and child are doing well."
            
            article = NewsArticle('society', headline, content, current_day)
            article.importance = 2
            newspaper.add_article(article)
        
        # Adoptions
        for adoption in self.recent_adoptions:
            headline = f"{adoption['adopter']} Welcomes {adoption['child']}"
            content = f"{adoption['adopter']} has adopted {adoption['child']} in {adoption['town']}. "
            content += "The adoption was finalized this week, and the family is settling in together."
            
            article = NewsArticle('society', headline, content, current_day)
            article.importance = 2
            newspaper.add_article(article)
    
    def _generate_market_reports(self, newspaper: Newspaper, market_manager, current_day: int):
        """Generate market report articles"""
        # Get tradeable commodities
        from market_system import TRADEABLE_COMMODITIES
        
        if not TRADEABLE_COMMODITIES:
            return
        
        # Sample some commodities for reporting
        commodity_ids = list(TRADEABLE_COMMODITIES.keys())
        sample_size = min(5, len(commodity_ids))
        sampled = random.sample(commodity_ids, sample_size)
        
        # Generate price comparison article
        headline = "Market Price Report"
        content = "Current commodity prices across major trading hubs:\n\n"
        
        for commodity_id in sampled:
            commodity = TRADEABLE_COMMODITIES[commodity_id]
            prices = market_manager.get_all_town_prices(commodity_id)
            
            if not prices:
                continue
            
            # Find highest and lowest prices
            highest_town = max(prices, key=prices.get)
            lowest_town = min(prices, key=prices.get)
            highest_price = prices[highest_town]
            lowest_price = prices[lowest_town]
            
            content += f"• {commodity.name}: "
            content += f"{lowest_price:.0f}g ({lowest_town}) to {highest_price:.0f}g ({highest_town})\n"
        
        article = NewsArticle('market', headline, content, current_day)
        article.importance = 4
        newspaper.add_article(article)
        
        # Arbitrage opportunities (requires level 60+)
        arbitrage_headline = "💰 TRADER'S TIP: Arbitrage Opportunities"
        arbitrage_content = "Savvy merchants report profitable trading routes:\n\n"
        
        opportunities_found = 0
        for commodity_id in sampled:
            arb = market_manager.find_arbitrage_opportunities(commodity_id)
            if arb:
                commodity = TRADEABLE_COMMODITIES[commodity_id]
                arbitrage_content += f"• {commodity.name}: "
                arbitrage_content += f"Buy in {arb['buy_town']} ({arb['buy_price']:.0f}g), "
                arbitrage_content += f"sell in {arb['sell_town']} ({arb['sell_price']:.0f}g) "
                arbitrage_content += f"for {arb['profit_percent']:.0f}% profit!\n"
                opportunities_found += 1
        
        if opportunities_found > 0:
            article = NewsArticle('market', arbitrage_headline, arbitrage_content, current_day)
            article.importance = 5
            newspaper.add_article(article)
        
        # Significant price changes
        for change in self.price_changes:
            direction = "surged" if change['percent_change'] > 0 else "dropped"
            headline = f"{change['commodity']} Prices {direction.title()} in {change['town']}"
            content = f"The price of {change['commodity']} has {direction} by {abs(change['percent_change']):.0f}% "
            content += f"in {change['town']}, now trading at {change['new_price']:.0f}g per unit. "
            
            if change['reason']:
                content += f"Market analysts attribute this to {change['reason']}."
            
            article = NewsArticle('market', headline, content, current_day)
            article.importance = 4
            newspaper.add_article(article)
    
    def _generate_world_events(self, newspaper: Newspaper, current_day: int):
        """Generate random world event flavor articles"""
        events = [
            ("Traveling Merchant Caravan Spotted", 
             "A large merchant caravan was seen traveling between towns. Guards report increased trade activity on major routes."),
            ("Dungeons Growing More Dangerous",
             "Adventurers report increased enemy activity in nearby dungeons. Citizens are advised to exercise caution when traveling."),
            ("Fishing Season in Full Swing",
             "Fishermen report excellent catches this week. Local markets expect abundant fish supplies."),
            ("Mining Operations Expand",
             "New ore deposits have been discovered near mountain towns. Mining operations are ramping up production."),
            ("Blacksmiths Report Material Shortage",
             "Local blacksmiths say they're struggling to keep up with demand for equipment repairs and new orders."),
            ("Inn Keeper Association Meets",
             "Inn keepers from across the realm gathered to discuss hospitality standards and pricing policies."),
            ("Festival Planning Underway",
             "Town organizers are preparing for the annual harvest festival. Expect celebrations in coming weeks."),
            ("Wilderness Dangers Increasing",
             "Rangers warn that hostile creatures are becoming more aggressive. Travel in groups when possible."),
        ]
        
        # Selection random events (1-2 per edition)
        num_events = random.randint(1, 2)
        selected_events = random.sample(events, min(num_events, len(events)))
        
        for headline, content in selected_events:
            article = NewsArticle('world', headline, content, current_day)
            article.importance = 1
            newspaper.add_article(article)
    
    def _clear_old_events(self):
        """Clear recorded events older than 1 day"""
        # We keep them for 1 day to ensure they appear in the newspaper
        # In a real implementation, you'd check timestamps
        # For now, we'll just limit list sizes
        self.recent_deaths = self.recent_deaths[-20:]
        self.recent_marriages = self.recent_marriages[-10:]
        self.recent_births = self.recent_births[-10:]
        self.recent_adoptions = self.recent_adoptions[-10:]
        self.mayor_actions = self.mayor_actions[-10:]
        self.price_changes = self.price_changes[-10:]
    
    def _generate_disease_outbreak_news(self, newspaper: Newspaper, disease_manager, current_day: int):
        """Generate disease outbreak and health warning articles"""
        if not disease_manager:
            return
        
        # Check for active outbreaks
        for town_name, diseases in disease_manager.town_outbreak_status.items():
            for disease_id, outbreak_data in diseases.items():
                if not outbreak_data.get('active', False):
                    continue
                
                # Get disease info
                from disease_system import DISEASE_DEFINITIONS
                disease = DISEASE_DEFINITIONS.get(disease_id)
                if not disease:
                    continue
                
                # Generate outbreak headline (with rumors/false alarms 20% of the time)
                is_rumor = random.random() < 0.20
                
                if disease_id == "plague":
                    if is_rumor:
                        headline = f"Unconfirmed Reports of Plague Near {town_name}"
                        content = f"Unverified rumors suggest possible plague cases near {town_name}. "
                        content += "Local officials have not confirmed the reports. "
                        content += "Citizens are advised to remain calm but vigilant."
                    else:
                        headline = f"⚠️ PLAGUE OUTBREAK IN {town_name.upper()}!"
                        content = f"Health officials confirm active plague outbreak in {town_name}. "
                        content += f"{outbreak_data.get('infected_count', 0)} cases reported. "
                        content += f"{outbreak_data.get('death_count', 0)} deaths confirmed. "
                        content += "\n\nCitizens are strongly advised to AVOID TRAVEL to this region. "
                        content += "Wear protective gear if entry is necessary. "
                        content += "The town has been placed under quarantine. "
                        content += "Those showing symptoms should seek immediate isolation."
                    importance = 5  # Highest importance
                
                elif disease_id in ["common_cold", "flu"]:
                    if is_rumor:
                        headline = f"Cold Season May Be Starting in {town_name}"
                        content = f"Some residents report mild cold symptoms in {town_name}. "
                        content += "Weather conditions favor seasonal illness. Stock up on herbs and rest."
                    else:
                        headline = f"{disease.name} Cases Rising in {town_name}"
                        content = f"Health officials report increased {disease.name.lower()} cases in {town_name}. "
                        content += f"{outbreak_data.get('infected_count', 0)} cases confirmed. "
                        content += "Citizens advised to rest, stay warm, and seek treatment if symptoms worsen. "
                        content += "Special foods and cure potions available at local shops."
                    importance = 3
                
                else:  # Other diseases
                    if is_rumor:
                        headline = f"Possible Health Concerns in {town_name}"
                        content = f"Unconfirmed reports of unusual illness in {town_name}. "
                        content += "Authorities investigating."
                    else:
                        headline = f"{disease.name} Outbreak in {town_name}"
                        content = f"{disease.name} cases confirmed in {town_name}. "
                        content += f"{outbreak_data.get('infected_count', 0)} infected. "
                        content += "Seek medical attention if symptoms develop."
                    importance = 4
                
                article = NewsArticle('world', headline, content, current_day)
                article.importance = importance
                newspaper.add_article(article)
        
        # Seasonal disease warnings (not rumors, always accurate)
        if current_day % 30 == 0:  # Monthly health tips
            season_check = (current_day // 90) % 4  # 0=spring, 1=summer, 2=fall, 3=winter
            
            if season_check in [2, 3]:  # Fall/Winter - cold/flu season
                headline = "Health Advisory: Cold and Flu Season Approaching"
                content = "As temperatures drop, health officials warn of increased cold and flu risk. "
                content += "Citizens advised to stock up on herbs, cure potions, and warm clothing. "
                content += "Maintain good hygiene and avoid crowded areas if feeling ill. "
                content += "Rest at inns can speed recovery from mild illnesses."
                
                article = NewsArticle('world', headline, content, current_day)
                article.importance = 3
                newspaper.add_article(article)
        
        # Survivor stories (plague survivors)
        if len(disease_manager.plague_survivors) > 0 and random.random() < 0.30:
            headline = "Plague Survivors Share Their Stories"
            content = f"{len(disease_manager.plague_survivors)} individuals have survived the plague so far. "
            content += "Survivors report that protective gear, quarantine measures, and strong constitution "
            content += "were key to their survival. Medical experts note survivors may have natural resistance. "
            content += "Children of survivors may inherit increased resistance to future outbreaks."
            
            article = NewsArticle('world', headline, content, current_day)
            article.importance = 4
            newspaper.add_article(article)
        
        # Quarantine status
        for town_name, is_quarantined in disease_manager.quarantine_zones.items():
            if is_quarantined:
                headline = f"{town_name} Under Quarantine"
                content = f"{town_name} remains under strict quarantine due to disease outbreak. "
                content += "Entry and exit restricted. Guards enforcing quarantine protocols. "
                content += "Essential supplies being delivered under supervision. "
                content += "Quarantine will be lifted once outbreak is contained."
                
                article = NewsArticle('world', headline, content, current_day)
                article.importance = 5
                newspaper.add_article(article)
        
        # Refugee news
        stats = disease_manager.get_infection_stats()
        if stats['active_outbreaks'] > 0:
            headline = "Refugees Fleeing Outbreak Zones"
            content = f"Citizens are evacuating plague-affected regions seeking safety elsewhere. "
            content += "Towns receiving refugees report increased population and resource strain. "
            content += "Humanitarian efforts underway to provide shelter and aid. "
            content += "Refugees remember those who helped them escape."
            
            article = NewsArticle('world', headline, content, current_day)
            article.importance = 4
            newspaper.add_article(article)


class NewspaperDistribution:
    """Manages newspaper availability and sales"""
    
    def __init__(self):
        self.current_edition = None
        self.archive = []  # Past editions
        self.max_archive_size = 30  # Keep 30 days of back issues
        self.daily_price = 10  # Base price
        
        # Track who has purchased today's paper
        self.subscribers = []  # NPCs who auto-buy
        self.sold_to_today = set()  # Track sales
    
    def publish_edition(self, newspaper: Newspaper):
        """Publish a new edition"""
        # Archive old edition
        if self.current_edition:
            self.archive.append(self.current_edition)
            if len(self.archive) > self.max_archive_size:
                self.archive.pop(0)
        
        self.current_edition = newspaper
        self.sold_to_today.clear()
        logger.info(f"[NEWSPAPER] Published edition #{newspaper.edition_number}")
    
    def purchase_newspaper(self, player, edition: Newspaper = None) -> Tuple[bool, str]:
        """Player purchases a newspaper"""
        target_edition = edition or self.current_edition
        
        if not target_edition:
            return False, "No newspaper available today."
        
        # Check if already purchased
        player_id = id(player)
        if player_id in self.sold_to_today and edition is None:
            return False, "You already have today's edition."
        
        # Check if player can afford it
        price = target_edition.price
        if player.dubloons < price:
            return False, f"Newspaper costs {price}g. You need {price - player.dubloons}g more."
        
        # Complete purchase
        player.dubloons -= price
        self.sold_to_today.add(player_id)
        
        # Add to player inventory as readable item
        if hasattr(player, 'inventory'):
            newspaper_item = f"newspaper_day_{target_edition.date}"
            player.inventory[newspaper_item] = player.inventory.get(newspaper_item, 0) + 1
        
        logger.info(f"[NEWSPAPER] Player purchased edition #{target_edition.edition_number} for {price}g")
        return True, f"Purchased newspaper for {price}g! Press N to read."
    
    def get_available_editions(self) -> List[Newspaper]:
        """Get list of all available editions (current + archive)"""
        editions = []
        if self.current_edition:
            editions.append(self.current_edition)
        editions.extend(self.archive)
        return editions
