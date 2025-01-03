import pygame
import json

class GameError(Exception):
    def __init__(self, message, error_type="general"):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)

class GameState:
    def __init__(self):
        self.state = "login"  # login, register, menu, game, pause, game_over, game_won
        self.current_user = {
            'username': None,
            'email': None,
            'high_score': 0,
            'total_games': 0,
            'play_time': 0,
            'achievements': []
        }
        self.score = 0
        self.level = 1
        self.lives = 3
        self.paused = False
        self.previous_state = None
        self.error_message = None
        self.error_timer = 0
        
    def change_state(self, new_state):
        try:
            self.previous_state = self.state
            self.state = new_state
            self.error_message = None
            self.error_timer = 0
        except Exception as e:
            self.set_error(f"Durum değiştirme hatası: {str(e)}")
            
    def return_to_previous(self):
        if self.previous_state:
            temp = self.state
            self.state = self.previous_state
            self.previous_state = temp
            
    def is_logged_in(self):
        return self.current_user is not None and self.current_user.get('username') is not None
        
    def login(self, user_data):
        try:
            if user_data and 'username' in user_data:
                self.current_user = {
                    'username': user_data.get('username'),
                    'email': user_data.get('email'),
                    'high_score': user_data.get('high_score', 0),
                    'total_games': user_data.get('total_games', 0),
                    'play_time': user_data.get('play_time', 0),
                    'achievements': user_data.get('achievements', [])
                }
                self.state = "menu"
                self.error_message = None
                self.error_timer = 0
                return True
            return False
        except Exception as e:
            self.set_error(f"Giriş hatası: {str(e)}")
            return False
        
    def logout(self):
        try:
            self.current_user = {
                'username': None,
                'email': None,
                'high_score': 0,
                'total_games': 0,
                'play_time': 0,
                'achievements': []
            }
            self.state = "login"
            self.score = 0
            self.level = 1
            self.error_message = None
            self.error_timer = 0
        except Exception as e:
            self.set_error(f"Çıkış hatası: {str(e)}")
            
    def set_error(self, message):
        self.error_message = message
        self.error_timer = pygame.time.get_ticks() + 3000  # 3 saniye göster
        
    def update_error(self):
        if self.error_message and pygame.time.get_ticks() > self.error_timer:
            self.error_message = None
            self.error_timer = 0
        
    def reset_game(self):
        self.score = 0
        self.level = 1
        self.lives = 3
        self.paused = False
        
class GameObjects:
    def __init__(self, screen_width, screen_height):
        # Top özellikleri
        self.ball_size = int(0.02 * screen_width)
        self.ball = pygame.Rect(
            screen_width // 2,
            screen_height // 2,
            self.ball_size,
            self.ball_size
        )
        self.ball_speed = [5, 5]
        self.balls = [self.ball]  # Çoklu top için
        
        # Raket özellikleri
        self.paddle_width = int(0.02 * screen_width)
        self.paddle_height = int(0.14 * screen_height)
        self.player_paddle = pygame.Rect(
            screen_width - self.paddle_width * 2,
            screen_height // 2 - self.paddle_height // 2,
            self.paddle_width,
            self.paddle_height
        )
        self.paddle_speed = 0
        
        # Güç-up'lar
        self.power_ups = []
        self.active_effects = {}
        
        # Engeller
        self.obstacles = []
        
    def reset(self):
        self.ball.center = (self.screen_width // 2, self.screen_height // 2)
        self.ball_speed = [5, 5]
        self.balls = [self.ball]
        self.power_ups.clear()
        self.active_effects.clear()
        self.obstacles.clear() 