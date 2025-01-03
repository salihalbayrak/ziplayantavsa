import pygame
import random
import math
import os
from game_objects import Ball

class PowerUpManager:
    def __init__(self):
        self.power_ups = []
        self.active_effects = {}
        self.fall_speed = 3
        self.extra_balls = []
        self.game_won = False
        self.game_lost = False
        
        # Joker ikonları ve sesleri
        self.powerup_assets = {
            "big_paddle": {
                "icon": "Assests/joker/buyuk.png",
                "sound": "Assests/sound/raket_büyüme.mp3"
            },
            "small_ball": {
                "icon": "Assests/joker/kucuktop.png", 
                "sound": "Assests/sound/küçük_top.mp3"
            },
            "multi_ball": {
                "icon": "Assests/joker/cogalantop.png",
                "sound": "Assests/sound/çoktu_top.mp3"
            },
            "laser": {
                "icon": "Assests/joker/lazer.png",
                "sound": "Assests/sound/lazer_atışı.mp3"
            },
            "sticky": {
                "icon": "Assests/joker/yapısgan.png",
                "sound": "Assests/sound/yapışma sesi.mp3"
            },
            "shield": {
                "icon": "Assests/joker/kalkan.png",
                "sound": "Assests/sound/kalkan.mp3"
            }
        }
        
        # Power-up türleri ve özellikleri
        self.power_up_types = {
            "big_paddle": {
                "color": (46, 204, 113),
                "duration": 10000,
                "icon": "↔",
                "description": "Büyük Raket"
            },
            "small_ball": {
                "color": (241, 196, 15),
                "duration": 8000,
                "icon": "○",
                "description": "Küçük Top"
            },
            "multi_ball": {
                "color": (155, 89, 182),
                "duration": 15000,
                "icon": "⚈",
                "description": "Çoklu Top"
            },
            "laser": {
                "color": (231, 76, 60),
                "duration": 12000,
                "icon": "↯",
                "description": "Lazer"
            },
            "sticky": {
                "color": (52, 152, 219),
                "duration": 10000,
                "icon": "≡",
                "description": "Yapışkan Raket"
            },
            "shield": {
                "color": (230, 126, 34),
                "duration": 8000,
                "icon": "⚡",
                "description": "Kalkan"
            }
        }
        
    def spawn_powerup(self, x, y):
        power_up_type = random.choice(list(self.power_up_types.keys()))
        
        # İkon yolunu al
        icon_path = self.powerup_assets[power_up_type]["icon"] if power_up_type in self.powerup_assets else None
        
        # İkonu yükle ve boyutlandır
        icon = None
        if icon_path and os.path.exists(icon_path):
            icon_img = pygame.image.load(icon_path)
            icon = pygame.transform.scale(icon_img, (30, 30))  # Joker boyutu 30x30
        
        power_up = {
            "rect": pygame.Rect(x, y, 30, 30),
            "type": power_up_type,
            "color": self.power_up_types[power_up_type]["color"],
            "creation_time": pygame.time.get_ticks(),
            "icon": icon
        }
        self.power_ups.append(power_up)
        
    def update(self, platform, ball):
        current_time = pygame.time.get_ticks()
        
        # Power-up'ları güncelle
        for power_up in self.power_ups[:]:
            power_up["rect"].y += self.fall_speed
            
            # Platform ile çarpışma kontrolü
            if power_up["rect"].colliderect(platform.rect):
                self.activate_power_up(power_up["type"], platform, ball)
                self.power_ups.remove(power_up)
            
            # Ekrandan çıktı mı kontrolü
            elif power_up["rect"].top > platform.screen_height:
                self.power_ups.remove(power_up)
                
        # Aktif efektleri güncelle
        for power_type in list(self.active_effects.keys()):
            if current_time > self.active_effects[power_type]["end_time"]:
                self.deactivate_power_up(power_type, platform, ball)
                
    def activate_power_up(self, power_type, platform, ball):
        current_time = pygame.time.get_ticks()
        duration = self.power_up_types[power_type]["duration"]
        
        # Ses çal
        if power_type in self.powerup_assets:
            s_path = self.powerup_assets[power_type].get("sound", None)
            if s_path and os.path.exists(s_path):
                try:
                    sound_fx = pygame.mixer.Sound(s_path)
                    sound_fx.set_volume(0.5)
                    sound_fx.play()
                except:
                    print(f"Ses dosyası yüklenemedi: {s_path}")
        
        # Önceki aynı türdeki efekti kaldır
        if power_type in self.active_effects:
            self.deactivate_power_up(power_type, platform, ball)
            
        # Yeni efekti uygula
        if power_type == "big_paddle":
            # Platform 3x büyür
            platform.width = platform.original_width * 2
            platform.rect.width = platform.width
            if platform.image:
                # Eğer yapışkan platform aktifse, yapışkan platform görselini büyüt
                if platform.sticky and platform.sticky_image:
                    platform.image = pygame.transform.scale(platform.sticky_image.copy(), 
                                                         (platform.width, platform.height))
                else:
                    platform.image = pygame.transform.scale(platform.original_image.copy(), 
                                                         (platform.width, platform.height))
                
        elif power_type == "small_ball":
            # Top küçülür
            ball.radius *= 0.5
            ball.rect.width = ball.radius * 2
            ball.rect.height = ball.radius * 2
            
        elif power_type == "multi_ball":
            # 3 top oluştur
            if not hasattr(self, 'extra_balls'):
                self.extra_balls = []
            
            # Mevcut topları temizle
            self.extra_balls.clear()
            
            # İki yeni top ekle
            for _ in range(2):  # Ana topla beraber 3 top olacak
                new_ball = Ball(ball.screen_width, ball.screen_height)
                new_ball.radius = ball.radius
                new_ball.speed = ball.speed
                new_ball.x = ball.x
                new_ball.y = ball.y
                new_ball.dx = ball.dx
                new_ball.dy = ball.dy
                new_ball.active = True
                new_ball.original_radius = ball.original_radius
                
                # Rastgele açılarla fırlat
                angle = random.uniform(-3*math.pi/4, -math.pi/4)
                new_ball.dx = math.cos(angle) * new_ball.speed
                new_ball.dy = math.sin(angle) * new_ball.speed
                
                self.extra_balls.append(new_ball)
                
        elif power_type == "laser":
            # Lazer özelliği aktif
            platform.has_laser = True
            platform.laser_damage = 1  # Tek vuruşluk hasar
            
        elif power_type == "sticky":
            # Yapışkan platform
            platform.sticky = True
            if platform.sticky_image:
                # Eğer büyük platform aktifse, yapışkan platform görselini büyük boyutta kullan
                if "big_paddle" in self.active_effects:
                    platform.image = pygame.transform.scale(platform.sticky_image.copy(), 
                                                         (platform.width, platform.height))
                else:
                    platform.image = platform.sticky_image.copy()
                
        elif power_type == "shield":
            # Kalkan tüm zemini kaplar
            platform.has_shield = True
            platform.shield_height = 10  # Kalkan yüksekliği
            platform.shield_rect = pygame.Rect(0, platform.screen_height - 20, 
                                            platform.screen_width, platform.shield_height)
            
        self.active_effects[power_type] = {
            "end_time": current_time + duration,
            "start_time": current_time
        }
        
    def deactivate_power_up(self, power_type, platform, ball):
        if power_type == "big_paddle":
            platform.width = platform.original_width
            platform.rect.width = platform.width
            if platform.image:
                # Eğer yapışkan platform hala aktifse, normal boyutta yapışkan görsel kullan
                if platform.sticky and platform.sticky_image:
                    platform.image = platform.sticky_image.copy()
                else:
                    platform.image = platform.original_image.copy()
                
        elif power_type == "small_ball":
            ball.radius = ball.original_radius
            ball.rect.width = ball.radius * 2
            ball.rect.height = ball.radius * 2
            
        elif power_type == "multi_ball":
            # Rastgele bir topu seç ve diğerlerini kaldır
            if hasattr(self, 'extra_balls') and len(self.extra_balls) > 0:
                surviving_ball = random.choice(self.extra_balls)
                self.extra_balls = [surviving_ball]
                
        elif power_type == "laser":
            platform.has_laser = False
            platform.laser_damage = 0
            platform.lasers.clear()
            
        elif power_type == "sticky":
            platform.sticky = False
            if platform.original_image:
                # Eğer büyük platform aktifse, normal görseli büyük boyutta kullan
                if "big_paddle" in self.active_effects:
                    platform.image = pygame.transform.scale(platform.original_image.copy(), 
                                                         (platform.width, platform.height))
                else:
                    platform.image = platform.original_image.copy()
                
        elif power_type == "shield":
            platform.has_shield = False
            platform.shield_rect = None
            
        if power_type in self.active_effects:
            del self.active_effects[power_type]
            
    def draw(self, screen):
        # Power-up'ları çiz
        for power_up in self.power_ups:
            if "icon" in power_up and power_up["icon"]:
                screen.blit(power_up["icon"], (power_up["rect"].x, power_up["rect"].y))
            else:
                pygame.draw.rect(screen, power_up["color"], power_up["rect"], border_radius=5)
                font = pygame.font.Font(None, 24)
                icon = font.render(self.power_up_types[power_up["type"]]["icon"], True, (255, 255, 255))
                icon_rect = icon.get_rect(center=power_up["rect"].center)
                screen.blit(icon, icon_rect)
            
        # Aktif efektleri göster
        y_offset = 50
        font = pygame.font.Font(None, 24)
        current_time = pygame.time.get_ticks()
        
        for power_type, effect_data in self.active_effects.items():
            remaining_time = (effect_data["end_time"] - current_time) / 1000
            power_info = self.power_up_types[power_type]
            
            text = f"{power_info['description']}: {remaining_time:.1f}s"
            text_surface = font.render(text, True, power_info["color"])
            screen.blit(text_surface, (10, y_offset))
            
            progress = (effect_data["end_time"] - current_time) / power_info["duration"]
            bar_width = 100
            bar_height = 5
            pygame.draw.rect(screen, (100, 100, 100), (120, y_offset + 8, bar_width, bar_height))
            pygame.draw.rect(screen, power_info["color"], 
                           (120, y_offset + 8, int(bar_width * progress), bar_height))
            
            y_offset += 30
            
        # Ekstra topları çiz
        if hasattr(self, 'extra_balls'):
            for extra_ball in self.extra_balls:
                if extra_ball.active:
                    extra_ball.move()  # Topları hareket ettir
                    extra_ball.draw(screen)  # Topları çiz