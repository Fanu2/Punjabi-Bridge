#!/usr/bin/env python3
"""
Punjabi Transliteration Tools - PySide6
Enhanced desktop version of the supplied Streamlit starter.

Run:
    py -m pip install PySide6
    py punjabi_transliteration_tools.py
"""

import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMessageBox, QPushButton, QPlainTextEdit, QSplitter,
    QStatusBar, QTabWidget, QVBoxLayout, QWidget
)

# Practical character-level Punjabi transliteration tables.
# This is intentionally transparent/editable rather than pretending to be
# a complete linguistic transliteration engine.
G2S = {
    "ਅ":"ا","ਆ":"آ","ਇ":"اِ","ਈ":"ای","ਉ":"اُ","ਊ":"او",
    "ਏ":"اے","ਐ":"اَے","ਓ":"او","ਔ":"اَو",
    "ਕ":"ک","ਖ":"کھ","ਗ":"گ","ਘ":"گھ","ਙ":"نگ",
    "ਚ":"چ","ਛ":"چھ","ਜ":"ج","ਝ":"جھ","ਞ":"نج",
    "ਟ":"ٹ","ਠ":"ٹھ","ਡ":"ڈ","ਢ":"ڈھ","ਣ":"ݨ",
    "ਤ":"ت","ਥ":"تھ","ਦ":"د","ਧ":"دھ","ਨ":"ن",
    "ਪ":"پ","ਫ":"پھ","ਬ":"ب","ਭ":"بھ","ਮ":"م",
    "ਯ":"ی","ਰ":"ر","ਲ":"ل","ਵ":"و","ੜ":"ڑ",
    "ਸ":"س","ਹ":"ہ","ਖ਼":"خ","ਗ਼":"غ","ਜ਼":"ز","ਫ਼":"ف","ਸ਼":"ش","ਲ਼":"ل",
    "ਾ":"ا","ਿ":"ِ","ੀ":"ی","ੁ":"ُ","ੂ":"و","ੇ":"ے","ੈ":"َے","ੋ":"و","ੌ":"َو",
    "ਂ":"ں","ੰ":"ں","ੱ":"ّ","੍":"ْ","਼":"ـ",
    "੦":"۰","੧":"۱","੨":"۲","੩":"۳","੪":"۴","੫":"۵","੬":"۶","੭":"۷","੮":"۸","੯":"۹",
    "।":"۔"
}

# Reverse mapping is deliberately based on canonical outputs. Ambiguous
# Shahmukhi spellings cannot always be uniquely reconstructed.
S2G = {v:k for k,v in G2S.items() if len(v) == 1}
# Useful multi-character sequences first.
S2G_MULTI = sorted(
    [(v,k) for k,v in G2S.items() if len(v) > 1],
    key=lambda x: len(x[0]), reverse=True
)

def transliterate_g2s(text):
    return "".join(G2S.get(ch, ch) for ch in text)

def transliterate_s2g(text):
    out = text
    for src, dst in S2G_MULTI:
        out = out.replace(src, dst)
    return "".join(S2G.get(ch, ch) for ch in out)

def copy_text(editor):
    editor.selectAll()
    editor.copy()
    editor.moveCursor(QTextCursor.Start)
    editor.deselect()

class Editor(QPlainTextEdit):
    def __init__(self, placeholder):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.setFont(QFont("Noto Sans", 15))
        self.setMinimumHeight(250)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Punjabi Transliteration Tools")
        self.resize(1320, 820)
        self.gurmukhi = Editor("Type or paste Punjabi in Gurmukhi…\n\nExample:\nਸਤ ਸ੍ਰੀ ਅਕਾਲ")
        self.shahmukhi = Editor("Type or paste Punjabi in Shahmukhi…\n\nExample:\nست سری اکال")
        self._build()
        self._apply_theme()
        self.statusBar().showMessage("Ready")

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(22,18,22,18)
        main.setSpacing(14)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("ਪੰਜਾਬੀ  Punjabi Transliteration Tools")
        title.setObjectName("title")
        subtitle = QLabel("Gurmukhi ↔ Shahmukhi • fast desktop text workspace")
        subtitle.setObjectName("subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()

        self.swap = QPushButton("⇄  Swap Text")
        self.clear = QPushButton("✕  Clear")
        self.open_btn = QPushButton("📂  Open Text")
        self.save_btn = QPushButton("💾  Save Text")
        header.addWidget(self.open_btn)
        header.addWidget(self.save_btn)
        header.addWidget(self.swap)
        header.addWidget(self.clear)
        main.addLayout(header)

        tabs = QTabWidget()
        main.addWidget(tabs, 1)

        workspace = QWidget()
        wl = QVBoxLayout(workspace)
        wl.setContentsMargins(8,14,8,8)

        split = QSplitter(Qt.Horizontal)
        split.setChildrenCollapsible(False)

        left = self._panel("GURMUKHI", "Gurmukhi Input", self.gurmukhi)
        right = self._panel("SHAHMUKHI", "Shahmukhi Output", self.shahmukhi)
        split.addWidget(left)
        split.addWidget(right)
        split.setSizes([620,620])
        wl.addWidget(split, 1)

        actions = QHBoxLayout()
        self.g2s = QPushButton("→  Transliterate Gurmukhi → Shahmukhi")
        self.s2g = QPushButton("←  Transliterate Shahmukhi → Gurmukhi")
        self.copy_left = QPushButton("Copy Gurmukhi")
        self.copy_right = QPushButton("Copy Shahmukhi")
        actions.addWidget(self.g2s)
        actions.addWidget(self.s2g)
        actions.addStretch()
        actions.addWidget(self.copy_left)
        actions.addWidget(self.copy_right)
        wl.addLayout(actions)

        tabs.addTab(workspace, "  Transliteration  ")

        tools = QWidget()
        tl = QVBoxLayout(tools)
        info = QLabel(
            "Language tools workspace\n\n"
            "The starter Streamlit app used dummy reverse-text output. "
            "This desktop version replaces that with a transparent Unicode "
            "character mapping, while keeping the mapping easy to improve "
            "or replace with a full Punjabi transliteration engine later."
        )
        info.setWordWrap(True)
        info.setObjectName("info")
        tl.addWidget(info)

        stats = QGridLayout()
        self.gstats = QLabel("Gurmukhi characters: 0")
        self.sstats = QLabel("Shahmukhi characters: 0")
        stats.addWidget(self.gstats, 0, 0)
        stats.addWidget(self.sstats, 0, 1)
        tl.addLayout(stats)

        hint = QLabel(
            "Tip: For production-quality linguistic transliteration, plug a "
            "validated Punjabi Gurmukhi/Shahmukhi transliteration library "
            "into transliterate_g2s() and transliterate_s2g()."
        )
        hint.setWordWrap(True)
        tl.addWidget(hint)
        tl.addStretch()
        tabs.addTab(tools, "  Tools & Notes  ")

        footer = QHBoxLayout()
        footer.addWidget(QLabel("Direction"))
        self.direction = QComboBox()
        self.direction.addItems(["Gurmukhi → Shahmukhi", "Shahmukhi → Gurmukhi"])
        footer.addWidget(self.direction)
        footer.addStretch()
        self.count = QLabel("Ready")
        footer.addWidget(self.count)
        main.addLayout(footer)

        self.g2s.clicked.connect(self.do_g2s)
        self.s2g.clicked.connect(self.do_s2g)
        self.swap.clicked.connect(self.do_swap)
        self.clear.clicked.connect(self.do_clear)
        self.copy_left.clicked.connect(lambda: self.gurmukhi.copy())
        self.copy_right.clicked.connect(lambda: self.shahmukhi.copy())
        self.open_btn.clicked.connect(self.open_text)
        self.save_btn.clicked.connect(self.save_text)
        self.gurmukhi.textChanged.connect(self.update_stats)
        self.shahmukhi.textChanged.connect(self.update_stats)

    def _panel(self, badge, heading, editor):
        box = QFrame()
        box.setObjectName("panel")
        lay = QVBoxLayout(box)
        badge_l = QLabel(badge)
        badge_l.setObjectName("badge")
        heading_l = QLabel(heading)
        heading_l.setObjectName("panelTitle")
        lay.addWidget(badge_l)
        lay.addWidget(heading_l)
        lay.addWidget(editor, 1)
        return box

    def _apply_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background:#10131a; color:#eef2f7; }
            QLabel#title { font-size:28px; font-weight:800; color:#f8fafc; }
            QLabel#subtitle { font-size:14px; color:#9aa7b8; }
            QFrame#panel { background:#181d27; border:1px solid #2b3442; border-radius:14px; }
            QLabel#badge { color:#d9a441; font-size:11px; font-weight:800; letter-spacing:1px; }
            QLabel#panelTitle { font-size:17px; font-weight:700; }
            QPlainTextEdit { background:#0f141c; border:1px solid #303a49; border-radius:10px; padding:12px; color:#f8fafc; selection-background-color:#4b5563; }
            QPlainTextEdit:focus { border:1px solid #8b5cf6; }
            QPushButton { background:#222936; border:1px solid #3a4555; border-radius:8px; padding:9px 13px; font-weight:650; color:#f2f5f8; }
            QPushButton:hover { background:#303847; }
            QPushButton:pressed { background:#3b4556; }
            QTabWidget::pane { border:1px solid #2b3442; border-radius:10px; }
            QTabBar::tab { background:#171c25; padding:10px 18px; margin-right:3px; border-radius:7px; }
            QTabBar::tab:selected { background:#6d4aff; color:white; }
            QLabel#info { background:#181d27; border:1px solid #2b3442; border-radius:12px; padding:22px; font-size:15px; }
            QComboBox { background:#202632; border:1px solid #3a4555; border-radius:7px; padding:7px 10px; }
        """)
        self.g2s.setStyleSheet("QPushButton{background:#7657e8;border:0;padding:11px 16px;border-radius:8px;font-weight:700;} QPushButton:hover{background:#886df0;}")
        self.s2g.setStyleSheet("QPushButton{background:#167c80;border:0;padding:11px 16px;border-radius:8px;font-weight:700;} QPushButton:hover{background:#21959a;}")

    def do_g2s(self):
        text = self.gurmukhi.toPlainText()
        if not text.strip():
            return
        self.shahmukhi.setPlainText(transliterate_g2s(text))
        self.statusBar().showMessage("Gurmukhi → Shahmukhi completed")

    def do_s2g(self):
        text = self.shahmukhi.toPlainText()
        if not text.strip():
            return
        self.gurmukhi.setPlainText(transliterate_s2g(text))
        self.statusBar().showMessage("Shahmukhi → Gurmukhi completed")

    def do_swap(self):
        a, b = self.gurmukhi.toPlainText(), self.shahmukhi.toPlainText()
        self.gurmukhi.setPlainText(b)
        self.shahmukhi.setPlainText(a)
        self.statusBar().showMessage("Text swapped")

    def do_clear(self):
        self.gurmukhi.clear()
        self.shahmukhi.clear()
        self.statusBar().showMessage("Cleared")

    def open_text(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open text", "", "Text files (*.txt *.md *.srt);;All files (*.*)")
        if not path:
            return
        try:
            text = Path(path).read_text(encoding="utf-8-sig")
            # Put imported text on the side selected by the direction combo.
            if self.direction.currentIndex() == 0:
                self.gurmukhi.setPlainText(text)
            else:
                self.shahmukhi.setPlainText(text)
            self.statusBar().showMessage(f"Loaded {Path(path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Open error", str(e))

    def save_text(self):
        text = self.gurmukhi.toPlainText() if self.direction.currentIndex() == 0 else self.shahmukhi.toPlainText()
        if not text:
            QMessageBox.information(self, "Nothing to save", "There is no text to save.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save text", "punjabi.txt", "Text files (*.txt);;Markdown (*.md)")
        if path:
            Path(path).write_text(text, encoding="utf-8")
            self.statusBar().showMessage(f"Saved {Path(path).name}")

    def update_stats(self):
        g = len(self.gurmukhi.toPlainText())
        s = len(self.shahmukhi.toPlainText())
        self.gstats.setText(f"Gurmukhi characters: {g}")
        self.sstats.setText(f"Shahmukhi characters: {s}")
        self.count.setText(f"{g + s} characters")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Punjabi Transliteration Tools")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
