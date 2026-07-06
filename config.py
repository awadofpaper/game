class Config:
    GAME_TITLE = "Open World RPG"
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60
    WORLD_WIDTH = 104000
    WORLD_HEIGHT = 104000
    TILE_SIZE = 64  # Increased from 52 for better performance (fewer tiles to render)
    PLAYER_SPEED = 5  # pixels per frame (normal walking speed)
    SPRINT_SPEED = 12  # pixels per frame (sprint speed - 2.4x faster)
    SPRINT_STAMINA_COST = 0.8  # stamina consumed per frame while sprinting
    SAVE_FILE = "savegame.json"
    WORLD_FILE = "world.json"
    LANGUAGES = ["en", "es", "fr"]
    DEFAULT_LANGUAGE = "en"
    # Add more config as needed
