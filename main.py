"""
F1 TURBO - Racing Game

Ovládanie:
- Šípky vľavo/vpravo: pohyb auta
- SPACE: štart hry z menu
- ENTER: potvrdenie v menu

Cieľ hry:
- Vyhýbať sa prekážkam a zostať na ceste
- Získať čo najvyššie skóre
"""

from game.game import Game


if __name__ == "__main__":
    game = Game()
    game.run()