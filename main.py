#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C++ MASTER — main.py  (the application)

All content lives in mods.py. Features: lesson pages with C++ syntax
highlighting, inline quizzes, Quiz Center, real-compiler Playground,
Leitner flashcards, cheat sheet, glossary, bookmarks, auto-saved notes,
daily streaks, dashboard, full-text search, dark/light themes, zoom,
progress export. Persisted to ~/.cpp_master.json.

pip install PySide6 && python3 main.py
"""

import datetime, hashlib, html, json, os, random, re, shutil, sys, tempfile, time

try:
    from PySide6.QtCore import Qt, QTimer, QProcess
    from PySide6.QtGui import (QColor, QFont, QKeySequence, QShortcut,
                               QSyntaxHighlighter, QTextCharFormat)
    from PySide6.QtWidgets import (QApplication, QButtonGroup, QComboBox,
        QFileDialog, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
        QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar, QPushButton,
        QRadioButton, QScrollArea, QSpinBox, QSplitter, QStackedWidget,
        QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
        QVBoxLayout, QWidget)
except ImportError:
    print("PySide6 required:  pip install PySide6"); sys.exit(1)

from mods import MODS, FLASHCARDS, CHEATSHEET, GLOSSARY, TOTAL_LESSONS

APP_TITLE = "C++ Master — Learn Modern C++"
SETTINGS_PATH = os.path.join(os.path.expanduser("~"), ".cpp_master.json")

# ============================================================================
#  SYNTAX HIGHLIGHTING
# ============================================================================
HC = {"kw": "#c792ea", "type": "#82aaff", "str": "#c3e88d", "num": "#f78c6c",
      "com": "#6b7382", "prep": "#ff9cac", "std": "#4fd6be"}
KEYWORDS = set("""alignas alignof and and_eq asm auto bitand bitor break case catch class
co_await co_return co_yield compl concept const consteval constexpr constinit const_cast
continue decltype default delete do dynamic_cast else enum explicit export extern false
final for friend goto if inline import module mutable namespace new noexcept not not_eq
nullptr operator or or_eq override private protected public register reinterpret_cast
requires return sizeof static static_assert static_cast struct switch template this
thread_local throw true try typedef typeid typename union using virtual void volatile
while xor xor_eq""".split())
STDTYPES = set("""bool char char8_t char16_t char32_t double float int long short signed
unsigned void wchar_t size_t ssize_t int8_t int16_t int32_t int64_t uint8_t uint16_t
uint32_t uint64_t string string_view vector map set unordered_map unordered_set multimap
list forward_list deque array queue stack priority_queue pair tuple optional variant any
span function thread jthread mutex lock_guard scoped_lock unique_lock atomic future
promise packaged_task expected generator filesystem path error_code atomic_ref
flat_map flat_set bitset regex chrono duration time_point coroutine_handle
istream ostream iostream fstream stringstream ostringstream""".split())


class CppHighlighter(QSyntaxHighlighter):
    NUM_RE = re.compile(r"(?:0[xX][0-9a-fA-F']+|0[bB][01']+|\d[\d']*(?:\.\d[\d']*)?(?:[eE][+-]?\d+)?)[uUlLfF]*")
    WORD_RE = re.compile(r"[A-Za-z_]\w*")

    def __init__(self, doc):
        super().__init__(doc)
        self.f = {}
        for k, col in HC.items():
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(col))
            self.f[k] = fmt

    def highlightBlock(self, text):
        self.setCurrentBlockState(0)
        n, i, f = len(text), 0, self.f
        if self.previousBlockState() == 1:
            j = text.find("*/")
            if j < 0:
                self.setFormat(0, n, f["com"]); self.setCurrentBlockState(1); return
            self.setFormat(0, j + 2, f["com"]); i = j + 2
        elif text.lstrip().startswith("#"):
            self.setFormat(0, n, f["prep"]); return
        while i < n:
            c = text[i]
            two = text[i:i + 2]
            if two == "//":
                self.setFormat(i, n - i, f["com"]); return
            if two == "/*":
                j = text.find("*/", i + 2)
                if j < 0:
                    self.setFormat(i, n - i, f["com"]); self.setCurrentBlockState(1); return
                self.setFormat(i, j + 2 - i, f["com"]); i = j + 2; continue
            if c in "\"'":
                j = i + 1
                while j < n and text[j] != c:
                    j += 2 if text[j] == "\\" else 1
                end = min(j + 1, n)
                self.setFormat(i, end - i, f["str"]); i = end; continue
            if c.isdigit():
                m = self.NUM_RE.match(text, i)
                if m:
                    self.setFormat(i, m.end() - i, f["num"]); i = m.end(); continue
            if c.isalpha() or c == "_":
                m = self.WORD_RE.match(text, i)
                w = m.group(0)
                if w in KEYWORDS:
                    self.setFormat(i, len(w), f["kw"])
                elif w in STDTYPES:
                    self.setFormat(i, len(w), f["type"])
                elif w == "std":
                    self.setFormat(i, 3, f["std"])
                i = m.end(); continue
            i += 1


# ============================================================================
#  RENDERING
# ============================================================================
STD_COLORS = {"C++98": "#8a8f98", "C++11": "#3fb27f", "C++14": "#3aa9a0",
              "C++17": "#4f8ef7", "C++20": "#9d7bf5", "C++23": "#f06bb3",
              "C++26": "#ff9cac", "Core": "#e0a645"}

def md_like(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`",
               r"<code style='background-color:#2a2e38;color:#8fd3ff;"
               r"padding:1px 4px;border-radius:3px;'>\1</code>", s)
    return s

def mono_font(size=10):
    f = QFont()
    try:
        f.setFamilies(["Consolas", "Menlo", "DejaVu Sans Mono", "Courier New", "monospace"])
    except AttributeError:
        f.setFamily("Consolas")
    f.setStyleHint(QFont.Monospace)
    f.setPointSize(size)
    return f


class CodeBlock(QWidget):
    def __init__(self, code, output=None):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(0, 2, 0, 0); v.setSpacing(3)
        bar = QHBoxLayout()
        lang = QLabel("C++"); lang.setStyleSheet("color:#7d8590;font-size:11px;")
        cp = QPushButton("Copy"); cp.setFixedHeight(22); cp.setCursor(Qt.PointingHandCursor)
        cp.clicked.connect(lambda: self._copy(cp))
        bar.addWidget(lang); bar.addStretch(1); bar.addWidget(cp)
        v.addLayout(bar)
        self.edit = QPlainTextEdit(); self.edit.setObjectName("code")
        self.edit.setReadOnly(True); self.edit.setFont(mono_font(10))
        self.edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.edit.setPlainText(code.strip("\n"))
        lines = code.strip("\n").count("\n") + 1
        self.edit.setFixedHeight(self.edit.fontMetrics().lineSpacing() * lines + 16)
        CppHighlighter(self.edit.document())
        v.addWidget(self.edit)
        if output is not None:
            lab = QLabel("▶ Output")
            lab.setStyleSheet("color:#7ee787;font-size:11px;font-weight:600;")
            v.addWidget(lab)
            out = QPlainTextEdit(); out.setObjectName("output"); out.setReadOnly(True)
            out.setFont(mono_font(10)); out.setPlainText(output.strip("\n"))
            olines = min(output.strip("\n").count("\n") + 1, 14)
            out.setFixedHeight(out.fontMetrics().lineSpacing() * olines + 16)
            v.addWidget(out)

    def _copy(self, btn):
        QApplication.clipboard().setText(self.edit.toPlainText())
        btn.setText("Copied ✓")
        QTimer.singleShot(1300, lambda: btn.setText("Copy"))


class InlineQuestion(QFrame):
    def __init__(self, q, number):
        super().__init__()
        self.q = q; self.setObjectName("note")
        v = QVBoxLayout(self); v.setContentsMargins(12, 10, 12, 10)
        ql = QLabel(md_like(f"**Q{number}. {q['q']}**")); ql.setWordWrap(True)
        v.addWidget(ql)
        self.radios = []; self.group = QButtonGroup(self)
        for ch in q["ch"]:
            r = QRadioButton(md_like(ch)); r.setCursor(Qt.PointingHandCursor)
            self.group.addButton(r); self.radios.append(r); v.addWidget(r)
        row = QHBoxLayout()
        self.btn = QPushButton("Check"); self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.clicked.connect(self.check)
        self.fb = QLabel(""); self.fb.setWordWrap(True); self.fb.hide()
        row.addWidget(self.btn); row.addStretch(1); v.addLayout(row); v.addWidget(self.fb)

    def check(self):
        sel = next((i for i, r in enumerate(self.radios) if r.isChecked()), None)
        if sel is None:
            self.fb.setText("<span style='color:#e0a645'>Pick an option first.</span>")
            self.fb.show(); return
        for r in self.radios:
            r.setEnabled(False)
        self.btn.setEnabled(False)
        a = self.q["a"]
        self.radios[a].setStyleSheet("color:#7ee787;font-weight:600;")
        if sel == a:
            text = "✅ Correct!"
        else:
            self.radios[sel].setStyleSheet("color:#ff7b72;")
            text = f"❌ Correct answer: {md_like(self.q['ch'][a])}"
        if self.q.get("why"):
            text += "<br>" + md_like(self.q["why"])
        self.fb.setText(text); self.fb.show()


def render_blocks(lesson, layout):
    for b in lesson["blocks"]:
        t = b["t"]
        if t == "text":
            lbl = QLabel(md_like(b["x"])); lbl.setWordWrap(True); layout.addWidget(lbl)
        elif t == "h":
            lbl = QLabel(md_like(b["x"]))
            lbl.setStyleSheet("font-size:16px;font-weight:700;color:#5aa2f0;margin-top:8px;")
            layout.addWidget(lbl)
        elif t == "code":
            layout.addWidget(CodeBlock(b["x"], b.get("out")))
        elif t in ("note", "warn"):
            fr = QFrame(); fr.setObjectName(t)
            h = QHBoxLayout(fr); h.setContentsMargins(12, 8, 12, 8)
            icon = QLabel("💡" if t == "note" else "⚠️")
            lbl = QLabel(md_like(b["x"])); lbl.setWordWrap(True)
            h.addWidget(icon, 0, Qt.AlignTop); h.addWidget(lbl, 1)
            layout.addWidget(fr)
        elif t == "table":
            hd, rows = b["hd"], b["rows"]
            tb = QTableWidget(len(rows), len(hd))
            tb.setHorizontalHeaderLabels([c.replace("`", "") for c in hd])
            for r, cells in enumerate(rows):
                for c2, cell in enumerate(cells):
                    tb.setItem(r, c2, QTableWidgetItem(str(cell).replace("`", "")))
            tb.setEditTriggers(QTableWidget.NoEditTriggers)
            tb.verticalHeader().setVisible(False)
            tb.setAlternatingRowColors(True)
            tb.horizontalHeader().setStretchLastSection(True)
            tb.resizeColumnsToContents()
            layout.addWidget(tb)


# ============================================================================
#  LESSON PAGE
# ============================================================================
class LessonPage(QWidget):
    def __init__(self, main, mi, li):
        super().__init__()
        self.main, self.mi, self.li = main, mi, li
        lesson = MODS[mi]["lessons"][li]
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget(); v = QVBoxLayout(inner)
        v.setContentsMargins(22, 18, 22, 18); v.setSpacing(10)

        head = QHBoxLayout()
        title = QLabel(lesson["title"]); title.setObjectName("lessonTitle"); title.setWordWrap(True)
        head.addWidget(title, 1)
        self.bmBtn = QPushButton("☆ Bookmark")
        self.bmBtn.setCursor(Qt.PointingHandCursor)
        self.bmBtn.clicked.connect(main.toggle_bookmark_current)
        head.addWidget(self.bmBtn, 0, Qt.AlignTop)
        chip = QLabel(lesson["std"])
        chip.setStyleSheet(f"background:{STD_COLORS.get(lesson['std'], '#888')};"
                           "color:#10131a;border-radius:9px;padding:3px 10px;font-weight:700;")
        head.addWidget(chip, 0, Qt.AlignTop)
        v.addLayout(head)

        sub = QLabel(f'Module {mi + 1} · {MODS[mi]["title"]}')
        sub.setStyleSheet("color:#7d8590;font-size:12px;")
        v.addWidget(sub)
        render_blocks(lesson, v)

        if lesson["quiz"]:
            qh = QLabel("🧠 Check yourself")
            qh.setStyleSheet("font-size:16px;font-weight:700;color:#5aa2f0;margin-top:8px;")
            v.addWidget(qh)
            for i, q in enumerate(lesson["quiz"], 1):
                v.addWidget(InlineQuestion(q, i))

        nh = QLabel("📝 My notes (auto-saved)")
        nh.setStyleSheet("font-size:14px;font-weight:700;color:#5aa2f0;margin-top:8px;")
        v.addWidget(nh)
        self.notes = QPlainTextEdit(); self.notes.setObjectName("notes")
        self.notes.setFont(mono_font(10))
        self.notes.setPlaceholderText("Write your own summary, gotchas, questions…")
        self.notes.setFixedHeight(90)
        self.notes.setPlainText(main.store.data.get("notes", {}).get(f"{mi}-{li}", ""))
        self._ntimer = QTimer(self); self._ntimer.setSingleShot(True)
        self._ntimer.timeout.connect(self.save_notes)
        self.notes.textChanged.connect(lambda: self._ntimer.start(700))
        v.addWidget(self.notes)

        v.addStretch(1)
        nav = QHBoxLayout()
        self.prevBtn = QPushButton("← Previous"); self.nextBtn = QPushButton("Next →")
        self.doneBtn = QPushButton("Mark lesson as complete")
        self.doneBtn.setObjectName("primary")
        for b in (self.prevBtn, self.doneBtn, self.nextBtn):
            b.setCursor(Qt.PointingHandCursor)
        self.prevBtn.clicked.connect(lambda: main.step_lesson(-1))
        self.nextBtn.clicked.connect(lambda: main.step_lesson(1))
        self.doneBtn.clicked.connect(main.toggle_done_current)
        nav.addWidget(self.prevBtn); nav.addStretch(1)
        nav.addWidget(self.doneBtn); nav.addStretch(1)
        nav.addWidget(self.nextBtn)
        v.addLayout(nav)
        scroll.setWidget(inner); outer.addWidget(scroll)
        self.refresh_done()

    def save_notes(self):
        key = f"{self.mi}-{self.li}"
        self.main.store.data.setdefault("notes", {})[key] = self.notes.toPlainText()
        self.main.store.save()

    def refresh_done(self):
        key = f"{self.mi}-{self.li}"
        done = self.main.store.is_done(key)
        self.doneBtn.setText("✅ Completed — click to unmark" if done
                             else "Mark lesson as complete")
        marked = key in self.main.store.data.get("bookmarks", [])
        self.bmBtn.setText("★ Bookmarked" if marked else "☆ Bookmark")


# ============================================================================
#  FLASHCARDS  (Leitner spaced repetition)
# ============================================================================
CARD_INTERVALS = [60, 600, 86400, 3 * 86400, 7 * 86400]

class Flashcards(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        main.store.data.setdefault("cards", {})
        self.cards = [{"id": hashlib.md5(f.encode()).hexdigest()[:10], "f": f, "b": b}
                      for f, b in FLASHCARDS]
        self.current = None
        v = QVBoxLayout(self); v.setContentsMargins(22, 18, 22, 18)
        t = QLabel("🗂 Flashcards — Spaced Repetition")
        t.setObjectName("lessonTitle"); v.addWidget(t)
        self.info = QLabel(""); self.info.setStyleSheet("color:#7d8590;")
        v.addWidget(self.info)
        self.card = QFrame(); self.card.setObjectName("note")
        cv = QVBoxLayout(self.card); cv.setContentsMargins(24, 22, 24, 22)
        self.front = QLabel(""); self.front.setWordWrap(True)
        self.front.setStyleSheet("font-size:19px;font-weight:700;")
        self.front.setAlignment(Qt.AlignCenter); cv.addWidget(self.front)
        self.back = QLabel(""); self.back.setWordWrap(True)
        self.back.setStyleSheet("font-size:16px;color:#7ee787;")
        self.back.setAlignment(Qt.AlignCenter); self.back.hide(); cv.addWidget(self.back)
        v.addWidget(self.card, 1)
        row = QHBoxLayout()
        self.showBtn = QPushButton("👁 Show answer"); self.showBtn.setObjectName("primary")
        self.showBtn.clicked.connect(self.reveal)
        self.againBtn = QPushButton("✖ Again"); self.goodBtn = QPushButton("✔ Good")
        self.easyBtn = QPushButton("⚡ Easy")
        for b in (self.againBtn, self.goodBtn, self.easyBtn):
            b.setEnabled(False); b.clicked.connect(self._grade(b))
        row.addWidget(self.showBtn); row.addStretch(1)
        row.addWidget(self.againBtn); row.addWidget(self.goodBtn); row.addWidget(self.easyBtn)
        v.addLayout(row)
        self.nextBtn = QPushButton("Next card →"); self.nextBtn.clicked.connect(self.pick)
        self.nextBtn.setCursor(Qt.PointingHandCursor)
        v.addWidget(self.nextBtn, 0, Qt.AlignRight)
        self.pick()

    def _state(self, c):
        return self.main.store.data["cards"].setdefault(c["id"], {"box": 0, "due": 0})

    def pick(self):
        now = time.time()
        due = [c for c in self.cards if self._state(c)["due"] <= now]
        fresh = [c for c in self.cards if self._state(c)["box"] == 0]
        pool = due or fresh or self.cards
        if not pool:
            self.front.setText("No cards in the deck."); return
        self.current = random.choice(pool)
        self.front.setText(self.current["f"])
        self.back.hide()
        self.showBtn.setEnabled(True)
        for b in (self.againBtn, self.goodBtn, self.easyBtn):
            b.setEnabled(False)
        known = sum(1 for c in self.cards if self._state(c)["box"] >= 3)
        self.info.setText(f"Deck: {len(self.cards)} cards · {known} in long-term "
                          f"memory · {len(due)} due now")

    def reveal(self):
        self.back.setText(self.current["b"]); self.back.show()
        self.showBtn.setEnabled(False)
        for b in (self.againBtn, self.goodBtn, self.easyBtn):
            b.setEnabled(True)

    def _grade(self, btn):
        def go():
            st = self._state(self.current)
            if btn is self.againBtn:
                st["box"] = 0
            elif btn is self.goodBtn:
                st["box"] = min(st["box"] + 1, len(CARD_INTERVALS) - 1)
            else:
                st["box"] = min(st["box"] + 2, len(CARD_INTERVALS) - 1)
            st["due"] = time.time() + CARD_INTERVALS[st["box"]]
            self.main.store.save()
            self.pick()
        return go


# ============================================================================
#  CHEAT SHEET & GLOSSARY
# ============================================================================
class CheatSheet(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(22, 18, 22, 18)
        t = QLabel("📋 Cheat Sheet"); t.setObjectName("lessonTitle"); v.addWidget(t)
        self.search = QLineEdit(); self.search.setPlaceholderText("Filter snippets…")
        self.search.textChanged.connect(self._filter); v.addWidget(self.search)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget(); self.body = QVBoxLayout(inner)
        self.body.setContentsMargins(0, 10, 0, 10); self.body.setSpacing(8)
        self.sections = []
        for cat, snippets in CHEATSHEET:
            hdr = QLabel(cat)
            hdr.setStyleSheet("font-size:15px;font-weight:700;color:#5aa2f0;")
            self.body.addWidget(hdr)
            blocks = []
            for title, code in snippets:
                lbl = QLabel(title); lbl.setStyleSheet("font-weight:600;")
                self.body.addWidget(lbl)
                blk = CodeBlock(code); self.body.addWidget(blk)
                blocks.append((lbl, blk, (title + " " + code).lower()))
            self.body.addSpacing(4)
            self.sections.append((hdr, blocks))
        scroll.setWidget(inner); v.addWidget(scroll)

    def _filter(self, text):
        q = text.strip().lower()
        for hdr, blocks in self.sections:
            any_vis = False
            for lbl, blk, hay in blocks:
                vis = not q or q in hay
                lbl.setVisible(vis); blk.setVisible(vis)
                any_vis = any_vis or vis
            hdr.setVisible(any_vis)


class Glossary(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(22, 18, 22, 18)
        t = QLabel("📖 Glossary"); t.setObjectName("lessonTitle"); v.addWidget(t)
        self.search = QLineEdit(); self.search.setPlaceholderText("Filter terms…")
        self.search.textChanged.connect(self._filter); v.addWidget(self.search)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget(); body = QVBoxLayout(inner)
        body.setContentsMargins(0, 10, 0, 10); body.setSpacing(6)
        self.entries = []
        for term, definition in GLOSSARY:
            fr = QFrame(); fr.setObjectName("note")
            h = QHBoxLayout(fr); h.setContentsMargins(12, 8, 12, 8)
            tl = QLabel(f"<b>{term}</b>"); tl.setFixedWidth(160); tl.setWordWrap(True)
            dl = QLabel(definition); dl.setWordWrap(True)
            h.addWidget(tl, 0, Qt.AlignTop); h.addWidget(dl, 1)
            body.addWidget(fr)
            self.entries.append((fr, (term + " " + definition).lower()))
        body.addStretch(1)
        scroll.setWidget(inner); v.addWidget(scroll)

    def _filter(self, text):
        q = text.strip().lower()
        for fr, hay in self.entries:
            fr.setVisible(not q or q in hay)


# ============================================================================
#  QUIZ CENTER
# ============================================================================
class QuizCenter(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.qs, self.idx, self.score = [], 0, 0
        root = QVBoxLayout(self); root.setContentsMargins(22, 18, 22, 18)
        title = QLabel("❓ Quiz Center"); title.setObjectName("lessonTitle"); root.addWidget(title)
        info = QLabel("Random questions drawn from every lesson quiz. Choose a module and go!")
        info.setWordWrap(True); root.addWidget(info)
        top = QHBoxLayout()
        top.addWidget(QLabel("Module:"))
        self.combo = QComboBox(); self.combo.addItem("All modules")
        for m in MODS:
            self.combo.addItem(m["title"])
        top.addWidget(self.combo)
        top.addWidget(QLabel("Questions:"))
        self.spin = QSpinBox(); self.spin.setRange(1, 30); self.spin.setValue(10)
        top.addWidget(self.spin)
        self.startBtn = QPushButton("▶ Start quiz"); self.startBtn.setObjectName("primary")
        self.startBtn.setCursor(Qt.PointingHandCursor)
        self.startBtn.clicked.connect(self.start); top.addWidget(self.startBtn)
        top.addStretch(1); root.addLayout(top)

        self.area = QWidget(); av = QVBoxLayout(self.area)
        av.setContentsMargins(0, 12, 0, 0)
        self.prog = QLabel(""); self.prog.setStyleSheet("color:#7d8590;"); av.addWidget(self.prog)
        self.qLabel = QLabel(""); self.qLabel.setWordWrap(True)
        self.qLabel.setStyleSheet("font-size:15px;font-weight:600;margin-top:6px;")
        av.addWidget(self.qLabel)
        self.optBox = QVBoxLayout(); av.addLayout(self.optBox)
        self.fb = QLabel(""); self.fb.setWordWrap(True); av.addWidget(self.fb)
        btns = QHBoxLayout()
        self.submitBtn = QPushButton("Submit answer"); self.submitBtn.setObjectName("primary")
        self.nextBtn2 = QPushButton("Next →"); self.nextBtn2.setEnabled(False)
        self.submitBtn.clicked.connect(self.submit); self.nextBtn2.clicked.connect(self.next_q)
        btns.addWidget(self.submitBtn); btns.addWidget(self.nextBtn2); btns.addStretch(1)
        av.addLayout(btns)
        self.result = QLabel(""); self.result.setWordWrap(True)
        self.result.setStyleSheet("font-size:16px;font-weight:700;")
        av.addWidget(self.result)
        self.area.hide(); root.addStretch(1)

    def start(self):
        sel = self.combo.currentText()
        pool = [x for x in self.main.quiz_bank if sel == "All modules" or x[0] == sel]
        if not pool:
            self.result.setText("No questions available for this selection.")
            self.result.show(); return
        self.result.hide()
        random.shuffle(pool)
        self.qs = []
        for mt, src, q in pool[: min(self.spin.value(), len(pool))]:
            order = list(range(len(q["ch"])))
            random.shuffle(order)
            self.qs.append({"q": q["q"], "ch": [q["ch"][i] for i in order],
                            "a": order.index(q["a"]), "why": q.get("why", ""), "src": src})
        self.idx, self.score = 0, 0
        self.area.show(); self.show_q()

    def show_q(self):
        q = self.qs[self.idx]
        self.prog.setText(f"Question {self.idx + 1} of {len(self.qs)}   ·   "
                          f"score {self.score}   ·   {q['src']}")
        self.qLabel.setText(md_like(q["q"]))
        self.fb.clear(); self.nextBtn2.setEnabled(False); self.submitBtn.setEnabled(True)
        while self.optBox.count():
            item = self.optBox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.buttons = QButtonGroup(self)
        for ch in q["ch"]:
            r = QRadioButton(md_like(ch)); r.setCursor(Qt.PointingHandCursor)
            self.buttons.addButton(r); self.optBox.addWidget(r)

    def submit(self):
        sel = next((i for i, b in enumerate(self.buttons.buttons()) if b.isChecked()), None)
        if sel is None:
            self.fb.setText("<span style='color:#e0a645'>Pick an option first.</span>")
            return
        q = self.qs[self.idx]
        for b in self.buttons.buttons():
            b.setEnabled(False)
        self.buttons.buttons()[q["a"]].setStyleSheet("color:#7ee787;font-weight:600;")
        if sel == q["a"]:
            self.score += 1; text = "✅ Correct!"
        else:
            self.buttons.buttons()[sel].setStyleSheet("color:#ff7b72;")
            text = f"❌ Correct: {md_like(q['ch'][q['a']])}"
        if q["why"]:
            text += "<br>" + md_like(q["why"])
        self.fb.setText(text)
        self.submitBtn.setEnabled(False); self.nextBtn2.setEnabled(True)
        self.nextBtn2.setText("See results →" if self.idx == len(self.qs) - 1 else "Next →")

    def next_q(self):
        self.idx += 1
        if self.idx < len(self.qs):
            self.show_q()
        else:
            self.finish()

    def finish(self):
        pct = round(100 * self.score / len(self.qs))
        face = "🏆" if pct >= 90 else "🎉" if pct >= 70 else "📖" if pct >= 50 else "💪"
        self.result.setText(f"{face} {self.score}/{len(self.qs)} — {pct}%")
        self.result.show()
        key = self.combo.currentText()
        best = self.main.store.data["best"].get(key, 0)
        if pct > best:
            self.main.store.data["best"][key] = pct
        self.main.store.data.setdefault("quiz_history", []).append(
            {"when": datetime.date.today().isoformat(), "key": key, "pct": pct})
        self.main.store.save()
        self.nextBtn2.setEnabled(False)
        self.main.refresh_dashboard()


# ============================================================================
#  PLAYGROUND
# ============================================================================
PRESETS = {
    "Starter": r'''#include <iostream>

int main() {
    std::cout << "Hello from the playground!\n";
}''',
    "Vector + Algorithm": r'''#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    std::vector<int> v{5, 2, 8, 1};
    std::sort(v.begin(), v.end());
    for (int x : v) std::cout << x << ' ';
    std::cout << '\n';
}''',
    "Lambda Fun": r'''#include <algorithm>
#include <iostream>
#include <vector>

int main() {
    std::vector<int> v{1,2,3,4,5,6};
    int evens = std::count_if(v.begin(), v.end(), [](int x){ return x % 2 == 0; });
    std::cout << "evens: " << evens << '\n';
}''',
    "Classes & Virtual": r'''#include <iostream>
#include <memory>

struct Animal { virtual void speak() const { std::cout << "...\n"; } virtual ~Animal() = default; };
struct Dog : Animal { void speak() const override { std::cout << "woof\n"; } };

int main() {
    std::unique_ptr<Animal> a = std::make_unique<Dog>();
    a->speak();
}''',
    "Templates": r'''#include <iostream>

template <typename T>
T maxOf(T a, T b) { return a > b ? a : b; }

int main() { std::cout << maxOf(3, 7) << '\n'; }''',
    "Threads": r'''#include <iostream>
#include <thread>

int main() {
    std::thread t([]{ std::cout << "from another thread\n"; });
    t.join();
}''',
    "Bit Tricks": r'''#include <bit>
#include <iostream>

int main() {
    unsigned f = 0;
    f |= (1u << 3);
    std::cout << std::popcount(0b1011u) << ' ' << std::has_single_bit(8u)
              << ' ' << f << '\n';
}''',
}
MSVC_STD = {"c++11": "c++14", "c++14": "c++14", "c++17": "c++17",
            "c++20": "c++20", "c++23": "c++latest"}

def detect_compiler():
    for name in ("g++", "clang++", "c++", "cl"):
        p = shutil.which(name)
        if p:
            return p, (name == "cl")
    return None, False


class Playground(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.compiler, self.is_msvc = detect_compiler()
        self.proc = None; self.exe_path = None; self.workdir = None; self.retry_stds = []
        v = QVBoxLayout(self); v.setContentsMargins(22, 18, 22, 18)
        t = QLabel("🧪 Code Playground"); t.setObjectName("lessonTitle"); v.addWidget(t)
        info = ("Compiler found: " + os.path.basename(self.compiler) if self.compiler
                else "No C++ compiler found on PATH — the editor works, but 'Run' "
                     "needs g++, clang++ or MSVC cl installed.")
        cl = QLabel(info); cl.setStyleSheet("color:#7d8590;"); v.addWidget(cl)
        row = QHBoxLayout()
        row.addWidget(QLabel("Preset:"))
        self.preset = QComboBox(); self.preset.addItems(PRESETS.keys())
        self.preset.currentTextChanged.connect(self.load_preset); row.addWidget(self.preset)
        row.addWidget(QLabel("  Standard:"))
        self.std = QComboBox()
        for data, label in [("c++11", "C++11"), ("c++14", "C++14"), ("c++17", "C++17"),
                            ("c++20", "C++20"), ("c++23", "C++23")]:
            self.std.addItem(label, data)
        self.std.setCurrentIndex(3); row.addWidget(self.std)
        row.addStretch(1)
        self.runBtn = QPushButton("▶ Run"); self.runBtn.setObjectName("primary")
        self.runBtn.setCursor(Qt.PointingHandCursor)
        self.runBtn.clicked.connect(self.run_code); row.addWidget(self.runBtn)
        v.addLayout(row)
        self.editor = QPlainTextEdit(); self.editor.setObjectName("code")
        self.editor.setFont(mono_font(11)); self.editor.setPlainText(PRESETS["Starter"])
        CppHighlighter(self.editor.document()); v.addWidget(self.editor, 1)
        olab = QLabel("Console"); olab.setStyleSheet("color:#7d8590;font-size:11px;")
        v.addWidget(olab)
        self.output = QPlainTextEdit(); self.output.setObjectName("output")
        self.output.setReadOnly(True); self.output.setFont(mono_font(10))
        self.output.setPlainText("Ready."); v.addWidget(self.output, 1)
        self.timer = QTimer(self); self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timeout)

    def load_preset(self, name):
        self.editor.setPlainText(PRESETS.get(name, ""))

    def log(self, s):
        self.output.appendPlainText(s)

    def run_code(self):
        if self.proc is not None:
            return
        if not self.compiler:
            self.log("\n⚠ No compiler found. Install g++ (MSYS2 / apt / Xcode tools) "
                     "and make sure it is on PATH."); return
        self.workdir = tempfile.mkdtemp(prefix="cppplay_")
        src = os.path.join(self.workdir, "main.cpp")
        with open(src, "w", encoding="utf-8") as f:
            f.write(self.editor.toPlainText())
        self.exe_path = os.path.join(self.workdir,
                                     "prog" + (".exe" if os.name == "nt" else ""))
        std = self.std.currentData()
        self.retry_stds = ["c++20", "c++17"] if std not in ("c++17",) else []
        self.runBtn.setEnabled(False)
        self.log(f"\n$ compiling ({std}) …")
        self._compile(std)

    def _compile(self, std):
        if self.is_msvc:
            args = ["/nologo", "/EHsc", "/utf-8", f"/std:{MSVC_STD.get(std, 'c++20')}",
                    f"/Fe:{self.exe_path}", os.path.join(self.workdir, "main.cpp")]
        else:
            args = [f"-std={std}", "-Wall", os.path.join(self.workdir, "main.cpp"),
                    "-o", self.exe_path]
        self.proc = QProcess(self); self.proc.finished.connect(self._compiled)
        self.proc.setWorkingDirectory(self.workdir)
        self.timer.start(30000); self.proc.start(self.compiler, args)

    def _compiled(self, code, status):
        self.timer.stop()
        err = bytes(self.proc.readAllStandardError()).decode(errors="replace")
        out = bytes(self.proc.readAllStandardOutput()).decode(errors="replace")
        failed = (code != 0 or status == QProcess.CrashExit)
        if failed and err and \
                re.search(r"unrecognized|invalid value|unknown option.*std", err) \
                and self.retry_stds:
            fallback = self.retry_stds.pop(0)
            self.proc = None
            self.log(f"  {self.std.currentData()} unsupported — retrying with {fallback}")
            return self._compile(fallback)
        if failed:
            self.log("❌ Compilation failed:\n" + (err or out or "(no message)"))
            self._cleanup(); return
        self.log("✔ compiled — running…\n")
        self.proc = QProcess(self); self.proc.finished.connect(self._ran)
        self.proc.setWorkingDirectory(self.workdir)
        self.timer.start(10000); self.proc.start(self.exe_path, [])

    def _ran(self, code, status):
        self.timer.stop()
        out = bytes(self.proc.readAllStandardOutput()).decode(errors="replace")
        err = bytes(self.proc.readAllStandardError()).decode(errors="replace")
        if out:
            self.log(out.rstrip())
        if err:
            self.log("[stderr] " + err.rstrip())
        self.log(f"\n— program exited with code {code}" +
                 (" (crashed)" if status == QProcess.CrashExit else ""))
        self._cleanup()

    def timeout(self):
        if self.proc:
            self.proc.kill(); self.log("\n⏱ killed after timeout.")

    def _cleanup(self):
        self.proc = None; self.runBtn.setEnabled(True)
        if self.workdir:
            shutil.rmtree(self.workdir, ignore_errors=True); self.workdir = None


# ============================================================================
#  DASHBOARD
# ============================================================================
def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w:
            w.deleteLater()
        elif item.layout():
            clear_layout(item.layout())


class Dashboard(QWidget):
    def __init__(self, main):
        super().__init__()
        self.main = main
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget(); self.body = QVBoxLayout(inner)
        self.body.setContentsMargins(22, 18, 22, 18); self.body.setSpacing(10)
        scroll.setWidget(inner); outer.addWidget(scroll)

    def refresh(self):
        clear_layout(self.body)
        store, main = self.main.store, self.main
        done = len(store.data["completed"])
        title = QLabel("📊 Your Progress"); title.setObjectName("lessonTitle")
        self.body.addWidget(title)
        streak = store.data.get("streak", {})
        st = (f"🔥 {streak.get('count', 0)}-day streak" if streak.get("count")
              else "🌙 Start a streak today!")
        self.body.addWidget(QLabel(st))
        pct = round(100 * done / TOTAL_LESSONS) if TOTAL_LESSONS else 0
        self.body.addWidget(QLabel(f"{done} of {TOTAL_LESSONS} lessons complete ({pct}%)"))
        bar = QProgressBar(); bar.setRange(0, max(TOTAL_LESSONS, 1)); bar.setValue(done)
        bar.setTextVisible(False); bar.setFixedHeight(12); self.body.addWidget(bar)

        btn = QPushButton("▶ Continue where you left off"); btn.setObjectName("primary")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(main.load_first_incomplete)
        self.body.addWidget(btn); self.body.addSpacing(6)

        std_total, std_done = {}, {}
        for mi, m in enumerate(MODS):
            for li, les in enumerate(m["lessons"]):
                std_total[les["std"]] = std_total.get(les["std"], 0) + 1
                if store.is_done(f"{mi}-{li}"):
                    std_done[les["std"]] = std_done.get(les["std"], 0) + 1
        chips = QHBoxLayout()
        for stdn in ["Core", "C++98", "C++11", "C++14", "C++17", "C++20", "C++23", "C++26"]:
            if stdn not in std_total:
                continue
            col = STD_COLORS.get(stdn, "#888")
            chip = QLabel(f"{stdn}: {std_done.get(stdn, 0)}/{std_total[stdn]}")
            chip.setStyleSheet(f"background:{col};color:#10131a;border-radius:9px;"
                               "padding:3px 10px;font-weight:700;")
            chips.addWidget(chip)
        chips.addStretch(1)
        self.body.addLayout(chips); self.body.addSpacing(8)

        mh = QLabel("Modules")
        mh.setStyleSheet("font-size:16px;font-weight:700;color:#5aa2f0;")
        self.body.addWidget(mh)
        for mi, m in enumerate(MODS):
            n = len(m["lessons"])
            d = sum(1 for li in range(n) if store.is_done(f"{mi}-{li}"))
            row = QHBoxLayout()
            lbl = QLabel(m["title"]); lbl.setMinimumWidth(230); row.addWidget(lbl)
            pb = QProgressBar(); pb.setRange(0, n); pb.setValue(d)
            pb.setTextVisible(False); pb.setFixedHeight(10)
            row.addWidget(pb, 1)
            cnt = QLabel(f"{d}/{n}"); cnt.setStyleSheet("color:#7d8590;"); row.addWidget(cnt)
            self.body.addLayout(row)

        if store.data.get("bookmarks"):
            self.body.addSpacing(10)
            bh = QLabel("⭐ Bookmarks")
            bh.setStyleSheet("font-size:16px;font-weight:700;color:#5aa2f0;")
            self.body.addWidget(bh)
            for key in store.data["bookmarks"]:
                try:
                    mi2, li2 = map(int, key.split("-"))
                except ValueError:
                    continue
                if mi2 >= len(MODS) or li2 >= len(MODS[mi2]["lessons"]):
                    continue
                les = MODS[mi2]["lessons"][li2]
                b = QPushButton(f"⭐ {les['title']}  ({MODS[mi2]['title']})")
                b.setCursor(Qt.PointingHandCursor)
                b.clicked.connect(lambda _=False, a=mi2, c=li2: main.load_lesson(a, c))
                self.body.addWidget(b)

        if store.data.get("best"):
            self.body.addSpacing(10)
            qh = QLabel("Best quiz scores")
            qh.setStyleSheet("font-size:16px;font-weight:700;color:#5aa2f0;")
            self.body.addWidget(qh)
            for k, pct in sorted(store.data["best"].items()):
                self.body.addWidget(QLabel(f"• {k}: {pct}%"))
        hist = store.data.get("quiz_history", [])[-5:]
        if hist:
            self.body.addWidget(QLabel("Recent: " + " · ".join(
                f"{h['key'][:18]} {h['pct']}%" for h in hist)))
        self.body.addStretch(1)


# ============================================================================
#  PERSISTENCE
# ============================================================================
class Store:
    def __init__(self):
        self.path = SETTINGS_PATH
        self.data = {"completed": [], "theme": "dark", "last": None, "best": {},
                     "bookmarks": [], "notes": {}, "cards": {}, "quiz_history": [],
                     "zoom": 1.0, "streak": {"last": "", "count": 0}}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.data.update(json.load(f))
        except Exception:
            pass

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def is_done(self, key):
        return key in self.data["completed"]

    def set_done(self, key, done):
        cl = self.data["completed"]
        if done and key not in cl:
            cl.append(key)
        elif not done and key in cl:
            cl.remove(key)
        self.save()


# ============================================================================
#  THEMES
# ============================================================================
DARK_QSS = """
QMainWindow, QWidget { background:#1b1d23; color:#dfe3ea; font-size:13px; }
QTreeWidget { background:#20232a; border:none; }
QTreeWidget::item { padding:5px; border-radius:4px; }
QTreeWidget::item:selected { background:#33517a; color:white; }
QLineEdit, QComboBox, QSpinBox { background:#262a33; border:1px solid #3a3f4b;
    border-radius:6px; padding:5px 8px; }
QPushButton { background:#2f3542; border:1px solid #414a5c; border-radius:6px;
    padding:6px 14px; color:#dfe3ea; }
QPushButton:hover { background:#3a4254; }
QPushButton:disabled { color:#666; }
QPushButton#primary { background:#3b6ea5; border-color:#3b6ea5; color:white; font-weight:700; }
QPushButton#primary:hover { background:#4580c2; }
QPlainTextEdit#code { background:#14161b; color:#e8eaf0; border:1px solid #2c303a;
    border-radius:6px; selection-background-color:#33517a; }
QPlainTextEdit#output { background:#0f1310; color:#9fe3a1; border:1px solid #263a26;
    border-radius:6px; }
QPlainTextEdit#notes { background:#22252d; color:#dfe3ea; border:1px solid #3a3f4b;
    border-radius:6px; }
QFrame#note { background:rgba(72,140,220,0.10); border:1px solid #33517a; border-radius:6px; }
QFrame#warn { background:rgba(230,150,60,0.10); border:1px solid #7a5a33; border-radius:6px; }
QLabel#lessonTitle { font-size:22px; font-weight:700; color:#eaf0fa; }
QTableWidget { background:#20232a; border:1px solid #333; gridline-color:#333; border-radius:4px; }
QHeaderView::section { background:#2a2e37; color:#dfe3ea; border:none; padding:5px; }
QProgressBar { background:#262a33; border:none; border-radius:5px; }
QProgressBar::chunk { background:#3b6ea5; border-radius:5px; }
QScrollBar:vertical { background:#1b1d23; width:10px; }
QScrollBar::handle:vertical { background:#3a4050; border-radius:5px; min-height:30px; }
QScrollBar:horizontal { background:#1b1d23; height:10px; }
QScrollBar::handle:horizontal { background:#3a4050; border-radius:5px; min-width:30px; }
QMenu { background:#262a33; border:1px solid #3a3f4b; }
QMenu::item:selected { background:#33517a; }
"""
LIGHT_QSS = """
QMainWindow, QWidget { background:#f5f6f8; color:#24292f; font-size:13px; }
QTreeWidget { background:#ffffff; border:none; }
QTreeWidget::item { padding:5px; border-radius:4px; }
QTreeWidget::item:selected { background:#3b6ea5; color:white; }
QLineEdit, QComboBox, QSpinBox { background:#ffffff; border:1px solid #ccd1d9;
    border-radius:6px; padding:5px 8px; }
QPushButton { background:#e8ebf0; border:1px solid #ccd1d9; border-radius:6px;
    padding:6px 14px; color:#24292f; }
QPushButton:hover { background:#dde2e9; }
QPushButton:disabled { color:#999; }
QPushButton#primary { background:#3b6ea5; border-color:#3b6ea5; color:white; font-weight:700; }
QPlainTextEdit#code { background:#14161b; color:#e8eaf0; border:1px solid #2c303a; border-radius:6px; }
QPlainTextEdit#output { background:#0f1310; color:#9fe3a1; border:1px solid #263a26; border-radius:6px; }
QPlainTextEdit#notes { background:#ffffff; color:#24292f; border:1px solid #ccd1d9; border-radius:6px; }
QFrame#note { background:rgba(59,110,165,0.08); border:1px solid #9cc0e8; border-radius:6px; }
QFrame#warn { background:rgba(230,150,60,0.12); border:1px solid #e0b070; border-radius:6px; }
QLabel#lessonTitle { font-size:22px; font-weight:700; color:#1a2733; }
QTableWidget { background:#ffffff; border:1px solid #ccd1d9; gridline-color:#e5e8ec; }
QHeaderView::section { background:#eceff3; color:#24292f; border:none; padding:5px; }
QProgressBar { background:#e0e4ea; border:none; border-radius:5px; }
QProgressBar::chunk { background:#3b6ea5; border-radius:5px; }
QMenu { background:#ffffff; border:1px solid #ccd1d9; }
QMenu::item:selected { background:#3b6ea5; color:white; }
"""

def build_qss(theme, zoom=1.0):
    fs = max(9, int(13 * zoom))
    base = DARK_QSS if theme == "dark" else LIGHT_QSS
    return base.replace("font-size:13px", f"font-size:{fs}px")

MODULE_ICONS = ["🚀", "🧱", "🔀", "🔧", "📚", "🧠", "🏛️", "🧬", "🎒", "🛡️", "⚡",
                "🧮", "🧩", "🏗️", "✨", "🎯", "🛠️", "📦", "🌳", "⚙️", "🐞",
                "🔌", "🔬", "🧵", "🏎️", "🌐", "🔢", "📡", "💾", "🎛️", "🔮"]
SPECIAL_COUNT = 6  # dashboard, playground, quiz, flashcards, cheatsheet, glossary


# ============================================================================
#  MAIN WINDOW
# ============================================================================
class MainWindow(QMainWindow):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.pages = {}
        self.tree_map = {}
        self.flat = [(mi, li) for mi, m in enumerate(MODS)
                     for li in range(len(m["lessons"]))]
        self.current = None
        self.setWindowTitle(APP_TITLE)
        self.resize(1420, 920)
        self.statusBar().showMessage("Ready")

        today = datetime.date.today().isoformat()
        st = store.data.setdefault("streak", {"last": "", "count": 0})
        if st["last"] != today:
            y = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
            st["count"] = st["count"] + 1 if st["last"] == y else 1
            st["last"] = today; store.save()

        self.quiz_bank = [(m["title"], f'{m["title"]} › {les["title"]}', q)
                          for m in MODS for les in m["lessons"] for q in les["quiz"]]

        central = QWidget(); root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        top = QHBoxLayout(); top.setContentsMargins(10, 8, 10, 8)
        logo = QLabel("⚡ C++ Master")
        logo.setStyleSheet("font-size:16px;font-weight:800;color:#5aa2f0;")
        top.addWidget(logo)
        rnd = QPushButton("🎲"); rnd.setToolTip("Random lesson (Ctrl+R)")
        rnd.setFixedWidth(36); rnd.setCursor(Qt.PointingHandCursor)
        rnd.clicked.connect(self.random_lesson); top.addWidget(rnd)
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search lessons…  (topics, keywords, code)")
        self.search.setFixedWidth(340)
        self.search.textChanged.connect(self.filter_tree)
        top.addStretch(1); top.addWidget(self.search)
        self.progLabel = QLabel("")
        self.progLabel.setStyleSheet("color:#7d8590;padding-left:12px;")
        top.addWidget(self.progLabel)
        root.addLayout(top)

        split = QSplitter(Qt.Horizontal)
        self.tree = QTreeWidget(); self.tree.setHeaderLabel("Course")
        self.tree.itemClicked.connect(self.on_tree); split.addWidget(self.tree)
        self.stack = QStackedWidget(); split.addWidget(self.stack)
        split.setStretchFactor(0, 0); split.setStretchFactor(1, 1)
        split.setSizes([330, 1090]); root.addWidget(split, 1)
        self.setCentralWidget(central)

        self.build_pages(); self.build_tree(); self.build_menus(); self.build_shortcuts()
        self.update_counts()
        last = store.data.get("last")
        if last and "-" in last:
            try:
                mi, li = map(int, last.split("-"))
                if (mi, li) in self.flat:
                    self.load_lesson(mi, li)
            except ValueError:
                pass

    def build_pages(self):
        self.dashboard = Dashboard(self); self.stack.addWidget(self.dashboard)
        self.playground = Playground(self); self.stack.addWidget(self.playground)
        self.quizcenter = QuizCenter(self); self.stack.addWidget(self.quizcenter)
        self.flashcards = Flashcards(self); self.stack.addWidget(self.flashcards)
        self.cheatsheet = CheatSheet(); self.stack.addWidget(self.cheatsheet)
        self.glossary = Glossary(); self.stack.addWidget(self.glossary)
        self.special_index = {"dash": 0, "play": 1, "quiz": 2, "flash": 3,
                              "cheat": 4, "gloss": 5}
        self.stack.setCurrentIndex(0)

    def build_tree(self):
        specials = [("🏠  Dashboard", "dash"), ("🧪  Playground", "play"),
                    ("❓  Quiz Center", "quiz"), ("🗂  Flashcards", "flash"),
                    ("📋  Cheat Sheet", "cheat"), ("📖  Glossary", "gloss")]
        for label, key in specials:
            it = QTreeWidgetItem([label]); it.setData(0, Qt.UserRole, ("page", key))
            self.tree.addTopLevelItem(it)
        for mi, m in enumerate(MODS):
            mt = QTreeWidgetItem([f'{MODULE_ICONS[mi % len(MODULE_ICONS)]}  {m["title"]}'])
            mt.setToolTip(0, m.get("desc", "")); self.tree.addTopLevelItem(mt)
            for li, les in enumerate(m["lessons"]):
                k = f"{mi}-{li}"
                done = self.store.is_done(k)
                star = "⭐" if k in self.store.data.get("bookmarks", []) else ""
                it = QTreeWidgetItem(
                    [f'{"✅" if done else "▫"}{star} {li + 1}. {les["title"]}'])
                it.setData(0, Qt.UserRole, ("lesson", mi, li))
                mt.addChild(it); self.tree_map[(mi, li)] = it
        self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def build_menus(self):
        mb = self.menuBar()
        mnav = mb.addMenu("&Navigate")
        a = mnav.addAction("Previous lesson"); a.setShortcut("Ctrl+Left")
        a.triggered.connect(lambda: self.step_lesson(-1))
        a = mnav.addAction("Next lesson"); a.setShortcut("Ctrl+Right")
        a.triggered.connect(lambda: self.step_lesson(1))
        a = mnav.addAction("Random lesson"); a.setShortcut("Ctrl+R")
        a.triggered.connect(self.random_lesson)
        mnav.addSeparator()
        for label, key, sc in [("Dashboard", "dash", "Ctrl+D"),
                               ("Playground", "play", "Ctrl+P"),
                               ("Quiz Center", "quiz", "Ctrl+Q"),
                               ("Flashcards", "flash", "Ctrl+L"),
                               ("Cheat Sheet", "cheat", "Ctrl+E"),
                               ("Glossary", "gloss", "Ctrl+G")]:
            a = mnav.addAction(label); a.setShortcut(sc)
            a.triggered.connect(lambda _=False, k=key: self.show_special(k))

        mfile = mb.addMenu("&File")
        a = mfile.addAction("Export progress…")
        a.triggered.connect(self.export_progress)
        mfile.addSeparator()
        a = mfile.addAction("Reset progress…")
        a.triggered.connect(self.reset_progress)
        a = mfile.addAction("Exit"); a.triggered.connect(self.close)

        mview = mb.addMenu("&View")
        a = mview.addAction("Zoom in"); a.setShortcut("Ctrl++")
        a.triggered.connect(lambda: self.set_zoom(+0.1))
        a = mview.addAction("Zoom out"); a.setShortcut("Ctrl+-")
        a.triggered.connect(lambda: self.set_zoom(-0.1))
        a = mview.addAction("Reset zoom")
        a.triggered.connect(lambda: self.set_zoom(None))
        a = mview.addAction("Toggle light / dark theme")
        a.triggered.connect(self.toggle_theme)

        mhelp = mb.addMenu("&Help")
        a = mhelp.addAction("About")
        a.triggered.connect(lambda: QMessageBox.information(
            self, "About",
            f"{APP_TITLE}\n\n{TOTAL_LESSONS} lessons · {len(MODS)} modules · "
            f"C++98 → C++26\n{len(FLASHCARDS)} flashcards · {len(GLOSSARY)} glossary terms\n"
            "Shortcuts: Ctrl+←/→ lessons · Ctrl+R random · Ctrl+F search\n"
            "Ctrl+D dash · Ctrl+P play · Ctrl+Q quiz · Ctrl+L cards · Ctrl+E cheats"))

    def build_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+F"), self, self._focus_search)
        QShortcut(QKeySequence("Escape"), self.search, lambda: self.search.clear())

    def _focus_search(self):
        self.search.setFocus(); self.search.selectAll()

    # ---------- navigation ----------
    def on_tree(self, item, _col):
        data = item.data(0, Qt.UserRole)
        if not data:
            return
        if data[0] == "page":
            self.show_special(data[1])
        elif data[0] == "lesson":
            self.load_lesson(data[1], data[2])

    def show_special(self, key):
        self.stack.setCurrentIndex(self.special_index[key])
        self.current = None
        if key == "dash":
            self.dashboard.refresh()
        self.setWindowTitle(APP_TITLE)

    def load_lesson(self, mi, li):
        key = (mi, li)
        page = self.pages.get(key)
        if page is None:
            page = LessonPage(self, mi, li); self.pages[key] = page
            self.stack.addWidget(page)
        self.stack.setCurrentWidget(page)
        self.current = key
        self.store.data["last"] = f"{mi}-{li}"; self.store.save()
        item = self.tree_map.get(key)
        if item:
            self.tree.blockSignals(True)
            self.tree.setCurrentItem(item); self.tree.blockSignals(False)
            self.tree.scrollToItem(item)
        self.setWindowTitle(f'{MODS[mi]["lessons"][li]["title"]} — {APP_TITLE}')
        page.refresh_done()

    def step_lesson(self, d):
        if self.current is None:
            idx = 0
        else:
            idx = (self.flat.index(self.current) + d) % len(self.flat)
        self.load_lesson(*self.flat[idx])

    def random_lesson(self):
        self.load_lesson(*random.choice(self.flat))

    def load_first_incomplete(self):
        for mi, li in self.flat:
            if not self.store.is_done(f"{mi}-{li}"):
                return self.load_lesson(mi, li)
        if self.flat:
            self.load_lesson(*self.flat[0])

    # ---------- progress ----------
    def toggle_done_current(self):
        if not self.current:
            return
        mi, li = self.current
        key = f"{mi}-{li}"
        done = not self.store.is_done(key)
        self.store.set_done(key, done)
        item = self.tree_map[key]
        star = "⭐" if key in self.store.data.get("bookmarks", []) else ""
        item.setText(0, f'{"✅" if done else "▫"}{star} {li + 1}. '
                        f'{MODS[mi]["lessons"][li]["title"]}')
        self.pages[key].refresh_done()
        self.update_counts()

    def toggle_bookmark_current(self):
        if not self.current:
            return
        mi, li = self.current
        key = f"{mi}-{li}"
        bms = self.store.data.setdefault("bookmarks", [])
        marked = key in bms
        if marked:
            bms.remove(key)
        else:
            bms.append(key)
        self.store.save()
        item = self.tree_map[key]
        done = self.store.is_done(key)
        star = "" if marked else "⭐"
        item.setText(0, f'{"✅" if done else "▫"}{star} {li + 1}. '
                        f'{MODS[mi]["lessons"][li]["title"]}')
        self.pages[key].refresh_done()
        self.dashboard.refresh()

    def update_counts(self):
        done = len(self.store.data["completed"])
        pct = round(100 * done / TOTAL_LESSONS) if TOTAL_LESSONS else 0
        self.progLabel.setText(f"📈 {done}/{TOTAL_LESSONS} lessons ({pct}%)")
        for mi, m in enumerate(MODS):
            n = len(m["lessons"])
            d = sum(1 for li in range(n) if self.store.is_done(f"{mi}-{li}"))
            it = self.tree.topLevelItem(SPECIAL_COUNT + mi)
            if it:
                it.setText(0, f"{MODULE_ICONS[mi % len(MODULE_ICONS)]}  "
                              f"{m['title']}   [{d}/{n}]")
        self.dashboard.refresh()

    def reset_progress(self):
        if QMessageBox.question(self, "Reset progress",
                                "Erase all completed lessons, bookmarks, notes and "
                                "quiz scores?") == QMessageBox.Yes:
            self.store.data.update({"completed": [], "best": {}, "bookmarks": [],
                                    "notes": {}, "cards": {}, "quiz_history": [],
                                    "last": None})
            self.store.save()
            while self.stack.count() > SPECIAL_COUNT:
                w = self.stack.widget(SPECIAL_COUNT)
                self.stack.removeWidget(w); w.deleteLater()
            self.pages.clear()
            for (mi, li), item in self.tree_map.items():
                item.setText(0, f"▫ {li + 1}. {MODS[mi]['lessons'][li]['title']}")
            self.update_counts()

    def export_progress(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export progress",
                                              "cpp_master_progress.json", "JSON (*.json)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.store.data, f, indent=2)
            self.statusBar().showMessage("Progress exported ✓", 3000)

    # ---------- themes / zoom ----------
    def set_zoom(self, delta):
        z = (1.0 if delta is None
             else max(0.7, min(2.0, self.store.data.get("zoom", 1.0) + delta)))
        self.store.data["zoom"] = z; self.store.save()
        QApplication.instance().setStyleSheet(
            build_qss(self.store.data.get("theme", "dark"), z))

    def toggle_theme(self):
        theme = "light" if self.store.data.get("theme") == "dark" else "dark"
        self.store.data["theme"] = theme; self.store.save()
        QApplication.instance().setStyleSheet(
            build_qss(theme, self.store.data.get("zoom", 1.0)))

    # ---------- search ----------
    def _blob(self, mi, li):
        les = MODS[mi]["lessons"][li]
        parts = [les["title"]]
        for b in les["blocks"]:
            parts.append(str(b.get("x", "")))
        return " ".join(parts).lower()

    def filter_tree(self, text):
        q = text.strip().lower()
        for mi, m in enumerate(MODS):
            mt = self.tree.topLevelItem(SPECIAL_COUNT + mi)
            visible = 0
            for li, les in enumerate(m["lessons"]):
                it = self.tree_map[(mi, li)]
                match = (q in it.text(0).lower() or q in self._blob(mi, li))
                it.setHidden(bool(q) and not match)
                if not it.isHidden():
                    visible += 1
            mt.setHidden(bool(q) and visible == 0)
            if q:
                mt.setExpanded(visible > 0)
            else:
                mt.setExpanded(False)

    def refresh_dashboard(self):
        self.dashboard.refresh()

    def closeEvent(self, event):
        self.store.save(); event.accept()


# ============================================================================
#  APP ENTRY
# ============================================================================
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName(APP_TITLE)
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}
    app.setStyleSheet(build_qss(cfg.get("theme", "dark"), cfg.get("zoom", 1.0)))
    win = MainWindow(Store())
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()