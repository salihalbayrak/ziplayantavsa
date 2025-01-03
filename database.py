import sqlite3
from game_states import GameError
import hashlib

class Database:
    def __init__(self):
        try:
            self.conn = sqlite3.connect('scores.db')
            self.create_tables()
        except Exception as e:
            raise GameError(f"Veritabanı başlatma hatası: {str(e)}", "database")
            
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                email TEXT,
                high_score INTEGER DEFAULT 0,
                total_games INTEGER DEFAULT 0,
                play_time INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
        
    def close(self):
        if hasattr(self, 'conn'):
            self.conn.close()
            
    def get_high_scores(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT username, high_score 
                FROM users 
                ORDER BY high_score DESC 
                LIMIT 10
            """)
            return cursor.fetchall()
        except Exception as e:
            raise GameError(f"Skor tablosu yüklenemedi: {str(e)}", "database")
            
    def hash_password(self, password):
        """Şifreyi güvenli bir şekilde hashle"""
        return hashlib.sha256(password.encode()).hexdigest()
            
    def register_user(self, username, password, email):
        """Yeni kullanıcı kaydı oluştur"""
        try:
            cursor = self.conn.cursor()
            
            # Kullanıcı adı kontrolü
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return False  # Kullanıcı adı zaten var
                
            # Şifreyi hashle
            hashed_password = self.hash_password(password)
            
            # Yeni kullanıcıyı ekle
            cursor.execute("""
                INSERT INTO users (username, password, email)
                VALUES (?, ?, ?)
            """, (username, hashed_password, email))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            raise GameError(f"Kullanıcı kaydı oluşturulamadı: {str(e)}", "database")
            
    def login_user(self, username, password):
        """Kullanıcı girişi kontrol et"""
        try:
            cursor = self.conn.cursor()
            
            # Şifreyi hashle
            hashed_password = self.hash_password(password)
            
            # Kullanıcıyı kontrol et
            cursor.execute("""
                SELECT username, email, high_score, total_games, play_time
                FROM users 
                WHERE username = ? AND password = ?
            """, (username, hashed_password))
            
            user_data = cursor.fetchone()
            if user_data:
                return {
                    'username': user_data[0],
                    'email': user_data[1],
                    'high_score': user_data[2],
                    'total_games': user_data[3],
                    'play_time': user_data[4],
                    'achievements': []  # Başarımlar için ayrı bir tablo oluşturulabilir
                }
            return None
            
        except Exception as e:
            raise GameError(f"Giriş yapılamadı: {str(e)}", "database")
            
    def update_high_score(self, username, score):
        """Kullanıcının yüksek skorunu güncelle"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET high_score = MAX(high_score, ?)
                WHERE username = ?
            """, (score, username))
            self.conn.commit()
        except Exception as e:
            raise GameError(f"Yüksek skor güncellenemedi: {str(e)}", "database")
            
    def update_stats(self, username, play_time=0):
        """Kullanıcı istatistiklerini güncelle"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET total_games = total_games + 1,
                    play_time = play_time + ?
                WHERE username = ?
            """, (play_time, username))
            self.conn.commit()
        except Exception as e:
            raise GameError(f"İstatistikler güncellenemedi: {str(e)}", "database") 