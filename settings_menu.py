import pygame
import json
from settings import Settings

class SettingsMenu:
    def __init__(self, screen, screen_width, screen_height, db):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.db = db
        self.settings = Settings()
        
        # Renkler
        self.colors = {
            "background": (44, 62, 80),
            "text": (236, 240, 241),
            "button": self.settings.get_setting("graphics", "button_color"),
            "button_hover": self.settings.get_setting("graphics", "button_hover_color"),
            "slider_bg": (149, 165, 166),
            "slider_fg": (46, 204, 113),
            "category_active": self.settings.get_setting("graphics", "active_color"),
            "category_inactive": self.settings.get_setting("graphics", "button_color")
        }
        
        # Fontlar
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 32)
        
        # Kategoriler ve ayarlar
        self.categories = ["Ses", "Grafik", "Kontroller", "Oynanış"]
        self.current_category = 0
        
        # UI elemanları
        self.sliders = {}
        self.buttons = {}
        self.checkboxes = {}
        self.create_ui_elements()
        
        # Aktif elemanlar
        self.active_slider = None
        self.dragging = False
        
    def create_ui_elements(self):
        # Ses ayarları için sliderlar
        self.sliders["sound"] = {
            "Ana Ses": {"value": self.settings.get_setting("sound", "master_volume"), "key": "master_volume"},
            "Müzik": {"value": self.settings.get_setting("sound", "music_volume"), "key": "music_volume"},
            "Efektler": {"value": self.settings.get_setting("sound", "effects_volume"), "key": "effects_volume"}
        }
        
        # Grafik ayarları için checkboxlar ve tema butonları
        self.checkboxes["graphics"] = {
            "Parçacık Efektleri": {"value": self.settings.get_setting("graphics", "particle_effects"), "key": "particle_effects"},
            "Ekran Sarsıntısı": {"value": self.settings.get_setting("graphics", "screen_shake"), "key": "screen_shake"}
        }
        
        # Tema butonları
        self.theme_buttons = {
            "classic": {
                "rect": pygame.Rect(50, 280, 120, 40),
                "text": "Klasik",
                "colors": self.settings.theme_colors["classic"]
            },
            "desert": {
                "rect": pygame.Rect(190, 280, 120, 40),
                "text": "Çöl",
                "colors": self.settings.theme_colors["desert"]
            },
            "ice": {
                "rect": pygame.Rect(330, 280, 120, 40),
                "text": "Buz",
                "colors": self.settings.theme_colors["ice"]
            }
        }
        
        # Kontrol ayarları için checkboxlar ve sliderlar
        self.checkboxes["controls"] = {
            "Klavye Aktif": {"value": self.settings.get_setting("controls", "keyboard_enabled"), "key": "keyboard_enabled"},
            "Fare Aktif": {"value": self.settings.get_setting("controls", "mouse_enabled"), "key": "mouse_enabled"}
        }
        self.sliders["controls"] = {
            "Fare Hassasiyeti": {"value": self.settings.get_setting("controls", "mouse_sensitivity"), "key": "mouse_sensitivity"}
        }
        
        # Oynanış ayarları için sliderlar
        self.sliders["gameplay"] = {
            "Top Hızı": {"value": self.settings.get_setting("gameplay", "ball_speed"), "key": "ball_speed"},
            "Platform Boyutu": {"value": self.settings.get_setting("gameplay", "platform_size"), "key": "platform_size"},
            "Güçlendirme Sıklığı": {"value": self.settings.get_setting("gameplay", "power_up_frequency"), "key": "power_up_frequency"}
        }
        
        # Butonlar
        button_width = 200
        button_height = 40
        self.buttons = {
            "save": pygame.Rect(self.screen_width - button_width - 20, self.screen_height - button_height - 20,
                              button_width, button_height),
            "reset": pygame.Rect(20, self.screen_height - button_height - 20,
                               button_width, button_height)
        }
        
    def draw(self):
        # Arka plan
        self.screen.fill(self.colors["background"])
        
        # Başlık
        title = self.title_font.render("AYARLAR", True, self.colors["text"])
        title_rect = title.get_rect(centerx=self.screen_width//2, y=20)
        self.screen.blit(title, title_rect)
        
        # Kategoriler
        self.draw_categories()
        
        # Aktif kategori ayarları
        if self.current_category == 0:  # Ses
            self.draw_sliders("sound")
        elif self.current_category == 1:  # Grafik
            self.draw_checkboxes("graphics")
            self.draw_theme_buttons()  # Tema butonlarını çiz
        elif self.current_category == 2:  # Kontroller
            self.draw_checkboxes("controls")
            self.draw_sliders("controls")
        elif self.current_category == 3:  # Oynanış
            self.draw_sliders("gameplay")
            
        # Butonlar
        self.draw_buttons()
        
    def draw_categories(self):
        total_width = len(self.categories) * 150
        start_x = (self.screen_width - total_width) // 2
        
        for i, category in enumerate(self.categories):
            color = self.colors["category_active"] if i == self.current_category else self.colors["category_inactive"]
            text = self.text_font.render(category, True, self.colors["text"])
            rect = pygame.Rect(start_x + i * 150, 80, 140, 40)
            
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
            
    def draw_sliders(self, category):
        start_y = 150
        for i, (name, data) in enumerate(self.sliders.get(category, {}).items()):
            # Slider başlığı
            text = self.text_font.render(f"{name}: {int(data['value'] * 100)}%", True, self.colors["text"])
            self.screen.blit(text, (50, start_y + i * 80))
            
            # Slider arka planı
            slider_rect = pygame.Rect(50, start_y + i * 80 + 30, 300, 10)
            pygame.draw.rect(self.screen, self.colors["slider_bg"], slider_rect, border_radius=5)
            
            # Slider değeri
            value_rect = pygame.Rect(50, start_y + i * 80 + 30, 300 * data["value"], 10)
            pygame.draw.rect(self.screen, self.colors["slider_fg"], value_rect, border_radius=5)
            
            # Slider düğmesi
            knob_pos = (50 + 300 * data["value"], start_y + i * 80 + 35)
            pygame.draw.circle(self.screen, self.colors["slider_fg"], knob_pos, 10)
            
    def draw_checkboxes(self, category):
        start_y = 150
        for i, (name, data) in enumerate(self.checkboxes.get(category, {}).items()):
            # Checkbox metni
            text = self.text_font.render(name, True, self.colors["text"])
            self.screen.blit(text, (50, start_y + i * 50))
            
            # Checkbox
            checkbox_rect = pygame.Rect(300, start_y + i * 50, 20, 20)
            pygame.draw.rect(self.screen, self.colors["text"], checkbox_rect, 2)
            
            if data["value"]:
                pygame.draw.rect(self.screen, self.colors["slider_fg"], 
                               checkbox_rect.inflate(-6, -6))
                
    def draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for name, rect in self.buttons.items():
            color = self.colors["button_hover"] if rect.collidepoint(mouse_pos) else self.colors["button"]
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            
            text = self.text_font.render("Kaydet" if name == "save" else "Sıfırla", True, self.colors["text"])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
            
    def draw_theme_buttons(self):
        current_theme = self.settings.get_setting("graphics", "theme")
        mouse_pos = pygame.mouse.get_pos()
        
        # Tema seçimi başlığı
        text = self.text_font.render("Tema Seçimi:", True, self.colors["text"])
        self.screen.blit(text, (50, 240))
        
        # Tema butonları
        for theme_id, theme in self.theme_buttons.items():
            # Buton rengi (aktif tema veya hover durumu)
            if theme_id == current_theme:
                color = theme["colors"]["active"]
            elif theme["rect"].collidepoint(mouse_pos):
                color = theme["colors"]["button_hover"]
            else:
                color = theme["colors"]["button"]
                
            # Buton çizimi
            pygame.draw.rect(self.screen, color, theme["rect"], border_radius=5)
            
            # Buton metni
            text = self.text_font.render(theme["text"], True, self.colors["text"])
            text_rect = text.get_rect(center=theme["rect"].center)
            self.screen.blit(text, text_rect)
            
            # Renk önizlemesi
            preview_rect = pygame.Rect(theme["rect"].centerx - 25, theme["rect"].bottom + 10, 50, 10)
            pygame.draw.rect(self.screen, theme["colors"]["button"], preview_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Kategori seçimi
            if 80 <= event.pos[1] <= 120:
                total_width = len(self.categories) * 150
                start_x = (self.screen_width - total_width) // 2
                for i in range(len(self.categories)):
                    if start_x + i * 150 <= event.pos[0] <= start_x + (i + 1) * 150:
                        self.current_category = i
                        return True
            
            # Tema butonları kontrolü
            if self.current_category == 1:  # Grafik kategorisi
                for theme_id, theme in self.theme_buttons.items():
                    if theme["rect"].collidepoint(event.pos):
                        # Temayı uygula
                        self.settings.apply_theme(theme_id)
                        # Menü renklerini güncelle
                        self.colors.update({
                            "button": self.settings.get_setting("graphics", "button_color"),
                            "button_hover": self.settings.get_setting("graphics", "button_hover_color"),
                            "category_active": self.settings.get_setting("graphics", "active_color"),
                            "category_inactive": self.settings.get_setting("graphics", "button_color")
                        })
                        self.save_settings()
                        return True
            
            # Slider kontrolü
            if self.current_category in [0, 2, 3]:  # Ses, Kontroller, Oynanış
                category = ["sound", "controls", "gameplay"][self.current_category]
                for name, data in self.sliders.get(category, {}).items():
                    slider_rect = pygame.Rect(50, 150 + list(self.sliders[category].keys()).index(name) * 80 + 30, 300, 20)
                    if slider_rect.collidepoint(event.pos):
                        self.active_slider = (category, name)
                        self.dragging = True
                        return True
            
            # Checkbox kontrolü
            if self.current_category in [1, 2]:  # Grafik, Kontroller
                category = ["graphics", "controls"][self.current_category - 1]
                for name, data in self.checkboxes.get(category, {}).items():
                    checkbox_rect = pygame.Rect(300, 150 + list(self.checkboxes[category].keys()).index(name) * 50, 20, 20)
                    if checkbox_rect.collidepoint(event.pos):
                        data["value"] = not data["value"]
                        self.settings.set_setting(category, data["key"], data["value"])
                        return True
            
            # Buton kontrolü
            for name, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    if name == "save":
                        self.save_settings()
                    elif name == "reset":
                        self.reset_settings()
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
                self.active_slider = None
                self.save_settings()
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging and self.active_slider:
                category, name = self.active_slider
                slider_rect = pygame.Rect(50, 150 + list(self.sliders[category].keys()).index(name) * 80 + 30, 300, 20)
                value = (event.pos[0] - slider_rect.x) / slider_rect.width
                value = max(0, min(1, value))
                self.sliders[category][name]["value"] = value
                self.settings.set_setting(category, self.sliders[category][name]["key"], value)
                return True
                
        return False
        
    def save_settings(self):
        self.settings.save_settings()
        self.settings.apply_sound_settings()
        self.settings.apply_graphics_settings()
        self.settings.apply_control_settings()
        self.settings.apply_gameplay_settings()
        
    def reset_settings(self):
        self.settings.reset_to_default()
        self.create_ui_elements()  # UI elemanlarını varsayılan değerlerle yeniden oluştur 