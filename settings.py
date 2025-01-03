import json
import os
import pygame

class Settings:
    def __init__(self):
        self.settings_file = "settings.json"
        # Tema renkleri
        self.theme_colors = {
            "classic": {
                "button": (52, 152, 219),  # Mavi
                "button_hover": (41, 128, 185),
                "active": (46, 204, 113)  # Yeşil
            },
            "desert": {
                "button": (230, 126, 34),  # Turuncu
                "button_hover": (211, 84, 0),
                "active": (243, 156, 18)  # Sarı
            },
            "ice": {
                "button": (142, 68, 173),  # Mor
                "button_hover": (125, 60, 152),
                "active": (155, 89, 182)  # Açık Mor
            }
        }
        
        self.default_settings = {
            "sound": {
                "master_volume": 0.8,
                "music_volume": 0.7,
                "effects_volume": 0.8,
                "mute": False
            },
            "graphics": {
                "theme": "classic",
                "button_color": self.theme_colors["classic"]["button"],
                "button_hover_color": self.theme_colors["classic"]["button_hover"],
                "active_color": self.theme_colors["classic"]["active"],
                "particle_effects": True,
                "screen_shake": True
            },
            "controls": {
                "mouse_sensitivity": 1.0,
                "keyboard_enabled": True,
                "mouse_enabled": True,
                "key_bindings": {
                    "left": pygame.K_LEFT,
                    "right": pygame.K_RIGHT,
                    "pause": pygame.K_ESCAPE,
                    "launch": pygame.K_SPACE
                }
            },
            "gameplay": {
                "difficulty": "normal",
                "ball_speed": 1.0,
                "platform_size": 1.0,
                "power_up_frequency": 1.0
            }
        }
        self.settings = self.load_settings()
        
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                # Eksik ayarları varsayılanlarla tamamla
                return self.merge_settings(self.default_settings, loaded_settings)
            return self.default_settings.copy()
        except Exception as e:
            print(f"Ayarlar yüklenirken hata: {e}")
            return self.default_settings.copy()
    
    def merge_settings(self, default, loaded):
        """Yüklenen ayarları varsayılan ayarlarla birleştirir"""
        merged = default.copy()
        for key, value in loaded.items():
            if key in merged:
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = self.merge_settings(merged[key], value)
                else:
                    merged[key] = value
        return merged
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata: {e}")
            return False
    
    def get_setting(self, category, setting):
        """Belirli bir ayarı getirir"""
        try:
            return self.settings[category][setting]
        except KeyError:
            return self.default_settings[category][setting]
    
    def set_setting(self, category, setting, value):
        """Belirli bir ayarı günceller"""
        try:
            self.settings[category][setting] = value
            return True
        except KeyError:
            return False
    
    def reset_to_default(self, category=None):
        """Ayarları varsayılana döndürür"""
        if category:
            if category in self.settings:
                self.settings[category] = self.default_settings[category].copy()
        else:
            self.settings = self.default_settings.copy()
        return self.save_settings()
    
    def apply_sound_settings(self):
        """Ses ayarlarını uygular"""
        try:
            master = self.settings["sound"]["master_volume"]
            music_volume = self.settings["sound"]["music_volume"] * master
            effects_volume = self.settings["sound"]["effects_volume"] * master
            
            if not self.settings["sound"]["mute"]:
                # Müzik ses seviyesini ayarla
                if pygame.mixer.get_init():  # Mixer başlatılmış mı kontrol et
                    # Müzik sesini ayarla
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.set_volume(music_volume)
                    
                    # Efekt seslerini ayarla
                    for i in range(pygame.mixer.get_num_channels()):
                        channel = pygame.mixer.Channel(i)
                        if channel.get_busy():
                            channel.set_volume(effects_volume)
            else:
                if pygame.mixer.get_init():
                    pygame.mixer.music.set_volume(0)
                    for i in range(pygame.mixer.get_num_channels()):
                        channel = pygame.mixer.Channel(i)
                        if channel.get_busy():
                            channel.set_volume(0)
            
            return True
        except Exception as e:
            print(f"Ses ayarları uygulanırken hata: {e}")
            return False
    
    def apply_graphics_settings(self):
        """Grafik ayarlarını uygular"""
        # Tema ve renk ayarlarını uygula
        return self.settings["graphics"]
    
    def apply_control_settings(self):
        """Kontrol ayarlarını uygular"""
        return self.settings["controls"]
    
    def apply_gameplay_settings(self):
        """Oynanış ayarlarını uygular"""
        return self.settings["gameplay"]
    
    def apply_theme(self, theme_name):
        """Tema renklerini uygular"""
        if theme_name in self.theme_colors:
            theme = self.theme_colors[theme_name]
            self.settings["graphics"]["button_color"] = theme["button"]
            self.settings["graphics"]["button_hover_color"] = theme["button_hover"]
            self.settings["graphics"]["active_color"] = theme["active"]
            self.settings["graphics"]["theme"] = theme_name
            return True
        return False 