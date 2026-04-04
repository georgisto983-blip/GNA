"""Animal theme data — colour palettes, SVG silhouettes, and floating symbols.

Each animal theme has:
  - dark + light colour palettes
  - path to SVG silhouette
  - list of small Unicode symbols to scatter in the overlay
"""

from pathlib import Path

_ASSETS = Path(__file__).resolve().parent.parent / "assets" / "animals"

# ──────────────────────────────────────────────────────────────────
# Per-animal metadata
# ──────────────────────────────────────────────────────────────────

ANIMAL_THEMES: dict[str, dict] = {}


def _reg(name: str, *, svg: str, symbols: list[str],
         dark: dict, light: dict):
    ANIMAL_THEMES[name] = {
        'svg': str(_ASSETS / svg),
        'symbols': symbols,
        'dark': dark,
        'light': light,
    }


# ── Cat — warm purples / soft pinks, mysterious ──
_reg('Cat', svg='cat.svg',
     symbols=['🐾', '🐟', '🧶', '✨', '🐱'],
     dark={
         'bg': '#1a1020', 'bg_dark': '#140c1a', 'surface': '#241a30',
         'surface2': '#302440', 'surface3': '#3c2e50', 'border': '#4a3860',
         'text': '#f0e8ff', 'text_dim': '#8868a0', 'text_bright': '#c8a8e0',
         'primary': '#c870e8', 'primary_hover': '#d888f0', 'primary_dim': '#b058d0',
         'btn_text': '#140c1a', 'accent': '#e080b0',
         'success': '#50d880', 'error': '#f05060', 'warning': '#e0a840',
     },
     light={
         'bg': '#e8d8f0', 'bg_dark': '#dccce4', 'surface': '#f2e6fa',
         'surface2': '#d4c2e0', 'surface3': '#c8b4d4', 'border': '#b09cc0',
         'text': '#201028', 'text_dim': '#907898', 'text_bright': '#483058',
         'primary': '#9838c0', 'primary_hover': '#a848d0', 'primary_dim': '#8428b0',
         'btn_text': '#ffffff', 'accent': '#c048a0',
         'success': '#209850', 'error': '#c03050', 'warning': '#b08020',
     })

# ── Dog — warm oranges / golden browns, friendly ──
_reg('Dog', svg='dog.svg',
     symbols=['🐾', '🦴', '🎾', '❤️', '🐕'],
     dark={
         'bg': '#201408', 'bg_dark': '#181004', 'surface': '#2c1e10',
         'surface2': '#3a2a1a', 'surface3': '#483624', 'border': '#584430',
         'text': '#fff0e0', 'text_dim': '#a08060', 'text_bright': '#d0b890',
         'primary': '#e09030', 'primary_hover': '#f0a848', 'primary_dim': '#c87820',
         'btn_text': '#181004', 'accent': '#60b0e0',
         'success': '#50d870', 'error': '#f05050', 'warning': '#e0b030',
     },
     light={
         'bg': '#f0dcc8', 'bg_dark': '#e4d0bc', 'surface': '#fae8d4',
         'surface2': '#dcc8b0', 'surface3': '#cebca4', 'border': '#b8a488',
         'text': '#281808', 'text_dim': '#907860', 'text_bright': '#504028',
         'primary': '#b06810', 'primary_hover': '#c07818', 'primary_dim': '#984e08',
         'btn_text': '#ffffff', 'accent': '#3878c0',
         'success': '#208848', 'error': '#c03040', 'warning': '#a07818',
     })

# ── Bear — deep warm browns, cozy forest ──
_reg('Bear', svg='bear.svg',
     symbols=['🐾', '🍯', '🌲', '🐻', '🌿'],
     dark={
         'bg': '#1c1408', 'bg_dark': '#141004', 'surface': '#281e10',
         'surface2': '#342818', 'surface3': '#403422', 'border': '#50422c',
         'text': '#f8f0e0', 'text_dim': '#988060', 'text_bright': '#c8b890',
         'primary': '#a87830', 'primary_hover': '#c09040', 'primary_dim': '#906820',
         'btn_text': '#f8f0e0', 'accent': '#70a060',
         'success': '#50c868', 'error': '#e05050', 'warning': '#d0a040',
     },
     light={
         'bg': '#e4d8c4', 'bg_dark': '#d8ccb8', 'surface': '#f0e4d0',
         'surface2': '#d0c4ac', 'surface3': '#c4b89c', 'border': '#ac9c80',
         'text': '#201808', 'text_dim': '#887060', 'text_bright': '#484028',
         'primary': '#7c5c20', 'primary_hover': '#8c6c2c', 'primary_dim': '#6c4c14',
         'btn_text': '#ffffff', 'accent': '#487838',
         'success': '#208848', 'error': '#b83838', 'warning': '#987018',
     })

# ── Penguin — icy blues / navy, arctic feel ──
_reg('Penguin', svg='penguin.svg',
     symbols=['❄️', '🐟', '🧊', '⭐', '🐧'],
     dark={
         'bg': '#081420', 'bg_dark': '#040e18', 'surface': '#101e30',
         'surface2': '#1a2840', 'surface3': '#243450', 'border': '#2e4060',
         'text': '#e0f0ff', 'text_dim': '#5080a8', 'text_bright': '#90b8d8',
         'primary': '#40a0e0', 'primary_hover': '#58b8f0', 'primary_dim': '#3088c8',
         'btn_text': '#040e18', 'accent': '#80c8ff',
         'success': '#40d880', 'error': '#f06060', 'warning': '#e0a840',
     },
     light={
         'bg': '#cce0f0', 'bg_dark': '#c0d4e4', 'surface': '#d8ecf8',
         'surface2': '#b8ccdc', 'surface3': '#acc0d0', 'border': '#90a8bc',
         'text': '#081828', 'text_dim': '#607890', 'text_bright': '#283848',
         'primary': '#1870a8', 'primary_hover': '#2080b8', 'primary_dim': '#106098',
         'btn_text': '#ffffff', 'accent': '#4898d0',
         'success': '#189048', 'error': '#c03040', 'warning': '#a07818',
     })

# ── Giraffe — warm yellows / amber / safari browns ──
_reg('Giraffe', svg='giraffe.svg',
     symbols=['🍃', '🌴', '🌻', '🦒', '☀️'],
     dark={
         'bg': '#1e1808', 'bg_dark': '#161204', 'surface': '#2a2210',
         'surface2': '#362c18', 'surface3': '#443822', 'border': '#54462c',
         'text': '#fff8e0', 'text_dim': '#a09060', 'text_bright': '#d0c090',
         'primary': '#d0a020', 'primary_hover': '#e0b830', 'primary_dim': '#b88810',
         'btn_text': '#161204', 'accent': '#d08030',
         'success': '#50c868', 'error': '#e05050', 'warning': '#d0a030',
     },
     light={
         'bg': '#ece0c0', 'bg_dark': '#e0d4b4', 'surface': '#f6eacc',
         'surface2': '#d8ccaa', 'surface3': '#ccc098', 'border': '#b4a880',
         'text': '#282010', 'text_dim': '#887860', 'text_bright': '#484028',
         'primary': '#a88010', 'primary_hover': '#b89018', 'primary_dim': '#907008',
         'btn_text': '#ffffff', 'accent': '#a06820',
         'success': '#208848', 'error': '#b83838', 'warning': '#907018',
     })

# ── Crane — elegant white / grey / red accent, Japanese-inspired ──
_reg('Crane', svg='crane.svg',
     symbols=['🌸', '🍂', '💮', '🪶', '🏯'],
     dark={
         'bg': '#181818', 'bg_dark': '#121212', 'surface': '#242424',
         'surface2': '#303030', 'surface3': '#3c3c3c', 'border': '#4a4a4a',
         'text': '#f0f0f0', 'text_dim': '#808080', 'text_bright': '#c0c0c0',
         'primary': '#d03030', 'primary_hover': '#e04040', 'primary_dim': '#b82020',
         'btn_text': '#f0f0f0', 'accent': '#e8e8e8',
         'success': '#50c868', 'error': '#e05050', 'warning': '#d0a040',
     },
     light={
         'bg': '#e4dcd4', 'bg_dark': '#d8d0c8', 'surface': '#eee6de',
         'surface2': '#d0c8c0', 'surface3': '#c4bcb4', 'border': '#a8a098',
         'text': '#1a1a18', 'text_dim': '#888480', 'text_bright': '#484440',
         'primary': '#b02020', 'primary_hover': '#c02828', 'primary_dim': '#981818',
         'btn_text': '#ffffff', 'accent': '#303030',
         'success': '#208848', 'error': '#b83030', 'warning': '#987018',
     })

# ── Owl — deep navy / gold / amber, nocturnal & wise ──
_reg('Owl', svg='owl.svg',
     symbols=['⭐', '🌙', '✨', '🦉', '🌟'],
     dark={
         'bg': '#0e1028', 'bg_dark': '#0a0c20', 'surface': '#161838',
         'surface2': '#202248', 'surface3': '#2a2c58', 'border': '#343668',
         'text': '#f0f0ff', 'text_dim': '#6068a0', 'text_bright': '#a0a8d0',
         'primary': '#d0a030', 'primary_hover': '#e0b840', 'primary_dim': '#b88820',
         'btn_text': '#0a0c20', 'accent': '#8080ff',
         'success': '#40d878', 'error': '#f05060', 'warning': '#e0a840',
     },
     light={
         'bg': '#d8d4e4', 'bg_dark': '#ccc8d8', 'surface': '#e4e0f0',
         'surface2': '#c4c0d0', 'surface3': '#b8b4c4', 'border': '#9c98ac',
         'text': '#181028', 'text_dim': '#787490', 'text_bright': '#383450',
         'primary': '#a87810', 'primary_hover': '#b88818', 'primary_dim': '#906808',
         'btn_text': '#ffffff', 'accent': '#5050a0',
         'success': '#208848', 'error': '#b83040', 'warning': '#987018',
     })

# ── Deer — forest green / warm brown / golden highlights ──
_reg('Deer', svg='deer.svg',
     symbols=['🍀', '🍂', '🌿', '🦌', '🌲'],
     dark={
         'bg': '#101a10', 'bg_dark': '#0a140a', 'surface': '#1a2618',
         'surface2': '#243222', 'surface3': '#2e3e2c', 'border': '#3a4c36',
         'text': '#e8f8e8', 'text_dim': '#609060', 'text_bright': '#98c898',
         'primary': '#60a840', 'primary_hover': '#70c050', 'primary_dim': '#509030',
         'btn_text': '#0a140a', 'accent': '#c0a050',
         'success': '#50d870', 'error': '#e05050', 'warning': '#d0a040',
     },
     light={
         'bg': '#d0e0cc', 'bg_dark': '#c4d4c0', 'surface': '#dcecd8',
         'surface2': '#bcceb8', 'surface3': '#b0c2ac', 'border': '#94aa90',
         'text': '#101a10', 'text_dim': '#607860', 'text_bright': '#2a3e2a',
         'primary': '#388828', 'primary_hover': '#409830', 'primary_dim': '#2c7820',
         'btn_text': '#ffffff', 'accent': '#907830',
         'success': '#209048', 'error': '#b83838', 'warning': '#907018',
     })


# ── Ordered list of animal family names ──
ANIMAL_FAMILIES = list(ANIMAL_THEMES.keys())
