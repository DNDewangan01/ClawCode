#!/usr/bin/env python3
"""
ClawCode Advanced - GUI Version
A modern code editor with advanced features
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog, QMessageBox,
    QMenuBar, QMenu, QAction, QToolBar, QStatusBar, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTabWidget, QLineEdit
)
from PyQt5.QtCore import Qt, QFileInfo
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette


class CodeEditor(QTextEdit):
    """Advanced code editor with syntax highlighting support"""
    
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Consolas", 12))
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                selection-background-color: #264f78;
            }
        """)
        self.current_file = None
    
    def load_file(self, filepath):
        """Load a file into the editor"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self.setPlainText(content)
                self.current_file = filepath
                return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
            return False
    
    def save_file(self, filepath=None):
        """Save the current file"""
        if filepath is None:
            filepath = self.current_file
        
        if filepath is None:
            return False
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())
                self.current_file = filepath
                return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            return False


class FileExplorer(QTreeWidget):
    """File explorer widget"""
    
    def __init__(self, root_path="."):
        super().__init__()
        self.root_path = root_path
        self.setHeaderHidden(True)
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #252526;
                color: #cccccc;
                border: none;
            }
            QTreeWidget::item:hover {
                background-color: #2a2d2e;
            }
            QTreeWidget::item:selected {
                background-color: #37373d;
            }
        """)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.load_directory(root_path)
    
    def load_directory(self, path):
        """Load directory structure"""
        self.clear()
        root_item = QTreeWidgetItem([path.split('/')[-1] or '/'])
        root_item.setData(0, Qt.UserRole, path)
        self.addTopLevelItem(root_item)
        self.populate_directory(root_item, path)
        self.expandAll()
    
    def populate_directory(self, parent_item, path):
        """Recursively populate directory contents"""
        import os
        try:
            items = sorted(os.listdir(path))
            for item in items:
                if item.startswith('.'):
                    continue
                full_path = os.path.join(path, item)
                child_item = QTreeWidgetItem([item])
                child_item.setData(0, Qt.UserRole, full_path)
                
                if os.path.isdir(full_path):
                    child_item.setText(0, f"📁 {item}")
                    parent_item.addChild(child_item)
                    # Only go 2 levels deep to avoid performance issues
                    if self.get_depth(parent_item) < 2:
                        self.populate_directory(child_item, full_path)
                else:
                    ext = QFileInfo(item).suffix()
                    icon = self.get_file_icon(ext)
                    child_item.setText(0, f"{icon} {item}")
                    parent_item.addChild(child_item)
        except PermissionError:
            pass
    
    def get_depth(self, item):
        """Get the depth of an item in the tree"""
        depth = 0
        while item.parent():
            depth += 1
            item = item.parent()
        return depth
    
    def get_file_icon(self, ext):
        """Get icon based on file extension"""
        icons = {
            'py': '🐍',
            'js': '📜',
            'html': '🌐',
            'css': '🎨',
            'json': '📋',
            'md': '📝',
            'txt': '📄',
            'rs': '⚙️',
            'toml': '⚙️',
        }
        return icons.get(ext.lower(), '📄')
    
    def on_item_double_clicked(self, item, column):
        """Handle double-click on file item"""
        filepath = item.data(0, Qt.UserRole)
        if filepath and QFileInfo(filepath).isFile():
            # Emit signal to open file (will be connected by main window)
            self.parent().parent().open_file(filepath)


class ClawCodeGUI(QMainWindow):
    """Main ClawCode Advanced GUI Window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ClawCode Advanced - Code Editor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        
        # Apply dark theme
        self.apply_dark_theme()
    
    def setup_ui(self):
        """Setup the main UI components"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Splitter for file explorer and editor
        splitter = QSplitter(Qt.Horizontal)
        
        # File explorer
        self.file_explorer = FileExplorer()
        self.file_explorer.setMinimumWidth(250)
        self.file_explorer.setMaximumWidth(400)
        splitter.addWidget(self.file_explorer)
        
        # Right side panel (editor + tabs)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Tab widget for multiple files
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        right_layout.addWidget(self.tab_widget)
        
        # Create first editor tab
        self.create_new_tab()
        
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        
        main_layout.addWidget(splitter)
    
    def create_new_tab(self, filepath=None):
        """Create a new editor tab"""
        editor = CodeEditor()
        if filepath:
            editor.load_file(filepath)
            tab_name = QFileInfo(filepath).fileName()
        else:
            tab_name = "Untitled"
        
        index = self.tab_widget.addTab(editor, tab_name)
        self.tab_widget.setCurrentIndex(index)
        return editor
    
    def close_tab(self, index):
        """Close a tab"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            # Don't close the last tab, just clear it
            editor = self.tab_widget.widget(0)
            editor.clear()
            editor.current_file = None
            self.tab_widget.setTabText(0, "Untitled")
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(lambda: self.current_editor().undo())
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(lambda: self.current_editor().redo())
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(lambda: self.current_editor().cut())
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(lambda: self.current_editor().copy())
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(lambda: self.current_editor().paste())
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(lambda: self.current_editor().selectAll())
        edit_menu.addAction(select_all_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("&Reset Zoom", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # New file button
        new_btn = QAction("📄 New", self)
        new_btn.triggered.connect(self.new_file)
        toolbar.addAction(new_btn)
        
        # Open file button
        open_btn = QAction("📂 Open", self)
        open_btn.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_btn)
        
        # Save file button
        save_btn = QAction("💾 Save", self)
        save_btn.triggered.connect(self.save_file)
        toolbar.addAction(save_btn)
        
        toolbar.addSeparator()
        
        # Run button (placeholder for future functionality)
        run_btn = QAction("▶️ Run", self)
        run_btn.triggered.connect(self.run_code)
        toolbar.addAction(run_btn)
    
    def setup_statusbar(self):
        """Setup status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Status labels
        self.position_label = QLabel("Ln 1, Col 1")
        self.file_label = QLabel("No file opened")
        self.encoding_label = QLabel("UTF-8")
        
        self.statusbar.addPermanentWidget(self.encoding_label)
        self.statusbar.addPermanentWidget(self.file_label)
        self.statusbar.addPermanentWidget(self.position_label)
        
        self.statusbar.showMessage("Ready")
    
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QMenuBar {
                background-color: #2d2d30;
                color: #cccccc;
            }
            QMenuBar::item:selected {
                background-color: #3e3e42;
            }
            QMenu {
                background-color: #2d2d30;
                color: #cccccc;
                border: 1px solid #3e3e42;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
            QToolBar {
                background-color: #2d2d30;
                border: none;
                padding: 5px;
                spacing: 10px;
            }
            QToolButton {
                background-color: transparent;
                color: #cccccc;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QToolButton:hover {
                background-color: #3e3e42;
            }
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
            QTabWidget::pane {
                border: none;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #cccccc;
                padding: 8px 20px;
                border: none;
                border-right: 1px solid #1e1e1e;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3e3e42;
            }
            QSplitter::handle {
                background-color: #3e3e42;
                width: 1px;
            }
        """)
    
    def current_editor(self):
        """Get the current active editor"""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            return self.tab_widget.widget(current_index)
        return None
    
    def new_file(self):
        """Create a new file"""
        self.create_new_tab()
        self.statusbar.showMessage("New file created")
    
    def open_file_dialog(self):
        """Open file dialog"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "All Files (*);;Python Files (*.py);;JavaScript Files (*.js);;HTML Files (*.html);;CSS Files (*.css)"
        )
        if filepath:
            self.open_file(filepath)
    
    def open_file(self, filepath):
        """Open a specific file"""
        editor = self.create_new_tab(filepath)
        if editor:
            self.file_label.setText(QFileInfo(filepath).fileName())
            self.statusbar.showMessage(f"Opened: {filepath}")
    
    def save_file(self):
        """Save current file"""
        editor = self.current_editor()
        if editor and editor.current_file:
            if editor.save_file():
                self.statusbar.showMessage(f"Saved: {editor.current_file}")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save file with new name"""
        editor = self.current_editor()
        if editor:
            filepath, _ = QFileDialog.getSaveFileName(
                self,
                "Save File As",
                "",
                "All Files (*);;Python Files (*.py);;JavaScript Files (*.js);;HTML Files (*.html);;CSS Files (*.css)"
            )
            if filepath:
                if editor.save_file(filepath):
                    index = self.tab_widget.currentIndex()
                    self.tab_widget.setTabText(index, QFileInfo(filepath).fileName())
                    self.file_label.setText(QFileInfo(filepath).fileName())
                    self.statusbar.showMessage(f"Saved as: {filepath}")
    
    def run_code(self):
        """Run the current code (placeholder for future implementation)"""
        editor = self.current_editor()
        if editor and editor.current_file:
            self.statusbar.showMessage("Run functionality coming soon!")
            QMessageBox.information(self, "Info", "Run functionality will be implemented in the next version.")
        else:
            QMessageBox.warning(self, "Warning", "Please save the file before running.")
    
    def zoom_in(self):
        """Zoom in the editor"""
        editor = self.current_editor()
        if editor:
            font = editor.font()
            font.setPointSize(font.pointSize() + 1)
            editor.setFont(font)
    
    def zoom_out(self):
        """Zoom out the editor"""
        editor = self.current_editor()
        if editor:
            font = editor.font()
            if font.pointSize() > 8:
                font.setPointSize(font.pointSize() - 1)
                editor.setFont(font)
    
    def reset_zoom(self):
        """Reset zoom to default"""
        editor = self.current_editor()
        if editor:
            font = editor.font()
            font.setPointSize(12)
            editor.setFont(font)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About ClawCode Advanced",
            "<h2>ClawCode Advanced</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A modern code editor with advanced features:</p>"
            "<ul>"
            "<li>Multi-tab editing</li>"
            "<li>File explorer</li>"
            "<li>Dark theme</li>"
            "<li>Syntax highlighting support</li>"
            "<li>Zoom controls</li>"
            "</ul>"
            "<p>Built with PyQt5</p>"
        )
    
    def closeEvent(self, event):
        """Handle close event"""
        reply = QMessageBox.question(
            self,
            'Exit',
            'Are you sure you want to exit?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application info
    app.setApplicationName("ClawCode Advanced")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = ClawCodeGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
