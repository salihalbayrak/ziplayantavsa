import pygame
from game_objects import Platform, Ball, BlockManager
from power_up_system import PowerUpManager
import os
import math

class GameLogic:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.combo = 0
        self.last_hit_time = 0
        self.combo_timeout = 2000  # 2 saniye
        
        # Ses efektleri
        self.sounds = {}
        self.load_sounds()
        
    def load_sounds(self):
        """Ses dosyalarını yükle"""
        sound_files = {
            "hit": "Assests/topsesi.mp3",
            "score": "Assests/skorses.mp3"
        }
        
        for name, path in sound_files.items():
            try:
                if os.path.exists(path):
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(0.5)  # Ses seviyesini ayarla
                    self.sounds[name] = sound
            except:
                print(f"Ses dosyası yüklenemedi: {path}")
        
    def play_sound(self, sound_name):
        """Ses çal"""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                print(f"Ses çalınamadı: {sound_name}")
                
    def check_collisions(self, ball, platform, block_manager, power_up_manager, game_state):
        # Can kaybı kontrolü
        if ball.y + ball.radius > self.screen_height:
            game_state.lives -= 1
            if game_state.lives <= 0:
                game_state.change_state("game_over")
                if "gameover" in self.sounds:
                    self.sounds["gameover"].play()
            else:
                ball.reset()
                platform.reset()
                if "hit" in self.sounds:
                    self.sounds["hit"].play()
            return game_state.score

        # Ekstra toplar için can kaybı kontrolü
        if hasattr(power_up_manager, 'extra_balls'):
            for extra_ball in power_up_manager.extra_balls[:]:
                if extra_ball.y + extra_ball.radius > self.screen_height:
                    power_up_manager.extra_balls.remove(extra_ball)

        # Duvar çarpışmaları
        if ball.x - ball.radius <= 0:
            ball.x = ball.radius
            ball.dx = abs(ball.dx)
            self.play_sound("hit")
        elif ball.x + ball.radius >= self.screen_width:
            ball.x = self.screen_width - ball.radius
            ball.dx = -abs(ball.dx)
            self.play_sound("hit")
            
        if ball.y - ball.radius <= 0:
            ball.y = ball.radius
            ball.dy = abs(ball.dy)
            self.play_sound("hit")
            
        # Platform çarpışması
        platform_rect = platform.rect.inflate(-10, -5)  # Daha hassas çarpışma için
        ball_rect = pygame.Rect(ball.x - ball.radius, ball.y - ball.radius,
                              ball.radius * 2, ball.radius * 2)
                              
        if platform_rect.colliderect(ball_rect):
            # Çarpışma noktasını hesapla
            hit_point = (ball.x - platform.rect.x) / platform.rect.width
            
            # Gelen açıyı hesapla
            incoming_angle = math.atan2(ball.dy, ball.dx)
            
            # Yeni açıyı hesapla (platform pozisyonuna göre)
            bounce_angle = math.pi * (0.25 + 0.5 * hit_point)  # 45° ile 135° arası
            
            # Hızı koru
            speed = math.sqrt(ball.dx * ball.dx + ball.dy * ball.dy)
            
            # Yapışkan platform kontrolü
            if platform.sticky:
                ball.attach_to_platform(platform)
            else:
                # Yeni hız vektörlerini hesapla
                ball.dx = speed * math.cos(bounce_angle)
                ball.dy = -abs(speed * math.sin(bounce_angle))  # Yukarı yönlendir
                
                # Topun platformun içine girmesini önle
                ball.y = platform.rect.y - ball.radius
            
            self.play_sound("hit")
            
        # Çoğalan top güncellemesi
        if hasattr(power_up_manager, 'extra_balls'):
            for extra_ball in power_up_manager.extra_balls:
                # Duvar çarpışmaları
                if extra_ball.x - extra_ball.radius <= 0:
                    extra_ball.x = extra_ball.radius
                    extra_ball.dx = abs(extra_ball.dx)
                elif extra_ball.x + extra_ball.radius >= self.screen_width:
                    extra_ball.x = self.screen_width - extra_ball.radius
                    extra_ball.dx = -abs(extra_ball.dx)
                    
                if extra_ball.y - extra_ball.radius <= 0:
                    extra_ball.y = extra_ball.radius
                    extra_ball.dy = abs(extra_ball.dy)
                
                # Platform çarpışması
                extra_ball_rect = pygame.Rect(extra_ball.x - extra_ball.radius, 
                                           extra_ball.y - extra_ball.radius,
                                           extra_ball.radius * 2, extra_ball.radius * 2)
                
                if platform_rect.colliderect(extra_ball_rect):
                    # Çarpışma noktasını hesapla
                    hit_point = (extra_ball.x - platform.rect.x) / platform.rect.width
                    
                    # Gelen açıyı hesapla
                    incoming_angle = math.atan2(extra_ball.dy, extra_ball.dx)
                    
                    # Yeni açıyı hesapla
                    bounce_angle = math.pi * (0.25 + 0.5 * hit_point)
                    
                    # Hızı koru
                    speed = math.sqrt(extra_ball.dx * extra_ball.dx + extra_ball.dy * extra_ball.dy)
                    
                    if platform.sticky:
                        extra_ball.attach_to_platform(platform)
                    else:
                        extra_ball.dx = speed * math.cos(bounce_angle)
                        extra_ball.dy = -abs(speed * math.sin(bounce_angle))
                        extra_ball.y = platform.rect.y - extra_ball.radius
                        
                # Blok çarpışmaları
                for block in block_manager.blocks[:]:
                    if extra_ball_rect.colliderect(block.rect):
                        # Çarpışma yönünü belirle
                        dx = extra_ball.x - block.rect.centerx
                        dy = extra_ball.y - block.rect.centery
                        
                        if abs(dx/block.rect.width) > abs(dy/block.rect.height):
                            extra_ball.dx = abs(extra_ball.dx) if dx > 0 else -abs(extra_ball.dx)
                        else:
                            extra_ball.dy = abs(extra_ball.dy) if dy > 0 else -abs(extra_ball.dy)
                        
                        if block.hit():
                            if block.contains_powerup:
                                power_up_manager.spawn_powerup(
                                    block.rect.centerx,
                                    block.rect.centery
                                )
                            block_manager.blocks.remove(block)
                            game_state.score += block.points
                            self.play_sound("score")
                        break
        
        # Kalkan kontrolü
        if platform.has_shield and platform.shield_rect:
            if ball.y + ball.radius >= platform.shield_rect.top:
                ball.dy = -abs(ball.dy)  # Topu yukarı yönlendir
                self.play_sound("hit")
            
            # Ekstra toplar için kalkan kontrolü
            if hasattr(power_up_manager, 'extra_balls'):
                for extra_ball in power_up_manager.extra_balls:
                    if extra_ball.y + extra_ball.radius >= platform.shield_rect.top:
                        extra_ball.dy = -abs(extra_ball.dy)  # Ekstra topu yukarı yönlendir
                        self.play_sound("hit")
            
        # Blok çarpışmaları
        blocks_to_remove = []
        for block in block_manager.blocks:
            # Lazer çarpışması
            if platform.has_laser:
                for laser in platform.lasers[:]:
                    if laser["rect"].colliderect(block.rect):
                        platform.lasers.remove(laser)
                        if block.hit():
                            if block.contains_powerup:
                                power_up_manager.spawn_powerup(
                                    block.rect.centerx,
                                    block.rect.centery
                                )
                            blocks_to_remove.append(block)
                            game_state.score += block.points
                            self.play_sound("score")
                        break
            
            # Top çarpışması
            ball_rect = pygame.Rect(ball.x - ball.radius, ball.y - ball.radius,
                                  ball.radius * 2, ball.radius * 2)
            
            if ball_rect.colliderect(block.rect):
                # Çarpışma yönünü belirle
                dx = ball.x - block.rect.centerx
                dy = ball.y - block.rect.centery
                
                if abs(dx/block.rect.width) > abs(dy/block.rect.height):
                    ball.dx = abs(ball.dx) if dx > 0 else -abs(ball.dx)
                else:
                    ball.dy = abs(ball.dy) if dy > 0 else -abs(ball.dy)
                
                # Bloğu vur
                if ball.strong or block.hit():
                    # Blok kırılma sesi
                    if game_state.level in [1, 2, 3]:
                        sound_paths = {
                            1: "Assests/tas/taş_blok_kırılma.mp3",
                            2: "Assests/col/cam_kırılma.mp3",
                            3: "Assests/buz/buzsesi.mp3"
                        }
                        sound_path = sound_paths[game_state.level]
                        try:
                            if os.path.exists(sound_path):
                                sound = pygame.mixer.Sound(sound_path)
                                sound.set_volume(0.5)
                                sound.play()
                        except:
                            print(f"Blok kırılma sesi çalınamadı: {sound_path}")
                            
                    if block.contains_powerup:
                        power_up_manager.spawn_powerup(
                            block.rect.centerx,
                            block.rect.centery
                        )
                    blocks_to_remove.append(block)
                    game_state.score += block.points * (1 + self.combo * 0.1)
                    self.combo += 1
                    self.play_sound("score")
                break
                
        # Blokları kaldır ve skoru güncelle
        for block in blocks_to_remove:
            if block in block_manager.blocks:
                block_manager.blocks.remove(block)
                
        # Combo süresini kontrol et
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time > self.combo_timeout:
            self.combo = 0
        self.last_hit_time = current_time
        
        return game_state.score
        
    def update_score(self, points, game_state):
        game_state.score += points
        return game_state.score 