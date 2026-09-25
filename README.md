<img src="ie_icon.png" width="80" align="right" hspace="10" alt="Internet Explorative Icon">

# Internet Explorative

[![Release](https://img.shields.io/github/v/release/DanDevProjects/Internet_Explorative?style=flat-square)](https://github.com/DanDevProjects/Internet_Explorative/releases)
[![Downloads](https://img.shields.io/github/downloads/DanDevProjects/Internet_Explorative/total?style=flat-square)](https://github.com/DanDevProjects/Internet_Explorative/releases)
[![Stars](https://img.shields.io/github/stars/DanDevProjects/Internet_Explorative?style=flat-square)](https://github.com/DanDevProjects/Internet_Explorative/stargazers)
[![Issues](https://img.shields.io/github/issues/DanDevProjects/Internet_Explorative?style=flat-square)](https://github.com/DanDevProjects/Internet_Explorative/issues)
[![License](https://img.shields.io/github/license/DanDevProjects/Internet_Explorative?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-Qt6-blue?style=flat-square)](https://www.riverbankcomputing.com/software/pyqt/)
[![Chromium](https://img.shields.io/badge/Chromium-140-blue?style=flat-square&logo=googlechrome&logoColor=white)](https://www.chromium.org/)
[![macOS](https://img.shields.io/badge/macOS-Primary-black?style=flat-square&logo=apple&logoColor=white)](#system-requirements)
[![Windows](https://img.shields.io/badge/Windows-Experimental-lightgrey?style=flat-square&logo=windows&logoColor=black)](#system-requirements)

**WARNING:** This project is vibe-coded. While I do my best to keep everything working, bugs and unexpected behavior may still occur.

## About Internet Explorative

**Internet Explorative** is a lightweight, privacy-focused web browser designed to recreate the familiar look and feel of **Internet Explorer** while bringing it into the modern web.

Built with **Python** and **PyQt6**, Internet Explorative uses **Qt WebEngine** and Chromium 140.0.7339.225 to provide a modern browsing experience while maintaining an Internet Explorer-inspired interface.

### Features

- Internet Explorer-inspired user interface
- Chromium-based web rendering
- Built-in ad blocker
- Lightweight application
- Multiple search engine options
- No account required
- No sign-up required
- No intentional browsing-history tracking
- Supports macOS and Windows
- Simple and familiar browsing experience

The application itself is very small, at less than 200 KB before its bundled dependencies. Typical memory usage is under 500 MB depending on the number and complexity of open pages.

> **Extension support:** Browser extensions are not currently supported. Extensions cannot be installed from the Chrome Web Store or imported from extension files. Extension support may be introduced in a future release.

---

## Announcement

Internet Explorative is currently taking a **Mac-first development approach**.

Windows versions are still planned, but the next major release will focus primarily on macOS.

If you are a Windows user who wants to try an alternative browser immediately, you can check out **rinFox**:

https://github.com/travy-patty/rinfox/releases/tag/Release

You may also experiment with running the macOS version through **WSL 2**, although this is not officially supported and may not work reliably.

---

## Setting Up

Internet Explorative is designed to be simple.

After installing a release, there is no account creation or complicated setup process. A welcome screen is planned for a future release, but currently you can simply launch the browser and start browsing.

Internet Explorative does not require:

- An account
- A login
- A subscription
- A sign-up process
- Personal information
- A browsing profile

The project is independently developed and does not have the infrastructure or intention to store users' browsing history.

The default search engine is currently Google, but you can also configure the browser to use **DuckDuckGo**.

---

## System Requirements

### Software

#### macOS

- macOS 10.14 Mojave or later, Catalina recommended

#### Windows

- Windows 10 or later

### Hardware

#### Processor

**Intel**

Any Intel processor supported by the required version of macOS.

Older Intel processors may work if the operating system itself supports them.

**Apple Silicon**

- M1 or later

**Windows**

Any processor capable of running Windows 10 or later should generally be sufficient.

### Memory

- **4 GB minimum, 8 GB recommended**

### Storage

- **700 MB:** Minimum recommended free space, though 1 GB is recommended.

---

# Diagnostics / Build It Yourself

If Internet Explorative does not open correctly, or you want to troubleshoot a problem yourself, this section walks you through running it from source and rebuilding the app.

You only need this section if the pre-built app is not working or you want to diagnose a problem yourself.

## Build Requirements

You will need:

- Python 3.10 or later
- PyQt6
- PyQt6-WebEngine
- Git (recommended)
- PyInstaller (optional)
- The Internet Explorative source code

The main application file is:

    InternetExplorative.py

The project icon is:

    ie_icon.png

---

## 1. Install Python

Download Python from:

https://www.python.org/downloads/

After installing Python, verify that it is available from your terminal.

    python --version

On some systems, you may need to use:

    python3 --version

You should see a Python version number such as:

    Python 3.12.x

---

## 2. Clone the Repository

Using Git, clone the repository:

    git clone https://github.com/DanDevProjects/Internet_Explorative.git

Then enter the project directory:

    cd Internet_Explorative

Alternatively, you can download the repository as a ZIP file directly from GitHub and extract it.

---

## 3. Create a Virtual Environment

Creating a virtual environment is recommended because it keeps the project's Python dependencies separate from the rest of your system.

### macOS / Linux

    python3 -m venv .venv

Activate it:

    source .venv/bin/activate

### Windows

    python -m venv .venv

Activate it:

    .venv\Scripts\activate

Once activated, your terminal should indicate that the `.venv` environment is being used.

---

## 4. Install PyQt6

Upgrade pip first:

    python -m pip install --upgrade pip

Then install the required packages:

    python -m pip install PyQt6 PyQt6-WebEngine

If your system uses `python3`, use:

    python3 -m pip install --upgrade pip

    python3 -m pip install PyQt6 PyQt6-WebEngine

> **Important:** `PyQt6-WebEngine` is required. Internet Explorative uses Qt WebEngine to provide its Chromium-based browser engine.

---

## 5. Run Internet Explorative From Source

Once the dependencies have been installed, you can launch the browser directly from Python.

Run:

    python InternetExplorative.py

Or:

    python3 InternetExplorative.py

If the browser launches successfully, your Python and PyQt6 environment is configured correctly.

Running the browser directly from Python is useful for development and troubleshooting because any errors will normally be visible in the terminal.

---

# Building a Standalone Application

PyInstaller is **optional**.

You only need PyInstaller if you want to package Internet Explorative into a standalone application that can be launched without manually running the Python file.

## 6. Install PyInstaller

Install PyInstaller with:

    python -m pip install pyinstaller

Verify the installation:

    pyinstaller --version

---

## 7. Basic PyInstaller Build

You can create a standalone application with:

    pyinstaller --windowed --name "Internet Explorative" InternetExplorative.py

After the build finishes, PyInstaller will normally create:

    build/

and:

    dist/

The final application will be inside the `dist` directory.

---

# Application Icon

Internet Explorative uses:

    ie_icon.png

PNG is useful for the project's source files and documentation.

However, PyInstaller generally works best with platform-specific application icon formats.

### macOS

macOS applications normally use:

    .icns

You may therefore want to convert:

    ie_icon.png

into:

    ie_icon.icns

Then build using:

    pyinstaller --windowed --name "Internet Explorative" --icon=ie_icon.icns InternetExplorative.py

The resulting application should appear as:

    dist/Internet Explorative.app

### Windows

Windows normally uses:

    .ico

Convert:

    ie_icon.png

into:

    ie_icon.ico

Then build using:

    pyinstaller --windowed --name "Internet Explorative" --icon=ie_icon.ico InternetExplorative.py

The resulting executable should appear as:

    dist\Internet Explorative.exe

> **Note:** You can keep `ie_icon.png` in the repository even if you create `.icns` or `.ico` versions for application packaging.

---

# macOS Build

For macOS, the recommended PyInstaller command is:

    pyinstaller --windowed --name "Internet Explorative" --icon=ie_icon.icns InternetExplorative.py

The resulting application should be located at:

    dist/Internet Explorative.app

If macOS prevents the application from opening, this may be related to application signing, notarization, or Gatekeeper.

You may need to manually allow the application in:

**System Settings → Privacy & Security**

---

# Windows Build

For Windows, use:

    pyinstaller --windowed --name "Internet Explorative" --icon=ie_icon.ico InternetExplorative.py

The executable should appear at:

    dist\Internet Explorative.exe

Windows Defender or SmartScreen may display a warning when running a self-built executable.

This can happen when an application is not digitally signed.

---

# Troubleshooting

If Internet Explorative does not launch, first make sure the required packages are installed:

    python -m pip install --upgrade PyQt6 PyQt6-WebEngine

You can check the installed PyQt6 version with:

    python -m pip show PyQt6

Check PyQt6-WebEngine with:

    python -m pip show PyQt6-WebEngine

Then try launching the source version directly:

    python InternetExplorative.py

If the source version works but the packaged application does not, the problem may be related to PyInstaller, Qt WebEngine resources, application paths, or other bundled files.

### Python Not Found

If your terminal reports that Python cannot be found, make sure Python is installed and available in your system PATH.

You can also try:

    python3 InternetExplorative.py

instead of:

    python InternetExplorative.py

### PyQt6-WebEngine Not Found

If you receive an error related to WebEngine, reinstall the package:

    python -m pip install --upgrade PyQt6-WebEngine

### Application Opens and Immediately Closes

Try running the source version from a terminal:

    python InternetExplorative.py

Running it this way may display an error message that is hidden when launching a packaged application.

---

# Clean a Previous PyInstaller Build

If you have already built the application and want to perform a clean build, remove the previous build files.

### macOS / Linux

    rm -rf build dist

    rm -f *.spec

### Windows PowerShell

    Remove-Item -Recurse -Force build, dist

    Remove-Item *.spec

Then build the application again:

    pyinstaller --windowed --name "Internet Explorative" InternetExplorative.py

---

# Reporting Build Problems

If you encounter a problem while building Internet Explorative, please include as much of the following information as possible:

- Operating system
- Operating system version
- Python version
- PyQt6 version
- PyQt6-WebEngine version
- PyInstaller version
- The command you used
- The complete error message
- Whether `python InternetExplorative.py` works before packaging

This information makes it much easier to determine whether the issue is related to Internet Explorative, Python, PyQt6, Qt WebEngine, Chromium, or PyInstaller.

---

# Contributing

You are welcome to fork this project.

However, there is one important rule:

**You may NOT use my username as part of your fork or project identity.**

If you do not want to create a fork but would like to improve Internet Explorative, you are welcome to contribute changes and add features to the project.

Please see:

`CONTRIBUTING.md`

for more information.

---

# Bugs

If you discover a bug, please report it through the GitHub Discussions page or the project's bug report system.

When reporting a bug, please provide:

- What happened
- What you expected to happen
- Your operating system
- Your Internet Explorative version
- Steps to reproduce the problem
- Screenshots or error messages if available

I will do my best to investigate and fix reported issues.

---

# Known Issues

### Malware / SmartScreen Warnings

When opening the 11.0 versions or the 1.0 versions, macOS or Windows may display security warnings.

Windows may display a Windows SmartScreen warning, while macOS may warn that the application cannot be verified.

> To proceed, you may need to manually allow the application through your operating system's security settings.

### Share Option

The share option is currently unavailable in the newer version.

> This is planned to be fixed in a future release. For now, you may need to manually copy the link.

### Older Releases

If you have trouble opening the older releases, go to:

**System Settings → Privacy & Security → Open Anyway**

This may be necessary because the release is a pre-release build.

For a more stable experience, use **11.1 Build 1102**.

---

# Q&A

### If Chromium 140 is already unsupported by Google, why does Internet Explorative say it is supported?

The Chromium 140 mentioned here refers to the Chromium version included with the available PyQt6-WebEngine package.

This is the latest Chromium version currently available to this project through PyQt6-WebEngine.

### Why won't my app open because my operating system says it may be malware?

Internet Explorative is not intentionally distributed as malware.

Security warnings can occur because self-built or independently distributed applications may not have the same code-signing and notarization credentials as applications distributed through official app stores.

If you downloaded a release, make sure it came from the official Internet Explorative GitHub repository or another trusted source.

### Do I need PyInstaller?

No.

PyInstaller is only required if you want to package the Python source code into a standalone application.

You can run Internet Explorative directly with:

    python InternetExplorative.py

### Do I need Python if I download a pre-built release?

No.

Python is only required when running Internet Explorative from source or building the application yourself.

### Can I install Chrome extensions?

No. Browser extensions are currently **not supported**.

Extensions cannot be installed from the Chrome Web Store or imported from extension files.

Extension support may be considered for a future release.

---

# Thank You

Thank you for checking out **Internet Explorative**!

This project is independently developed and continuously evolving.

I hope you enjoy using it as much as I enjoy building it.

**Thank you, and I hope you like it!**
