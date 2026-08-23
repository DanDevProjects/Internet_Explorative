import os
import sys

from PyQt5.QtCore import QPointF, QRect, QRectF, QSettings, QSize, Qt, QUrl
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPixmap
from PyQt5.QtWebEngineWidgets import (
    QWebEngineDownloadItem,
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineView,
)
from PyQt5.QtWidgets import (
    QAbstractButton,
    QAction,
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
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QStatusBar,
    QTabBar,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


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
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

    # Fallback placeholder pixmap if image file is missing
    fallback = QPixmap(size, size)
    fallback.fill(QColor("#0078d7"))
    return QIcon(fallback)


class CustomCloseButton(QAbstractButton):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.underMouse():
            painter.setBrush(QColor("#e81123"))
            painter.setPen(Qt.NoPen)
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
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def tabInserted(self, index):
        super().tabInserted(index)
        btn = CustomCloseButton(self)
        btn.clicked.connect(lambda _, b=btn: self.handle_close_click(b))
        self.setTabButton(index, QTabBar.RightSide, btn)

    def handle_close_click(self, btn):
        for i in range(self.count()):
            if self.tabButton(i, QTabBar.RightSide) == btn:
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


class InternetOptionsDialog(QDialog):

    def __init__(
        self, current_home, current_engine, is_dark, is_ie_ua, parent=None
    ):
        super().__init__(parent)
        self.setWindowTitle("Internet Options & Settings")
        self.setFixedSize(500, 390)
        self.setStyleSheet("""
            QDialog { background-color: #f4f4f4; font-family: 'Segoe UI', Arial; }
            QLabel { font-size: 12px; color: #222222; }
            QLineEdit { background: white; border: 1px solid #a0a0a0; padding: 4px; border-radius: 2px; color: #000000; }
            
            QComboBox { 
                background: white; 
                border: 1px solid #a0a0a0; 
                padding: 4px 8px; 
                border-radius: 2px; 
                color: #000000;
                min-width: 140px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #000000;
                selection-background-color: #0078d7;
                selection-color: #ffffff;
                border: 1px solid #a0a0a0;
                padding: 4px;
                outline: 0px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 24px;
                padding: 2px 8px;
                color: #000000;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078d7;
                color: #ffffff;
            }

            QPushButton { background: #e1e1e1; border: 1px solid #adadad; padding: 5px 14px; border-radius: 2px; color: #000000; }
            QPushButton:hover { background: #e5f1fb; border-color: #0078d7; }
            QGroupBox { font-weight: bold; font-size: 12px; border: 1px solid #d0d0d0; margin-top: 8px; padding-top: 10px; color: #222222; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }
            QCheckBox { color: #222222; }
        """)

        layout = QVBoxLayout(self)

        gen_box = QGroupBox("General")
        gen_layout = QFormLayout(gen_box)

        self.home_input = QLineEdit(current_home)
        gen_layout.addRow("Home Page:", self.home_input)

        self.search_engine = QComboBox()
        self.search_engine.addItems(["Google", "Bing", "DuckDuckGo", "Yahoo"])
        self.search_engine.setCurrentText(current_engine)
        gen_layout.addRow("Default Search:", self.search_engine)

        layout.addWidget(gen_box)

        app_box = QGroupBox("Appearance & Compatibility")
        app_layout = QVBoxLayout(app_box)

        self.dark_mode_cb = QCheckBox("Enable Dark Mode Theme")
        self.dark_mode_cb.setChecked(is_dark)
        app_layout.addWidget(self.dark_mode_cb)

        self.ie_ua_cb = QCheckBox("Emulate Internet Explorer 11 User-Agent")
        self.ie_ua_cb.setChecked(is_ie_ua)
        app_layout.addWidget(self.ie_ua_cb)

        layout.addWidget(app_box)

        priv_box = QGroupBox("Browsing History & Cache")
        priv_layout = QHBoxLayout(priv_box)

        clear_cache_btn = QPushButton("Clear Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        priv_layout.addWidget(clear_cache_btn)

        clear_cookies_btn = QPushButton("Clear Cookies")
        clear_cookies_btn.clicked.connect(self.clear_cookies)
        priv_layout.addWidget(clear_cookies_btn)

        layout.addWidget(priv_box)

        layout.addSpacing(10)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

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
            "dark_mode": self.dark_mode_cb.isChecked(),
            "ie_ua": self.ie_ua_cb.isChecked(),
        }


class AboutIEDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Internet Explorative")
        self.setFixedSize(420, 200)
        self.setWindowIcon(load_ie11_icon(32))
        self.setStyleSheet("""
            QDialog { background-color: #ffffff; font-family: 'Segoe UI', Arial; }
            QLabel { color: #333333; font-size: 12px; }
            QPushButton { background-color: #e1e1e1; border: 1px solid #adadad; padding: 4px 20px; }
        """)

        layout = QVBoxLayout(self)
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
            "Internet Explorative 11 version: 11.0.2<br><b>Engine:</b>"
            " QtWebEngine / Chromium"
        )
        info_layout.addWidget(title_label)
        info_layout.addWidget(ver_label)
        top_layout.addLayout(info_layout)

        layout.addLayout(top_layout)
        layout.addWidget(QLabel("© 2026 DanDevProjects. All rights reserved."))

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box, alignment=Qt.AlignRight)


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
        self.is_dark_mode = self.settings.value("dark_mode", False, type=bool)
        self.is_ie_ua = self.settings.value("ie_ua", False, type=bool)
        self.downloads_history = []

        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.handle_download)

        if self.is_ie_ua:
            ie_ua = (
                "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0)"
                " like Gecko"
            )
            profile.setHttpUserAgent(ie_ua)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(6, 6, 6, 6)
        header_layout.setSpacing(3)

        self.back_btn = QPushButton("←")
        self.back_btn.setObjectName("backBtn")
        self.back_btn.setFixedSize(42, 42)
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self.navigate_back)
        header_layout.addWidget(self.back_btn, alignment=Qt.AlignVCenter)

        self.forward_btn = QToolButton()
        self.forward_btn.setProperty("class", "navBtn")
        self.forward_btn.setText("→")
        self.forward_btn.setFixedSize(28, 32)
        self.forward_btn.clicked.connect(self.navigate_forward)
        header_layout.addWidget(self.forward_btn, alignment=Qt.AlignVCenter)

        self.reload_btn = QToolButton()
        self.reload_btn.setProperty("class", "navBtn")
        self.reload_btn.setText("⟳")
        self.reload_btn.setFixedSize(28, 32)
        self.reload_btn.clicked.connect(self.navigate_reload)
        header_layout.addWidget(self.reload_btn, alignment=Qt.AlignVCenter)

        self.url_bar = QLineEdit()
        self.url_bar.setObjectName("urlBar")
        self.url_bar.setFixedHeight(32)
        self.url_bar.setPlaceholderText("Search or enter web address")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        header_layout.addWidget(
            self.url_bar, stretch=3, alignment=Qt.AlignVCenter
        )

        self.tab_bar = CustomTabBar()
        self.tab_bar.setMovable(True)
        self.tab_bar.setSelectionBehaviorOnRemove(QTabBar.SelectPreviousTab)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.currentChanged.connect(self.current_tab_changed)
        header_layout.addWidget(
            self.tab_bar, stretch=2, alignment=Qt.AlignVCenter
        )

        self.add_tab_btn = QToolButton()
        self.add_tab_btn.setProperty("class", "navBtn")
        self.add_tab_btn.setText("+")
        self.add_tab_btn.setToolTip("Open New Tab")
        self.add_tab_btn.setFixedSize(28, 32)
        self.add_tab_btn.clicked.connect(
            lambda: self.add_new_tab(QUrl(self.home_url), "New Tab")
        )
        header_layout.addWidget(self.add_tab_btn, alignment=Qt.AlignVCenter)

        self.home_btn = QToolButton()
        self.home_btn.setProperty("class", "navBtn")
        self.home_btn.setText("🏠")
        self.home_btn.setFixedSize(32, 32)
        self.home_btn.clicked.connect(self.navigate_home)
        header_layout.addWidget(self.home_btn, alignment=Qt.AlignVCenter)

        self.fav_btn = QToolButton()
        self.fav_btn.setProperty("class", "navBtn")
        self.fav_btn.setText("★")
        self.fav_btn.setToolTip("Add to Favorites")
        self.fav_btn.setFixedSize(32, 32)
        self.fav_btn.clicked.connect(self.add_bookmark)
        header_layout.addWidget(self.fav_btn, alignment=Qt.AlignVCenter)

        downloads_act = QAction("View Downloads", self)
        downloads_act.triggered.connect(self.show_downloads)

        options_act = QAction("Internet Options", self)
        options_act.triggered.connect(self.show_internet_options)

        clear_bm_act = QAction("Delete All Favorites", self)
        clear_bm_act.triggered.connect(
            lambda: (
                self.settings.remove("saved_bookmarks"),
                self.load_bookmarks(),
            )
        )

        about_act = QAction("About Internet Explorative", self)
        about_act.triggered.connect(self.show_about_dialog)

        self.tools_btn = QToolButton()
        self.tools_btn.setProperty("class", "navBtn")
        self.tools_btn.setObjectName("toolsBtn")
        self.tools_btn.setText("⚙")
        self.tools_btn.setToolTip("Tools & Settings")
        self.tools_btn.setFixedSize(32, 32)
        self.tools_btn.setPopupMode(QToolButton.InstantPopup)

        tools_dropdown = QMenu(self)
        tools_dropdown.addAction(downloads_act)
        tools_dropdown.addSeparator()
        tools_dropdown.addAction(options_act)
        tools_dropdown.addAction(clear_bm_act)
        tools_dropdown.addSeparator()
        tools_dropdown.addAction(about_act)
        self.tools_btn.setMenu(tools_dropdown)
        header_layout.addWidget(self.tools_btn, alignment=Qt.AlignVCenter)

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

        close_act = QAction("Exit", self)
        close_act.triggered.connect(self.close)
        file_menu.addAction(close_act)

        menubar.addMenu("Edit")
        menubar.addMenu("View")
        self.fav_menu_obj = menubar.addMenu("Favorites")

        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction(downloads_act)
        tools_menu.addAction(options_act)
        tools_menu.addAction(clear_bm_act)

        help_menu = menubar.addMenu("Help")
        help_menu.addAction(about_act)

        self.setStatusBar(QStatusBar(self))
        self.apply_theme()
        self.load_bookmarks()

        self.add_new_tab(QUrl(self.home_url), "New Tab")

    def apply_theme(self):
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
            QPushButton#backBtn:hover {{ 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a92ed, stop:1 #0066c4);
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

    def handle_download(self, download_item: QWebEngineDownloadItem):
        default_path = os.path.join(
            os.path.expanduser("~"),
            "Downloads",
            download_item.suggestedFileName(),
        )
        path, _ = QFileDialog.getSaveFileName(self, "Save File", default_path)
        if path:
            download_item.setPath(path)
            download_item.accept()
            self.downloads_history.append(download_item.suggestedFileName())
            self.statusBar().showMessage(
                f"Downloading: {download_item.suggestedFileName()}..."
            )

    def add_new_tab(self, qurl, label):
        browser = QWebEngineView()
        browser.setUrl(qurl)

        stack_index = self.web_stack.addWidget(browser)
        tab_index = self.tab_bar.addTab(label)

        self.tab_bar.setCurrentIndex(tab_index)
        self.web_stack.setCurrentIndex(stack_index)

        browser.urlChanged.connect(lambda q, b=browser: self.update_url(q, b))
        browser.loadFinished.connect(
            lambda _, b=browser: self.update_tab_state(b)
        )

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
            browser.reload()

    def navigate_home(self):
        browser = self.current_browser()
        if browser:
            browser.setUrl(QUrl(self.home_url))

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
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
                }
                base = engines.get(
                    self.search_engine, "https://www.google.com/search?q="
                )
                text = base + text.replace(" ", "+")

        browser = self.current_browser()
        if browser:
            browser.setUrl(QUrl(text))

    def update_url(self, qurl, browser):
        if browser == self.current_browser():
            self.url_bar.setText(qurl.toString())
            self.statusBar().showMessage(qurl.toString())
            self.update_nav_buttons(browser)

    def update_tab_state(self, browser):
        index = self.web_stack.indexOf(browser)
        if index != -1 and index < self.tab_bar.count():
            title = browser.page().title() or "New Tab"
            display_title = (title[:12] + "...") if len(title) > 12 else title
            self.tab_bar.setTabText(index, display_title)
        if browser == self.current_browser():
            self.statusBar().showMessage("Done")
            self.update_nav_buttons(browser)

    def add_bookmark(self):
        browser = self.current_browser()
        if not browser:
            return
        url = browser.url().toString()
        title = browser.page().title() or url

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

    def load_bookmarks(self):
        self.fav_menu_obj.clear()
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
        dialog = InternetOptionsDialog(
            self.home_url,
            self.search_engine,
            self.is_dark_mode,
            self.is_ie_ua,
            self,
        )
        if dialog.exec_() == QDialog.Accepted:
            res = dialog.get_settings()
            if res["home"]:
                self.home_url = res["home"]
                self.settings.setValue("home_page", self.home_url)
            self.search_engine = res["engine"]
            self.settings.setValue("search_engine", self.search_engine)
            self.is_dark_mode = res["dark_mode"]
            self.settings.setValue("dark_mode", self.is_dark_mode)
            self.is_ie_ua = res["ie_ua"]
            self.settings.setValue("ie_ua", self.is_ie_ua)

            profile = QWebEngineProfile.defaultProfile()
            if self.is_ie_ua:
                ie_ua = (
                    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0;"
                    " rv:11.0) like Gecko"
                )
                profile.setHttpUserAgent(ie_ua)
            else:
                profile.setHttpUserAgent("")

            self.apply_theme()

    def show_downloads(self):
        msg = (
            "\n".join(self.downloads_history)
            if self.downloads_history
            else "No recent downloads."
        )
        QMessageBox.information(self, "Downloads", msg)

    def show_about_dialog(self):
        dialog = AboutIEDialog(self)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Internet Explorative")
    app.setWindowIcon(load_ie11_icon(32))
    window = IE11Browser()
    window.show()
    sys.exit(app.exec_())
