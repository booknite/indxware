import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QScrollArea, QMessageBox, QMenu, QAction, QShortcut
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence

# ===================
# Colors
# ===================
BG = "#232634"  # Background color
TEXT = "#cad3f5"  # Default text color
ACCENT = "#b7bdf8"  # Highlighted text color
HIGHLIGHT = "#3b4261"  # Background highlight color
COMMAND_COLOR = "#f5bde6"  # Command text color (pink)
CATEGORY_COLOR = "#ff9e64"  # Category title color (orange)

DIVIDER = '-'  # Divider symbol, seperates note title and text in JSON file.

COMMANDS_FILE = 'commands.json'  # Name of JSON file to load/save commands

# ===================
# Hotkeys
# ===================
SHORTCUTS = {
    "save_commands": "Ctrl+S",   # Shortcut to save command list
    "load_commands": "Ctrl+L",   # Shortcut to load command list
    "exit": "Ctrl+Q",            # Shortcut to exit the application
    "toggle_frameless": "Ctrl+G"  # Shortcut to toggle frameless window
}


class StickyNote(QWidget):
    def __init__(self):
        super().__init__()
        self.frameless = True  
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Start in frameless mode
        self.setGeometry(50, 50, 300, 400)  # Initial size and position
        self.setMinimumSize(250, 200)  
        self.setStyleSheet(f"background-color: {BG}; border-radius: 10px;")
        self.initUI()
        self.initShortcuts()
        self.load_commands()

    # ===================
    # UI Setup
    # ===================
    def initUI(self):
        layout = QVBoxLayout()

        # Search Bar
        self.searchBar = QLineEdit(self)
        self.searchBar.setPlaceholderText('Search')
        self.searchBar.setStyleSheet(f"""
            padding: 5px; 
            font-size: 14px; 
            color: {TEXT}; 
            background-color: {HIGHLIGHT}; 
            border-radius: 5px;
        """)
        self.searchBar.textChanged.connect(self.highlight_commands)  
        self.searchBar.returnPressed.connect(self.toggle_search_filter)
        layout.addWidget(self.searchBar)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none;")

        commandWidget = QWidget()
        self.commandLayout = QVBoxLayout()
        commandWidget.setLayout(self.commandLayout)

        scroll.setWidget(commandWidget)
        layout.addWidget(scroll)

        self.setLayout(layout)

        # Right-click menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.filtered = False  # Filter toggle state

    # ===================
    # Shortcut/Hotkey Setup
    # ===================
    def initShortcuts(self):
        """Initialize keyboard shortcuts."""
        QShortcut(QKeySequence(SHORTCUTS["save_commands"]), self, self.save_commands)
        QShortcut(QKeySequence(SHORTCUTS["load_commands"]), self, self.load_commands)
        QShortcut(QKeySequence(SHORTCUTS["exit"]), self, self.close)
        QShortcut(QKeySequence(SHORTCUTS["toggle_frameless"]), self, self.toggle_frameless)

    # ===================
    # Right-click Menu
    # ===================
    def show_context_menu(self, pos):
        """Display context menu with right-click options."""
        context_menu = QMenu(self)
        context_menu.setStyleSheet(f"color: {TEXT}; background-color: {BG};")

        save_action = QAction(f"Save Commands ({SHORTCUTS['save_commands']})", self)
        save_action.triggered.connect(self.save_commands)
        context_menu.addAction(save_action)

        load_action = QAction(f"Load Commands ({SHORTCUTS['load_commands']})", self)
        load_action.triggered.connect(self.load_commands)
        context_menu.addAction(load_action)

        toggle_frameless_action = QAction(f"Toggle Frameless ({SHORTCUTS['toggle_frameless']})", self)
        toggle_frameless_action.triggered.connect(self.toggle_frameless)
        context_menu.addAction(toggle_frameless_action)

        exit_action = QAction(f"Exit ({SHORTCUTS['exit']})", self)
        exit_action.triggered.connect(self.close)
        context_menu.addAction(exit_action)

        context_menu.exec_(self.mapToGlobal(pos))

    # ===================
    # Commands and Display
    # ===================
    def load_commands(self):
        """Load commands from JSON file."""
        if os.path.exists(COMMANDS_FILE):
            try:
                with open(COMMANDS_FILE, 'r') as file:
                    self.commands = json.load(file)
            except json.JSONDecodeError:
                self.show_popup("Error", "Failed to load the command list. File might be corrupted.", "critical")
                self.commands = []
        else:
            # Default command set (VIM)
            self.commands = [
                { "category": "Global Commands" },
                ":w - Save",
                ":q - Quit",
                ":wq - Save and Quit",
                { "category": "Editing" },
                "i - Insert Mode",
                "dd - Delete Line",
                "yy - Yank Line",
                "p - Paste",
                { "category": "Search and Replace" },
                "/search - Search",
                ":s - Replace",
                "u - Undo",
                "Ctrl+r - Redo"
            ]
        self.display_commands()

    def save_commands(self):
        try:
            with open(COMMANDS_FILE, 'w') as file:
                json.dump(self.commands, file, indent=4)
            self.show_popup("Success", "Commands saved successfully.", "information")
        except Exception as e:
            self.show_popup("Error", f"Failed to save the command list: {e}", "critical")

    def display_commands(self):

        # Clear the layout first
        for i in reversed(range(self.commandLayout.count())):
            widget = self.commandLayout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Add commands to the layout
        self.command_labels = []
        for command in self.commands:
            label = self.create_command_label(command)
            self.command_labels.append(label)
            self.commandLayout.addWidget(label)

    def create_command_label(self, command):

        label = QLabel(self)

        if isinstance(command, dict) and "category" in command:
            # Display category
            label.setText(f'<span style="color:{CATEGORY_COLOR};"><b>{command["category"]}</b></span>')
            label.setStyleSheet(f"padding: 5px; font-size: 16px;")
        else:
            # Display command
            if DIVIDER in command:
                cmd, desc = command.split(DIVIDER, 1)
            else:
                cmd, desc = command, ""

            label.setText(f'<span style="color:{COMMAND_COLOR};">{cmd.strip()}</span> {DIVIDER} <span style="color:{TEXT};">{desc.strip()}</span>')
            label.setStyleSheet(f"padding: 5px; font-size: 14px;")
            label.setTextFormat(Qt.RichText)

        return label

    # ===================
    # Toggle Frameless Window
    # ===================
    def toggle_frameless(self):

        self.frameless = not self.frameless  # Toggle
        if self.frameless:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.show()  

    # ===================
    # Search and Highlighting
    # ===================
    def highlight_commands(self):
        """Highlight matching commands based on the search term."""
        search_term = self.searchBar.text().lower()
        for label in self.command_labels:
            label_text = label.text().lower()
            if search_term in label_text and search_term != "":
                label.setStyleSheet(f"""
                    color: {ACCENT};
                    background-color: {HIGHLIGHT};
                    padding: 5px;
                    font-size: 14px;
                    border-radius: 5px;
                """)
            else:
                label.setStyleSheet(f"""
                    color: {TEXT};
                    background-color: {BG};
                    padding: 5px;
                    font-size: 14px;
                """)

    def toggle_search_filter(self):
        search_term = self.searchBar.text().lower()

        if not self.filtered and search_term != "":
            # Filter and show only matching commands
            for label in self.command_labels:
                if search_term in label.text().lower():
                    label.show()
                else:
                    label.hide()
            self.filtered = True
        else:
            # Show all commands
            self.display_commands()
            self.highlight_commands() 
            self.filtered = False

    # ===================
    # Utility
    # ===================
    def show_popup(self, title, message, icon_type="information"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStyleSheet(f"color: {TEXT}; background-color: {BG};")
        if icon_type == "information":
            msg_box.setIcon(QMessageBox.Information)
        elif icon_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)
        elif icon_type == "critical":
            msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def mousePressEvent(self, event):
        self.is_moving = True
        self.startPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.is_moving:
            self.move(self.pos() + event.globalPos() - self.startPos)
            self.startPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.is_moving = False


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Set default font
    font = QFont()
    font.setFamily("Arial")
    font.setPointSize(12)
    app.setFont(font)

    note = StickyNote()
    note.show()
    sys.exit(app.exec_())

