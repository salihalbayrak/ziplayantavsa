import random
import pygame
import os
import math

class LevelSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.current_level = 1
        self.max_level = 3  # Maksimum seviye sayısı
        self.levels = {}
        
        # Seviye tasarımları
        self.level_designs = {
            1: {
                "background": "Assests/tas/taşlı_kısım.png",
                "platform": "Assests/tas/alt_platform_taş.png",
                "block_single_hit": "Assests/tas/tek_vuruş_taş.png", 
                "block_double_hit": "Assests/tas/iki_vuruş_taş.png",
                "block_break_sound": "Assests/tas/taş_blok_kırılma.mp3",
                "sticky_platform": "Assests/tas/tasyapisgan.png"
            },
            2: {
                "background": "Assests/col/çöl_kısmı.png",
                "platform": "Assests/col/alt_platform_çöl.png",
                "block_single_hit": "Assests/col/tek_vuruş_çöl.png",
                "block_double_hit": "Assests/col/iki_vuruş_çöl.png", 
                "block_break_sound": "Assests/col/cam_kırılma.mp3",
                "sticky_platform": "Assests/col/colyapisgan.png"
            },
            3: {
                "background": "Assests/buz/Buzlu_kısım_background.png",
                "platform": "Assests/buz/alt_platform_buz.png",
                "block_single_hit": "Assests/buz/tek_vuruş_buz.png",
                "block_double_hit": "Assests/buz/iki_vuruşta_buz.png",
                "block_break_sound": "Assests/buz/buzsesi.mp3",
                "boss": "Assests/buz/son_bölüm_yeni.png",
                "sticky_platform": "Assests/buz/buzyapisgan.png"
            }
        }
        
        # Ekstra sesler
        self.extra_sounds = {
            "menu_music": "Assests/sound/giriş_ekranı_sesi.mp3",
            "level_up": "Assests/sound/level_atlama.mp3",
            "lose_game": "Assests/sound/kaybetme_sesi.mp3"
        }
        
        self.create_levels()
        
    def create_levels(self):
        # Her seviye için blok düzenini oluştur
        for level in range(1, 11):  # 10 seviye
            self.levels[level] = {
                "block_count": 3 + level * 2,  # Her seviyede artan blok sayısı
                "hard_block_chance": min(0.1 * level, 0.5),  # Sert blok olasılığı (max %50)
                "special_block_chance": min(0.05 * level, 0.3),  # Özel blok olasılığı (max %30)
                "powerup_chance": min(0.2 + 0.02 * level, 0.4),  # Power-up düşme olasılığı (max %40)
                "ball_speed": min(5 + level * 0.5, 10),  # Top hızı (max 10)
                "points_multiplier": 1 + level * 0.1,  # Puan çarpanı
                "block_types": self.get_level_block_types(level)  # Seviyeye özel blok türleri
            }
            
    def get_level_block_types(self, level):
        # Temel blok türleri
        block_types = ["normal", "hard"]
        
        # Seviye 3'ten sonra özel bloklar ekle
        if level >= 3:
            block_types.extend(["explosive", "multi_hit"])
        
        # Seviye 5'ten sonra daha fazla özel blok
        if level >= 5:
            block_types.extend(["power_up", "mystery"])
            
        # Seviye 7'den sonra nadir bloklar
        if level >= 7:
            block_types.extend(["indestructible", "moving"])
            
        return block_types
            
    def get_level_layout(self, level, block_manager):
        if level > 10:
            level = 10  # Maksimum seviye
            
        level_data = self.levels[level]
        
        # Blok yöneticisini temizle
        block_manager.blocks.clear()
        
        # Seviyeye göre farklı dizilim desenleri
        patterns = [
            self.create_random_pattern,
            self.create_zigzag_pattern,
            self.create_diamond_pattern,
            self.create_circle_pattern,
            self.create_v_pattern
        ]
        
        # Rastgele bir desen seç
        selected_pattern = random.choice(patterns)
        selected_pattern(level, level_data, block_manager)
        
        # Blok görsellerini ayarla
        if level in self.level_designs:
            design = self.level_designs[level]
            for block in block_manager.blocks:
                if block.block_type == "normal" and "block_single_hit" in design:
                    img = pygame.image.load(design["block_single_hit"])
                    block.image = pygame.transform.scale(img, (block.rect.width, block.rect.height))
                elif block.block_type == "hard" and "block_double_hit" in design:
                    img = pygame.image.load(design["block_double_hit"])
                    block.double_hit_image = pygame.transform.scale(img, (block.rect.width, block.rect.height))
                    block.image = block.double_hit_image
                elif block.block_type == "boss" and "boss" in design:
                    img = pygame.image.load(design["boss"])
                    block.image = pygame.transform.scale(img, (block.rect.width, block.rect.height))
        
        return {
            "ball_speed": level_data["ball_speed"],
            "points_multiplier": level_data["points_multiplier"]
        }

    def create_random_pattern(self, level, level_data, block_manager):
        """Tamamen rastgele blok dizilimi"""
        rows = min(3 + level, 8)
        cols = self.screen_width // (block_manager.block_width + block_manager.padding)
        
        for row in range(rows):
            for col in range(cols):
                if random.random() < 0.7:  # %70 blok oluşturma şansı
                    x = col * (block_manager.block_width + block_manager.padding)
                    y = row * (block_manager.block_height + block_manager.padding) + 50
                    
                    # Blok türünü belirle
                    if random.random() < level_data["hard_block_chance"]:
                        block_type = "hard"
                    elif random.random() < level_data["special_block_chance"] and len(level_data["block_types"]) > 2:
                        block_type = random.choice(level_data["block_types"][2:])
                    else:
                        block_type = "normal"
                        
                    block_manager.create_block(x, y, block_type, level_data["powerup_chance"])

    def create_zigzag_pattern(self, level, level_data, block_manager):
        """Zigzag şeklinde blok dizilimi"""
        rows = min(3 + level, 8)
        cols = self.screen_width // (block_manager.block_width + block_manager.padding)
        
        for row in range(rows):
            start_col = row % 2  # Her satırda başlangıç noktasını değiştir
            for col in range(start_col, cols, 2):
                x = col * (block_manager.block_width + block_manager.padding)
                y = row * (block_manager.block_height + block_manager.padding) + 50
                
                block_type = self.get_random_block_type(level_data)
                block_manager.create_block(x, y, block_type, level_data["powerup_chance"])

    def create_diamond_pattern(self, level, level_data, block_manager):
        """Elmas şeklinde blok dizilimi"""
        rows = min(3 + level, 8)
        cols = self.screen_width // (block_manager.block_width + block_manager.padding)
        center_col = cols // 2
        
        for row in range(rows):
            distance_from_center = abs(row - rows//2)
            start_col = center_col - distance_from_center
            end_col = center_col + distance_from_center + 1
            
            for col in range(start_col, end_col):
                if 0 <= col < cols:
                    x = col * (block_manager.block_width + block_manager.padding)
                    y = row * (block_manager.block_height + block_manager.padding) + 50
                    
                    block_type = self.get_random_block_type(level_data)
                    block_manager.create_block(x, y, block_type, level_data["powerup_chance"])

    def create_circle_pattern(self, level, level_data, block_manager):
        """Daire şeklinde blok dizilimi"""
        rows = min(3 + level, 8)
        cols = self.screen_width // (block_manager.block_width + block_manager.padding)
        center_row = rows // 2
        center_col = cols // 2
        radius = min(rows, cols) // 2
        
        for row in range(rows):
            for col in range(cols):
                distance = math.sqrt((row - center_row)**2 + (col - center_col)**2)
                if distance <= radius:
                    x = col * (block_manager.block_width + block_manager.padding)
                    y = row * (block_manager.block_height + block_manager.padding) + 50
                    
                    block_type = self.get_random_block_type(level_data)
                    block_manager.create_block(x, y, block_type, level_data["powerup_chance"])

    def create_v_pattern(self, level, level_data, block_manager):
        """V şeklinde blok dizilimi"""
        rows = min(3 + level, 8)
        cols = self.screen_width // (block_manager.block_width + block_manager.padding)
        
        for row in range(rows):
            start_col = row
            end_col = cols - row
            
            for col in range(start_col, end_col):
                x = col * (block_manager.block_width + block_manager.padding)
                y = row * (block_manager.block_height + block_manager.padding) + 50
                
                block_type = self.get_random_block_type(level_data)
                block_manager.create_block(x, y, block_type, level_data["powerup_chance"])

    def get_random_block_type(self, level_data):
        """Rastgele blok türü seç"""
        if random.random() < level_data["hard_block_chance"]:
            return "hard"
        elif random.random() < level_data["special_block_chance"] and len(level_data["block_types"]) > 2:
            return random.choice(level_data["block_types"][2:])
        return "normal"
        
    def is_level_complete(self, block_manager):
        # Yıkılabilir blok kaldı mı kontrol et
        for block in block_manager.blocks:
            if block.block_type != "indestructible":
                return False
        return True
        
    def get_level_info(self, level):
        if level in self.levels:
            return self.levels[level]
        return None 
        
    def start_level(self, level):
        self.current_level = level
        return self.get_level_info(level) 
        
    def load_level_assets(self, level, platform):
        """Seviye görsellerini ve seslerini yükle"""
        print(f"Seviye {level} için görsel yükleniyor...")
        if level in self.level_designs:
            design = self.level_designs[level]
            print(f"Level tasarımı bulundu: {design}")
            
            # Platform görsellerini yükle ve boyutlandır
            if "platform" in design:
                print(f"Platform görseli yükleniyor: {design['platform']}")
                platform_img = pygame.image.load(design["platform"])
                platform.set_image(platform_img)
                
            if "sticky_platform" in design:
                print(f"Yapışkan platform görseli yükleniyor: {design['sticky_platform']}")
                sticky_img = pygame.image.load(design["sticky_platform"])
                platform.set_sticky_image(sticky_img)
                
            # Arka plan görselini yükle ve boyutlandır
            if "background" in design:
                try:
                    print(f"Arka plan yükleniyor: {design['background']}")
                    bg_img = pygame.image.load(design["background"])
                    scaled_bg = pygame.transform.scale(bg_img, (self.screen_width, self.screen_height))
                    print("Arka plan başarıyla yüklendi ve ölçeklendirildi")
                    return scaled_bg
                except Exception as e:
                    print(f"Arka plan yüklenemedi: {design['background']}, Hata: {e}")
                    return None
            else:
                print("Arka plan tasarımda bulunamadı")
        else:
            print(f"Seviye {level} için tasarım bulunamadı")
        return None 

    def is_game_complete(self, current_level):
        # Oyun bitişini kontrol et (3. seviye tamamlandıysa)
        return current_level > self.max_level