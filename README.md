# 🏎️ F1 TURBO

Arkádová 2D racing hra vytvorená v **Pygame**, inšpirovaná klasickými top‑down pretekárskymi hrami. Hráč ovláda formulu, vyhýba sa prekážkam, sleduje dynamicky sa krútiacu cestu a snaží sa dosiahnuť čo najvyššie skóre.

---

## 🎮 Základné informácie

* **Názov hry:** F1 TURBO
* **Žáner:** Arkádová pretekárska hra (top‑down)
* **Technológia:** Python 3 + Pygame
* **Typ projektu:** Školský / hobby projekt

---

## 🕹️ Ovládanie

| Klávesa | Funkcia                              |
| ------- | ------------------------------------ |
| ⬅ / ➡   | Pohyb auta doľava / doprava          |
| ESC     | Pauza počas hry / návrat späť        |
| SPACE   | Spustenie hry z menu                 |
| ENTER   | Potvrdenie (game over, zadanie mena) |
| Q       | Návrat do menu z pauzy               |

---

## 🎯 Cieľ hry

* Zostať **na ceste** (nespadnúť do trávy)
* Vyhýbať sa **ostatným formulám**
* Prejsť čo najviac prekážok
* Dosiahnuť **čo najvyššie skóre** a zapísať sa do tabuľky TOP jazdcov

---

## 📈 Herné mechaniky

### Skóre

* +1 bod za každú úspešne prejdenú prekážku
* Malý **časový bonus** za prežitie

### Obtiažnosť

* Obtiažnosť sa zvyšuje každých **10 bodov**:

  * zvyšuje sa rýchlosť hry
  * prekážky sa objavujú častejšie

### Kolízie

* Kolízia nastane, ak:

  * hráč vyjde mimo asfalt (na trávu)
  * narazí do iného auta

---

## 🧠 Herné stavy (Game States)

Hra používa stavový systém:

* **MENU** – hlavné menu hry
* **PLAYING** – aktívna hra
* **PAUSED** – pauza
* **GAME_OVER** – koniec hry
* **ENTERING_NAME** – zadanie mena pri highscore

---

## 🛣️ Cesta (Road System)

* Cesta je tvorená **segmentmi**, ktoré sa posúvajú smerom nadol
* Dynamické zakrivenie pomocou plynulej interpolácie (easing)
* Stred cesty sa neustále mení → hráč musí reagovať

---

## 🚗 Autá

### Hráč (Player)

* Ovládanie šípkami
* Obmedzený pohyb len v rámci obrazovky
* Kolízia sa rieši pomocou `pygame.Rect`

### Prekážky (ObstacleCar)

* Náhodný spawn
* Náhodný horizontálny posun v rámci cesty
* Skóre sa pripisuje po ich úspešnom prejdení

---

## 🖥️ UI a dizajn

* Moderné **glass‑morphism** panely
* Neonové farby (cyan, gold, warning red)
* Animované tlačidlá s hover efektom
* Tachometer rýchlosti
* HUD s:

  * skóre
  * úrovňou (stage)
  * rýchlosťou

---

## 🏆 Highscore systém

* Skóre sa ukladá do súboru **`highscores.txt`**
* Maximálne **15 záznamov**
* Po dosiahnutí rekordu hráč zadá meno
* Skóre sú zoradené zostupne

---

## 📁 Štruktúra projektu

```
src/
├── game/
│   └── game.py            # Hlavná herná logika
├── cars/
│   ├── player.py          # Auto hráča
│   └── obstacle.py        # Prekážky
├── road/
│   └── road.py            # Dynamická cesta
├── score/
│   └── score_manager.py   # Skóre a highscores
├── ui/
│   └── ui_manager.py      # UI, menu, HUD
├── settings.py            # Globálne nastavenia
└── main.py                # Spustenie hry
```

---

## ▶️ Spustenie hry

1. Nainštaluj Pygame:

   ```bash
   pip install pygame
   ```
2. Spusti hru:

   ```bash
   python src/main.py
   ```

---

## ✨ Možné vylepšenia

* Zvukové efekty a hudba
* Viac typov prekážok
* Power‑upy (zrýchlenie, štít)
* Animácie explózií
* Multiplayer (lokálny)

---

## 👨‍💻 Autor

Projekt vytvorený ako **študentská / tréningová hra v Pythone** so zameraním na:

* hernú architektúru
* prácu so stavmi
* kolízie
* UI dizajn

---

🏁 **Good luck, racer!**
