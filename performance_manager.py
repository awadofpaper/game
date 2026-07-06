"""
Performance Management System
Comprehensive performance presets and monitoring
"""

import json
import os
import time
import pygame
from enum import Enum
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

# Try to import psutil for system information
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("psutil not available - system monitoring will be limited")

class PerformancePreset(Enum):
    """Performance preset levels"""
    POTATO = "potato"
    LOW = "low" 
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"
    CUSTOM = "custom"

@dataclass
class PerformanceSettings:
    """Performance configuration settings"""
    # Graphics Settings
    target_fps: int = 60
    vsync: bool = True
    particle_density: float = 1.0
    shadow_quality: str = "medium"  # "off", "low", "medium", "high"
    lighting_quality: str = "medium"  # "off", "low", "medium", "high"
    texture_quality: str = "medium"  # "low", "medium", "high"
    
    # Rendering Settings
    max_visible_entities: int = 100
    max_particles: int = 500
    render_distance: int = 1000
    ui_animation_speed: float = 1.0
    
    # Update Frequencies (lower = better performance)
    ai_update_interval: int = 1  # frames between AI updates
    physics_update_interval: int = 1
    weather_update_interval: int = 5
    
    # Memory Management
    auto_cleanup_interval: float = 30.0  # seconds
    cache_size_limit: int = 50  # MB
    garbage_collection_frequency: int = 300  # frames
    
    # Advanced Settings
    multi_threading: bool = True
    occlusion_culling: bool = True
    frustum_culling: bool = True
    batched_rendering: bool = True

class PerformanceManager:
    """Manages performance settings and monitoring"""
    
    def __init__(self):
        self.settings_file = "performance_settings.json"
        self.current_preset = PerformancePreset.MEDIUM
        
        # Performance presets
        self.presets = {
            PerformancePreset.POTATO: PerformanceSettings(
                target_fps=30,
                vsync=False,
                particle_density=0.2,
                shadow_quality="off",
                lighting_quality="off",
                texture_quality="low",
                max_visible_entities=25,
                max_particles=50,
                render_distance=500,
                ui_animation_speed=0.5,
                ai_update_interval=3,
                physics_update_interval=2,
                weather_update_interval=10,
                auto_cleanup_interval=15.0,
                cache_size_limit=20,
                multi_threading=False,
                occlusion_culling=True,
                frustum_culling=True,
                batched_rendering=True
            ),
            
            PerformancePreset.LOW: PerformanceSettings(
                target_fps=45,
                vsync=False,
                particle_density=0.5,
                shadow_quality="low",
                lighting_quality="low",
                texture_quality="low",
                max_visible_entities=50,
                max_particles=200,
                render_distance=750,
                ui_animation_speed=0.8,
                ai_update_interval=2,
                physics_update_interval=1,
                weather_update_interval=8,
                auto_cleanup_interval=20.0,
                cache_size_limit=30,
                multi_threading=True,
                occlusion_culling=True,
                frustum_culling=True,
                batched_rendering=True
            ),
            
            PerformancePreset.MEDIUM: PerformanceSettings(
                target_fps=60,
                vsync=True,
                particle_density=1.0,
                shadow_quality="medium",
                lighting_quality="medium",
                texture_quality="medium",
                max_visible_entities=100,
                max_particles=500,
                render_distance=1000,
                ui_animation_speed=1.0,
                ai_update_interval=1,
                physics_update_interval=1,
                weather_update_interval=5,
                auto_cleanup_interval=30.0,
                cache_size_limit=50,
                multi_threading=True,
                occlusion_culling=True,
                frustum_culling=True,
                batched_rendering=True
            ),
            
            PerformancePreset.HIGH: PerformanceSettings(
                target_fps=120,
                vsync=False,
                particle_density=1.5,
                shadow_quality="high",
                lighting_quality="high",
                texture_quality="high",
                max_visible_entities=200,
                max_particles=1000,
                render_distance=1500,
                ui_animation_speed=1.2,
                ai_update_interval=1,
                physics_update_interval=1,
                weather_update_interval=3,
                auto_cleanup_interval=45.0,
                cache_size_limit=100,
                multi_threading=True,
                occlusion_culling=True,
                frustum_culling=True,
                batched_rendering=True
            ),
            
            PerformancePreset.ULTRA: PerformanceSettings(
                target_fps=144,
                vsync=False,
                particle_density=2.0,
                shadow_quality="high",
                lighting_quality="high", 
                texture_quality="high",
                max_visible_entities=500,
                max_particles=2000,
                render_distance=2000,
                ui_animation_speed=1.5,
                ai_update_interval=1,
                physics_update_interval=1,
                weather_update_interval=1,
                auto_cleanup_interval=60.0,
                cache_size_limit=200,
                multi_threading=True,
                occlusion_culling=False,  # Disabled for maximum quality
                frustum_culling=False,
                batched_rendering=True
            )
        }
        
        # Current settings (starts with medium preset)
        self.current_settings = self.presets[PerformancePreset.MEDIUM]
        
        # Performance monitoring
        self.fps_history = []
        self.frame_times = []
        self.memory_usage_history = []
        self.last_cleanup_time = time.time()
        self.frame_count = 0
        
        # System info
        self.system_info = self._get_system_info()
        
        # Load saved settings
        self.load_settings()
    
    def _get_system_info(self) -> Dict:
        """Get system hardware information"""
        if not PSUTIL_AVAILABLE:
            import platform as plat
            import sys
            return {
                "cpu_cores": "Unknown",
                "cpu_threads": "Unknown", 
                "total_memory_gb": "Unknown",
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                "platform": plat.system()
            }
        
        try:
            # CPU info
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            # Memory info
            memory = psutil.virtual_memory()
            
            # Basic system info
            return {
                "cpu_cores": cpu_count,
                "cpu_threads": cpu_count_logical,
                "total_memory_gb": round(memory.total / (1024**3), 1),
                "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}",
                "platform": psutil.sys.platform
            }
        except Exception as e:
            import platform as plat
            import sys
            return {
                "cpu_cores": "Unknown",
                "cpu_threads": "Unknown", 
                "total_memory_gb": "Unknown",
                "python_version": "Unknown",
                "platform": "Unknown",
                "error": str(e)
            }
    
    def apply_preset(self, preset: PerformancePreset):
        """Apply a performance preset"""
        if preset in self.presets:
            self.current_preset = preset
            if preset != PerformancePreset.CUSTOM:
                self.current_settings = self.presets[preset]
            self.save_settings()
            return True
        return False
    
    def get_current_settings(self) -> PerformanceSettings:
        """Get current performance settings"""
        return self.current_settings
    
    def update_setting(self, setting_name: str, value):
        """Update a specific setting and switch to custom preset"""
        if hasattr(self.current_settings, setting_name):
            setattr(self.current_settings, setting_name, value)
            self.current_preset = PerformancePreset.CUSTOM
            self.save_settings()
            return True
        return False
    
    def get_recommended_preset(self) -> PerformancePreset:
        """Recommend a preset based on system specs"""
        try:
            memory_gb = self.system_info.get("total_memory_gb", 0)
            cpu_cores = self.system_info.get("cpu_cores", 1)
            
            # Simple heuristic based on available info
            if isinstance(memory_gb, (int, float)):
                if memory_gb >= 16 and cpu_cores >= 8:
                    return PerformancePreset.ULTRA
                elif memory_gb >= 8 and cpu_cores >= 4:
                    return PerformancePreset.HIGH
                elif memory_gb >= 4 and cpu_cores >= 2:
                    return PerformancePreset.MEDIUM
                elif memory_gb >= 2:
                    return PerformancePreset.LOW
                else:
                    return PerformancePreset.POTATO
            else:
                return PerformancePreset.MEDIUM  # Safe default
        except:
            return PerformancePreset.MEDIUM
    
    def update_performance_stats(self, dt: float, fps: float):
        """Update performance monitoring statistics"""
        self.frame_count += 1
        
        # Track FPS
        self.fps_history.append(fps)
        if len(self.fps_history) > 120:  # Keep last 2 seconds at 60fps
            self.fps_history.pop(0)
        
        # Track frame times
        self.frame_times.append(dt * 1000)  # Convert to milliseconds
        if len(self.frame_times) > 120:
            self.frame_times.pop(0)
        
        # Track memory usage periodically
        if self.frame_count % 60 == 0:  # Every second at 60fps
            if PSUTIL_AVAILABLE:
                try:
                    memory = psutil.virtual_memory()
                    self.memory_usage_history.append(memory.percent)
                    if len(self.memory_usage_history) > 300:  # Keep 5 minutes of data
                        self.memory_usage_history.pop(0)
                except:
                    pass
        
        # Auto cleanup if needed
        current_time = time.time()
        if current_time - self.last_cleanup_time >= self.current_settings.auto_cleanup_interval:
            self._trigger_cleanup()
            self.last_cleanup_time = current_time
    
    def track_fps(self, fps: float):
        """Track FPS for performance monitoring"""
        self.fps_history.append(fps)
        if len(self.fps_history) > 300:  # Keep last 5 minutes at 60fps
            self.fps_history.pop(0)
    
    def track_frame_time(self, frame_time: float):
        """Track frame time in seconds"""
        frame_time_ms = frame_time * 1000  # Convert to milliseconds
        self.frame_times.append(frame_time_ms)
        if len(self.frame_times) > 300:  # Keep last 5 minutes
            self.frame_times.pop(0)
    
    def _trigger_cleanup(self):
        """Trigger garbage collection and cleanup"""
        import gc
        collected = gc.collect()
        return collected
    
    def get_performance_stats(self) -> Dict:
        """Get current performance statistics"""
        stats = {
            "current_fps": self.fps_history[-1] if self.fps_history else 0,
            "average_fps": sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0,
            "min_fps": min(self.fps_history) if self.fps_history else 0,
            "max_fps": max(self.fps_history) if self.fps_history else 0,
            "target_fps": self.current_settings.target_fps,
            "frame_time_ms": self.frame_times[-1] if self.frame_times else 0,
            "avg_frame_time_ms": sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0,
        }
        
        # Add memory info if available
        if PSUTIL_AVAILABLE:
            try:
                memory = psutil.virtual_memory()
                stats.update({
                    "memory_percent": memory.percent,
                    "memory_used_gb": round(memory.used / (1024**3), 1),
                    "memory_available_gb": round(memory.available / (1024**3), 1)
                })
            except:
                stats.update({
                    "memory_percent": 0,
                    "memory_used_gb": 0,
                    "memory_available_gb": 0
                })
        else:
            stats.update({
                "memory_percent": 0,
                "memory_used_gb": 0,
                "memory_available_gb": 0
            })
        
        return stats
    
    def get_performance_health(self) -> Tuple[str, str]:
        """Get overall performance health status"""
        if not self.fps_history:
            return "unknown", "No performance data available"
        
        avg_fps = sum(self.fps_history) / len(self.fps_history)
        target_fps = self.current_settings.target_fps
        
        performance_ratio = avg_fps / target_fps if target_fps > 0 else 1
        
        if performance_ratio >= 0.95:
            return "excellent", f"Performance excellent ({avg_fps:.1f}/{target_fps} FPS)"
        elif performance_ratio >= 0.85:
            return "good", f"Performance good ({avg_fps:.1f}/{target_fps} FPS)"
        elif performance_ratio >= 0.70:
            return "fair", f"Performance fair ({avg_fps:.1f}/{target_fps} FPS)"
        elif performance_ratio >= 0.50:
            return "poor", f"Performance poor ({avg_fps:.1f}/{target_fps} FPS)"
        else:
            return "critical", f"Performance critical ({avg_fps:.1f}/{target_fps} FPS)"
    
    def auto_adjust_performance(self):
        """Automatically adjust settings based on current performance"""
        if len(self.fps_history) < 60:  # Need enough data
            return False
        
        avg_fps = sum(self.fps_history[-60:]) / 60  # Last second average
        target_fps = self.current_settings.target_fps
        
        performance_ratio = avg_fps / target_fps if target_fps > 0 else 1
        
        # If performance is poor, try to improve it
        if performance_ratio < 0.7:
            # Reduce particle density
            if self.current_settings.particle_density > 0.2:
                self.current_settings.particle_density *= 0.8
                return True
            
            # Reduce max entities
            if self.current_settings.max_visible_entities > 25:
                self.current_settings.max_visible_entities = int(self.current_settings.max_visible_entities * 0.8)
                return True
            
            # Increase AI update interval
            if self.current_settings.ai_update_interval < 5:
                self.current_settings.ai_update_interval += 1
                return True
        
        # If performance is excellent, we could increase quality
        elif performance_ratio > 1.2 and self.current_preset != PerformancePreset.ULTRA:
            # Increase particle density
            if self.current_settings.particle_density < 2.0:
                self.current_settings.particle_density *= 1.1
                return True
        
        return False
    
    def reset_to_preset(self, preset: PerformancePreset = None):
        """Reset settings to a specific preset or recommended preset"""
        if preset is None:
            preset = self.get_recommended_preset()
        
        self.apply_preset(preset)
    
    def save_settings(self):
        """Save performance settings to file"""
        try:
            settings_data = {
                "current_preset": self.current_preset.value,
                "custom_settings": {
                    "target_fps": self.current_settings.target_fps,
                    "vsync": self.current_settings.vsync,
                    "particle_density": self.current_settings.particle_density,
                    "shadow_quality": self.current_settings.shadow_quality,
                    "lighting_quality": self.current_settings.lighting_quality,
                    "texture_quality": self.current_settings.texture_quality,
                    "max_visible_entities": self.current_settings.max_visible_entities,
                    "max_particles": self.current_settings.max_particles,
                    "render_distance": self.current_settings.render_distance,
                    "ui_animation_speed": self.current_settings.ui_animation_speed,
                    "ai_update_interval": self.current_settings.ai_update_interval,
                    "physics_update_interval": self.current_settings.physics_update_interval,
                    "weather_update_interval": self.current_settings.weather_update_interval,
                    "auto_cleanup_interval": self.current_settings.auto_cleanup_interval,
                    "cache_size_limit": self.current_settings.cache_size_limit,
                    "garbage_collection_frequency": self.current_settings.garbage_collection_frequency,
                    "multi_threading": self.current_settings.multi_threading,
                    "occlusion_culling": self.current_settings.occlusion_culling,
                    "frustum_culling": self.current_settings.frustum_culling,
                    "batched_rendering": self.current_settings.batched_rendering
                }
            }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings_data, f, indent=2)
        except Exception as e:
            print(f"Error saving performance settings: {e}")
    
    def load_settings(self):
        """Load performance settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings_data = json.load(f)
                
                # Load preset
                preset_name = settings_data.get("current_preset", "medium")
                try:
                    self.current_preset = PerformancePreset(preset_name)
                except ValueError:
                    self.current_preset = PerformancePreset.MEDIUM
                
                # Load custom settings if it's a custom preset
                if self.current_preset == PerformancePreset.CUSTOM and "custom_settings" in settings_data:
                    custom = settings_data["custom_settings"]
                    self.current_settings = PerformanceSettings(**custom)
                else:
                    # Use preset settings
                    if self.current_preset in self.presets:
                        self.current_settings = self.presets[self.current_preset]
                        
        except Exception as e:
            print(f"Error loading performance settings: {e}")
            # Use defaults if loading fails

# Global performance manager instance
_performance_manager = None

def get_performance_manager() -> PerformanceManager:
    """Get the global performance manager instance"""
    global _performance_manager
    if _performance_manager is None:
        _performance_manager = PerformanceManager()
    return _performance_manager

# Convenience functions
def get_current_performance_settings() -> PerformanceSettings:
    """Get current performance settings"""
    return get_performance_manager().get_current_settings()

def apply_performance_preset(preset: PerformancePreset) -> bool:
    """Apply a performance preset"""
    return get_performance_manager().apply_preset(preset)

def get_performance_stats() -> Dict:
    """Get current performance statistics"""
    return get_performance_manager().get_performance_stats()

def update_performance_monitoring(dt: float, fps: float):
    """Update performance monitoring (call this each frame)"""
    get_performance_manager().update_performance_stats(dt, fps)