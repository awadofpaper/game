"""
NPC Skill Switching System
Allows gatherer NPCs to change professions with training periods, cooldowns, and skill retention
"""
import random
from logger_config import logger


class SkillSwitchRecord:
    """Records a skill switch event for an NPC"""
    def __init__(self, npc_id, old_profession, new_profession, start_day, training_days):
        self.npc_id = npc_id
        self.old_profession = old_profession
        self.new_profession = new_profession
        self.start_day = start_day
        self.training_days = training_days
        self.complete_day = start_day + training_days
        self.completed = False
        self.old_skill_level = 0  # Stored before switch
        self.new_skill_level = 1  # Starting level in new profession


class NPCSkillSwitchingSystem:
    """Manages profession changes for gatherer NPCs"""
    
    def __init__(self, game_time):
        self.game_time = game_time
        self.active_training = {}  # {npc_id: SkillSwitchRecord}
        self.switch_history = []  # All completed switches
        self.cooldowns = {}  # {npc_id: day_when_cooldown_ends}
        
        # Configuration
        self.base_training_days = 7  # Base training period
        self.cooldown_days = 30  # 30 days before can switch again
        self.skill_retention_percentage = 0.5  # Keep 50% of old skill level
        
        # Tool requirements for each profession
        self.required_tools = {
            'miner': ['bronze_pickaxe', 'iron_pickaxe', 'steel_pickaxe', 'pickaxe'],
            'woodcutter': ['bronze_axe', 'iron_axe', 'steel_axe', 'axe'],
            'fisher': ['fishing_net', 'fishing_rod']
        }
        
        # Profession to skill name mapping
        self.profession_skills = {
            'miner': 'Mining',
            'woodcutter': 'Woodcutting',
            'fisher': 'Fishing'
        }
        
        logger.info("[SKILL SWITCH] NPC skill switching system initialized")
    
    def can_switch_profession(self, npc, new_profession):
        """Check if NPC can switch to new profession"""
        npc_id = id(npc)
        
        # Check if already training
        if npc_id in self.active_training:
            return False, "Already training for new profession"
        
        # Check cooldown
        if npc_id in self.cooldowns:
            cooldown_end = self.cooldowns[npc_id]
            if self.game_time.day_count < cooldown_end:
                days_remaining = cooldown_end - self.game_time.day_count
                return False, f"Must wait {days_remaining} more days before switching"
        
        # Check if switching to same profession
        if npc.gatherer_type == new_profession:
            return False, "Already working in that profession"
        
        # Check if has required tool and money
        tool_check = self.check_tool_requirements(npc, new_profession)
        if not tool_check[0]:
            return False, tool_check[1]
        
        # Check if has enough gold for training (100g cost)
        training_cost = 100
        if npc.dubloons < training_cost:
            return False, f"Need {training_cost}g for training (has {npc.dubloons}g)"
        
        return True, "Can switch profession"
    
    def check_tool_requirements(self, npc, profession):
        """Check if NPC has required tool for profession"""
        required = self.required_tools.get(profession, [])
        
        # Check inventory for any of the required tools
        for tool_name in required:
            if tool_name in npc.inventory and npc.inventory[tool_name] > 0:
                return True, tool_name
        
        # Check if NPC's current tool matches (for starting tool)
        if npc.tool in required:
            return True, npc.tool
        
        return False, f"Need one of: {', '.join(required)}"
    
    def start_profession_switch(self, npc, new_profession):
        """Begin profession switching process"""
        npc_id = id(npc)
        
        # Validate switch
        can_switch, reason = self.can_switch_profession(npc, new_profession)
        if not can_switch:
            return False, reason
        
        # Get old skill level
        old_skill = self.profession_skills.get(npc.gatherer_type, 'Mining')
        old_skill_level = npc.skills_manager.get_level(old_skill)
        
        # Calculate training time (base 7 days, reduced by 1 day per 5 levels in old skill)
        training_days = max(3, self.base_training_days - (old_skill_level // 5))
        
        # Deduct training cost
        training_cost = 100
        npc.dubloons -= training_cost
        
        # Create training record
        record = SkillSwitchRecord(
            npc_id, npc.gatherer_type, new_profession,
            self.game_time.day_count, training_days
        )
        record.old_skill_level = old_skill_level
        
        self.active_training[npc_id] = record
        
        # NPC goes idle during training
        from gatherer_npc import GathererState
        npc.state = GathererState.IDLE
        npc.is_training = True  # Visual indicator flag
        
        logger.info(f"[SKILL SWITCH] {npc.name} started training {npc.gatherer_type} → {new_profession} ({training_days} days)")
        
        return True, f"Training started! Will take {training_days} days"
    
    def update_training(self):
        """Check and complete any finished training periods"""
        completed = []
        
        for npc_id, record in self.active_training.items():
            if not record.completed and self.game_time.day_count >= record.complete_day:
                record.completed = True
                completed.append(npc_id)
        
        return completed
    
    def complete_profession_switch(self, npc):
        """Complete the profession switch for an NPC"""
        npc_id = id(npc)
        
        if npc_id not in self.active_training:
            return False, "No active training"
        
        record = self.active_training[npc_id]
        
        if not record.completed:
            days_remaining = record.complete_day - self.game_time.day_count
            return False, f"Training not complete ({days_remaining} days remaining)"
        
        # Store old skill at reduced level
        old_skill = self.profession_skills.get(record.old_profession, 'Mining')
        old_skill_level = npc.skills_manager.get_level(old_skill)
        retained_level = max(1, int(old_skill_level * self.skill_retention_percentage))
        
        # Set retained skill level
        npc.skills_manager.skills[old_skill].level = retained_level
        npc.skills_manager.skills[old_skill].xp = npc.skills_manager.skills[old_skill].xp_for_next_level(retained_level) // 2
        
        # Change profession
        old_profession = npc.gatherer_type
        npc.gatherer_type = record.new_profession
        
        # Update tool
        npc.tool = self._get_tool_for_profession(npc, record.new_profession)
        
        # Update color
        npc.color = npc._get_type_color()
        
        # Set new skill to level 1
        new_skill = self.profession_skills.get(record.new_profession, 'Mining')
        npc.skills_manager.skills[new_skill].level = 1
        npc.skills_manager.skills[new_skill].xp = 0
        
        # Set cooldown
        self.cooldowns[npc_id] = self.game_time.day_count + self.cooldown_days
        
        # Move to history
        self.switch_history.append(record)
        del self.active_training[npc_id]
        # Clear training flag
        npc.is_training = False
        
        
        logger.info(f"[SKILL SWITCH] {npc.name} completed training: {old_profession} → {record.new_profession}")
        logger.info(f"[SKILL SWITCH] Retained {old_skill} at level {retained_level} (was {old_skill_level})")
        
        return True, f"Now working as {record.new_profession}! Old skill retained at {retained_level}"
    
    def _get_tool_for_profession(self, npc, profession):
        """Get best available tool for profession from NPC inventory"""
        required_tools = self.required_tools.get(profession, [])
        
        # Priority order (best to worst)
        tool_priority = {
            'miner': ['steel_pickaxe', 'iron_pickaxe', 'bronze_pickaxe', 'pickaxe'],
            'woodcutter': ['steel_axe', 'iron_axe', 'bronze_axe', 'axe'],
            'fisher': ['fishing_rod', 'fishing_net']
        }
        
        priority_list = tool_priority.get(profession, required_tools)
        
        # Check inventory in priority order
        for tool_name in priority_list:
            if tool_name in npc.inventory and npc.inventory[tool_name] > 0:
                return tool_name
        
        # Fallback to basic tool
        if profession == 'miner':
            return 'bronze_pickaxe'
        elif profession == 'woodcutter':
            return 'bronze_axe'
        else:
            return 'fishing_net'
    
    def cancel_training(self, npc):
        """Cancel active training (loses half the training cost)"""
        npc_id = id(npc)
        
        if npc_id not in self.active_training:
            return False, "No active training to cancel"
        
        record = self.active_training[npc_id]
        
        # Refund 50% of training cost
        refund = 50
        npc.dubloons += refund
        
        # Remove from active training
        del self.active_training[npc_id]
        
        # Clear training flag
        npc.is_training = False
        
        logger.info(f"[SKILL SWITCH] {npc.name} cancelled training {record.old_profession} → {record.new_profession}")
        
        return True, f"Training cancelled. Refunded {refund}g"
    
    def get_training_info(self, npc):
        """Get training info for an NPC"""
        npc_id = id(npc)
        
        if npc_id not in self.active_training:
            return None
        
        record = self.active_training[npc_id]
        days_remaining = max(0, record.complete_day - self.game_time.day_count)
        progress = 1.0 - (days_remaining / record.training_days)
        
        return {
            'old_profession': record.old_profession,
            'new_profession': record.new_profession,
            'days_remaining': days_remaining,
            'days_total': record.training_days,
            'progress': progress,
            'completed': record.completed
        }
    
    def get_cooldown_info(self, npc):
        """Get cooldown info for an NPC"""
        npc_id = id(npc)
        
        if npc_id not in self.cooldowns:
            return None
        
        cooldown_end = self.cooldowns[npc_id]
        if self.game_time.day_count >= cooldown_end:
            # Cooldown expired, remove it
            del self.cooldowns[npc_id]
            return None
        
        days_remaining = cooldown_end - self.game_time.day_count
        return {
            'days_remaining': days_remaining,
            'cooldown_total': self.cooldown_days
        }
    
    def auto_suggest_profession_switch(self, npc, market_manager=None):
        """Suggest profession switch based on market conditions or random chance"""
        npc_id = id(npc)
        
        # Don't suggest if on cooldown or training
        if npc_id in self.cooldowns or npc_id in self.active_training:
            return None
        
        # Only suggest if NPC has been in profession for a while (check skill level)
        current_skill = self.profession_skills.get(npc.gatherer_type, 'Mining')
        current_level = npc.skills_manager.get_level(current_skill)
        
        if current_level < 10:
            return None  # Too new to profession
        
        # 5% chance per day to consider switching
        if random.random() > 0.05:
            return None
        
        # Choose random new profession
        professions = ['miner', 'woodcutter', 'fisher']
        available = [p for p in professions if p != npc.gatherer_type]
        
        if not available:
            return None
        
        suggested_profession = random.choice(available)
        
        # Check if can afford and has tools
        can_switch, reason = self.can_switch_profession(npc, suggested_profession)
        
        if can_switch:
            logger.info(f"[SKILL SWITCH] {npc.name} considering switch to {suggested_profession}")
            return suggested_profession
        
        return None
    
    def auto_execute_switch(self, npc, suggested_profession):
        """Automatically execute a suggested profession switch"""
        # 30% chance NPC accepts the suggestion
        if random.random() > 0.3:
            return False, "NPC declined profession change"
        
        success, message = self.start_profession_switch(npc, suggested_profession)
        return success, message
    
    def get_stats(self):
        """Get system statistics"""
        return {
            'active_training': len(self.active_training),
            'active_cooldowns': len(self.cooldowns),
            'total_switches': len(self.switch_history),
            'miners_training': len([r for r in self.active_training.values() if r.new_profession == 'miner']),
            'woodcutters_training': len([r for r in self.active_training.values() if r.new_profession == 'woodcutter']),
            'fishers_training': len([r for r in self.active_training.values() if r.new_profession == 'fisher'])
        }
