
# indxware.py

**indxware.py** is a lightweight tool to quickly search and recall commands, notes, or any indexed data. I originally made this for VIM commands, but changed it to accent any JSON file for notes/commands.

## Features

![indxware.py](indxware-demo-1.gif)

* **Quick Search**: Type in the search bar and instantly filter your indexed notes or commands. Press Enter to toggle between the filtered view and the full list.
* **Customizable Categories**: Organize your notes or commands into categories with a simple JSON file (`vim.json`), (`python.json`),(`linux.json`), (`commands.json`), etc.
* **Hotkeys**: 
  - `Ctrl+L` to load a new JSON file.
  - `Ctrl+U` to toggle between two opacity levels (95% and 80%).
  - `Ctrl+G` to toggle frameless mode.
  - `Ctrl+Q` to exit the application.
* **Right-click Menu**: Load a new file, toggle opacity or frameless mode, or exit via the context menu.
* **Resizable & Frameless Mode**: Resize the window as needed, or remove the frame for a minimalist look.

## Prerequisites

* Python 3
* PyQt5 (`pip install PyQt5`)

## Usage

1. Run the script using Python3: 
   ```bash
   python3 indxware.py
   ```
2. Type in the search bar to filter through commands or notes.
3. Press **Enter** to toggle between the filtered and full list views.
4. Toggle the frameless window with **Ctrl+G** or adjust opacity with **Ctrl+U**.

### Customizing Categories

Categories are defined in a `.json` file located in the same directory as `indxware.py`. The structure is simple: each category is labeled with `"category"`, and commands or notes are added as strings.

```json
[
    { "category": "Global Commands" },
    ":w - Save",
    ":q - Quit",
    ":wq - Save and Quit",
    { "category": "Editing" },
    "i - Insert Mode",
    "dd - Delete Line",
    "yy - Yank Line"
]
```

To add a new category or note:
1. Open `commands.json` in a text editor.
2. Add new categories using the `"category"` key.
3. List your commands or notes under each category.
4. Save and reload the file.

### Customizing Colors and Opacity

You can adjust the color scheme and opacity by modifying the variables at the top of the Python script:

```python
BG = "#232634"  # Background color
TEXT = "#cad3f5"  # Text color
ACCENT = "#b7bdf8"  # Highlighted text color
HIGHLIGHT = "#3b4261"  # Highlight background color
OPACITY_LEVEL_1 = 0.95  # Default higher opacity
OPACITY_LEVEL_2 = 0.8   # Lower opacity
```

Want to tweak the colors or adjust opacity? Just change the hex values or opacity levels.

