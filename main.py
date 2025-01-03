import pygame
import sys
from database import Database
import os
from game_objects import Platform, Ball, BlockManager
from game_logic import GameLogic
from level_system import LevelSystem
from power_up_system import PowerUpManager
from leaderboard import Leaderboard
from game_settings import GameSettings
from profile import Profile
from game_states import GameState, GameError
import math

# Renk tanımlamaları
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (52, 152, 219)
RED = (231, 76, 60)

# Pygame'i başlat
pygame.init()
if not pygame.mixer.get_init():
    pygame.mixer.init()

# Ekran ayarları
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Breakout")

# Ses efektleri
def load_sound(file_path):
    try:
        return pygame.mixer.Sound(file_path)
    except Exception as e:
        print(f"Ses dosyası yüklenemedi ({file_path}): {e}")
        return None

try:
    # Ses dosyalarının yolları
    sound_files = {
        "hit": "Assests/topsesi.mp3",
        "score": "Assests/skorses.mp3",
        "background": "Assests/background_sound.mp3",
        "gameover": "Assests/gameover.mp3",
        "menu_music": "Assests/sound/giriş_ekranı_sesi.mp3",
        "level_up": "Assests/sound/level_atlama.mp3",
        "lose_game": "Assests/sound/kaybetme_sesi.mp3"
    }
    
    # Ses dosyalarını yükle
    sounds = {}
    for sound_name, file_path in sound_files.items():
        if os.path.exists(file_path):
            sounds[sound_name] = load_sound(file_path)
        else:
            print(f"Ses dosyası bulunamadı: {file_path}")
            
    # Arka plan müziğini başlat
    if sounds.get("menu_music"):
        sounds["menu_music"].play(-1)
except Exception as e:
    print(f"Ses sistemi başlatılırken hata: {e}")

# Görsel dosyaları yükleme fonksiyonu
def load_image(file_path, size=None):
    try:
        if not os.path.exists(file_path):
            print(f"Görsel dosyası bulunamadı: {file_path}")
            return None
            
        image = pygame.image.load(file_path)
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except Exception as e:
        print(f"Görsel dosyası yüklenemedi ({file_path}): {e}")
        return None

# Modern Menü Sınıfı
class ModernMenu:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Renkler
        self.colors = {
            "primary": (52, 152, 219),     # Ana renk (Mavi)
            "secondary": (46, 204, 113),    # İkincil renk (Yeşil)
            "accent": (155, 89, 182),       # Vurgu rengi (Mor)
            "warning": (231, 76, 60),       # Uyarı rengi (Kırmızı)
            "background": (44, 62, 80),     # Arka plan rengi (Koyu mavi)
            "text": (236, 240, 241)         # Metin rengi (Beyaz)
        }
        
        try:
            # Font
            self.title_font = pygame.font.Font(None, int(screen_height * 0.1))
            self.button_font = pygame.font.Font(None, int(screen_height * 0.05))
            
            # Animasyon değişkenleri
            self.animation_offset = 0
            
            # Butonlar
            self.create_buttons()
            
            # Arka plan görseli
            self.background = load_image("images/arka_plan.jpg", (screen_width, screen_height))
            
        except Exception as e:
            print(f"Menü başlatılırken hata: {e}")
            self.background = None
            
    def create_buttons(self):
        try:
            button_width = 250
            button_height = 50
            button_spacing = 20
            start_y = self.screen_height * 0.35
            
            self.buttons = {
                "play": self.create_button("Oyuna Başla", start_y, self.colors["primary"]),
                "profile": self.create_button("Profil", start_y + button_height + button_spacing, self.colors["secondary"]),
                "leaderboard": self.create_button("Skor Tablosu", start_y + 2 * (button_height + button_spacing), self.colors["accent"]),
                "settings": self.create_button("Ayarlar", start_y + 3 * (button_height + button_spacing), self.colors["primary"]),
                "exit": self.create_button("Çıkış", start_y + 4 * (button_height + button_spacing), self.colors["warning"])
            }
        except Exception as e:
            print(f"Butonlar oluşturulurken hata: {e}")
            self.buttons = {}
            
    def create_button(self, text, y_pos, color):
        button_width = 250
        button_height = 50
        return {
            "rect": pygame.Rect((self.screen_width - button_width) // 2, y_pos, 
                              button_width, button_height),
            "text": text,
            "color": color,
            "hover": False
        }
            
    def update(self, mouse_pos):
        try:
            for button in self.buttons.values():
                button["hover"] = button["rect"].collidepoint(mouse_pos)
                
            # Animasyon güncelleme
            self.animation_offset = (self.animation_offset + 2) % 360
        except Exception as e:
            print(f"Menü güncellenirken hata: {e}")
            
    def draw(self):
        try:
            # Arka plan
            if self.background:
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill(self.colors["background"])
            
            # Başlık
            title = self.title_font.render("BREAKOUT", True, self.colors["text"])
            title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height * 0.2))
            self.screen.blit(title, title_rect)
            
            # Butonları çiz
            for button in self.buttons.values():
                self.draw_button(button)
                
        except Exception as e:
            print(f"Menü çizilirken hata: {e}")
            # Hata durumunda basit bir menü çiz
            self.draw_fallback_menu()
            
    def draw_button(self, button):
        try:
            # Hover efekti
            color = button["color"]
            if button["hover"]:
                color = tuple(min(c + 30, 255) for c in color)
                
            # Buton arka planı
            pygame.draw.rect(self.screen, color, button["rect"], border_radius=10)
            
            # Buton kenarlığı
            if button["hover"]:
                pygame.draw.rect(self.screen, self.colors["text"], 
                               button["rect"], 3, border_radius=10)
            
            # Buton metni
            text = self.button_font.render(button["text"], True, self.colors["text"])
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
            
            # Animasyonlu vurgu efekti
            if button["hover"]:
                self.draw_button_glow(button, color)
                
        except Exception as e:
            print(f"Buton çizilirken hata: {e}")
            
    def draw_button_glow(self, button, color):
        try:
            glow_surface = pygame.Surface((button["rect"].width + 20, 
                                         button["rect"].height + 20), 
                                        pygame.SRCALPHA)
            glow_color = color + (128,)  # Alpha değeri ekle
            pygame.draw.rect(glow_surface, glow_color, 
                           (10, 10, button["rect"].width, button["rect"].height), 
                           border_radius=10)
            self.screen.blit(glow_surface, 
                           (button["rect"].x - 10, button["rect"].y - 10))
        except Exception as e:
            print(f"Buton efekti çizilirken hata: {e}")
            
    def draw_fallback_menu(self):
        try:
            self.screen.fill(self.colors["background"])
            text = self.button_font.render("Menü yüklenemedi", True, self.colors["text"])
            text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(text, text_rect)
        except Exception as e:
            print(f"Yedek menü çizilirken hata: {e}")
            
    def handle_click(self, mouse_pos):
        try:
            for button_name, button in self.buttons.items():
                if button["rect"].collidepoint(mouse_pos):
                    return button_name
            return None
        except Exception as e:
            print(f"Menü tıklama işlenirken hata: {e}")
            return None

# Hata yönetimi için özel sınıf
class GameError(Exception):
    def __init__(self, message, error_type="general"):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)

def handle_error(error, screen, font):
    error_types = {
        "database": "Veritabanı Hatası",
        "file": "Dosya Hatası",
        "sound": "Ses Hatası",
        "general": "Genel Hata"
    }
    
    error_title = error_types.get(error.error_type, "Bilinmeyen Hata")
    error_surface = pygame.Surface((400, 200))
    error_surface.fill((44, 62, 80))  # Koyu mavi arka plan
    
    # Başlık
    title_text = font.render(error_title, True, (231, 76, 60))  # Kırmızı
    title_rect = title_text.get_rect(centerx=200, y=20)
    error_surface.blit(title_text, title_rect)
    
    # Hata mesajı
    message_lines = [error.message[i:i+30] for i in range(0, len(error.message), 30)]
    for i, line in enumerate(message_lines):
        message_text = font.render(line, True, (236, 240, 241))  # Beyaz
        message_rect = message_text.get_rect(centerx=200, y=80 + i*30)
        error_surface.blit(message_text, message_rect)
    
    # Ekrana çiz
    screen.blit(error_surface, 
               ((screen.get_width() - 400) // 2, 
                (screen.get_height() - 200) // 2))
    pygame.display.flip()
    
    # Hata logunu kaydet
    with open("error_log.txt", "a") as log_file:
        log_file.write(f"[{pygame.time.get_ticks()}] {error_title}: {error.message}\n")

# Veritabanı ve oyun durumu başlatma
try:
    db = Database()
    game_state = GameState()
except Exception as e:
    print(f"Başlatma hatası: {e}")
    pygame.quit()
    sys.exit(1)
# Oyun nesneleri
platform = Platform(screen_width, screen_height)
ball = Ball(screen_width, screen_height)
block_manager = BlockManager(screen_width)
power_up_manager = PowerUpManager()
level_system = LevelSystem(screen_width, screen_height)
game_logic = GameLogic(screen_width, screen_height)

# Menü ve UI nesneleri
menu = ModernMenu(screen, screen_width, screen_height)
leaderboard = Leaderboard(screen, screen_width, screen_height)
settings_menu = GameSettings(screen, screen_width, screen_height, db)
profile_menu = Profile(screen, screen_width, screen_height)

# GameSettings'e game_state'i ekle
settings_menu.set_game_state(game_state)

# Font
try:
    default_font = pygame.font.Font(None, 36)  # Default sistem fontu
    title_font = pygame.font.Font(None, 72)    # Başlık için büyük font
    button_font = pygame.font.Font(None, 32)   # Butonlar için orta boy font
except Exception as e:
    print(f"Font yükleme hatası: {e}")
    pygame.quit()
    sys.exit(1)

# Login ekranı için modern input box sınıfı
class ModernInputBox:
    def __init__(self, x, y, w, h, text='', password=False, placeholder=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = (52, 152, 219)  # Mavi
        self.color_active = (46, 204, 113)    # Yeşil
        self.color = self.color_inactive
        self.text = text
        self.password = password
        self.placeholder = placeholder
        self.placeholder_color = (149, 165, 166)  # Gri
        self.text_color = (255, 255, 255)  # Beyaz
        self.active = False
        try:
            self.font = pygame.font.Font(None, 32)
            self.txt_surface = self.font.render(
                text if text else placeholder,
                True,
                self.text_color if text else self.placeholder_color
            )
        except Exception as e:
            print(f"Input box font hatası: {e}")
            self.font = None
            self.txt_surface = None
        
    def handle_event(self, event):
        if not self.font:  # Font yüklenemezse eventi işleme
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Tıklama pozisyonunu kontrol et
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.color = self.color_active
            else:
                self.active = False
                self.color = self.color_inactive
            return False
            
        if event.type == pygame.KEYDOWN:
            if not self.active:
                return False
                
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_TAB:
                self.active = False
                self.color = self.color_inactive
                return True
            else:
                if event.unicode.isprintable():
                    self.text += event.unicode
                    
            # Metin yüzeyini güncelle
            display_text = '*' * len(self.text) if self.password else self.text
            if display_text:
                self.txt_surface = self.font.render(
                    display_text,
                    True,
                    self.text_color
                )
            else:
                self.txt_surface = self.font.render(
                    self.placeholder,
                    True,
                    self.placeholder_color
                )
                
        return False

    def draw(self, screen):
        if not self.font or not self.txt_surface:  # Font veya yüzey yoksa çizme
            return
            
        # Arka plan
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        
        # Metin
        if len(self.text) > 0:
            display_text = '*' * len(self.text) if self.password else self.text
            self.txt_surface = self.font.render(display_text, True, self.text_color)
        else:
            self.txt_surface = self.font.render(self.placeholder, True, self.placeholder_color)
            
        # Metni ortala
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)
        
        # Aktif kenarlık
        if self.active:
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=5)

# Input boxları oluştur
try:
    username_box = ModernInputBox(
        screen_width//2 - 150,
        screen_height//2 - 60,
        300, 40,
        placeholder='Kullanıcı Adı'
    )
    password_box = ModernInputBox(
        screen_width//2 - 150,
        screen_height//2,
        300, 40,
        password=True,
        placeholder='Şifre'
    )
    email_box = ModernInputBox(
        screen_width//2 - 150,
        screen_height//2 + 60,
        300, 40,
        placeholder='E-posta'
    )
except Exception as e:
    print(f"Input box oluşturma hatası: {e}")
    pygame.quit()
    sys.exit(1)

def reset_game():
    try:
        # Oyun durumunu sıfırla
        game_state.reset_game()  # GameState'in reset metodunu çağır
        
        # Oyun nesnelerini sıfırla
        ball.reset()
        platform.reset()
        
        # Blokları tamamen sıfırla
        block_manager.blocks.clear()  # Mevcut blokları temizle
        
        # İlgili level tasarımını al ve blokları yeniden oluştur
        level_data = level_system.get_level_layout(game_state.level, block_manager)
        
        # Seviye görsellerini yükle
        global current_background
        current_background = level_system.load_level_assets(game_state.level, platform)
        
        # Top hızını level datasından ayarla
        ball.speed = level_data["ball_speed"]
        ball.original_speed = ball.speed
        
        # Power-up'ları temizle
        power_up_manager.power_ups.clear()
        power_up_manager.active_effects.clear()
        
        # Menü müziğini durdur, oyun müziğini başlat
        if sounds.get("menu_music"):
            sounds["menu_music"].stop()
        if sounds.get("background"):
            sounds["background"].play(-1)

    except Exception as e:
        raise GameError(f"Oyun sıfırlanırken hata: {str(e)}", "general")

def handle_game_input():
    try:
        keys = pygame.key.get_pressed()
        
        # Platform kontrolü - klavye
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            platform.move("left", screen_width)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            platform.move("right", screen_width)
            
        # Platform kontrolü - fare
        mouse_x, _ = pygame.mouse.get_pos()
        platform_center = platform.rect.centerx
        if abs(mouse_x - platform_center) > 5:  # Küçük bir ölü bölge
            if mouse_x < platform_center:
                platform.move("left", screen_width)
            else:
                platform.move("right", screen_width)
            
        # Top fırlatma
        if not ball.active and (keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]):
            ball.launch()
            if "hit" in sounds:
                sounds["hit"].play()
            
        # Yapışkan platform kontrolü
        if platform.sticky and ball.active:
            if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
                platform.sticky = False
                ball.launch()
                if "hit" in sounds:
                    sounds["hit"].play()
                    
        # Lazer kontrolü
        if platform.has_laser and (keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]):
            platform.shoot_laser()
            
        # Platform lazerlerini güncelle
        platform.update_lasers()
                    
        # Menüye dönme
        if keys[pygame.K_m]:
            game_state.change_state("menu")
            
    except Exception as e:
        raise GameError(f"Oyun girişi işlenirken hata: {e}", "general")

def draw_game():
    try:
        # Arka planı çiz
        if 'current_background' in globals():
            print(f"current_background değişkeni mevcut: {current_background is not None}")
            if current_background is not None:
                screen.blit(current_background, (0, 0))
                print("Arka plan çizildi")
            else:
                print("current_background None")
                screen.fill((44, 62, 80))
        else:
            print("current_background değişkeni bulunamadı")
            screen.fill((44, 62, 80))  # yedek koyu mavi arka plan
        
        # Oyun nesnelerini çiz
        platform.draw(screen)
        ball.draw(screen)
        block_manager.draw(screen)
        power_up_manager.draw(screen)
        
        # HUD
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Skor: {game_state.score}", True, WHITE)
        lives_text = font.render(f"Can: {game_state.lives}", True, WHITE)
        level_text = font.render(f"Seviye: {game_state.level}", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (screen_width - 100, 10))
        screen.blit(level_text, (screen_width // 2 - 50, 10))
        
        if game_state.paused:
            pause_text = font.render("DURAKLAT", True, WHITE)
            pause_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(pause_text, pause_rect)
            
    except Exception as e:
        raise GameError(f"Oyun çizilirken hata: {e}", "general")

def check_game_over():
    try:
        if game_state.lives <= 0:
            # Yüksek skoru güncelle
            if game_state.is_logged_in():
                db.update_high_score(game_state.current_user['username'], game_state.score)
            
            # Oyun bitti sesini çal
            if "gameover" in sounds:
                sounds["gameover"].play()
                
            # Oyun durumunu değiştir
            game_state.change_state("game_over")
    except Exception as e:
        game_state.set_error(f"Oyun sonu kontrolü sırasında hata: {str(e)}")

def update_game():
    try:
        if not game_state.paused:
            # Top ve platform güncellemeleri
            if ball.active:
                ball.move()
                
            # Çarpışma kontrolü ve skor güncellemesi
            if game_state.state == "game":  # Sadece oyun durumunda skor güncelle
                new_score = game_logic.check_collisions(ball, platform, block_manager, power_up_manager, game_state)
                if new_score > game_state.score:
                    game_state.score = new_score
                    if "score" in sounds:
                        sounds["score"].play()
            
            # Can kaybı kontrolü
            if ball.y + ball.radius > screen_height:
                game_state.lives -= 1
                if game_state.lives <= 0:
                    # Yüksek skoru güncelle
                    if game_state.is_logged_in():
                        db.update_high_score(game_state.current_user['username'], game_state.score)
                    # Oyun bitti sesini çal
                    if "lose_game" in sounds:
                        sounds["lose_game"].play()
                    game_state.change_state("game_over")
                else:
                    ball.reset()
                    platform.reset()
            
            # Level kontrolü
            if level_system.is_level_complete(block_manager):
                game_state.level += 1
                print(f"Yeni seviye: {game_state.level}")
                
                # Oyun tamamlandı mı kontrol et
                if level_system.is_game_complete(game_state.level):
                    # Oyun kazanıldı
                    if "level_up" in sounds:
                        sounds["level_up"].play()
                    game_state.change_state("game_won")
                else:
                    # Sonraki seviyeye geç
                    # Oyun nesnelerini sıfırla
                    ball.reset()
                    platform.reset()
                    
                    # Yeni level için arkaplanı güncelle
                    global current_background
                    current_background = level_system.load_level_assets(game_state.level, platform)
                    print(f"Yeni arkaplan yüklendi: {current_background is not None}")
                    
                    # Level tasarımını yükle
                    level_data = level_system.get_level_layout(game_state.level, block_manager)
                    ball.speed = level_data["ball_speed"]
                    
                    # Level up sesini çal
                    if "level_up" in sounds:
                        sounds["level_up"].play()
                    
                    # Power-up'ları temizle
                    power_up_manager.power_ups.clear()
                    power_up_manager.active_effects.clear()
            
            # Power-up güncelleme
            power_up_manager.update(platform, ball)
            
            # Blok güncellemeleri
            block_manager.update()
            
            # Yapışkan platform kontrolü
            if platform.sticky and ball.active:
                ball.attach_to_platform(platform)
                
    except Exception as e:
        raise GameError(f"Oyun güncellenirken hata: {e}", "general")

def draw_modern_login_screen():
    try:
        # Arka plan
        try:
            background = pygame.image.load("images/arka_plan.jpg")
            background = pygame.transform.scale(background, (screen_width, screen_height))
            screen.blit(background, (0, 0))
        except:
            screen.fill((44, 62, 80))  # Koyu mavi
        
        # Yarı saydam overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Başlık
        title = title_font.render("Giriş Yap", True, (255, 255, 255))
        title_rect = title.get_rect(center=(screen_width//2, screen_height//4))
        screen.blit(title, title_rect)
        
        # Input boxları çiz
        username_box.draw(screen)
        password_box.draw(screen)
        
        # Butonları çiz
        login_button = pygame.Rect(screen_width//2 - 150, screen_height//2 + 100, 300, 50)
        register_button = pygame.Rect(screen_width//2 - 150, screen_height//2 + 170, 300, 50)
        
        # Buton renkleri ve efektleri
        mouse_pos = pygame.mouse.get_pos()
        
        # Giriş butonu
        login_color = (46, 204, 113) if login_button.collidepoint(mouse_pos) else (52, 152, 219)
        pygame.draw.rect(screen, login_color, login_button, border_radius=25)
        
        # Kayıt butonu
        register_color = (231, 76, 60) if register_button.collidepoint(mouse_pos) else (192, 57, 43)
        pygame.draw.rect(screen, register_color, register_button, border_radius=25)
        
        # Buton metinleri
        login_text = button_font.render("Giriş", True, (255, 255, 255))
        register_text = button_font.render("Kayıt Ol", True, (255, 255, 255))
        
        # Buton metinlerini ortala
        login_text_rect = login_text.get_rect(center=login_button.center)
        register_text_rect = register_text.get_rect(center=register_button.center)
        
        screen.blit(login_text, login_text_rect)
        screen.blit(register_text, register_text_rect)
                                   
        # Hata mesajı (eğer varsa)
        if hasattr(game_state, 'error_message') and game_state.error_message:
            error_text = button_font.render(game_state.error_message, True, (231, 76, 60))
            error_rect = error_text.get_rect(center=(screen_width//2, screen_height//2 + 240))
            screen.blit(error_text, error_rect)
            
    except Exception as e:
        print(f"Login ekranı çizilirken hata: {e}")

def draw_modern_register_screen():
    try:
        # Arka plan
        try:
            background = pygame.image.load("images/arka_plan.jpg")
            background = pygame.transform.scale(background, (screen_width, screen_height))
            screen.blit(background, (0, 0))
        except:
            screen.fill((44, 62, 80))  # Koyu mavi
        
        # Yarı saydam overlay
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Başlık
        title = title_font.render("Kayıt Ol", True, (255, 255, 255))
        title_rect = title.get_rect(center=(screen_width//2, screen_height//4))
        screen.blit(title, title_rect)
        
        # Input boxları çiz
        username_box.draw(screen)
        password_box.draw(screen)
        email_box.draw(screen)
        
        # Butonları çiz
        register_button = pygame.Rect(screen_width//2 - 150, screen_height//2 + 170, 300, 50)
        back_button = pygame.Rect(20, 20, 100, 40)
        
        # Buton renkleri ve efektleri
        mouse_pos = pygame.mouse.get_pos()
        
        # Kayıt butonu
        register_color = (46, 204, 113) if register_button.collidepoint(mouse_pos) else (52, 152, 219)
        pygame.draw.rect(screen, register_color, register_button, border_radius=25)
        
        # Geri butonu
        back_color = (231, 76, 60) if back_button.collidepoint(mouse_pos) else (192, 57, 43)
        pygame.draw.rect(screen, back_color, back_button, border_radius=20)
        
        # Buton metinleri
        register_text = button_font.render("Kayıt Ol", True, (255, 255, 255))
        back_text = button_font.render("Geri", True, (255, 255, 255))
        
        # Buton metinlerini ortala
        register_text_rect = register_text.get_rect(center=register_button.center)
        back_text_rect = back_text.get_rect(center=back_button.center)
        
        screen.blit(register_text, register_text_rect)
        screen.blit(back_text, back_text_rect)
                               
        # Hata mesajı (eğer varsa)
        if hasattr(game_state, 'error_message') and game_state.error_message:
            error_text = button_font.render(game_state.error_message, True, (231, 76, 60))
            error_rect = error_text.get_rect(center=(screen_width//2, screen_height//2 + 240))
            screen.blit(error_text, error_rect)
            
    except Exception as e:
        print(f"Kayıt ekranı çizilirken hata: {e}")

def handle_login_events(event):
    try:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Giriş butonu kontrolü
            login_button = pygame.Rect(screen_width//2 - 150, screen_height//2 + 100, 300, 50)
            if login_button.collidepoint(mouse_pos):
                if not username_box.text or not password_box.text:
                    game_state.set_error("Kullanıcı adı ve şifre gerekli!")
                    return False
                    
                user_data = db.login_user(username_box.text, password_box.text)
                if user_data:
                    game_state.login(user_data)
                    username_box.text = ""
                    password_box.text = ""
                    return True
                else:
                    game_state.set_error("Hatalı kullanıcı adı veya şifre!")
                    return False
                    
            # Kayıt ol butonu kontrolü
            register_button = pygame.Rect(screen_width//2 - 150, screen_height//2 + 170, 300, 50)
            if register_button.collidepoint(mouse_pos):
                game_state.change_state("register")
                return True
                
        # Input box olaylarını işle
        username_box.handle_event(event)
        password_box.handle_event(event)
        return False
    except Exception as e:
        game_state.set_error(f"Giriş işlemi sırasında hata: {str(e)}")
        return False

def handle_register_events(event):
    try:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Kayıt ol butonu kontrolü
            register_button = pygame.Rect(screen_width//2 - 150, screen_height//2 + 170, 300, 50)
            if register_button.collidepoint(mouse_pos):
                if not username_box.text or not password_box.text or not email_box.text:
                    game_state.set_error("Tüm alanları doldurun!")
                    return False
                    
                if db.register_user(username_box.text, password_box.text, email_box.text):
                    game_state.change_state("login")
                    username_box.text = ""
                    password_box.text = ""
                    email_box.text = ""
                    game_state.set_error("Kayıt başarılı! Giriş yapabilirsiniz.")
                    return True
                else:
                    game_state.set_error("Bu kullanıcı adı zaten kullanılıyor!")
                    return False
                    
            # Geri butonu kontrolü
            back_button = pygame.Rect(20, 20, 100, 40)
            if back_button.collidepoint(mouse_pos):
                game_state.change_state("login")
                username_box.text = ""
                password_box.text = ""
                email_box.text = ""
                return True
                
        # Input box olaylarını işle
        username_box.handle_event(event)
        password_box.handle_event(event)
        email_box.handle_event(event)
        return False
        
    except Exception as e:
        game_state.set_error(f"Kayıt işlemi sırasında hata: {str(e)}")
        return False

class GameOverMenu:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.colors = {
            "background": (44, 62, 80),
            "button": (52, 152, 219),
            "button_hover": (41, 128, 185),
            "text": (255, 255, 255)
        }
        self.buttons = {
            "restart": {
                "rect": pygame.Rect(screen_width//2 - 150, screen_height//2, 300, 50),
                "text": "Tekrar Başla",
                "color": self.colors["button"]
            },
            "menu": {
                "rect": pygame.Rect(screen_width//2 - 150, screen_height//2 + 70, 300, 50),
                "text": "Ana Menüye Dön",
                "color": self.colors["button"]
            }
        }
        self.title_font = pygame.font.Font(None, 74)
        self.button_font = pygame.font.Font(None, 36)
        
    def draw(self, score):
        try:
            # Arka plan resmi
            background_img = pygame.image.load("C:\\ziplayan_tavsan\\Oyun\\Assests\\gameover_success.png")
            background_img = pygame.transform.scale(background_img, (self.screen_width, self.screen_height))
            self.screen.blit(background_img, (0, 0))
        except Exception as e:
            print(f"Arka plan resmi yüklenemedi: {e}")
            # Arka plan yüklenemezse yarı saydam siyah arka plan
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(200)
            self.screen.blit(overlay, (0, 0))
        
        # Oyun Bitti yazısı
        title = self.title_font.render("OYUN BİTTİ", True, self.colors["text"])
        title_rect = title.get_rect(center=(self.screen_width//2, self.screen_height//3))
        self.screen.blit(title, title_rect)
        
        # Skor
        score_text = self.button_font.render(f"Skor: {score}", True, self.colors["text"])
        score_rect = score_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 50))
        self.screen.blit(score_text, score_rect)
        
        # Butonları çiz
        self._draw_buttons()

    def draw_win_screen(self, score):
        try:
            # Arka plan resmi
            background_img = pygame.image.load("C:\\ziplayan_tavsan\\Oyun\\Assests\\gameover_success.png")
            background_img = pygame.transform.scale(background_img, (self.screen_width, self.screen_height))
            self.screen.blit(background_img, (0, 0))
        except Exception as e:
            print(f"Arka plan resmi yüklenemedi: {e}")
            # Arka plan yüklenemezse yarı saydam siyah arka plan
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(200)
            self.screen.blit(overlay, (0, 0))
        
        # Kazandınız yazısı
        title = self.title_font.render("KAZANDINIZ!", True, (46, 204, 113))  # Yeşil renk
        title_rect = title.get_rect(center=(self.screen_width//2, self.screen_height//3))
        self.screen.blit(title, title_rect)
        
        # Tebrik mesajı
        congrats = self.button_font.render("Tüm seviyeleri başarıyla tamamladınız!", True, self.colors["text"])
        congrats_rect = congrats.get_rect(center=(self.screen_width//2, self.screen_height//2 - 80))
        self.screen.blit(congrats, congrats_rect)
        
        # Skor
        score_text = self.button_font.render(f"Final Skor: {score}", True, self.colors["text"])
        score_rect = score_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 30))
        self.screen.blit(score_text, score_rect)
        
        # Butonları çiz
        self._draw_buttons()

    def _draw_buttons(self):
        # Butonları çiz
        mouse_pos = pygame.mouse.get_pos()
        for button_name, button in self.buttons.items():
            color = self.colors["button_hover"] if button["rect"].collidepoint(mouse_pos) else button["color"]
            pygame.draw.rect(self.screen, color, button["rect"], border_radius=10)
            
            text = self.button_font.render(button["text"], True, self.colors["text"])
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
            
    def handle_click(self, pos):
        for button_name, button in self.buttons.items():
            if button["rect"].collidepoint(pos):
                return button_name
        return None

# Oyun sonu menüsünü oluştur
game_over_menu = GameOverMenu(screen, screen_width, screen_height)

# Ana oyun döngüsü
running = True
clock = pygame.time.Clock()

# Oyun durumu ve nesneleri başlat
try:
    game_state = GameState()
    platform = Platform(screen_width, screen_height)
    ball = Ball(screen_width, screen_height)
    block_manager = BlockManager(screen_width)
    power_up_manager = PowerUpManager()
    level_system = LevelSystem(screen_width, screen_height)
    game_logic = GameLogic(screen_width, screen_height)
    menu = ModernMenu(screen, screen_width, screen_height)
    leaderboard = Leaderboard(screen, screen_width, screen_height)
    settings_menu = GameSettings(screen, screen_width, screen_height, db)
    profile_menu = Profile(screen, screen_width, screen_height)
    settings_menu.set_game_state(game_state)  # GameState'i settings_menu'ye ekle
except Exception as e:
    print(f"Oyun başlatılırken hata: {e}")
    pygame.quit()
    sys.exit(1)

while running:
    try:
        # FPS sınırı
        clock.tick(60)
        
        # Fare pozisyonunu al
        mouse_pos = pygame.mouse.get_pos()
        
        # Hata mesajı kontrolü
        game_state.update_error()
        
        # Event yönetimi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if db:
                    db.close()
                running = False
                
            # Game over ekranı için buton kontrolleri
            if game_state.state == "game_over" and event.type == pygame.MOUSEBUTTONDOWN:
                action = game_over_menu.handle_click(event.pos)
                if action == "restart":
                    # Önce yüksek skoru güncelle
                    if game_state.is_logged_in():
                        db.update_high_score(game_state.current_user['username'], game_state.score)
                    # Sonra oyunu sıfırla
                    reset_game()
                    game_state.change_state("game")
                elif action == "menu":
                    # Menüye dönmeden önce yüksek skoru güncelle
                    if game_state.is_logged_in():
                        db.update_high_score(game_state.current_user['username'], game_state.score)
                    game_state.change_state("menu")
                    if sounds.get("menu_music"):
                        sounds["menu_music"].play(-1)
                
            # Oyun kazanma ekranı için buton kontrolleri
            if game_state.state == "game_won" and event.type == pygame.MOUSEBUTTONDOWN:
                action = game_over_menu.handle_click(event.pos)
                if action == "restart":
                    # Önce yüksek skoru güncelle
                    if game_state.is_logged_in():
                        db.update_high_score(game_state.current_user['username'], game_state.score)
                    # Sonra oyunu sıfırla
                    reset_game()
                    game_state.change_state("game")
                elif action == "menu":
                    # Menüye dönmeden önce yüksek skoru güncelle
                    if game_state.is_logged_in():
                        db.update_high_score(game_state.current_user['username'], game_state.score)
                    game_state.change_state("menu")
                    if sounds.get("menu_music"):
                        sounds["menu_music"].play(-1)
                
            # Input box'lar için event handling
            if game_state.state in ["login", "register"]:
                if game_state.state == "login":
                    username_box.handle_event(event)
                    password_box.handle_event(event)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        handle_login_events(event)
                elif game_state.state == "register":
                    username_box.handle_event(event)
                    password_box.handle_event(event)
                    email_box.handle_event(event)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        handle_register_events(event)
                
            # Diğer event'ler
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state.state == "game":
                        game_state.paused = not game_state.paused
                    elif game_state.state != "menu":
                        game_state.change_state("menu")
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state.state == "menu":
                    try:
                        action = menu.handle_click(mouse_pos)
                        if action:
                            if action == "play":
                                if game_state.is_logged_in():
                                    game_state.change_state("game")
                                    reset_game()
                                else:
                                    game_state.set_error("Lütfen önce giriş yapın")
                            elif action == "profile":
                                if game_state.is_logged_in():
                                    game_state.change_state("profile")
                                else:
                                    game_state.set_error("Lütfen önce giriş yapın")
                            elif action == "leaderboard":
                                game_state.change_state("leaderboard")
                            elif action == "settings":
                                game_state.change_state("settings")
                            elif action == "exit":
                                if db:
                                    db.close()
                                running = False
                    except Exception as e:
                        game_state.set_error(f"Menü hatası: {str(e)}")
                
                elif game_state.state == "profile":
                    try:
                        result = profile_menu.handle_event(event)
                        if result == "menu":
                            game_state.change_state("menu")
                    except Exception as e:
                        game_state.set_error(f"Profil hatası: {str(e)}")
                
                elif game_state.state == "leaderboard":
                    try:
                        result = leaderboard.handle_event(event)
                        if result == "menu":
                            game_state.change_state("menu")
                    except Exception as e:
                        game_state.set_error(f"Skor tablosu hatası: {str(e)}")
                
                elif game_state.state == "settings":
                    try:
                        result = settings_menu.handle_event(event)
                        if result == "menu":
                            game_state.change_state("menu")
                    except Exception as e:
                        game_state.set_error(f"Ayarlar hatası: {str(e)}")
        
        # Oyun mantığı
        if game_state.state == "game" and not game_state.paused:
            try:
                # Oyun girdilerini işle
                handle_game_input()
                
                # Oyun nesnelerini güncelle
                if ball.active:
                    ball.move()
                    
                # Çarpışma kontrolleri ve skor güncellemesi
                new_score = game_logic.check_collisions(ball, platform, block_manager, power_up_manager, game_state)
                if new_score > game_state.score:
                    game_state.score = new_score
                    if "score" in sounds:
                        sounds["score"].play()
                
                # Power-up güncelleme
                power_up_manager.update(platform, ball)
                
                # Blok güncellemeleri
                block_manager.update()
                
                # Level kontrolü
                if level_system.is_level_complete(block_manager):
                    game_state.level += 1
                    print(f"Yeni seviye: {game_state.level}")
                    
                    # Oyun tamamlandı mı kontrol et
                    if level_system.is_game_complete(game_state.level):
                        # Oyun kazanıldı
                        if "level_up" in sounds:
                            sounds["level_up"].play()
                        game_state.change_state("game_won")
                    else:
                        # Sonraki seviyeye geç
                        # Oyun nesnelerini sıfırla
                        ball.reset()
                        platform.reset()
                        
                        # Yeni level için arkaplanı güncelle
                        global current_background
                        current_background = level_system.load_level_assets(game_state.level, platform)
                        print(f"Yeni arkaplan yüklendi: {current_background is not None}")
                        
                        # Level tasarımını yükle
                        level_data = level_system.get_level_layout(game_state.level, block_manager)
                        ball.speed = level_data["ball_speed"]
                        
                        # Level up sesini çal
                        if "level_up" in sounds:
                            sounds["level_up"].play()
                        
                        # Power-up'ları temizle
                        power_up_manager.power_ups.clear()
                        power_up_manager.active_effects.clear()
                    
                # Çarpışma kontrolleri ve skor güncellemesi
                new_score = game_logic.check_collisions(ball, platform, block_manager, power_up_manager, game_state)
                if new_score > game_state.score:
                    game_state.score = new_score
                    if "score" in sounds:
                        sounds["score"].play()
                
                # Yapışkan platform kontrolü
                if platform.sticky and ball.active:
                    ball.attach_to_platform(platform)
                    
            except Exception as e:
                game_state.set_error(f"Oyun hatası: {str(e)}")
                
            # Menü tuşu kontrolü
            keys = pygame.key.get_pressed()
            if keys[pygame.K_m]:
                game_state.change_state("menu")
        
        # Ekranı temizle
        screen.fill(BLACK)
        
        # Duruma göre çizim
        try:
            if game_state.state == "menu":
                menu.update(mouse_pos)
                menu.draw()
                
            elif game_state.state == "profile":
                profile_menu.draw(game_state.current_user)
                
            elif game_state.state == "leaderboard":
                scores = db.get_high_scores() if db else []
                leaderboard.draw(scores)
                
            elif game_state.state == "settings":
                settings_menu.draw()
                
            elif game_state.state == "game":
                # Önce arkaplanı çiz
                if 'current_background' in globals() and current_background is not None:
                    screen.blit(current_background, (0, 0))
                else:
                    screen.fill((44, 62, 80))  # yedek koyu mavi arka plan
                
                # Oyun nesnelerini çiz
                platform.draw(screen)
                ball.draw(screen)
                block_manager.draw(screen)
                power_up_manager.draw(screen)
                
                # HUD (Heads-Up Display)
                score_text = default_font.render(f"Skor: {game_state.score}", True, WHITE)
                level_text = default_font.render(f"Level: {game_state.level}", True, WHITE)
                lives_text = default_font.render(f"Can: {game_state.lives}", True, WHITE)
                
                screen.blit(score_text, (10, 10))
                screen.blit(level_text, (screen_width - 100, 10))
                screen.blit(lives_text, (10, screen_height - 30))
                
                # Duraklatma menüsü
                if game_state.paused:
                    # Yarı saydam siyah overlay
                    overlay = pygame.Surface((screen_width, screen_height))
                    overlay.fill((0, 0, 0))
                    overlay.set_alpha(128)
                    screen.blit(overlay, (0, 0))
                    
                    pause_text = default_font.render("OYUN DURAKLATILDI", True, WHITE)
                    continue_text = default_font.render("Devam etmek için ESC'ye basın", True, WHITE)
                    menu_text = default_font.render("Ana menüye dönmek için M'ye basın", True, WHITE)
                    
                    screen.blit(pause_text, (screen_width//2 - pause_text.get_width()//2, screen_height//2 - 60))
                    screen.blit(continue_text, (screen_width//2 - continue_text.get_width()//2, screen_height//2))
                    screen.blit(menu_text, (screen_width//2 - menu_text.get_width()//2, screen_height//2 + 40))
                
            elif game_state.state == "login":
                draw_modern_login_screen()
                
            elif game_state.state == "register":
                draw_modern_register_screen()
                
            elif game_state.state == "game_over":
                game_over_menu.draw(game_state.score)
                
            elif game_state.state == "game_won":
                game_over_menu.draw_win_screen(game_state.score)
                
            # Hata mesajını göster
            if game_state.error_message:
                error_text = button_font.render(game_state.error_message, True, RED)
                error_rect = error_text.get_rect(center=(screen_width // 2, screen_height - 30))
                screen.blit(error_text, error_rect)
                
        except Exception as e:
            print(f"Çizim hatası: {e}")
            
        # Ekranı güncelle
        pygame.display.flip()
        
    except Exception as e:
        print(f"Ana döngü hatası: {e}")
        continue

# Oyunu kapat
pygame.quit()
sys.exit()

