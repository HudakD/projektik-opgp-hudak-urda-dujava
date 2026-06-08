import os
from src.settings import SCORE_FILE, MAX_HIGHSCORES, COINS_FILE

class ScoreManager:
    def __init__(self):
        self.current_score = 0
        self.highscores = self.load_highscores()
        self.coins = self.load_coins()
        self.session_coins = 0
        self.unlocked_skins = self.load_unlocked_skins()
        if 0 not in self.unlocked_skins:
            self.unlocked_skins.add(0)
            self.save_unlocked_skins()

    def load_highscores(self):
        if not os.path.exists(SCORE_FILE):
            return []
        try:
            with open(SCORE_FILE, 'r') as f:
                scores = []
                for line in f:
                    line = line.strip()
                    if line:
                        name, score = line.split(',')
                        scores.append({'name': name, 'score': int(float(score))})
                return sorted(scores, key=lambda x: x['score'], reverse=True)
        except Exception as e:
            print(f"Chyba pri nacitani skore: {e}")
            return []

    def save_highscores(self):
        try:
            with open(SCORE_FILE, 'w') as f:
                for entry in self.highscores:
                    f.write(f"{entry['name']},{int(entry['score'])}\n")
        except Exception as e:
            print(f"Chyba pri ukladani skore: {e}")

    def add_score(self, name, score):
        self.highscores.append({'name': name, 'score': int(score)})
        self.highscores.sort(key=lambda x: x['score'], reverse=True)
        self.highscores = self.highscores[:20]
        self.save_highscores()

    def is_highscore(self, score):
        if len(self.highscores) < 20:
            return True
        return score > self.highscores[-1]['score']

    def increment_score(self, points=1):
        self.current_score += points

    def reset_score(self):
        self.current_score = 0

    def get_current_score(self):
        return self.current_score

    def get_highscores(self):
        return self.highscores

    # --- Coins ---
    def load_coins(self):
        try:
            if os.path.exists(COINS_FILE):
                with open(COINS_FILE, 'r') as f:
                    return int(f.read().strip())
        except Exception:
            pass
        return 0

    def save_coins(self):
        try:
            with open(COINS_FILE, 'w') as f:
                f.write(str(self.coins))
        except Exception as e:
            print(f"Chyba pri ukladani minci: {e}")

    def add_coins(self, amount):
        self.coins += amount
        self.session_coins += amount
        self.save_coins()

    def spend_coins(self, amount):
        if self.coins >= amount:
            self.coins -= amount
            self.save_coins()
            return True
        return False

    def reset_session_coins(self):
        self.session_coins = 0

    # --- Unlocked skins ---
    UNLOCKED_FILE = "unlocked_skins.txt"

    def load_unlocked_skins(self):
        try:
            if os.path.exists(self.UNLOCKED_FILE):
                with open(self.UNLOCKED_FILE, 'r') as f:
                    indices = [int(x.strip()) for x in f if x.strip()]
                    return set(indices)
        except Exception:
            pass
        return {0}

    def save_unlocked_skins(self):
        try:
            with open(self.UNLOCKED_FILE, 'w') as f:
                for idx in sorted(self.unlocked_skins):
                    f.write(f"{idx}\n")
        except Exception as e:
            print(f"Chyba pri ukladani skinov: {e}")

    def unlock_skin(self, index):
        if index in self.unlocked_skins:
            return False
        self.unlocked_skins.add(index)
        self.save_unlocked_skins()
        return True
