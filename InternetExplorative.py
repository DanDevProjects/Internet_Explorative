import multiprocessing
import os
import platform
import shutil
import subprocess
import sys
import urllib.parse

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import (
    PYQT_VERSION_STR,
    QT_VERSION_STR,
    QCoreApplication,
    QPropertyAnimation,
    QSettings,
    QSize,
    Qt,
    QTimer,
    QUrl,
)
from PyQt6.QtGui import (
    QAction,
    QColor,
    QDesktopServices,
    QFont,
    QIcon,
    QPainter,
    QPen,
    QPixmap,
)
from PyQt6.QtWebEngineCore import (
    QWebEngineDownloadRequest,
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineSettings,
    QWebEngineUrlRequestInterceptor,
    qWebEngineChromiumVersion,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGraphicsOpacityEffect,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QStatusBar,
    QTabBar,
    QTabWidget,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

DEFAULT_HOME_URL = "https://start.me/p/ogowEx/start"
MODERN_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
IE_UA = "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
PROFILES_ROOT = os.path.join(os.path.expanduser("~"), ".ie_explorative_profiles")


def get_available_profiles():
    os.makedirs(PROFILES_ROOT, exist_ok=True)
    profiles = [
        d for d in os.listdir(PROFILES_ROOT)
        if os.path.isdir(os.path.join(PROFILES_ROOT, d))
    ]
    if not profiles:
        profiles = ["Default"]
    return profiles


def get_profile_display_name(profile_dir_name):
    """Retrieves the custom user display name for a given profile directory."""
    config_path = os.path.join(PROFILES_ROOT, profile_dir_name, "profile_config.ini")
    if os.path.exists(config_path):
        settings = QSettings(config_path, QSettings.Format.IniFormat)
        user_name = settings.value("user_name", "")
        if user_name and str(user_name).strip():
            return str(user_name).strip()
    return profile_dir_name


class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()
        self.enabled = True
        self.blocked_domains = [
            "doubleclick.net",
            "googlesyndication.com",
            "google-analytics.com",
            "adservice.google",
            "adnxs.com",
            "criteo.com",
            "scorecardresearch.com",
            "amazon-adsystem.com",
            "ads.yahoo.com",
        ]

    def interceptRequest(self, info):
        if not self.enabled:
            return
        url_str = info.requestUrl().toString().lower()
        for domain in self.blocked_domains:
            if domain in url_str:
                info.block(True)
                break


class SelectAllLineEdit(QLineEdit):
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.selectAll()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.selectAll()


class IEWebPage(QWebEnginePage):
    def __init__(self, view, browser_window, profile=None):
        if profile:
            super().__init__(profile, view)
        else:
            super().__init__(view)
        self.browser_window = browser_window
        self.custom_url = ""

    def get_accent_color(self):
        return getattr(self.browser_window, "accent_color", "#0078d7")

    def get_user_name(self):
        return getattr(self.browser_window, "user_name", "Explorer")

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        url_str = url.toString().lower().strip().rstrip("/")
        if "ie://info" in url_str or url_str == "ie:info":
            self.custom_url = "ie://info"
            QTimer.singleShot(0, self.load_info_html)
            return False
        elif "ie://snake" in url_str or url_str == "ie:snake":
            self.custom_url = "ie://snake"
            QTimer.singleShot(0, self.load_snake_html)
            return False

        if url.scheme() not in ["about", "javascript"]:
            self.custom_url = ""

        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

    def createWindow(self, window_type):
        return self.browser_window.add_new_tab(qurl=None, label="Loading...", return_page=True)

    def load_info_html(self):
        self.custom_url = "ie://info"
        if hasattr(self.browser_window, "url_bar"):
            self.browser_window.url_bar.setText("ie://info")
        chromium_ver = qWebEngineChromiumVersion()
        qt_ver = getattr(QtCore, "QT_VERSION_STR", "Unknown")
        py_ver = sys.version.split()[0]
        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        ua = self.profile().httpUserAgent() or MODERN_UA
        accent = self.get_accent_color()
        user = self.get_user_name()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Internet Explorative - Information</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f4f4; color: #222; padding: 30px; margin: 0; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                h1 {{ color: {accent}; border-bottom: 2px solid {accent}; padding-bottom: 10px; font-size: 24px; }}
                p {{ color: #555; font-size: 14px; }}
                .card {{ background: white; border: 1px solid #d0d0d0; padding: 20px; border-radius: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); margin-top: 20px; }}
                h3 {{ margin-top: 0; color: #333; font-size: 16px; border-bottom: 1px solid #eee; padding-bottom: 8px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 13px; }}
                th {{ background: {accent}; color: white; width: 35%; }}
                td {{ background: #fafafa; color: #333; }}
                code {{ background: #eee; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Internet Explorative</h1>
                <p>System specifications and runtime inspection page.</p>
                <div class="card">
                    <h3>System & Profile Specifications</h3>
                    <table>
                        <tr><th>Active Profile</th><td><b>{self.browser_window.current_profile_name}</b></td></tr>
                        <tr><th>Profile User</th><td>{user}</td></tr>
                        <tr><th>Application Name</th><td>Internet Explorative</td></tr>
                        <tr><th>Version</th><td>11.1.2</td></tr>
                        <tr><th>Developer</th><td>DanDevProjects</td></tr>
                        <tr><th>Rendering Engine</th><td>QtWebEngine / Chromium</td></tr>
                        <tr><th>Chromium Engine Version</th><td>{chromium_ver}</td></tr>
                        <tr><th>Python Runtime Version</th><td>{py_ver}</td></tr>
                        <tr><th>Qt Library Version</th><td>{qt_ver}</td></tr>
                        <tr><th>Operating System</th><td>{os_info}</td></tr>
                        <tr><th>Active HTTP User-Agent</th><td><code>{ua}</code></td></tr>
                    </table>
                </div>
            </div>
        </body>
        </html>
        """
        self.setHtml(html, QUrl("about:blank"))

    def load_snake_html(self):
        self.custom_url = "ie://snake"
        if hasattr(self.browser_window, "url_bar"):
            self.browser_window.url_bar.setText("ie://snake")
        accent = self.get_accent_color()
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Explorative snake - Internet Explorative</title>
            <style>
                body {{ background: #1e1e1e; color: #fff; font-family: 'Segoe UI', Arial, sans-serif; text-align: center; margin: 0; padding-top: 40px; }}
                h1 {{ color: {accent}; margin-bottom: 5px; }}
                p {{ color: #aaa; font-size: 14px; }}
                canvas {{ background: #111; border: 2px solid {accent}; box-shadow: 0 0 20px rgba(0,120,215,0.3); margin-top: 20px; }}
                .score {{ font-size: 20px; font-weight: bold; margin-top: 15px; color: #4ec9b0; }}
            </style>
        </head>
        <body>
            <h1>Explorative snake</h1>
            <p>Use Arrow Keys to play. Eat the red food to grow!</p>
            <div class="score">Score: <span id="score">0</span></div>
            <canvas id="gameCanvas" width="400" height="400"></canvas>
            <script>
                const canvas = document.getElementById("gameCanvas");
                const ctx = canvas.getContext("2d");
                const grid = 20;
                let count = 0;
                let score = 0;

                let snake = {{ x: 160, y: 160, dx: grid, dy: 0, cells: [], maxCells: 4 }};
                let apple = {{ x: 320, y: 320 }};

                function getRandomInt(min, max) {{ return Math.floor(Math.random() * (max - min)) + min; }}

                function loop() {{
                    requestAnimationFrame(loop);
                    if (++count < 6) {{ return; }}
                    count = 0;
                    ctx.clearRect(0,0,canvas.width,canvas.height);

                    snake.x += snake.dx; snake.y += snake.dy;

                    if (snake.x < 0) {{ snake.x = canvas.width - grid; }}
                    else if (snake.x >= canvas.width) {{ snake.x = 0; }}
                    if (snake.y < 0) {{ snake.y = canvas.height - grid; }}
                    else if (snake.y >= canvas.height) {{ snake.y = 0; }}

                    snake.cells.unshift({{x: snake.x, y: snake.y}});
                    if (snake.cells.length > snake.maxCells) {{ snake.cells.pop(); }}

                    ctx.fillStyle = 'red';
                    ctx.fillRect(apple.x, apple.y, grid-1, grid-1);

                    ctx.fillStyle = '{accent}';
                    snake.cells.forEach(function(cell, index) {{
                        ctx.fillRect(cell.x, cell.y, grid-1, grid-1);
                        if (cell.x === apple.x && cell.y === apple.y) {{
                            snake.maxCells++;
                            score += 10;
                            document.getElementById('score').innerText = score;
                            apple.x = getRandomInt(0, 20) * grid;
                            apple.y = getRandomInt(0, 20) * grid;
                        }}
                        for (let i = index + 1; i < snake.cells.length; i++) {{
                            if (cell.x === snake.cells[i].x && cell.y === snake.cells[i].y) {{
                                snake.x = 160; snake.y = 160;
                                snake.cells = []; snake.maxCells = 4;
                                snake.dx = grid; snake.dy = 0;
                                score = 0;
                                document.getElementById('score').innerText = score;
                                apple.x = getRandomInt(0, 20) * grid;
                                apple.y = getRandomInt(0, 20) * grid;
                            }}
                        }}
                    }});
                }}

                document.addEventListener('keydown', function(e) {{
                    if (e.which === 37 && snake.dx === 0) {{ snake.dx = -grid; snake.dy = 0; }}
                    else if (e.which === 38 && snake.dy === 0) {{ snake.dy = -grid; snake.dx = 0; }}
                    else if (e.which === 39 && snake.dx === 0) {{ snake.dx = grid; snake.dy = 0; }}
                    else if (e.which === 40 && snake.dy === 0) {{ snake.dy = grid; snake.dx = 0; }}
                }});

                requestAnimationFrame(loop);
            </script>
        </body>
        </html>
        """
        self.setHtml(html, QUrl("about:blank"))


def load_ie11_icon(size=64):
    icon_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "ie_icon.icns"
    )
    if os.path.exists(icon_path):
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            return QIcon(
                pixmap.scaled(
                    size,
                    size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
    fallback = QPixmap(size, size)
    fallback.fill(QColor("#0078d7"))
    return QIcon(fallback)


class CustomCloseButton(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.underMouse():
            painter.setBrush(QColor("#e81123"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(self.rect(), 2, 2)
            pen = QPen(QColor("#ffffff"), 1.2)
        else:
            pen = QPen(QColor("#666666"), 1.0)

        painter.setPen(pen)
        margin = 3
        w = self.width() - margin
        h = self.height() - margin
        painter.drawLine(margin, margin, w, h)
        painter.drawLine(w, margin, margin, h)


class CustomTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(False)
        self.setExpanding(True)
        self.setFixedHeight(32)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

    def tabInserted(self, index):
        super().tabInserted(index)
        btn = CustomCloseButton(self)
        btn.clicked.connect(lambda _, b=btn: self.handle_close_click(b))
        self.setTabButton(index, QTabBar.ButtonPosition.RightSide, btn)

    def handle_close_click(self, btn):
        for i in range(self.count()):
            if self.tabButton(i, QTabBar.ButtonPosition.RightSide) == btn:
                self.tabCloseRequested.emit(i)
                break

    def tabSizeHint(self, index):
        count = self.count()
        if count == 0:
            return super().tabSizeHint(index)
        available_width = self.width() if self.width() > 0 else 300
        calc_width = int(available_width / count)
        final_width = max(60, min(140, calc_width))
        return QSize(final_width, 32)


class ProfileSwitchOverlay(QWidget):
    """Smooth visual animation card when switching profiles."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.hide()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.card = QWidget()
        self.card.setObjectName("switchCard")
        self.card.setFixedSize(320, 180)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 25, 30, 25)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel("👤")
        self.icon_label.setStyleSheet("font-size: 42px;")
        
        self.title_label = QLabel("Switching Profile...")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; font-family: 'Segoe UI', Arial;")

        self.sub_label = QLabel("Loading settings & workspace")
        self.sub_label.setStyleSheet("font-size: 12px; color: #888888; font-family: 'Segoe UI', Arial;")

        card_layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.sub_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.card)

        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(250)

    def start_switch(self, profile_name, accent_color, is_dark, on_middle_callback):
        self.resize(self.parent().size())
        self.raise_()

        bg = "#1e1e1e" if is_dark else "#f0f0f0"
        card_bg = "#2b2b2b" if is_dark else "#ffffff"
        fg = "#ffffff" if is_dark else "#222222"

        self.setStyleSheet(f"""
            ProfileSwitchOverlay {{ background-color: {bg}; }}
            #switchCard {{
                background-color: {card_bg};
                border: 2px solid {accent_color};
                border-radius: 10px;
            }}
            QLabel {{ color: {fg}; }}
        """)

        display_name = get_profile_display_name(profile_name)
        self.title_label.setText(f"Switching to {display_name}")
        self.opacity_effect.setOpacity(0.0)
        self.show()

        try:
            self.anim.finished.disconnect()
        except TypeError:
            pass

        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)

        def on_fade_in():
            on_middle_callback()
            QTimer.singleShot(200, start_fade_out)

        def start_fade_out():
            try:
                self.anim.finished.disconnect()
            except TypeError:
                pass
            self.anim.setStartValue(1.0)
            self.anim.setEndValue(0.0)
            self.anim.finished.connect(self.hide)
            self.anim.start()

        self.anim.finished.connect(on_fade_in)
        self.anim.start()


class ProfileManagerDialog(QDialog):
    """Dialog inside Tools menu to manage, add, or delete browser profiles."""
    def __init__(self, current_profile, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Profiles")
        self.resize(440, 280)
        self.active_profile = current_profile
        self.selected_profile = current_profile

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        layout.addWidget(QLabel("<b>Select Profile:</b>"))

        self.list_widget = QListWidget()
        self.profiles = get_available_profiles()
        for p in self.profiles:
            display_name = get_profile_display_name(p)
            entry_text = f"{display_name} [{p}]" if display_name != p else p
            item = QListWidgetItem(entry_text)
            self.list_widget.addItem(item)
            if p == current_profile:
                self.list_widget.setCurrentItem(item)

        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        switch_btn = QPushButton("Switch Profile")
        switch_btn.clicked.connect(self.switch_profile)

        new_btn = QPushButton("+ New Profile")
        new_btn.clicked.connect(self.create_profile)

        delete_btn = QPushButton("Delete Profile")
        delete_btn.clicked.connect(self.delete_profile)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)

        btn_layout.addWidget(switch_btn)
        btn_layout.addWidget(new_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def switch_profile(self):
        row = self.list_widget.currentRow()
        if 0 <= row < len(self.profiles):
            self.selected_profile = self.profiles[row]
            self.accept()

    def create_profile(self):
        name, ok = QInputDialog.getText(self, "New Profile", "Enter new profile name:")
        if ok and name.strip():
            clean_name = name.strip()
            p_dir = os.path.join(PROFILES_ROOT, clean_name)
            os.makedirs(p_dir, exist_ok=True)
            self.selected_profile = clean_name
            self.accept()

    def delete_profile(self):
        row = self.list_widget.currentRow()
        if not (0 <= row < len(self.profiles)):
            QMessageBox.warning(self, "Selection Required", "Please select a profile to delete.")
            return

        target_profile = self.profiles[row]

        if target_profile == self.active_profile:
            QMessageBox.warning(
                self,
                "Cannot Delete Active Profile",
                "You cannot delete the currently active profile. Please switch to another profile first.",
            )
            return

        if len(self.profiles) <= 1:
            QMessageBox.warning(
                self,
                "Cannot Delete Profile",
                "At least one profile must remain.",
            )
            return

        display_name = get_profile_display_name(target_profile)
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to permanently delete profile '{display_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            p_dir = os.path.join(PROFILES_ROOT, target_profile)
            if os.path.exists(p_dir):
                shutil.rmtree(p_dir, ignore_errors=True)

            if self.parent() and hasattr(self.parent(), "profiles_cache"):
                self.parent().profiles_cache.pop(target_profile, None)

            self.profiles.pop(row)
            self.list_widget.takeItem(row)

            if self.parent() and hasattr(self.parent(), "rebuild_profile_menus"):
                self.parent().rebuild_profile_menus()

            QMessageBox.information(
                self,
                "Profile Deleted",
                f"Profile '{display_name}' has been deleted.",
            )


class ShareDialog(QDialog):
    def __init__(self, page_title, page_url, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Share Web Page")
        self.setFixedSize(450, 300)

        bg = "#2b2b2b" if is_dark_mode else "#ffffff"
        fg = "#ffffff" if is_dark_mode else "#222222"
        btn_bg = "#3a3a3a" if is_dark_mode else "#f0f0f0"
        border_col = "#555" if is_dark_mode else "#ccc"

        self.setStyleSheet(f"""
            QDialog {{ background-color: {bg}; font-family: 'Segoe UI', Arial; color: {fg}; }}
            QLabel {{ color: {fg}; }}
            QPushButton {{
                background-color: {btn_bg};
                border: 1px solid {border_col};
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
                text-align: left;
                color: {fg};
            }}
            QPushButton:hover {{
                background-color: #0078d7;
                color: white;
                border-color: #0078d7;
            }}
        """)

        self.page_title = page_title or "Untitled Page"
        self.page_url = page_url

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel(f"<b>Sharing:</b> {self.page_title}")
        header.setWordWrap(True)
        url_sub = QLabel(f"<span style='color: #888;'>{self.page_url}</span>")
        url_sub.setWordWrap(True)
        layout.addWidget(header)
        layout.addWidget(url_sub)

        layout.addSpacing(10)

        btn_copy_url = QPushButton("📋  Copy Link URL")
        btn_copy_url.clicked.connect(self.copy_url)
        layout.addWidget(btn_copy_url)

        btn_copy_formatted = QPushButton("📝  Copy Title and Link")
        btn_copy_formatted.clicked.connect(self.copy_formatted)
        layout.addWidget(btn_copy_formatted)

        btn_external = QPushButton("🌐  Open in Default External Browser")
        btn_external.clicked.connect(self.open_external)
        layout.addWidget(btn_external)

        btn_email = QPushButton("✉️  Send via Email")
        btn_email.clicked.connect(self.send_email)
        layout.addWidget(btn_email)

        layout.addStretch()

    def copy_url(self):
        QApplication.clipboard().setText(self.page_url)
        QMessageBox.information(self, "Share", "URL copied to clipboard!")
        self.accept()

    def copy_formatted(self):
        text = f"{self.page_title} - {self.page_url}"
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Share", "Formatted link copied to clipboard!")
        self.accept()

    def open_external(self):
        QDesktopServices.openUrl(QUrl(self.page_url))
        self.accept()

    def send_email(self):
        subject = urllib.parse.quote(f"Check out this page: {self.page_title}")
        body = urllib.parse.quote(f"I wanted to share this page with you:\n\n{self.page_url}")
        mailto_url = QUrl(f"mailto:?subject={subject}&body={body}")
        QDesktopServices.openUrl(mailto_url)
        self.accept()


class DownloadsDialog(QDialog):
    def __init__(self, downloads, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads Manager")
        self.resize(500, 320)
        self.downloads = downloads

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(QLabel("<b>Recent Downloads:</b>"))

        self.list_widget = QListWidget()
        for item in self.downloads:
            self.list_widget.addItem(f"{item['name']}  —  ({item['path']})")
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        open_btn = QPushButton("Open File")
        open_btn.clicked.connect(self.open_file)
        show_btn = QPushButton("Show in Folder")
        show_btn.clicked.connect(self.show_in_folder)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(open_btn)
        btn_layout.addWidget(show_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def get_selected_item(self):
        row = self.list_widget.currentRow()
        if 0 <= row < len(self.downloads):
            return self.downloads[row]
        return None

    def open_file(self):
        item = self.get_selected_item()
        if item and os.path.exists(item["path"]):
            QDesktopServices.openUrl(QUrl.fromLocalFile(item["path"]))
        else:
            QMessageBox.warning(self, "Error", "File does not exist or no selection made.")

    def show_in_folder(self):
        item = self.get_selected_item()
        if item and os.path.exists(item["path"]):
            path = item["path"]
            if sys.platform == "darwin":
                subprocess.run(["open", "-R", path])
            elif sys.platform == "win32":
                subprocess.run(["explorer", "/select,", os.path.normpath(path)])
            else:
                subprocess.run(["xdg-open", os.path.dirname(path)])
        else:
            QMessageBox.warning(self, "Error", "File does not exist or no selection made.")


class ManageFavoritesDialog(QDialog):
    def __init__(self, bookmarks, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Favorite")
        self.resize(460, 340)
        self.bookmarks = list(bookmarks)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.addWidget(QLabel("Select a favorite to delete:"))

        self.list_widget = QListWidget()
        for bm in self.bookmarks:
            self.list_widget.addItem(f"{bm['title']} — {bm['url']}")
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_selected)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.deleted = False

    def delete_selected(self):
        row = self.list_widget.currentRow()
        if 0 <= row < len(self.bookmarks):
            del self.bookmarks[row]
            self.list_widget.takeItem(row)
            self.deleted = True
        else:
            QMessageBox.warning(self, "Selection", "Please select a favorite to delete first.")

    def get_bookmarks(self):
        return self.bookmarks


class InternetOptionsDialog(QDialog):
    def __init__(
        self, current_home, current_engine, theme_mode, is_ie_ua, is_adblock, is_warn_close, history_list, is_dark_mode, active_web_profile, current_accent="#0078d7", current_user="Explorer", parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle("Internet Options & Settings")
        self.resize(760, 560)
        self.setMinimumSize(720, 500)

        self.selected_accent = current_accent
        self.web_profile = active_web_profile

        bg = "#2b2b2b" if is_dark_mode else "#f4f4f4"
        fg = "#ffffff" if is_dark_mode else "#222222"
        input_bg = "#3a3a3a" if is_dark_mode else "#ffffff"
        border_col = "#555555" if is_dark_mode else "#a0a0a0"
        tab_bg = "#333333" if is_dark_mode else "#e1e1e1"
        tab_sel = "#3f3f3f" if is_dark_mode else "#ffffff"

        self.setStyleSheet(f"""
            QDialog {{ background-color: {bg}; font-family: 'Segoe UI', Arial; color: {fg}; }}
            QLabel {{ font-size: 12px; color: {fg}; }}
            QLineEdit {{ background: {input_bg}; border: 1px solid {border_col}; padding: 6px; border-radius: 2px; color: {fg}; }}
            QComboBox {{ 
                background: {input_bg}; 
                border: 1px solid {border_col}; 
                padding: 6px 10px; 
                border-radius: 2px; 
                color: {fg};
                min-width: 180px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {input_bg};
                color: {fg};
                selection-background-color: {self.selected_accent};
                selection-color: #ffffff;
                border: 1px solid {border_col};
                padding: 4px;
            }}
            QPushButton {{ background: {'#3a3a3a' if is_dark_mode else '#e1e1e1'}; border: 1px solid {border_col}; padding: 6px 16px; border-radius: 2px; color: {fg}; }}
            QPushButton:hover {{ background: {self.selected_accent}; color: white; border-color: {self.selected_accent}; }}
            QGroupBox {{ font-weight: bold; font-size: 12px; border: 1px solid {border_col}; margin-top: 10px; padding-top: 12px; color: {fg}; }}
            QCheckBox {{ color: {fg}; spacing: 8px; }}
            QTabWidget::pane {{ border: 1px solid {border_col}; background: {bg}; border-radius: 2px; }}
            QTabBar::tab {{ background: {tab_bg}; padding: 8px 24px; margin-right: 6px; border-top-left-radius: 3px; border-top-right-radius: 3px; color: {fg}; min-width: 120px; font-weight: 500; }}
            QTabBar::tab:selected {{ background: {tab_sel}; font-weight: bold; border-bottom: 2px solid {self.selected_accent}; color: {fg}; }}
            QListWidget {{ background: {input_bg}; color: {fg}; border: 1px solid {border_col}; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setElideMode(Qt.TextElideMode.ElideNone)
        layout.addWidget(self.tabs)

        # Tab 1: General & Profile Personalization
        gen_widget = QWidget()
        gen_layout = QFormLayout(gen_widget)
        gen_layout.setContentsMargins(20, 20, 20, 20)
        gen_layout.setVerticalSpacing(16)
        gen_layout.setHorizontalSpacing(16)

        self.user_name_input = QLineEdit(current_user)
        self.user_name_input.setPlaceholderText("Enter your profile user name")
        gen_layout.addRow("User Profile Name:", self.user_name_input)

        self.home_input = QLineEdit(current_home)
        self.home_input.setPlaceholderText(DEFAULT_HOME_URL)
        gen_layout.addRow("Home Page:", self.home_input)

        self.search_engine = QComboBox()
        self.search_engine.addItems([
            "DuckDuckGo", "Bing", "Google", "Yahoo", "Ecosia", "Qwant", "Baidu", "Startpage"
        ])
        if current_engine in [self.search_engine.itemText(i) for i in range(self.search_engine.count())]:
            self.search_engine.setCurrentText(current_engine)
        else:
            self.search_engine.setCurrentText("DuckDuckGo")
        gen_layout.addRow("Default Search:", self.search_engine)
        self.tabs.addTab(gen_widget, "General")

        # Tab 2: Appearance & Personalization
        app_widget = QWidget()
        app_layout = QFormLayout(app_widget)
        app_layout.setContentsMargins(20, 20, 20, 20)
        app_layout.setVerticalSpacing(16)
        app_layout.setHorizontalSpacing(16)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(theme_mode if theme_mode in ["Light", "Dark"] else "Light")
        app_layout.addRow("Theme Mode:", self.theme_combo)

        self.accent_btn = QPushButton("Pick Custom Accent Color")
        self.update_accent_btn_style()
        self.accent_btn.clicked.connect(self.choose_accent_color)
        app_layout.addRow("Accent Color:", self.accent_btn)

        self.ie_ua_cb = QCheckBox("Emulate Internet Explorer 11 User-Agent")
        self.ie_ua_cb.setChecked(is_ie_ua)
        app_layout.addRow("", self.ie_ua_cb)

        self.adblock_cb = QCheckBox("Enable Built-in Adblocker (On by default)")
        self.adblock_cb.setChecked(is_adblock)
        app_layout.addRow("", self.adblock_cb)

        self.warn_close_cb = QCheckBox("Show confirmation warning when closing browser")
        self.warn_close_cb.setChecked(is_warn_close)
        app_layout.addRow("", self.warn_close_cb)

        priv_box = QGroupBox("Profile Temporary Files & Cookies")
        priv_layout = QHBoxLayout(priv_box)
        priv_layout.setContentsMargins(12, 12, 12, 12)
        priv_layout.setSpacing(10)

        clear_cache_btn = QPushButton("Clear Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        priv_layout.addWidget(clear_cache_btn)

        clear_cookies_btn = QPushButton("Clear Cookies")
        clear_cookies_btn.clicked.connect(self.clear_cookies)
        priv_layout.addWidget(clear_cookies_btn)
        app_layout.addRow(priv_box)
        self.tabs.addTab(app_widget, "Appearance")

        # Tab 3: History
        hist_widget = QWidget()
        hist_layout = QVBoxLayout(hist_widget)
        hist_layout.setContentsMargins(20, 20, 20, 20)
        hist_layout.setSpacing(12)
        hist_layout.addWidget(QLabel("<b>Browsing History:</b>"))

        self.history_list = list(history_list)
        self.hist_list_widget = QListWidget()
        for h in self.history_list:
            self.hist_list_widget.addItem(h)
        hist_layout.addWidget(self.hist_list_widget)

        hist_btn_layout = QHBoxLayout()
        del_hist_btn = QPushButton("Delete Selected")
        del_hist_btn.clicked.connect(self.delete_selected_history)
        clear_hist_btn = QPushButton("Clear All History")
        clear_hist_btn.clicked.connect(self.clear_all_history)
        hist_btn_layout.addWidget(del_hist_btn)
        hist_btn_layout.addWidget(clear_hist_btn)
        hist_layout.addLayout(hist_btn_layout)
        self.tabs.addTab(hist_widget, "History")

        self.history_modified = False

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def choose_accent_color(self):
        color = QColorDialog.getColor(QColor(self.selected_accent), self, "Select Accent Color")
        if color.isValid():
            self.selected_accent = color.name()
            self.update_accent_btn_style()

    def update_accent_btn_style(self):
        self.accent_btn.setStyleSheet(
            f"background-color: {self.selected_accent}; color: white; font-weight: bold; border-radius: 3px;"
        )

    def delete_selected_history(self):
        row = self.hist_list_widget.currentRow()
        if 0 <= row < len(self.history_list):
            self.history_list.pop(row)
            self.hist_list_widget.takeItem(row)
            self.history_modified = True
        else:
            QMessageBox.warning(self, "Selection", "Please select a history entry to delete.")

    def clear_all_history(self):
        self.history_list.clear()
        self.hist_list_widget.clear()
        self.history_modified = True

    def clear_cache(self):
        if self.web_profile:
            self.web_profile.clearHttpCache()
            QMessageBox.information(self, "Cache Cleared", "Temporary cache for this profile cleared.")

    def clear_cookies(self):
        if self.web_profile:
            self.web_profile.cookieStore().deleteAllCookies()
            QMessageBox.information(self, "Cookies Cleared", "All cookies for this profile cleared.")

    def get_settings(self):
        home_text = self.home_input.text().strip()
        user_name = self.user_name_input.text().strip()
        return {
            "home": home_text if home_text else DEFAULT_HOME_URL,
            "user_name": user_name if user_name else "Explorer",
            "engine": self.search_engine.currentText(),
            "theme_mode": self.theme_combo.currentText(),
            "accent_color": self.selected_accent,
            "ie_ua": self.ie_ua_cb.isChecked(),
            "adblock": self.adblock_cb.isChecked(),
            "warn_close": self.warn_close_cb.isChecked(),
            "history": self.history_list if self.history_modified else None,
        }


class AboutIEDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Internet Explorative")
        self.setFixedSize(440, 220)
        self.setWindowIcon(load_ie11_icon(32))
        self.setStyleSheet("""
            QDialog { background-color: #ffffff; font-family: 'Segoe UI', Arial; }
            QLabel { color: #333333; font-size: 12px; }
            QPushButton { background-color: #e1e1e1; border: 1px solid #adadad; padding: 6px 20px; border-radius: 2px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        top_layout = QHBoxLayout()

        logo_label = QLabel()
        logo_label.setPixmap(load_ie11_icon(64).pixmap(64, 64))
        top_layout.addWidget(logo_label)

        info_layout = QVBoxLayout()
        title_label = QLabel(
            "<span style='font-size: 20px; color:"
            " #0076d6;'><b>Internet</b> Explorative</span>"
        )
        ver_label = QLabel(
            "Internet Explorative version: 11.1.2<br><b>Engine:</b>"
            " PyQt6 (Chromium 140)"
        )
        info_layout.addWidget(title_label)
        info_layout.addWidget(ver_label)
        top_layout.addLayout(info_layout)

        layout.addLayout(top_layout)
        layout.addWidget(
            QLabel(
                "© 2026 DanDevProjects. All rights reserved.<br><i>Tip: Type"
                " <b>ie://info</b> in address bar for system info.</i>"
            )
        )

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box, alignment=Qt.AlignmentFlag.AlignRight)


class IE11Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Internet Explorative")
        self.setWindowIcon(load_ie11_icon(32))
        self.resize(1240, 820)

        self.adblock_interceptor = AdBlockInterceptor()
        self.current_profile_name = "Default"
        self.web_profile = None
        self.settings = None
        self.profiles_cache = {}  # Cache active QWebEngineProfiles to prevent crash / release warnings

        self.init_ui()
        self.load_profile("Default", is_initial=True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "switch_overlay") and self.switch_overlay.isVisible():
            self.switch_overlay.resize(self.size())

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(6, 6, 6, 6)
        header_layout.setSpacing(4)

        self.back_btn = QPushButton("←")
        self.back_btn.setObjectName("backBtn")
        self.back_btn.setFixedSize(42, 42)
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.navigate_back)
        header_layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.forward_btn = QToolButton()
        self.forward_btn.setProperty("class", "navBtn")
        self.forward_btn.setText("→")
        self.forward_btn.setFixedSize(32, 32)
        self.forward_btn.clicked.connect(self.navigate_forward)
        header_layout.addWidget(self.forward_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.reload_btn = QToolButton()
        self.reload_btn.setObjectName("reloadBtn")
        self.reload_btn.setText("⟳")
        self.reload_btn.setFixedSize(32, 32)
        self.reload_btn.setToolTip("Reload Page")
        self.reload_btn.clicked.connect(self.navigate_reload)
        header_layout.addWidget(self.reload_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.url_bar = SelectAllLineEdit()
        self.url_bar.setObjectName("urlBar")
        self.url_bar.setFixedHeight(32)
        self.url_bar.setPlaceholderText("Search, enter web address, or ie://info")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        header_layout.addWidget(self.url_bar, stretch=3, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.tab_bar = CustomTabBar()
        self.tab_bar.setMovable(True)
        self.tab_bar.setSelectionBehaviorOnRemove(QTabBar.SelectionBehavior.SelectPreviousTab)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.currentChanged.connect(self.current_tab_changed)
        header_layout.addWidget(self.tab_bar, stretch=2, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.add_tab_btn = QToolButton()
        self.add_tab_btn.setProperty("class", "navBtn")
        self.add_tab_btn.setText("+")
        self.add_tab_btn.setToolTip("Open New Tab")
        self.add_tab_btn.setFixedSize(32, 32)
        self.add_tab_btn.clicked.connect(lambda: self.add_new_tab(QUrl(self.home_url), "New Tab"))
        header_layout.addWidget(self.add_tab_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.home_btn = QToolButton()
        self.home_btn.setProperty("class", "navBtn")
        self.home_btn.setText("🏠")
        self.home_btn.setFixedSize(32, 32)
        self.home_btn.clicked.connect(self.navigate_home)
        header_layout.addWidget(self.home_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.fav_btn = QToolButton()
        self.fav_btn.setProperty("class", "navBtn")
        self.fav_btn.setText("★")
        self.fav_btn.setToolTip("Add to Favorites")
        self.fav_btn.setFixedSize(32, 32)
        self.fav_btn.clicked.connect(self.add_bookmark)
        header_layout.addWidget(self.fav_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Actions for Tools Dropdown & Menubar
        downloads_act = QAction("View Downloads", self)
        downloads_act.triggered.connect(self.show_downloads)

        share_act = QAction("Share Page...", self)
        share_act.triggered.connect(self.share_current_page)

        options_act = QAction("Internet Options", self)
        options_act.triggered.connect(self.show_internet_options)

        delete_fav_act = QAction("Delete Favorite...", self)
        delete_fav_act.triggered.connect(self.delete_single_favorite)

        about_act = QAction("About Internet Explorative", self)
        about_act.triggered.connect(self.show_about_dialog)

        # Gear / Tools Button with Menu
        self.tools_btn = QToolButton()
        self.tools_btn.setProperty("class", "navBtn")
        self.tools_btn.setObjectName("toolsBtn")
        self.tools_btn.setText("⚙")
        self.tools_btn.setToolTip("Tools & Settings")
        self.tools_btn.setFixedSize(32, 32)
        self.tools_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.tools_dropdown = QMenu(self)
        
        # Switch Profile Submenu inside Tools
        self.profile_menu = QMenu("Switch Profile", self)
        self.tools_dropdown.addMenu(self.profile_menu)
        self.tools_dropdown.addSeparator()

        self.tools_dropdown.addAction(share_act)
        self.tools_dropdown.addAction(downloads_act)
        self.tools_dropdown.addSeparator()
        self.tools_dropdown.addAction(options_act)
        self.tools_dropdown.addAction(delete_fav_act)
        self.tools_dropdown.addSeparator()
        self.tools_dropdown.addAction(about_act)
        self.tools_btn.setMenu(self.tools_dropdown)
        header_layout.addWidget(self.tools_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.main_layout.addLayout(header_layout)

        self.bookmarks_bar = QToolBar("Bookmarks Bar")
        self.bookmarks_bar.setObjectName("bookmarksBar")
        self.bookmarks_bar.setMovable(False)
        self.main_layout.addWidget(self.bookmarks_bar)

        self.web_stack = QStackedWidget()
        self.main_layout.addWidget(self.web_stack)

        # Profile switch animation overlay
        self.switch_overlay = ProfileSwitchOverlay(self)

        # Menu Bar setup
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        new_tab_act = QAction("New Tab", self)
        new_tab_act.setShortcut("Ctrl+T")
        new_tab_act.triggered.connect(lambda: self.add_new_tab(QUrl(self.home_url), "New Tab"))
        file_menu.addAction(new_tab_act)

        open_file_act = QAction("Open File...", self)
        open_file_act.setShortcut("Ctrl+O")
        open_file_act.triggered.connect(self.open_local_file)
        file_menu.addAction(open_file_act)
        file_menu.addSeparator()
        file_menu.addAction(share_act)
        file_menu.addSeparator()

        exit_act = QAction("Exit", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        edit_menu = menubar.addMenu("Edit")
        cut_act = QAction("Cut", self)
        cut_act.setShortcut("Ctrl+X")
        cut_act.triggered.connect(lambda: self.focusWidget().cut() if hasattr(self.focusWidget(), "cut") else None)
        copy_act = QAction("Copy", self)
        copy_act.setShortcut("Ctrl+C")
        copy_act.triggered.connect(lambda: self.focusWidget().copy() if hasattr(self.focusWidget(), "copy") else None)
        paste_act = QAction("Paste", self)
        paste_act.setShortcut("Ctrl+V")
        paste_act.triggered.connect(lambda: self.focusWidget().paste() if hasattr(self.focusWidget(), "paste") else None)
        edit_menu.addActions([cut_act, copy_act, paste_act])

        view_menu = menubar.addMenu("View")
        zoom_in_act = QAction("Zoom In", self)
        zoom_in_act.setShortcut("Ctrl++")
        zoom_in_act.triggered.connect(self.zoom_in)
        zoom_out_act = QAction("Zoom Out", self)
        zoom_out_act.setShortcut("Ctrl+-")
        zoom_out_act.triggered.connect(self.zoom_out)
        view_menu.addActions([zoom_in_act, zoom_out_act])

        self.fav_menu_obj = menubar.addMenu("Favorites")
        add_fav_act = QAction("Add to Favorites", self)
        add_fav_act.setShortcut("Ctrl+D")
        add_fav_act.triggered.connect(self.add_bookmark)
        self.fav_menu_obj.addAction(add_fav_act)
        self.fav_menu_obj.addSeparator()

        tools_menu = menubar.addMenu("Tools")
        self.menubar_profile_menu = QMenu("Profiles", self)
        tools_menu.addMenu(self.menubar_profile_menu)
        tools_menu.addSeparator()
        tools_menu.addAction(share_act)
        tools_menu.addAction(downloads_act)
        tools_menu.addSeparator()
        tools_menu.addAction(options_act)
        tools_menu.addAction(delete_fav_act)

        help_menu = menubar.addMenu("Help")
        info_act = QAction("System Information (ie://info)", self)
        info_act.triggered.connect(lambda: self.add_new_tab(QUrl("ie://info"), "Info"))
        help_menu.addAction(info_act)
        help_menu.addSeparator()
        help_menu.addAction(about_act)

        self.setStatusBar(QStatusBar(self))

    def load_profile(self, profile_name: str, is_initial=False):
        """Loads and switches to an isolated profile."""
        def apply_profile_changes():
            # Safely clear open tabs and detach pages before changing active profile
            if not is_initial:
                while self.web_stack.count() > 0:
                    widget = self.web_stack.widget(0)
                    self.web_stack.removeWidget(widget)
                    if isinstance(widget, QWebEngineView):
                        widget.stop()
                        page = widget.page()
                        widget.setPage(None)
                        if page:
                            page.deleteLater()
                        widget.deleteLater()
                while self.tab_bar.count() > 0:
                    self.tab_bar.removeTab(0)
                QCoreApplication.processEvents()

            self.current_profile_name = profile_name
            profile_dir = os.path.join(PROFILES_ROOT, profile_name)
            os.makedirs(profile_dir, exist_ok=True)

            config_path = os.path.join(profile_dir, "profile_config.ini")
            self.settings = QSettings(config_path, QSettings.Format.IniFormat)

            # Retrieve or initialize persistent QWebEngineProfile
            if profile_name not in self.profiles_cache:
                p = QWebEngineProfile(f"ie_profile_{profile_name}", self)
                p.setPersistentStoragePath(os.path.join(profile_dir, "web_storage"))
                p.setCachePath(os.path.join(profile_dir, "web_cache"))
                p.downloadRequested.connect(self.handle_download)
                self.profiles_cache[profile_name] = p

            self.web_profile = self.profiles_cache[profile_name]

            saved_home = self.settings.value("home_page", DEFAULT_HOME_URL)
            self.home_url = str(saved_home) if saved_home else DEFAULT_HOME_URL

            self.user_name = str(self.settings.value("user_name", profile_name))
            self.accent_color = str(self.settings.value("accent_color", "#0078d7"))
            self.search_engine = str(self.settings.value("search_engine", "DuckDuckGo"))

            saved_theme = self.settings.value("theme_mode", "Light")
            self.theme_mode = saved_theme if saved_theme in ["Dark", "Light"] else "Light"
            self.is_dark_mode = self.resolve_dark_mode()

            self.is_ie_ua = self.settings.value("ie_ua", False, type=bool)
            self.is_adblock = self.settings.value("adblock", True, type=bool)
            self.warn_on_close = self.settings.value("warn_on_close", True, type=bool)
            self.downloads_history = self.settings.value("downloads_history", [])
            if not isinstance(self.downloads_history, list):
                self.downloads_history = []

            self.adblock_interceptor.enabled = self.is_adblock
            self.web_profile.setUrlRequestInterceptor(self.adblock_interceptor)

            web_settings = self.web_profile.settings()
            web_settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            web_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

            if self.is_ie_ua:
                self.web_profile.setHttpUserAgent(IE_UA)
            else:
                self.web_profile.setHttpUserAgent(MODERN_UA)

            self.apply_theme()
            self.load_bookmarks()
            self.rebuild_profile_menus()

            self.add_new_tab(QUrl(self.home_url), "New Tab")
            if not is_initial:
                display_name = get_profile_display_name(profile_name)
                self.statusBar().showMessage(f"Switched to profile: {display_name}", 4000)

        if is_initial:
            apply_profile_changes()
        else:
            self.switch_overlay.start_switch(
                profile_name,
                getattr(self, "accent_color", "#0078d7"),
                getattr(self, "is_dark_mode", False),
                apply_profile_changes
            )

    def rebuild_profile_menus(self):
        """Populates the Profiles submenus inside the Tools menu & Menubar with user display names."""
        for menu in [self.profile_menu, self.menubar_profile_menu]:
            menu.clear()
            profiles = get_available_profiles()
            for p in profiles:
                display_name = get_profile_display_name(p)
                label_str = display_name if display_name == p else f"{display_name} ({p})"
                
                label = f"✓ {label_str}" if p == self.current_profile_name else f"   {label_str}"
                act = QAction(label, self)
                act.triggered.connect(lambda checked, name=p: self.switch_profile_to(name))
                menu.addAction(act)

            menu.addSeparator()
            manage_act = QAction("Manage Profiles...", self)
            manage_act.triggered.connect(self.open_profile_manager)
            menu.addAction(manage_act)

    def switch_profile_to(self, profile_name: str):
        if profile_name != self.current_profile_name:
            self.load_profile(profile_name)

    def open_profile_manager(self):
        dialog = ProfileManagerDialog(self.current_profile_name, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.selected_profile:
                self.switch_profile_to(dialog.selected_profile)

    def cleanup_all_pages(self):
        while self.web_stack.count() > 0:
            widget = self.web_stack.widget(0)
            self.web_stack.removeWidget(widget)
            if isinstance(widget, QWebEngineView):
                widget.stop()
                page = widget.page()
                widget.setPage(None)
                if page:
                    page.deleteLater()
                widget.deleteLater()
        QCoreApplication.processEvents()

    def closeEvent(self, event):
        if not self.warn_on_close:
            self.cleanup_all_pages()
            event.accept()
            return
        display_name = get_profile_display_name(self.current_profile_name)
        reply = QMessageBox.question(
            self,
            "Close Tabs?",
            f"Do you want to exit Internet Explorative ({display_name})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.cleanup_all_pages()
            event.accept()
        else:
            event.ignore()

    def resolve_dark_mode(self):
        return self.theme_mode == "Dark"

    def add_to_history_cache(self, url_str):
        if not url_str or url_str.lower().startswith("ie://") or url_str == "about:blank":
            return
        history = self.settings.value("browsing_history", [])
        if not isinstance(history, list):
            history = []
        if url_str not in history:
            history.append(url_str)
            if len(history) > 200:
                history.pop(0)
            self.settings.setValue("browsing_history", history)

    def apply_theme(self):
        self.is_dark_mode = self.resolve_dark_mode()

        if self.web_profile:
            self.web_profile.settings().setAttribute(
                QWebEngineSettings.WebAttribute.ForceDarkMode, self.is_dark_mode
            )

        bg = "#1e1e1e" if self.is_dark_mode else "#f0f0f0"
        fg = "#ffffff" if self.is_dark_mode else "#222222"
        bar_bg = "#2d2d2d" if self.is_dark_mode else "#e1e1e1"
        tab_sel = "#383838" if self.is_dark_mode else "#ffffff"
        accent = self.accent_color

        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {bg}; }}
            QMenuBar {{ 
                background-color: {bg}; 
                border-bottom: 1px solid #333; 
                font-family: 'Segoe UI'; 
                font-size: 12px; 
                color: {fg};
            }}
            QMenuBar::item {{ padding: 3px 8px; color: {fg}; }}
            QMenuBar::item:selected {{ background: {accent}; color: white; }}

            QPushButton#backBtn {{
                background-color: {accent};
                color: white;
                border-radius: 21px;
                font-weight: bold;
                font-size: 22px;
                border: none;
            }}
            QPushButton#backBtn:hover:enabled {{ opacity: 0.85; }}
            QPushButton#backBtn:disabled {{
                background-color: {"#3a3a3a" if self.is_dark_mode else "#cccccc"};
                color: {"#777777" if self.is_dark_mode else "#888888"};
            }}

            QToolButton.navBtn {{
                background: transparent;
                border: 1px solid transparent;
                font-size: 14px;
                color: {fg};
                border-radius: 2px;
            }}
            QToolButton.navBtn:hover {{ background: {accent}; color: white; }}

            QToolButton#reloadBtn {{
                background: transparent;
                border: 1px solid transparent;
                font-size: 18px;
                font-weight: bold;
                color: {fg};
                border-radius: 2px;
            }}
            QToolButton#reloadBtn:hover {{ background: {accent}; color: white; }}

            QToolButton#toolsBtn::menu-indicator {{ image: none; width: 0px; }}

            QLineEdit#urlBar {{
                background: {"#2b2b2b" if self.is_dark_mode else "#ffffff"};
                border: 1px solid {"#555" if self.is_dark_mode else "#8e8e8e"};
                padding: 3px 6px;
                font-family: 'Segoe UI';
                font-size: 12px;
                border-radius: 2px;
                color: {fg};
            }}

            QTabBar {{ alignment: left; border: none; }}
            QTabBar::tab {{
                background: {bar_bg};
                border: 1px solid {"#444" if self.is_dark_mode else "#b5b5b5"};
                padding: 0px 8px;
                margin-right: 1px;
                font-family: 'Segoe UI';
                font-size: 11px;
                height: 30px;
                color: {fg};
            }}
            QTabBar::tab:selected {{
                background: {tab_sel};
                border-top: 2px solid {accent};
                font-weight: bold;
            }}

            QToolBar#bookmarksBar {{
                background: {bg};
                border-top: 1px solid {"#333" if self.is_dark_mode else "#e0e0e0"};
                border-bottom: 1px solid {"#333" if self.is_dark_mode else "#d0d0d0"};
                spacing: 4px;
                padding: 2px 6px;
            }}
            QToolBar#bookmarksBar QToolButton {{
                background: {bar_bg};
                border: 1px solid {"#444" if self.is_dark_mode else "#d0d0d0"};
                border-radius: 2px;
                font-family: 'Segoe UI';
                font-size: 11px;
                padding: 2px 6px;
                color: {fg};
            }}
            QToolBar#bookmarksBar QToolButton:hover {{ background: {accent}; color: white; }}
        """)

    def current_browser(self):
        return self.web_stack.currentWidget()

    def handle_download(self, download_item: QWebEngineDownloadRequest):
        default_path = os.path.join(
            os.path.expanduser("~"),
            "Downloads",
            download_item.downloadFileName(),
        )
        path, _ = QFileDialog.getSaveFileName(self, "Save File", default_path)
        if path:
            download_item.setDownloadDirectory(os.path.dirname(path))
            download_item.setDownloadFileName(os.path.basename(path))
            download_item.accept()

            self.downloads_history.append(
                {
                    "name": download_item.downloadFileName(),
                    "path": os.path.abspath(path),
                }
            )
            self.settings.setValue("downloads_history", self.downloads_history)
            self.statusBar().showMessage(f"Downloaded: {download_item.downloadFileName()}")
            self.show_downloads()

    def add_new_tab(self, qurl=None, label="New Tab", return_page=False):
        browser = QWebEngineView()
        page = IEWebPage(browser, self, self.web_profile)
        browser.setPage(page)

        stack_index = self.web_stack.addWidget(browser)
        tab_index = self.tab_bar.addTab(label)

        self.tab_bar.setCurrentIndex(tab_index)
        self.web_stack.setCurrentIndex(stack_index)
        browser.setFocus()

        browser.urlChanged.connect(lambda q, b=browser: self.update_url(q, b))
        browser.loadFinished.connect(lambda ok, b=browser: self.handle_page_loaded(ok, b))

        if qurl is not None:
            if not qurl.isEmpty():
                url_str = qurl.toString().lower().strip().rstrip("/")
                if "ie://info" in url_str or url_str == "ie:info":
                    page.custom_url = "ie://info"
                    self.url_bar.setText("ie://info")
                    QTimer.singleShot(0, page.load_info_html)
                elif "ie://snake" in url_str or url_str == "ie:snake":
                    page.custom_url = "ie://snake"
                    self.url_bar.setText("ie://snake")
                    QTimer.singleShot(0, page.load_snake_html)
                else:
                    page.custom_url = ""
                    browser.setUrl(qurl)

        if return_page:
            return page
        return browser

    def handle_page_loaded(self, ok, browser):
        self.update_tab_state(browser)
        url_str = browser.url().toString()
        if ok:
            self.add_to_history_cache(url_str)

    def close_tab(self, index):
        if 0 <= index < self.tab_bar.count():
            if self.tab_bar.count() > 1:
                widget_to_remove = self.web_stack.widget(index)
                if widget_to_remove:
                    self.web_stack.removeWidget(widget_to_remove)
                    if isinstance(widget_to_remove, QWebEngineView):
                        widget_to_remove.stop()
                        page = widget_to_remove.page()
                        widget_to_remove.setPage(None)
                        if page:
                            page.deleteLater()
                        widget_to_remove.deleteLater()
                self.tab_bar.removeTab(index)
                QCoreApplication.processEvents()
            else:
                self.close()

    def current_tab_changed(self, index):
        if 0 <= index < self.web_stack.count():
            self.web_stack.setCurrentIndex(index)
            browser = self.current_browser()
            if browser and isinstance(browser, QWebEngineView):
                browser.setFocus()
                page = browser.page()
                if isinstance(page, IEWebPage) and page.custom_url:
                    self.url_bar.setText(page.custom_url)
                else:
                    self.url_bar.setText(browser.url().toString())
                self.update_nav_buttons(browser)

    def update_nav_buttons(self, browser):
        self.back_btn.setEnabled(browser.history().canGoBack())
        self.forward_btn.setEnabled(browser.history().canGoForward())

    def navigate_back(self):
        browser = self.current_browser()
        if browser:
            if isinstance(browser.page(), IEWebPage):
                browser.page().custom_url = ""
            browser.back()

    def navigate_forward(self):
        browser = self.current_browser()
        if browser:
            if isinstance(browser.page(), IEWebPage):
                browser.page().custom_url = ""
            browser.forward()

    def navigate_reload(self):
        browser = self.current_browser()
        if browser and isinstance(browser.page(), IEWebPage):
            page = browser.page()
            if page.custom_url == "ie://info":
                QTimer.singleShot(0, page.load_info_html)
            elif page.custom_url == "ie://snake":
                QTimer.singleShot(0, page.load_snake_html)
            else:
                browser.reload()

    def navigate_home(self):
        browser = self.current_browser()
        if browser:
            target = self.home_url if self.home_url else DEFAULT_HOME_URL
            if isinstance(browser.page(), IEWebPage):
                browser.page().custom_url = ""
            browser.setUrl(QUrl(target))

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return

        text_lower = text.lower().strip().rstrip("/")
        if any(k in text_lower for k in ["ie://info", "ie://snake", "ie:info", "ie:snake"]):
            browser = self.current_browser()
            if browser and isinstance(browser.page(), IEWebPage):
                page = browser.page()
                if "info" in text_lower:
                    page.custom_url = "ie://info"
                    QTimer.singleShot(0, page.load_info_html)
                else:
                    page.custom_url = "ie://snake"
                    QTimer.singleShot(0, page.load_snake_html)
            else:
                if "info" in text_lower:
                    self.add_new_tab(QUrl("ie://info"), "Info")
                else:
                    self.add_new_tab(QUrl("ie://snake"), "Snake")
            return

        if not text.startswith("http://") and not text.startswith("https://") and not text.startswith("about:"):
            if "." in text and " " not in text:
                text = "https://" + text
            else:
                engines = {
                    "DuckDuckGo": "https://duckduckgo.com/?q=",
                    "Bing": "https://www.bing.com/search?q=",
                    "Google": "https://www.google.com/search?q=",
                    "Yahoo": "https://search.yahoo.com/search?p=",
                    "Ecosia": "https://www.ecosia.org/search?q=",
                    "Qwant": "https://www.qwant.com/?q=",
                    "Baidu": "https://www.baidu.com/s?wd=",
                    "Startpage": "https://www.startpage.com/sp/search?query=",
                }
                base = engines.get(self.search_engine, "https://duckduckgo.com/?q=")
                text = base + text.replace(" ", "+")

        browser = self.current_browser()
        if browser:
            if isinstance(browser.page(), IEWebPage):
                browser.page().custom_url = ""
            browser.setUrl(QUrl(text))
            browser.setFocus()

    def update_url(self, qurl, browser):
        if browser == self.current_browser():
            page = browser.page()
            if isinstance(page, IEWebPage) and page.custom_url:
                self.url_bar.setText(page.custom_url)
            else:
                self.url_bar.setText(qurl.toString())
            self.statusBar().showMessage(self.url_bar.text())
            self.update_nav_buttons(browser)

    def update_tab_state(self, browser):
        index = self.web_stack.indexOf(browser)
        if index != -1 and index < self.tab_bar.count():
            page = browser.page()
            if isinstance(page, IEWebPage) and page.custom_url:
                title_map = {"ie://info": "Info", "ie://snake": "Snake"}
                title = title_map.get(page.custom_url, "New Tab")
            else:
                title = page.title() or "New Tab"
            display_title = (title[:12] + "...") if len(title) > 12 else title
            self.tab_bar.setTabText(index, display_title)
        if browser == self.current_browser():
            self.statusBar().showMessage("Done")
            self.update_nav_buttons(browser)

    def share_current_page(self):
        browser = self.current_browser()
        if not browser:
            return
        url_str = self.url_bar.text()
        if not url_str or url_str == "about:blank":
            QMessageBox.warning(self, "Share", "No active web page to share.")
            return

        title = browser.page().title() or "Internet Explorative Page"
        dialog = ShareDialog(title, url_str, self.is_dark_mode, self)
        dialog.exec()

    def open_local_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Local File", "", "HTML Files (*.html *.htm);;All Files (*)"
        )
        if file_path:
            self.add_new_tab(QUrl.fromLocalFile(file_path), "Local File")

    def zoom_in(self):
        browser = self.current_browser()
        if browser:
            browser.setZoomFactor(browser.zoomFactor() + 0.1)

    def zoom_out(self):
        browser = self.current_browser()
        if browser:
            browser.setZoomFactor(max(0.25, browser.zoomFactor() - 0.1))

    def add_bookmark(self):
        browser = self.current_browser()
        if not browser:
            return
        url = self.url_bar.text()
        title = browser.page().title() or url
        if url.lower() == "ie://info":
            title = "Info"
        elif url.lower() == "ie://snake":
            title = "Explorative snake"

        bookmarks = self.settings.value("saved_bookmarks", [])
        if not isinstance(bookmarks, list):
            bookmarks = []

        new_bookmark = {"title": title, "url": url}
        if new_bookmark not in bookmarks:
            bookmarks.append(new_bookmark)
            self.settings.setValue("saved_bookmarks", bookmarks)
            self.load_bookmarks()
            display_name = get_profile_display_name(self.current_profile_name)
            QMessageBox.information(
                self, "Favorites", f"Added to Favorites in ({display_name}) profile!"
            )

    def delete_single_favorite(self):
        bookmarks = self.settings.value("saved_bookmarks", [])
        if not isinstance(bookmarks, list) or not bookmarks:
            QMessageBox.information(self, "Favorites", "No saved favorites to delete.")
            return

        dialog = ManageFavoritesDialog(bookmarks, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.deleted:
            self.settings.setValue("saved_bookmarks", dialog.get_bookmarks())
            self.load_bookmarks()
            QMessageBox.information(self, "Favorites", "Selected favorite deleted successfully.")

    def load_bookmarks(self):
        self.fav_menu_obj.clear()

        add_fav_act = QAction("Add to Favorites", self)
        add_fav_act.setShortcut("Ctrl+D")
        add_fav_act.triggered.connect(self.add_bookmark)
        self.fav_menu_obj.addAction(add_fav_act)
        self.fav_menu_obj.addSeparator()

        self.bookmarks_bar.clear()

        bookmarks = self.settings.value("saved_bookmarks", [])
        if not isinstance(bookmarks, list):
            bookmarks = []

        if not bookmarks:
            label = QLabel(" <i>No bookmarks saved. Click ★ to add current page.</i> ")
            label.setStyleSheet("color: #777; font-size: 11px;")
            self.bookmarks_bar.addWidget(label)
            return

        for bm in bookmarks:
            action = QAction(bm["title"], self)
            action.triggered.connect(
                lambda checked, u=bm["url"]: self.add_new_tab(QUrl(u), "Bookmark")
            )
            self.fav_menu_obj.addAction(action)

            btn = QToolButton()
            btn.setText("★ " + bm["title"])
            btn.setToolTip(bm["url"])
            btn.clicked.connect(
                lambda checked, u=bm["url"]: self.add_new_tab(QUrl(u), "Bookmark")
            )
            self.bookmarks_bar.addWidget(btn)

    def show_internet_options(self):
        history = self.settings.value("browsing_history", [])
        if not isinstance(history, list):
            history = []

        dialog = InternetOptionsDialog(
            self.home_url,
            self.search_engine,
            self.theme_mode,
            self.is_ie_ua,
            self.is_adblock,
            self.warn_on_close,
            history,
            self.is_dark_mode,
            self.web_profile,
            self.accent_color,
            self.user_name,
            self,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            res = dialog.get_settings()
            self.home_url = res["home"]
            self.settings.setValue("home_page", self.home_url)

            self.user_name = res["user_name"]
            self.settings.setValue("user_name", self.user_name)

            self.accent_color = res["accent_color"]
            self.settings.setValue("accent_color", self.accent_color)

            self.search_engine = res["engine"]
            self.settings.setValue("search_engine", self.search_engine)

            self.theme_mode = res["theme_mode"]
            self.settings.setValue("theme_mode", self.theme_mode)

            self.is_ie_ua = res["ie_ua"]
            self.settings.setValue("ie_ua", self.is_ie_ua)

            self.is_adblock = res["adblock"]
            self.settings.setValue("adblock", self.is_adblock)

            self.warn_on_close = res["warn_close"]
            self.settings.setValue("warn_on_close", self.warn_on_close)

            if res["history"] is not None:
                self.settings.setValue("browsing_history", res["history"])

            self.adblock_interceptor.enabled = self.is_adblock

            if self.is_ie_ua:
                self.web_profile.setHttpUserAgent(IE_UA)
            else:
                self.web_profile.setHttpUserAgent(MODERN_UA)

            self.apply_theme()
            self.rebuild_profile_menus()

            for i in range(self.web_stack.count()):
                w = self.web_stack.widget(i)
                if isinstance(w, QWebEngineView) and isinstance(w.page(), IEWebPage):
                    page = w.page()
                    if page.custom_url == "ie://info":
                        QTimer.singleShot(0, page.load_info_html)
                    elif page.custom_url == "ie://snake":
                        QTimer.singleShot(0, page.load_snake_html)
                    else:
                        w.reload()

    def show_downloads(self):
        dialog = DownloadsDialog(self.downloads_history, self)
        dialog.exec()

    def show_about_dialog(self):
        dialog = AboutIEDialog(self)
        dialog.exec()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    app.setApplicationName("Internet Explorative")
    app.setWindowIcon(load_ie11_icon(32))
    window = IE11Browser()
    window.show()
    sys.exit(app.exec())
