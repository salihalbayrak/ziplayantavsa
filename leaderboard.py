import pygame
import json
from datetime import datetime, timedelta

class Leaderboard:
    def __init__(self, screen, screen_width, screen_height):
        self.screen = screen
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Fontlar
        self.title_font = pygame.font.Font(None, int(0.08 * screen_height))
        self.header_font = pygame.font.Font(None, int(0.05 * screen_height))
        self.text_font = pygame.font.Font(None, int(0.04 * screen_height))
        
        # Renkler
        self.colors = {
            "primary": (52, 152, 219),     # Ana renk (Mavi)
            "secondary": (46, 204, 113),    # İkincil renk (Yeşil)
            "accent": (155, 89, 182),       # Vurgu rengi (Mor)
            "warning": (231, 76, 60),       # Uyarı rengi (Kırmızı)
            "background": (44, 62, 80),     # Arka plan rengi (Koyu mavi)
            "text": (236, 240, 241),        # Metin rengi (Beyaz)
            "gold": (255, 215, 0),          # Altın
            "silver": (192, 192, 192),      # Gümüş
            "bronze": (205, 127, 50)        # Bronz
        }
        
        # Kategoriler
        self.categories = ["Tüm Zamanlar", "Bu Hafta", "Bugün"]
        self.current_category = 0
        
        # Animasyon değişkenleri
        self.animation_offset = 0
        self.target_offset = 0
        
        # Geri butonu
        self.back_button = pygame.Rect(20, 20, 100, 40)
        
        try:
            self.background = pygame.image.load("images/arka_plan.jpg")
            self.background = pygame.transform.scale(self.background, (screen_width, screen_height))
        except:
            self.background = None
        
    def draw_score_card(self, pos, rank, score_data, highlight=False):
        x, y = pos
        width = self.screen_width * 0.8
        height = 60
        
        # Kart arka planı
        card_color = self.colors["primary"] if highlight else (41, 128, 185)
        pygame.draw.rect(self.screen, card_color, 
                        (x, y + self.animation_offset, width, height), 
                        border_radius=10)
        
        # Sıralama madalyası
        if rank <= 3:
            medal_colors = [self.colors["gold"], self.colors["silver"], self.colors["bronze"]]
            pygame.draw.circle(self.screen, medal_colors[rank-1], 
                             (x + 30, y + height//2 + self.animation_offset), 20)
            rank_text = self.header_font.render(str(rank), True, self.colors["text"])
        else:
            rank_text = self.header_font.render(f"#{rank}", True, self.colors["text"])
        
        rank_rect = rank_text.get_rect(center=(x + 30, y + height//2 + self.animation_offset))
        self.screen.blit(rank_text, rank_rect)
        
        # Oyuncu bilgileri (score_data bir tuple: (username, score))
        username, score = score_data
        name_text = self.text_font.render(str(username), True, self.colors["text"])
        score_text = self.text_font.render(str(score), True, self.colors["text"])
        
        self.screen.blit(name_text, (x + 80, y + 20 + self.animation_offset))
        self.screen.blit(score_text, (x + width - 150, y + 20 + self.animation_offset))
        
    def draw(self, scores):
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
        title = self.title_font.render("En Yüksek Skorlar", True, self.colors["text"])
        title_rect = title.get_rect(center=(self.screen_width//2, self.screen_height * 0.08))
        self.screen.blit(title, title_rect)
        
        # Kategori seçici
        category_y = self.screen_height * 0.15
        total_width = sum(self.text_font.size(cat)[0] for cat in self.categories) + 40 * (len(self.categories) - 1)
        start_x = (self.screen_width - total_width) // 2
        
        for i, category in enumerate(self.categories):
            text = self.text_font.render(category, True, 
                                       self.colors["secondary"] if i == self.current_category 
                                       else self.colors["text"])
            text_rect = text.get_rect(center=(start_x + i * (total_width // len(self.categories)), category_y))
            self.screen.blit(text, text_rect)
            
            if i == self.current_category:
                pygame.draw.line(self.screen, self.colors["secondary"], 
                               (text_rect.left, text_rect.bottom + 5),
                               (text_rect.right, text_rect.bottom + 5), 3)
        
        # Skor kartları
        if scores:
            start_y = self.screen_height * 0.25
            card_spacing = 70
            
            for i, score_data in enumerate(scores):
                self.draw_score_card(
                    (self.screen_width * 0.1, start_y + i * card_spacing),
                    i + 1,
                    score_data
                )
        else:
            # Skor yoksa mesaj göster
            no_scores_text = self.text_font.render("Henüz skor kaydı yok", True, self.colors["text"])
            text_rect = no_scores_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(no_scores_text, text_rect)
            
        # Geri butonu
        pygame.draw.rect(self.screen, self.colors["warning"], self.back_button, border_radius=5)
        back_text = self.text_font.render("Geri", True, self.colors["text"])
        text_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, text_rect)
        
        # Animasyon güncelleme
        if self.animation_offset != self.target_offset:
            self.animation_offset += (self.target_offset - self.animation_offset) * 0.1
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Geri butonu kontrolü
            if self.back_button.collidepoint(event.pos):
                return "menu"
                
            # Kategori seçimi
            category_y = self.screen_height * 0.15
            for i in range(len(self.categories)):
                rect = pygame.Rect(self.screen_width * (0.25 + i * 0.25) - 50,
                                 category_y - 20, 100, 40)
                if rect.collidepoint(event.pos):
                    self.current_category = i
                    return None
        return None 