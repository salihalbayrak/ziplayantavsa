import pygame
import json

class GameSettings:
    def __init__(self, screen, screen_width, screen_height, db):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.db = db
        
        # Ses sistemini başlat
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            pygame.mixer.set_num_channels(8)  # 8 ses kanalı ayarla
        
        # Settings instance'ı oluştur
        from settings import Settings
        self.settings_manager = Settings()
        
        # Ses ayarlarını uygula
        self.settings_manager.apply_sound_settings()
        
        # Fontlar
        self.title_font = pygame.font.Font(None, int(0.08 * screen_height))
        self.text_font = pygame.font.Font(None, int(0.04 * screen_height))
        
        # Renkler
        self.colors = {
            "primary": (52, 152, 219),     # Ana renk (Mavi)
            "secondary": (46, 204, 113),    # İkincil renk (Yeşil)
            "accent": (155, 89, 182),       # Vurgu rengi (Mor)
            "warning": (231, 76, 60),       # Uyarı rengi (Kırmızı)
            "background": (44, 62, 80),     # Arka plan rengi (Koyu mavi)
            "text": (236, 240, 241)         # Metin rengi (Beyaz)
        }
        
        # Ayar kategorileri
        self.categories = ["Ses", "Görsel", "Kontroller"]
        self.current_category = 0
        
        # Ses ayarları
        self.sound_settings = {
            "master_volume": 1.0,
            "music_volume": 0.7,
            "effects_volume": 0.8
        }
        
        # Tema ayarları
        self.themes = ["Klasik", "Neon", "Retro"]
        self.current_theme = 0
        
        # Kontrol ayarları
        self.control_settings = {
            "up": "UP",
            "down": "DOWN",
            "pause": "P",
            "power": "SPACE"
        }
        
        # Geri butonu
        self.back_button = pygame.Rect(20, 20, 100, 40)
        
        try:
            self.background = pygame.image.load("images/arka_plan.jpg")
            self.background = pygame.transform.scale(self.background, (screen_width, screen_height))
        except:
            self.background = None
            
    def draw(self):
        # Arka plan
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.colors["background"])
            
        # Yarı saydam overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Başlık
        title = self.title_font.render("Ayarlar", True, self.colors["text"])
        title_rect = title.get_rect(center=(self.screen_width//2, self.screen_height * 0.1))
        self.screen.blit(title, title_rect)
        
        # Kategori seçici
        category_y = self.screen_height * 0.2
        for i, category in enumerate(self.categories):
            text = self.text_font.render(category, True, 
                                       self.colors["secondary"] if i == self.current_category 
                                       else self.colors["text"])
            text_rect = text.get_rect(center=(self.screen_width * (0.25 + i * 0.25), category_y))
            self.screen.blit(text, text_rect)
            
            if i == self.current_category:
                pygame.draw.line(self.screen, self.colors["secondary"],
                               (text_rect.left, text_rect.bottom + 5),
                               (text_rect.right, text_rect.bottom + 5), 3)
        
        # Kategori içeriği
        content_y = self.screen_height * 0.3
        if self.current_category == 0:  # Ses ayarları
            self.draw_sound_settings(content_y)
        elif self.current_category == 1:  # Görsel ayarları
            self.draw_theme_settings(content_y)
        elif self.current_category == 2:  # Kontrol ayarları
            self.draw_control_settings(content_y)
            
        # Geri butonu
        pygame.draw.rect(self.screen, self.colors["warning"], self.back_button, border_radius=5)
        back_text = self.text_font.render("Geri", True, self.colors["text"])
        text_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, text_rect)
            
    def draw_sound_settings(self, start_y):
        sound_settings = self.settings_manager.settings["sound"]
        i = 0
        for name, value in sound_settings.items():
            if name == "mute":  # mute ayarını gösterme
                continue
                
            # Slider başlığı ve değer gösterimi
            display_name = {
                "master_volume": "Ana Ses",
                "music_volume": "Müzik Sesi",
                "effects_volume": "Efekt Sesleri"
            }.get(name, name.replace("_", " ").title())
            
            # Ses seviyesi hesaplama
            if name == "music_volume":
                display_value = value * sound_settings["master_volume"]
            elif name == "effects_volume":
                display_value = value * sound_settings["master_volume"]
            else:
                display_value = value
            
            text = self.text_font.render(display_name, True, self.colors["text"])
            self.screen.blit(text, (self.screen_width * 0.2, start_y + i * 80))
            
            # Slider çubuğu
            slider_rect = pygame.Rect(self.screen_width * 0.4, start_y + i * 80 + 30, 
                                    200, 10)
            pygame.draw.rect(self.screen, self.colors["text"], slider_rect)
            
            # Slider değeri
            value_rect = pygame.Rect(self.screen_width * 0.4, start_y + i * 80 + 30,
                                   200 * value, 10)
            pygame.draw.rect(self.screen, self.colors["primary"], value_rect)
            
            # Değer yüzdesi (gerçek ses seviyesini göster)
            value_text = self.text_font.render(f"{int(display_value * 100)}%", True, self.colors["text"])
            self.screen.blit(value_text, (self.screen_width * 0.4 + 220, start_y + i * 80 + 20))
            
            i += 1
            
    def draw_theme_settings(self, start_y):
        for i, theme in enumerate(self.themes):
            button_rect = pygame.Rect(self.screen_width * 0.3 + i * 150, start_y,
                                    120, 40)
            color = self.colors["secondary"] if i == self.current_theme else self.colors["primary"]
            pygame.draw.rect(self.screen, color, button_rect, border_radius=5)
            
            text = self.text_font.render(theme, True, self.colors["text"])
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
    def draw_control_settings(self, start_y):
        for i, (action, key) in enumerate(self.control_settings.items()):
            text = self.text_font.render(f"{action.title()}: {key}", True, self.colors["text"])
            self.screen.blit(text, (self.screen_width * 0.3, start_y + i * 40))
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Geri butonu kontrolü
            if self.back_button.collidepoint(mouse_pos):
                # Ayarları kaydet ve uygula
                self.settings_manager.save_settings()
                self.settings_manager.apply_sound_settings()
                return "menu"
            
            # Kategori seçimi
            category_y = self.screen_height * 0.2
            for i in range(len(self.categories)):
                rect = pygame.Rect(self.screen_width * (0.25 + i * 0.25) - 50,
                                 category_y - 20, 100, 40)
                if rect.collidepoint(mouse_pos):
                    self.current_category = i
                    return None
                    
            # Ses ayarları
            if self.current_category == 0:
                content_y = self.screen_height * 0.3
                sound_settings = self.settings_manager.settings["sound"]
                i = 0
                for key in sound_settings:
                    if key == "mute":  # mute ayarını atla
                        continue
                    slider_rect = pygame.Rect(self.screen_width * 0.4,
                                            content_y + i * 80 + 30, 200, 10)
                    if slider_rect.collidepoint(mouse_pos):
                        value = (mouse_pos[0] - slider_rect.x) / slider_rect.width
                        value = max(0, min(1, value))
                        self.settings_manager.set_setting("sound", key, value)
                        # Ses ayarlarını hemen uygula
                        self.settings_manager.apply_sound_settings()
                        return None
                    i += 1
                        
            # Tema ayarları
            elif self.current_category == 1:
                content_y = self.screen_height * 0.3
                for i in range(len(self.themes)):
                    button_rect = pygame.Rect(self.screen_width * 0.3 + i * 150,
                                            content_y, 120, 40)
                    if button_rect.collidepoint(mouse_pos):
                        self.current_theme = i
                        self.save_settings()
                        return None
                        
        return None
        
    def save_settings(self):
        if not hasattr(self, 'game_state') or not self.game_state.is_logged_in():
            return
            
        settings = {
            'sound': self.sound_settings,
            'theme': self.themes[self.current_theme],
            'controls': self.control_settings
        }
        
        try:
            if self.db and hasattr(self.db, 'update_user_settings'):
                self.db.update_user_settings(
                    self.game_state.current_user['username'],
                    settings
                )
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata oluştu: {e}")
        
    def load_settings(self):
        if not hasattr(self, 'game_state') or not self.game_state.is_logged_in():
            return
            
        try:
            if self.db and hasattr(self.db, 'get_user_settings'):
                settings = self.db.get_user_settings(
                    self.game_state.current_user['username']
                )
                if settings:
                    self.sound_settings = settings.get("sound", self.sound_settings)
                    try:
                        self.current_theme = self.themes.index(settings.get("theme", self.themes[0]))
                    except ValueError:
                        self.current_theme = 0
                    self.control_settings = settings.get("controls", self.control_settings)
        except Exception as e:
            print(f"Ayarlar yüklenirken hata oluştu: {e}")
            
    def set_game_state(self, game_state):
        self.game_state = game_state 