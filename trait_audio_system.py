"""
Racial Trait Audio System
Handles sound effects for trait activations and events
"""

import pygame
import os
import logging

logger = logging.getLogger(__name__)


class TraitAudioSystem:
    """Manages sound effects for racial traits"""
    
    def __init__(self):
        """Initialize the trait audio system"""
        self.enabled = True
        self.volume = 0.5
        self.sounds = {}
        self.last_played = {}  # Track last play time to prevent spam
        self.cooldown = 0.5  # 0.5 second cooldown between same sounds
        
        # Initialize pygame mixer if not already done
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                logger.info("Initialized pygame mixer for trait audio")
        except Exception as e:
            logger.warning(f"Failed to initialize pygame mixer: {e}")
            self.enabled = False
            return
        
        # Generate procedural sounds (since we don't have audio files)
        self._generate_trait_sounds()
    
    def _generate_trait_sounds(self):
        """Generate simple procedural sound effects"""
        try:
            import numpy as np
            
            sample_rate = 22050
            
            # Orc Rage - Deep aggressive roar/hit
            def generate_rage_sound():
                duration = 0.3
                samples = int(sample_rate * duration)
                t = np.linspace(0, duration, samples)
                
                # Low frequency sweep with noise
                freq_start = 80
                freq_end = 40
                freq = np.linspace(freq_start, freq_end, samples)
                signal = np.sin(2 * np.pi * freq * t)
                
                # Add harmonics
                signal += 0.3 * np.sin(4 * np.pi * freq * t)
                
                # Add noise for aggression
                noise = np.random.normal(0, 0.2, samples)
                signal = signal + noise
                
                # Envelope
                envelope = np.exp(-3 * t)
                signal = signal * envelope
                
                # Normalize and convert to 16-bit
                signal = np.clip(signal, -1, 1)
                signal = (signal * 32767).astype(np.int16)
                
                # Convert to stereo
                stereo = np.column_stack((signal, signal))
                return pygame.sndarray.make_sound(stereo)
            
            # Elf Mana - Ethereal chime
            def generate_mana_sound():
                duration = 0.4
                samples = int(sample_rate * duration)
                t = np.linspace(0, duration, samples)
                
                # High frequency bells
                signal = 0.5 * np.sin(2 * np.pi * 880 * t)  # A5
                signal += 0.3 * np.sin(2 * np.pi * 1100 * t)  # C#6
                signal += 0.2 * np.sin(2 * np.pi * 1320 * t)  # E6
                
                # Soft envelope
                envelope = np.exp(-4 * t)
                signal = signal * envelope
                
                # Normalize
                signal = np.clip(signal, -1, 1)
                signal = (signal * 32767 * 0.6).astype(np.int16)
                
                stereo = np.column_stack((signal, signal))
                return pygame.sndarray.make_sound(stereo)
            
            # Dwarf Stone - Heavy metallic clang
            def generate_stone_sound():
                duration = 0.35
                samples = int(sample_rate * duration)
                t = np.linspace(0, duration, samples)
                
                # Low metallic frequencies
                signal = 0.6 * np.sin(2 * np.pi * 200 * t)
                signal += 0.3 * np.sin(2 * np.pi * 400 * t)
                signal += 0.1 * np.sin(2 * np.pi * 600 * t)
                
                # Sharp attack
                attack = np.minimum(t * 100, 1)
                decay = np.exp(-5 * t)
                envelope = attack * decay
                signal = signal * envelope
                
                # Add metallic noise
                noise = np.random.normal(0, 0.1, samples)
                signal = signal + noise
                
                signal = np.clip(signal, -1, 1)
                signal = (signal * 32767 * 0.7).astype(np.int16)
                
                stereo = np.column_stack((signal, signal))
                return pygame.sndarray.make_sound(stereo)
            
            # Halfling Luck - Cheerful sparkle
            def generate_luck_sound():
                duration = 0.3
                samples = int(sample_rate * duration)
                t = np.linspace(0, duration, samples)
                
                # Ascending notes
                freqs = [523, 659, 784]  # C, E, G
                signal = np.zeros(samples)
                
                for i, freq in enumerate(freqs):
                    start = i * samples // 3
                    end = (i + 1) * samples // 3
                    t_section = t[start:end] - t[start]
                    signal[start:end] = 0.5 * np.sin(2 * np.pi * freq * t_section) * np.exp(-8 * t_section)
                
                signal = np.clip(signal, -1, 1)
                signal = (signal * 32767 * 0.5).astype(np.int16)
                
                stereo = np.column_stack((signal, signal))
                return pygame.sndarray.make_sound(stereo)
            
            # Tiefling Fire - Crackling fire whoosh
            def generate_fire_sound():
                duration = 0.4
                samples = int(sample_rate * duration)
                t = np.linspace(0, duration, samples)
                
                # White noise filtered for fire crackle
                noise = np.random.normal(0, 0.3, samples)
                
                # Low frequency rumble
                rumble = 0.4 * np.sin(2 * np.pi * 60 * t)
                
                signal = noise + rumble
                
                # Whoosh envelope
                envelope = np.exp(-3 * t) * (1 + 0.5 * np.sin(2 * np.pi * 5 * t))
                signal = signal * envelope
                
                signal = np.clip(signal, -1, 1)
                signal = (signal * 32767 * 0.6).astype(np.int16)
                
                stereo = np.column_stack((signal, signal))
                return pygame.sndarray.make_sound(stereo)
            
            # Human - Positive achievement chime
            def generate_human_sound():
                duration = 0.35
                samples = int(sample_rate * duration)
                t = np.linspace(0, duration, samples)
                
                # Harmonious chord
                signal = 0.4 * np.sin(2 * np.pi * 440 * t)  # A
                signal += 0.3 * np.sin(2 * np.pi * 554 * t)  # C#
                signal += 0.2 * np.sin(2 * np.pi * 659 * t)  # E
                
                envelope = np.exp(-4 * t)
                signal = signal * envelope
                
                signal = np.clip(signal, -1, 1)
                signal = (signal * 32767 * 0.5).astype(np.int16)
                
                stereo = np.column_stack((signal, signal))
                return pygame.sndarray.make_sound(stereo)
            
            # Generate all sounds
            self.sounds['orc_rage_activate'] = generate_rage_sound()
            self.sounds['orc_rage_deactivate'] = generate_stone_sound()  # Reuse stone sound
            self.sounds['elf_mana'] = generate_mana_sound()
            self.sounds['dwarf_stone'] = generate_stone_sound()
            self.sounds['halfling_luck'] = generate_luck_sound()
            self.sounds['tiefling_fire'] = generate_fire_sound()
            self.sounds['human_bonus'] = generate_human_sound()
            
            logger.info(f"Generated {len(self.sounds)} procedural trait sounds")
            
        except ImportError:
            logger.warning("NumPy not available - trait sounds disabled")
            self.enabled = False
        except Exception as e:
            logger.warning(f"Failed to generate trait sounds: {e}")
            self.enabled = False
    
    def play_sound(self, sound_name):
        """Play a trait sound effect"""
        if not self.enabled or sound_name not in self.sounds:
            return
        
        # Check cooldown
        current_time = pygame.time.get_ticks() / 1000.0
        if sound_name in self.last_played:
            if current_time - self.last_played[sound_name] < self.cooldown:
                return  # Skip if too soon
        
        try:
            sound = self.sounds[sound_name]
            sound.set_volume(self.volume)
            sound.play()
            self.last_played[sound_name] = current_time
        except Exception as e:
            logger.warning(f"Failed to play sound {sound_name}: {e}")
    
    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
    
    def set_enabled(self, enabled):
        """Enable or disable trait sounds"""
        self.enabled = enabled
    
    # Convenient methods for specific trait sounds
    def play_orc_rage_activate(self):
        """Play Orc rage activation sound"""
        self.play_sound('orc_rage_activate')
    
    def play_orc_rage_deactivate(self):
        """Play Orc rage deactivation sound"""
        self.play_sound('orc_rage_deactivate')
    
    def play_halfling_dodge(self):
        """Play Halfling dodge sound"""
        self.play_sound('halfling_luck')
    
    def play_halfling_double_loot(self):
        """Play Halfling double loot sound"""
        self.play_sound('halfling_luck')
    
    def play_dwarf_repair(self):
        """Play Dwarf free repair sound"""
        self.play_sound('dwarf_stone')
    
    def play_human_bonus(self):
        """Play Human bonus activation sound"""
        self.play_sound('human_bonus')
