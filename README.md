# 📄 Technical Document – Project Component Overview

## 1. `main.py` – Main Editor Interface

### Purpose  
Manages the **main GUI window**, handling JSON file loading, text display, editing, preview rendering, and automatic translation.

### Key Responsibilities  
- Builds the graphical interface (toolbars, text sections, preview box, sliders, navigation buttons).  
- Loads `.json` files containing in-game dialogue blocks.  
- Displays both original and editable text with special formatting.  
- Integrates with `preview_renderer` to visually simulate translated text.  
- Controls timing sliders for dialogue appearance (`appear_time`) and duration.  
- Automatically detects and saves edited translations.  
- Offers automatic translation using external services with fallback.  
- Dynamically updates UI according to user settings (theme, language).
- Monitoring the percentage of translation completed.

---

## 2. `preview_renderer.py` – Translation Preview Renderer

### Purpose  
Renders translated text visually over the **game's background image** using a **variable-width font (VWF)** extracted from the game.

### Key Responsibilities  
- `CustomPreviewWidget` class inherits from `QWidget` and renders using `QPainter`.  
- Loads a background image (`bg_image`) and custom font image (`font_image`).  
- Uses a `char_table` defining (x, y, width) for each character.  
- Precisely draws each character based on JSON `dialogo` metadata (position, line spacing, char limit).  
- Supports special characters and diacritics (e.g., á, ç, ê).  
- Allows dynamic reloading of font/background images using `load_config_from_json`.

---

## 3. `grid_widget.py` – Widget Grid and Alignment Manager

### Purpose  
Provides a drag-and-drop grid interface to **visually organize GUI widgets**, including grid snapping and visual alignment aids.

### Key Responsibilities  
- Draws a scalable, interactive grid (`wheelEvent`) on the main canvas.  
- Allows moving widgets using mouse + CTRL (with optional grid snapping).  
- Displays **red alignment lines** when widgets are aligned.  
- Automatically saves and restores widget positions via `save_widget_position` and `load_widget_positions`.

---

## 4. `config.py` – Settings, Translation, and Themes

### Purpose  
Handles all **application configuration**, such as UI language, color themes, and auto-translation service setup.

### Key Responsibilities  
- Loads/saves user settings from `settings.json`.  
- Provides a graphical `ConfigDialog` interface with options for:
  - Visual themes (e.g., Light, Dark, Military, MGS).  
  - UI language (pt_BR, en_US, es_ES).  
  - Auto-translation enable/disable.  
  - Optional ChatGPT API key input.  
- Determines which translation service is available via `get_active_translation_service`.  
- Executes translation with fallbacks using `traduzir_texto_automaticamente`:
  - Priority: ChatGPT → DeepL → Google Translate.

---

## 🧩 Overall Project Structure

- A **game text editor for dialogue translation**, focused on preserving in-game style.  
- **Modular GUI** components (custom preview, dynamic grid, theming).  
- **Full user customization** via settings panel (language, theme, translation).  
- **Continuous export/save** of edited JSONs.  
- **Accurate in-game simulation** with support for non-standard bitmap fonts.
