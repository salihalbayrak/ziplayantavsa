import pygame
import random

class PowerUp:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.type = type
        self.active = False
        self.duration = 10  # saniye
        self.start_time = 0
        
        # Güç-up türleri ve etkileri
        self.effects = {
            "big_paddle": 1.5,    # Raket boyutu çarpanı
            "small_ball": 0.7,    # Top boyutu çarpanı
            "slow_motion": 0.5,   # Hız çarpanı
            "multi_ball": 3,      # Top sayısı
            "shield": True        # Kalkan durumu
        }
        
    def apply_effect(self, game_objects):
        self.active = True
        self.start_time = pygame.time.get_ticks()
        
        if self.type == "big_paddle":
            game_objects["paddle"].height *= self.effects["big_paddle"]
        elif self.type == "small_ball":
            game_objects["ball"].width *= self.effects["small_ball"]
            game_objects["ball"].height *= self.effects["small_ball"]
        elif self.type == "slow_motion":
            game_objects["ball_speed"] *= self.effects["slow_motion"]
        elif self.type == "multi_ball":
            # Yeni toplar ekle
            for _ in range(self.effects["multi_ball"] - 1):
                new_ball = game_objects["ball"].copy()
                game_objects["balls"].append(new_ball)
        elif self.type == "shield":
            game_objects["shield_active"] = self.effects["shield"]
            
    def remove_effect(self, game_objects):
        self.active = False
        
        if self.type == "big_paddle":
            game_objects["paddle"].height /= self.effects["big_paddle"]
        elif self.type == "small_ball":
            game_objects["ball"].width /= self.effects["small_ball"]
            game_objects["ball"].height /= self.effects["small_ball"]
        elif self.type == "slow_motion":
            game_objects["ball_speed"] /= self.effects["slow_motion"]
        elif self.type == "multi_ball":
            game_objects["balls"] = [game_objects["balls"][0]]
        elif self.type == "shield":
            game_objects["shield_active"] = False

class DifficultyManager:
    def __init__(self):
        self.difficulties = {
            "easy": {
                "ball_speed": 5,
                "paddle_size": 1.2,
                "score_multiplier": 1,
                "powerup_frequency": 0.1,
                "obstacle_count": 0
            },
            "normal": {
                "ball_speed": 7,
                "paddle_size": 1.0,
                "score_multiplier": 1.5,
                "powerup_frequency": 0.05,
                "obstacle_count": 3
            },
            "hard": {
                "ball_speed": 10,
                "paddle_size": 0.8,
                "score_multiplier": 2,
                "powerup_frequency": 0.03,
                "obstacle_count": 5
            }
        }
        
    def apply_difficulty(self, difficulty, game_objects):
        settings = self.difficulties[difficulty]
        
        # Top hızını ayarla
        game_objects["ball_speed"] = settings["ball_speed"]
        
        # Raket boyutunu ayarla
        original_height = game_objects["paddle"].height
        game_objects["paddle"].height = original_height * settings["paddle_size"]
        
        # Engelleri ekle
        game_objects["obstacles"] = []
        for _ in range(settings["obstacle_count"]):
            obstacle = pygame.Rect(
                random.randint(100, 500),
                random.randint(100, 350),
                30, 30
            )
            game_objects["obstacles"].append(obstacle)
            
        return settings["score_multiplier"] 