import pygame

class Profile:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        
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
        
        # Geri butonu
        self.back_button = pygame.Rect(20, 20, 100, 40)
        
        try:
            self.background = pygame.image.load("images/arka_plan.jpg")
            self.background = pygame.transform.scale(self.background, (screen_width, screen_height))
        except:
            self.background = None
        
    def draw(self, user_data):
        if not user_data:
            return
            
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
        title = self.title_font.render("Profil", True, self.colors["text"])
        title_rect = title.get_rect(center=(self.screen_width//2, self.screen_height * 0.1))
        self.screen.blit(title, title_rect)
        
        # Kullanıcı bilgileri
        info_y = self.screen_height * 0.25
        spacing = 50
        
        # Kullanıcı adı
        username_text = self.text_font.render(f"Kullanıcı Adı: {user_data.get('username', 'N/A')}", 
                                            True, self.colors["text"])
        self.screen.blit(username_text, (self.screen_width * 0.2, info_y))
        
        # E-posta
        email_text = self.text_font.render(f"E-posta: {user_data.get('email', 'N/A')}", 
                                         True, self.colors["text"])
        self.screen.blit(email_text, (self.screen_width * 0.2, info_y + spacing))
        
        # En yüksek skor
        score_text = self.text_font.render(f"En Yüksek Skor: {user_data.get('high_score', 0)}", 
                                         True, self.colors["text"])
        self.screen.blit(score_text, (self.screen_width * 0.2, info_y + spacing * 2))
        
        # Toplam oyun sayısı
        games_text = self.text_font.render(f"Toplam Oyun: {user_data.get('total_games', 0)}", 
                                         True, self.colors["text"])
        self.screen.blit(games_text, (self.screen_width * 0.2, info_y + spacing * 3))
        
        # Toplam oynama süresi
        play_time = user_data.get('play_time', 0)
        hours = play_time // 3600
        minutes = (play_time % 3600) // 60
        time_text = self.text_font.render(f"Toplam Süre: {hours}s {minutes}d", 
                                        True, self.colors["text"])
        self.screen.blit(time_text, (self.screen_width * 0.2, info_y + spacing * 4))
        
        # Ortalama skor
        avg_score = user_data.get('avg_score', 0)
        avg_text = self.text_font.render(f"Ortalama Skor: {int(avg_score)}", 
                                       True, self.colors["text"])
        self.screen.blit(avg_text, (self.screen_width * 0.2, info_y + spacing * 5))
        
        # Başarımlar
        achievements = user_data.get('achievements', [])
        if achievements:
            achievements_title = self.text_font.render("Başarımlar:", True, self.colors["secondary"])
            self.screen.blit(achievements_title, (self.screen_width * 0.2, info_y + spacing * 6))
            
            for i, achievement in enumerate(achievements):
                achievement_text = self.text_font.render(f"• {achievement}", True, self.colors["text"])
                self.screen.blit(achievement_text, 
                               (self.screen_width * 0.25, info_y + spacing * (7 + i)))
                               
        # Geri butonu
        pygame.draw.rect(self.screen, self.colors["warning"], self.back_button, border_radius=5)
        back_text = self.text_font.render("Geri", True, self.colors["text"])
        text_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.collidepoint(event.pos):
                return "menu"
        return None 