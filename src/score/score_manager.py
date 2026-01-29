import os
from src.settings import SCORE_FILE, MAX_HIGHSCORES

class ScoreManager:

    def __init__(self):
        self.current_score = 0
        self.highscores = self.load_highscores()

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
                return scores
        except Exception as e:
            print(f"Chyba pri načítaní skóre: {e}")
            return []

    def save_highscores(self):
        try:
            with open(SCORE_FILE, 'w') as f:
                for entry in self.highscores:
                    f.write(f"{entry['name']},{int(entry['score'])}\n")
        except Exception as e:
            print(f"Chyba pri ukladaní skóre: {e}")

    def add_score(self, name, score):
        self.highscores.append({'name': name, 'score': score})
        self.highscores.sort(key=lambda x: x['score'], reverse=True)
        self.highscores = self.highscores[:MAX_HIGHSCORES]
        self.save_highscores()

    def is_highscore(self, score):
        if len(self.highscores) < MAX_HIGHSCORES:
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