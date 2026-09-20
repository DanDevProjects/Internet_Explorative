import os
import platform
import subprocess
import sys

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, QSettings, QSize, Qt, QUrl
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPen, QPixmap
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
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
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

# User-Agent Constants
MODERN_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
IE_UA = "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"


class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    """Interceptor to block common advertising and tracking network requests."""

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
    """A QLineEdit that automatically selects all text when focused or clicked."""

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.selectAll()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.selectAll()


class IEWebPage(QWebEnginePage):
    """Custom web page handling internal info pages, new tab creation, and target='_blank' links."""

    def __init__(self, browser_window, profile=None):
        if profile:
            super().__init__(profile, browser_window)
        else:
            super().__init__(browser_window)
        self.browser_window = browser_window

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        url_str = url.toString()
        if url_str.lower() == "ie://info":
            self.load_info_html()
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

    def createWindow(self, window_type):
        return self.browser_window.add_new_tab(QUrl(), "New Tab", return_page=True)

    def load_info_html(self):
        chromium_ver = qWebEngineChromiumVersion()
        qt_ver = getattr(QtCore, "QT_VERSION_STR", "Unknown")
        py_ver = sys.version.split()[0]
        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        ua = self.profile().httpUserAgent() or MODERN_UA

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Internet Explorative - Information</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f4f4; color: #222; padding: 30px; margin: 0; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                h1 {{ color: #0078d7; border-bottom: 2px solid #0078d7; padding-bottom: 10px; font-size: 24px; }}
                p {{ color: #555; font-size: 14px; }}
                .card {{ background: white; border: 1px solid #d0d0d0; padding: 20px; border-radius: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); margin-top: 20px; }}
                h3 {{ margin-top: 0; color: #333; font-size: 16px; border-bottom: 1px solid #eee; padding-bottom: 8px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 13px; }}
                th {{ background: #0078d7; color: white; width: 35%; }}
                td {{ background: #fafafa; color: #333; }}
                code {{ background: #eee; padding: 2px 6px; border-radius: 3px; font-family: monospace; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Internet Explorative 11</h1>
                <p>Internal information and runtime environment inspection page for Internet Explorative.</p>
                
                <div class="card">
                    <h3>System Specifications & Build Info</h3>
                    <table>
                        <tr><th>Application Name</th><td>Internet Explorative</td></tr>
                        <tr><th>Version</th><td>11.1</td></tr>
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
        self.setHtml(html, QUrl("ie://info"))


def load_ie11_icon(size=64):
    """Loads the Internet Explorer icon from a local file ('ie_icon.png')."""
    icon_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "ie_icon.png"
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
            QtGui.QDesktopServices.openUrl(QUrl.fromLocalFile(item["path"]))
        else:
            QMessageBox.warning(
                self, "Error", "File does not exist or no selection made."
            )

    def show_in_folder(self):
        item = self.get_selected_item()
        if item and os.path.exists(item["path"]):
            path = item["path"]
            if sys.platform == "darwin":
                subprocess.run(["open", "-R", path])
            elif sys.platform == "win32":
                subprocess.run(
                    ["explorer", "/select,", os.path.normpath(path)]
                )
            else:
                subprocess.run(["xdg-open", os.path.dirname(path)])
        else:
            QMessageBox.warning(
                self, "Error", "File does not exist or no selection made."
            )


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
            QMessageBox.warning(
                self, "Selection", "Please select a favorite to delete first."
            )

    def get_bookmarks(self):
        return self.bookmarks


class InternetOptionsDialog(QDialog):

    def __init__(
        self, current_home, current_engine, theme_mode, is_ie_ua, is_adblock, history_list, is_dark_mode, parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle("Internet Options & Settings")
        self.resize(760, 560)
        self.setMinimumSize(720, 500)

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
                selection-background-color: #0078d7;
                selection-color: #ffffff;
                border: 1px solid {border_col};
                padding: 4px;
            }}
            QPushButton {{ background: {'#3a3a3a' if is_dark_mode else '#e1e1e1'}; border: 1px solid {border_col}; padding: 6px 16px; border-radius: 2px; color: {fg}; }}
            QPushButton:hover {{ background: #0078d7; color: white; border-color: #0078d7; }}
            QGroupBox {{ font-weight: bold; font-size: 12px; border: 1px solid {border_col}; margin-top: 10px; padding-top: 12px; color: {fg}; }}
            QCheckBox {{ color: {fg}; spacing: 8px; }}
            QTabWidget::pane {{ border: 1px solid {border_col}; background: {bg}; border-radius: 2px; }}
            QTabBar::tab {{ background: {tab_bg}; padding: 8px 24px; margin-right: 6px; border-top-left-radius: 3px; border-top-right-radius: 3px; color: {fg}; min-width: 120px; font-weight: 500; }}
            QTabBar::tab:selected {{ background: {tab_sel}; font-weight: bold; border-bottom: 2px solid #0078d7; color: {fg}; }}
            QListWidget {{ background: {input_bg}; color: {fg}; border: 1px solid {border_col}; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setElideMode(Qt.TextElideMode.ElideNone)
        layout.addWidget(self.tabs)

        # Tab 1: General
        gen_widget = QWidget()
        gen_layout = QFormLayout(gen_widget)
        gen_layout.setContentsMargins(20, 20, 20, 20)
        gen_layout.setVerticalSpacing(16)
        gen_layout.setHorizontalSpacing(16)

        self.home_input = QLineEdit(current_home)
        gen_layout.addRow("Home Page:", self.home_input)

        self.search_engine = QComboBox()
        self.search_engine.addItems([
            "Google", "Bing", "DuckDuckGo", "Yahoo", "Ecosia", "Qwant", "Baidu", "Startpage"
        ])
        self.search_engine.setCurrentText(current_engine)
        gen_layout.addRow("Default Search:", self.search_engine)
        self.tabs.addTab(gen_widget, "General")

        # Tab 2: Appearance & Privacy
        app_widget = QWidget()
        app_layout = QFormLayout(app_widget)
        app_layout.setContentsMargins(20, 20, 20, 20)
        app_layout.setVerticalSpacing(16)
        app_layout.setHorizontalSpacing(16)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setCurrentText(theme_mode if theme_mode in ["Dark", "Light"] else "Dark")
        app_layout.addRow("Theme Mode:", self.theme_combo)

        self.ie_ua_cb = QCheckBox("Emulate Internet Explorer 11 User-Agent")
        self.ie_ua_cb.setChecked(is_ie_ua)
        app_layout.addRow("", self.ie_ua_cb)

        self.adblock_cb = QCheckBox("Enable Built-in Adblocker (On by default)")
        self.adblock_cb.setChecked(is_adblock)
        app_layout.addRow("", self.adblock_cb)

        priv_box = QGroupBox("Temporary Files & Cookies")
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

        # Tab 3: History Tab
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
        QWebEngineProfile.defaultProfile().clearHttpCache()
        QMessageBox.information(
            self, "Cache Cleared", "Temporary internet cache cleared."
        )

    def clear_cookies(self):
        QWebEngineProfile.defaultProfile().cookieStore().deleteAllCookies()
        QMessageBox.information(
            self, "Cookies Cleared", "All browsing cookies cleared."
        )

    def get_settings(self):
        return {
            "home": self.home_input.text().strip(),
            "engine": self.search_engine.currentText(),
            "theme_mode": self.theme_combo.currentText(),
            "ie_ua": self.ie_ua_cb.isChecked(),
            "adblock": self.adblock_cb.isChecked(),
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
            " #0076d6;'><b>Internet</b> Explorative 11</span>"
        )
        ver_label = QLabel(
            "Internet Explorative version: 11.1<br><b>Engine:</b>"
            " PyQt6 (Chromium 140)"
        )
        info_layout.addWidget(title_label)
        info_layout.addWidget(ver_label)
        top_layout.addLayout(info_layout)

        layout.addLayout(top_layout)
        layout.addWidget(
            QLabel(
                "© 2026 DanDevProjects. All rights reserved.<br><i>Tip: Type"
                " <b>ie://info</b> in address bar for system"
                " information.</i>"
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

        self.settings = QSettings("DanDevProjects", "InternetExplorative")
        self.home_url = self.settings.value(
            "home_page", "https://www.google.com"
        )
        self.search_engine = self.settings.value("search_engine", "Google")
        
        saved_theme = self.settings.value("theme_mode", "Dark")
        self.theme_mode = saved_theme if saved_theme in ["Dark", "Light"] else "Dark"
        self.is_dark_mode = self.resolve_dark_mode()

        self.is_ie_ua = self.settings.value("ie_ua", False, type=bool)
        self.is_adblock = self.settings.value("adblock", True, type=bool)
        self.downloads_history = []

        self.adblock_interceptor = AdBlockInterceptor()
        self.adblock_interceptor.enabled = self.is_adblock

        profile = QWebEngineProfile.defaultProfile()
        profile.setUrlRequestInterceptor(self.adblock_interceptor)
        profile.downloadRequested.connect(self.handle_download)

        if self.is_ie_ua:
            profile.setHttpUserAgent(IE_UA)
        else:
            profile.setHttpUserAgent(MODERN_UA)

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
        header_layout.addWidget(
            self.back_btn, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        self.forward_btn = QToolButton()
        self.forward_btn.setProperty("class", "navBtn")
        self.forward_btn.setText("→")
        self.forward_btn.setFixedSize(32, 32)
        self.forward_btn.clicked.connect(self.navigate_forward)
        header_layout.addWidget(
            self.forward_btn, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        self.reload_btn = QToolButton()
        self.reload_btn.setObjectName("reloadBtn")
        self.reload_btn.setText("⟳")
        self.reload_btn.setFixedSize(32, 32)
        self.reload_btn.setToolTip("Reload Page")
        self.reload_btn.clicked.connect(self.navigate_reload)
        header_layout.addWidget(
            self.reload_btn, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        self.url_bar = SelectAllLineEdit()
        self.url_bar.setObjectName("urlBar")
        self.url_bar.setFixedHeight(32)
        self.url_bar.setPlaceholderText(
            "Search, enter web address, or type ie://info"
        )
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        header_layout.addWidget(
            self.url_bar, stretch=3, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        self.tab_bar = CustomTabBar()
        self.tab_bar.setMovable(True)
        self.tab_bar.setSelectionBehaviorOnRemove(
            QTabBar.SelectionBehavior.SelectPreviousTab
        )
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.currentChanged.connect(self.current_tab_changed)
        header_layout.addWidget(
            self.tab_bar, stretch=2, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        self.add_tab_btn = QToolButton()
        self.add_tab_btn.setProperty("class", "navBtn")
        self.add_tab_btn.setText("+")
        self.add_tab_btn.setToolTip("Open New Tab")
        self.add_tab_btn.setFixedSize(32, 32)
        self.add_tab_btn.clicked.connect(
            lambda: self.add_new_tab(QUrl(self.home_url), "New Tab")
        )
        header_layout.addWidget(
            self.add_tab_btn, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        self.home_btn = QToolButton()
        self.home_btn.setProperty("class", "navBtn")
        self.home_btn.setText("🏠")
        self.home_btn.setFixedSize(32, 32)
        self.home_btn.clicked.connect(self.navigate_home)
        header_layout.addWidget(
            self.home_btn, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        self.fav_btn = QToolButton()
        self.fav_btn.setProperty("class", "navBtn")
        self.fav_btn.setText("★")
        self.fav_btn.setToolTip("Add to Favorites")
        self.fav_btn.setFixedSize(32, 32)
        self.fav_btn.clicked.connect(self.add_bookmark)
        header_layout.addWidget(
            self.fav_btn, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        downloads_act = QAction("View Downloads", self)
        downloads_act.triggered.connect(self.show_downloads)

        options_act = QAction("Internet Options", self)
        options_act.triggered.connect(self.show_internet_options)

        delete_fav_act = QAction("Delete Favorite...", self)
        delete_fav_act.triggered.connect(self.delete_single_favorite)

        about_act = QAction("About Internet Explorative", self)
        about_act.triggered.connect(self.show_about_dialog)

        self.tools_btn = QToolButton()
        self.tools_btn.setProperty("class", "navBtn")
        self.tools_btn.setObjectName("toolsBtn")
        self.tools_btn.setText("⚙")
        self.tools_btn.setToolTip("Tools & Settings")
        self.tools_btn.setFixedSize(32, 32)
        self.tools_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        tools_dropdown = QMenu(self)
        tools_dropdown.addAction(downloads_act)
        tools_dropdown.addSeparator()
        tools_dropdown.addAction(options_act)
        tools_dropdown.addAction(delete_fav_act)
        tools_dropdown.addSeparator()
        tools_dropdown.addAction(about_act)
        self.tools_btn.setMenu(tools_dropdown)
        header_layout.addWidget(
            self.tools_btn, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        self.main_layout.addLayout(header_layout)

        self.bookmarks_bar = QToolBar("Bookmarks Bar")
        self.bookmarks_bar.setObjectName("bookmarksBar")
        self.bookmarks_bar.setMovable(False)
        self.main_layout.addWidget(self.bookmarks_bar)

        self.web_stack = QStackedWidget()
        self.main_layout.addWidget(self.web_stack)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        new_tab_act = QAction("New Tab", self)
        new_tab_act.setShortcut("Ctrl+T")
        new_tab_act.triggered.connect(
            lambda: self.add_new_tab(QUrl(self.home_url), "New Tab")
        )
        file_menu.addAction(new_tab_act)

        open_file_act = QAction("Open File...", self)
        open_file_act.setShortcut("Ctrl+O")
        open_file_act.triggered.connect(self.open_local_file)
        file_menu.addAction(open_file_act)
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
        tools_menu.addAction(downloads_act)
        tools_menu.addAction(options_act)
        tools_menu.addAction(delete_fav_act)

        help_menu = menubar.addMenu("Help")
        info_act = QAction("Developer Information (ie://info)", self)
        info_act.triggered.connect(lambda: self.add_new_tab(QUrl("ie://info"), "Info"))
        help_menu.addAction(info_act)
        help_menu.addSeparator()
        help_menu.addAction(about_act)

        self.setStatusBar(QStatusBar(self))
        self.apply_theme()
        self.load_bookmarks()

        self.add_new_tab(QUrl(self.home_url), "New Tab")

    def resolve_dark_mode(self):
        return self.theme_mode == "Dark"

    def add_to_history_cache(self, url_str):
        if not url_str or url_str.lower() == "ie://info":
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
        
        profile = QWebEngineProfile.defaultProfile()
        profile.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ForceDarkMode, self.is_dark_mode
        )

        bg = "#1e1e1e" if self.is_dark_mode else "#f0f0f0"
        fg = "#ffffff" if self.is_dark_mode else "#222222"
        bar_bg = "#2d2d2d" if self.is_dark_mode else "#e1e1e1"
        tab_sel = "#383838" if self.is_dark_mode else "#ffffff"

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
            QMenuBar::item:selected {{ background: #0078d7; color: white; }}

            QPushButton#backBtn {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0081e0, stop:1 #0056a8);
                color: white;
                border-radius: 21px;
                font-weight: bold;
                font-size: 22px;
                border: 2px solid #004080;
            }}
            QPushButton#backBtn:hover:enabled {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a92ed, stop:1 #0066c4);
            }}
            QPushButton#backBtn:disabled {{
                background: {"#3a3a3a" if self.is_dark_mode else "#cccccc"};
                color: {"#777777" if self.is_dark_mode else "#888888"};
                border: 2px solid {"#555555" if self.is_dark_mode else "#b0b0b0"};
            }}

            QToolButton.navBtn {{
                background: transparent;
                border: 1px solid transparent;
                font-size: 14px;
                color: {fg};
                border-radius: 2px;
            }}
            QToolButton.navBtn:hover {{ 
                background: #0078d7; 
                color: white;
            }}

            QToolButton#reloadBtn {{
                background: transparent;
                border: 1px solid transparent;
                font-size: 18px;
                font-weight: bold;
                color: {fg};
                border-radius: 2px;
            }}
            QToolButton#reloadBtn:hover {{
                background: #0078d7;
                color: white;
            }}

            QToolButton#toolsBtn::menu-indicator {{
                image: none;
                width: 0px;
            }}

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
                border-top: 2px solid #0078d7;
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
            QToolBar#bookmarksBar QToolButton:hover {{
                background: #0078d7;
                color: white;
            }}
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
            self.statusBar().showMessage(
                f"Downloaded: {download_item.downloadFileName()}"
            )
            self.show_downloads()

    def add_new_tab(self, qurl, label, return_page=False):
        browser = QWebEngineView()
        page = IEWebPage(self, browser.page().profile())
        browser.setPage(page)

        stack_index = self.web_stack.addWidget(browser)
        tab_index = self.tab_bar.addTab(label)

        self.tab_bar.setCurrentIndex(tab_index)
        self.web_stack.setCurrentIndex(stack_index)
        browser.setFocus()

        if qurl.toString().lower() == "ie://info":
            page.load_info_html()
        elif qurl.toString():
            browser.setUrl(qurl)
        else:
            page.load_info_html()

        browser.urlChanged.connect(lambda q, b=browser: self.update_url(q, b))
        browser.loadFinished.connect(
            lambda ok, b=browser: self.handle_page_loaded(ok, b)
        )

        if return_page:
            return page
        return browser

    def handle_page_loaded(self, ok, browser):
        self.update_tab_state(browser)
        url_str = browser.url().toString()
        if ok:
            self.add_to_history_cache(url_str)

        if not ok and url_str.lower() != "ie://info":
            err_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Server Not Found</title>
                <style>
                    body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f4f4; color: #333; padding: 50px; text-align: center; }
                    .box { background: white; border: 1px solid #d0d0d0; max-width: 600px; margin: 0 auto; padding: 40px; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
                    h1 { color: #0078d7; font-size: 22px; margin-top: 0; }
                    p { font-size: 14px; color: #555; line-height: 1.5; }
                </style>
            </head>
            <body>
                <div class="box">
                    <h1>Server Not Found / Invalid Web Address</h1>
                    <p>Internet Explorative cannot display the requested webpage because the server could not be found, the network is offline, or the URL is invalid.</p>
                    <p><b>Please check the web address for typing errors or try your search query again.</b></p>
                </div>
            </body>
            </html>
            """
            browser.setHtml(err_html)

    def close_tab(self, index):
        if 0 <= index < self.tab_bar.count():
            if self.tab_bar.count() > 1:
                widget_to_remove = self.web_stack.widget(index)
                if widget_to_remove:
                    self.web_stack.removeWidget(widget_to_remove)
                    widget_to_remove.deleteLater()
                self.tab_bar.removeTab(index)
            else:
                self.close()

    def current_tab_changed(self, index):
        if 0 <= index < self.web_stack.count():
            self.web_stack.setCurrentIndex(index)
            browser = self.current_browser()
            if browser and isinstance(browser, QWebEngineView):
                browser.setFocus()
                self.url_bar.setText(browser.url().toString())
                self.update_nav_buttons(browser)

    def update_nav_buttons(self, browser):
        self.back_btn.setEnabled(browser.history().canGoBack())
        self.forward_btn.setEnabled(browser.history().canGoForward())

    def navigate_back(self):
        browser = self.current_browser()
        if browser:
            browser.back()

    def navigate_forward(self):
        browser = self.current_browser()
        if browser:
            browser.forward()

    def navigate_reload(self):
        browser = self.current_browser()
        if browser:
            if browser.url().toString().lower() == "ie://info":
                if isinstance(browser.page(), IEWebPage):
                    browser.page().load_info_html()
            else:
                browser.reload()

    def navigate_home(self):
        browser = self.current_browser()
        if browser:
            browser.setUrl(QUrl(self.home_url))

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return

        if text.lower() == "ie://info":
            browser = self.current_browser()
            if browser:
                if isinstance(browser.page(), IEWebPage):
                    browser.page().load_info_html()
                else:
                    self.add_new_tab(QUrl("ie://info"), "Info")
            return

        if not text.startswith("http://") and not text.startswith("https://"):
            if "." in text and " " not in text:
                text = "https://" + text
            else:
                engines = {
                    "Google": "https://www.google.com/search?q=",
                    "Bing": "https://www.bing.com/search?q=",
                    "DuckDuckGo": "https://duckduckgo.com/?q=",
                    "Yahoo": "https://search.yahoo.com/search?p=",
                    "Ecosia": "https://www.ecosia.org/search?q=",
                    "Qwant": "https://www.qwant.com/?q=",
                    "Baidu": "https://www.baidu.com/s?wd=",
                    "Startpage": "https://www.startpage.com/sp/search?query=",
                }
                base = engines.get(
                    self.search_engine, "https://www.google.com/search?q="
                )
                text = base + text.replace(" ", "+")

        browser = self.current_browser()
        if browser:
            browser.setUrl(QUrl(text))
            browser.setFocus()

    def update_url(self, qurl, browser):
        if browser == self.current_browser():
            self.url_bar.setText(qurl.toString())
            self.statusBar().showMessage(qurl.toString())
            self.update_nav_buttons(browser)

    def update_tab_state(self, browser):
        index = self.web_stack.indexOf(browser)
        if index != -1 and index < self.tab_bar.count():
            title = browser.page().title() or "New Tab"
            if browser.url().toString().lower() == "ie://info":
                title = "Info"
            display_title = (title[:12] + "...") if len(title) > 12 else title
            self.tab_bar.setTabText(index, display_title)
        if browser == self.current_browser():
            self.statusBar().showMessage("Done")
            self.update_nav_buttons(browser)

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
        url = browser.url().toString()
        title = browser.page().title() or url
        if url.lower() == "ie://info":
            title = "Info"

        bookmarks = self.settings.value("saved_bookmarks", [])
        if not isinstance(bookmarks, list):
            bookmarks = []

        new_bookmark = {"title": title, "url": url}
        if new_bookmark not in bookmarks:
            bookmarks.append(new_bookmark)
            self.settings.setValue("saved_bookmarks", bookmarks)
            self.load_bookmarks()
            QMessageBox.information(
                self, "Favorites", "Added to Favorites Bar successfully!"
            )

    def delete_single_favorite(self):
        bookmarks = self.settings.value("saved_bookmarks", [])
        if not isinstance(bookmarks, list) or not bookmarks:
            QMessageBox.information(
                self, "Favorites", "No saved favorites to delete."
            )
            return

        dialog = ManageFavoritesDialog(bookmarks, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.deleted:
            self.settings.setValue("saved_bookmarks", dialog.get_bookmarks())
            self.load_bookmarks()
            QMessageBox.information(
                self, "Favorites", "Selected favorite deleted successfully."
            )

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
            label = QLabel(
                " <i>No bookmarks saved. Click ★ to add current page.</i> "
            )
            label.setStyleSheet("color: #777; font-size: 11px;")
            self.bookmarks_bar.addWidget(label)
            return

        for bm in bookmarks:
            action = QAction(bm["title"], self)
            action.triggered.connect(
                lambda checked, u=bm["url"]: self.add_new_tab(
                    QUrl(u), "Bookmark"
                )
            )
            self.fav_menu_obj.addAction(action)

            btn = QToolButton()
            btn.setText("★ " + bm["title"])
            btn.setToolTip(bm["url"])
            btn.clicked.connect(
                lambda checked, u=bm["url"]: self.add_new_tab(
                    QUrl(u), "Bookmark"
                )
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
            history,
            self.is_dark_mode,
            self,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            res = dialog.get_settings()
            if res["home"]:
                self.home_url = res["home"]
                self.settings.setValue("home_page", self.home_url)
            self.search_engine = res["engine"]
            self.settings.setValue("search_engine", self.search_engine)
            
            self.theme_mode = res["theme_mode"]
            self.settings.setValue("theme_mode", self.theme_mode)

            self.is_ie_ua = res["ie_ua"]
            self.settings.setValue("ie_ua", self.is_ie_ua)

            self.is_adblock = res["adblock"]
            self.settings.setValue("adblock", self.is_adblock)

            if res["history"] is not None:
                self.settings.setValue("browsing_history", res["history"])

            self.adblock_interceptor.enabled = self.is_adblock

            profile = QWebEngineProfile.defaultProfile()
            if self.is_ie_ua:
                profile.setHttpUserAgent(IE_UA)
            else:
                profile.setHttpUserAgent(MODERN_UA)

            self.apply_theme()

            for i in range(self.web_stack.count()):
                w = self.web_stack.widget(i)
                if isinstance(w, QWebEngineView):
                    if w.url().toString().lower() == "ie://info":
                        if isinstance(w.page(), IEWebPage):
                            w.page().load_info_html()
                    else:
                        w.reload()

    def show_downloads(self):
        dialog = DownloadsDialog(self.downloads_history, self)
        dialog.exec()

    def show_about_dialog(self):
        dialog = AboutIEDialog(self)
        dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Internet Explorative")
    app.setWindowIcon(load_ie11_icon(32))
    window = IE11Browser()
    window.show()
    sys.exit(app.exec())
