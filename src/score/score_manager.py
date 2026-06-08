import os
from src.settings import (SCORE_FILE, MAX_HIGHSCORES, COINS_FILE, PITY_FILE,
                          EFFECTS, EFFECTS_FILE, EQUIPPED_EFFECTS_FILE, STARTER_EFFECTS)


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
        self.pity_epic, self.pity_legendary = self.load_pity()
        self.unlocked_effects = self.load_unlocked_effects()
        self.equipped_effects = self.load_equipped_effects()

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

    def get_coins(self):
        return self.coins

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

    # --- Pity counters ---
    def load_pity(self):
        try:
            if os.path.exists(PITY_FILE):
                with open(PITY_FILE, 'r') as f:
                    lines = [l.strip() for l in f if l.strip()]
                    if len(lines) >= 2:
                        return int(lines[0]), int(lines[1])
        except Exception:
            pass
        return 0, 0

    def save_pity(self):
        try:
            with open(PITY_FILE, 'w') as f:
                f.write(f"{self.pity_epic}\n{self.pity_legendary}\n")
        except Exception as e:
            print(f"Chyba pri ukladani pity: {e}")

    # --- Unlocked Effects ---
    def load_unlocked_effects(self):
        unlocked = set()
        try:
            if os.path.exists(EFFECTS_FILE):
                with open(EFFECTS_FILE, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            unlocked.add(int(line))
        except Exception:
            pass
        # Ensure starter effects are always present
        for idx in STARTER_EFFECTS:
            unlocked.add(idx)
        self.save_unlocked_effects_internal(unlocked)
        return unlocked

    def save_unlocked_effects_internal(self, unlocked_set):
        try:
            with open(EFFECTS_FILE, 'w') as f:
                for idx in sorted(unlocked_set):
                    f.write(f"{idx}\n")
        except Exception as e:
            print(f"Chyba pri ukladani efektov: {e}")

    def save_unlocked_effects(self):
        self.save_unlocked_effects_internal(self.unlocked_effects)

    def unlock_effect(self, index):
        if index in self.unlocked_effects:
            return False
        self.unlocked_effects.add(index)
        self.save_unlocked_effects()
        return True

    # --- Equipped Effects ---
    def load_equipped_effects(self):
        equipped = {}
        try:
            if os.path.exists(EQUIPPED_EFFECTS_FILE):
                with open(EQUIPPED_EFFECTS_FILE, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line:
                            etype, idx_str = line.split('=', 1)
                            if idx_str.isdigit():
                                equipped[etype] = int(idx_str)
        except Exception:
            pass
        return equipped

    def save_equipped_effects(self):
        try:
            with open(EQUIPPED_EFFECTS_FILE, 'w') as f:
                for etype, idx in self.equipped_effects.items():
                    f.write(f"{etype}={idx if idx is not None else ''}\n")
        except Exception as e:
            print(f"Chyba pri ukladani vybavenia: {e}")

    def equip_effect(self, effect_index):
        effect = EFFECTS[effect_index]
        etype = effect["type"]
        self.equipped_effects[etype] = effect_index
        self.save_equipped_effects()

    def unequip_effect(self, effect_type):
        self.equipped_effects[effect_type] = None
        self.save_equipped_effects()

    def get_active_effects(self):
        active = {}
        for etype, idx in self.equipped_effects.items():
            if idx is not None and 0 <= idx < len(EFFECTS):
                active[etype] = EFFECTS[idx]
            else:
                active[etype] = None
        return active
