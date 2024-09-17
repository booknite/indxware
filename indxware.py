import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QScrollArea, QMessageBox, QMenu, QAction, QShortcut, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence

# ===================
# Colors
# ===================
BG = "#232634"
TEXT = "#cad3f5"
ACCENT = "#b7bdf8"
HIGHLIGHT = "#3b4261"
COMMAND_COLOR = "#f5bde6"
CATEGORY_COLOR = "#ff9e64"

DIVIDER = '-'  # Divider symbol, separates note title and text in JSON file

DEFAULT_JSON_FILE = ''  # Default JSON file

SHORTCUTS = {
    "load_commands": "Ctrl+L",
    "exit": "Ctrl+Q",
    "toggle_frameless": "Ctrl+G",
    "toggle_opacity": "Ctrl+U"
}

# Set two preset opacity values for toggling
OPACITY_LEVEL_1 = 0.95  # Default higher opacity
OPACITY_LEVEL_2 = 0.8   # Lower opacity

class StickyNote(QWidget):
    def __init__(self, json_file=DEFAULT_JSON_FILE):
        super().__init__()
        self.json_file = json_file
        self.frameless = True
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(50, 50, 300, 400)
        self.setMinimumSize(250, 200)
        self.opacity = OPACITY_LEVEL_1  # Default opacity level
        self.setWindowOpacity(self.opacity)
        self.setStyleSheet(f"background-color: {BG}; border-radius: 10px;")
        self.initUI()
        self.initShortcuts()
        self.load_commands()

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

        # Display current JSON file name
        self.json_label = QLabel(self)
        self.json_label.setAlignment(Qt.AlignRight)
        self.json_label.setStyleSheet(f"color: {ACCENT}; padding-right: 10px; font-size: 16px;")
        layout.addWidget(self.json_label)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none;")

        commandWidget = QWidget()
        self.commandLayout = QVBoxLayout()
        commandWidget.setLayout(self.commandLayout)

        scroll.setWidget(commandWidget)
        layout.addWidget(scroll)

        self.setLayout(layout)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.filtered = False

    def initShortcuts(self):
        QShortcut(QKeySequence(SHORTCUTS["load_commands"]), self, self.load_commands_popup)
        QShortcut(QKeySequence(SHORTCUTS["exit"]), self, self.close)
        QShortcut(QKeySequence(SHORTCUTS["toggle_frameless"]), self, self.toggle_frameless)
        QShortcut(QKeySequence(SHORTCUTS["toggle_opacity"]), self, self.toggle_opacity)  # For toggling opacity

    def show_context_menu(self, pos):
        context_menu = QMenu(self)
        context_menu.setStyleSheet(f"color: {TEXT}; background-color: {BG};")

        load_action = QAction(f"Load Commands ({SHORTCUTS['load_commands']})", self)
        load_action.triggered.connect(self.load_commands_popup)
        context_menu.addAction(load_action)

        toggle_frameless_action = QAction(f"Toggle Frameless ({SHORTCUTS['toggle_frameless']})", self)
        toggle_frameless_action.triggered.connect(self.toggle_frameless)
        context_menu.addAction(toggle_frameless_action)

        toggle_opacity_action = QAction(f"Toggle Opacity ({SHORTCUTS['toggle_opacity']})", self)  # Added for toggle opacity
        toggle_opacity_action.triggered.connect(self.toggle_opacity)
        context_menu.addAction(toggle_opacity_action)

        exit_action = QAction(f"Exit ({SHORTCUTS['exit']})", self)
        exit_action.triggered.connect(self.close)
        context_menu.addAction(exit_action)

        context_menu.exec_(self.mapToGlobal(pos))

    def load_commands_popup(self): 
        file_dialog = QFileDialog()
        self.json_file, _ = file_dialog.getOpenFileName(self, "Select JSON file", "", "JSON Files (*.json)")
        if self.json_file:
            self.load_commands()

    def load_commands(self):
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r') as file:
                    self.commands = json.load(file)
                    self.json_label.setText(os.path.basename(self.json_file).replace('.json', ''))
            except json.JSONDecodeError:
                self.show_popup("Error", "Failed to load the command list. File might be corrupted.", "critical")
                self.commands = []
        else:
            self.commands = []
        self.display_commands()

    def display_commands(self):
        for i in reversed(range(self.commandLayout.count())):
            widget = self.commandLayout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        self.command_labels = []
        for command in self.commands:
            label = self.create_command_label(command)
            self.command_labels.append(label)
            self.commandLayout.addWidget(label)

    def create_command_label(self, command):
        label = QLabel(self)

        if isinstance(command, dict) and "category" in command:
            label.setText(f'<span style="color:{CATEGORY_COLOR};"><b>{command["category"]}</b></span>')
            label.setStyleSheet(f"padding: 5px; font-size: 16px;")
        else:
            if DIVIDER in command:
                cmd, desc = command.split(DIVIDER, 1)
            else:
                cmd, desc = command, ""
            label.setText(f'<span style="color:{COMMAND_COLOR};">{cmd.strip()}</span> {DIVIDER} <span style="color:{TEXT};">{desc.strip()}</span>')
            label.setStyleSheet(f"padding: 5px; font-size: 14px;")
            label.setTextFormat(Qt.RichText)

        # Allow text selection
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        return label

    def toggle_frameless(self):
        self.frameless = not self.frameless
        if self.frameless:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.show()

    def toggle_opacity(self):
        # Toggle between the two preset opacity levels
        if self.opacity == OPACITY_LEVEL_1:
            self.opacity = OPACITY_LEVEL_2
        else:
            self.opacity = OPACITY_LEVEL_1
        self.setWindowOpacity(self.opacity)

    def highlight_commands(self):
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
            for label in self.command_labels:
                if search_term in label.text().lower():
                    label.show()
                else:
                    label.hide()
            self.filtered = True
        else:
            self.display_commands()
            self.highlight_commands()
            self.filtered = False

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

    font = QFont()
    font.setFamily("Arial")
    font.setPointSize(12)
    app.setFont(font)

    note = StickyNote()
    note.show()
    sys.exit(app.exec_())

