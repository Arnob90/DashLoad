# [Dashload] - Download Manager

**⚠️ Status: Pre-Alpha / In-Development ⚠️**

**This project is currently in a very early stage of development (pre-alpha). Expect bugs, incomplete features, and frequent breaking changes. It is primarily intended for developers interested in contributing or experimenting.**

A modern, multi-segmented download manager built with React (Electron) for the frontend and Python for the backend.

## ✨ Features

- **Multi-segmented Downloads:** Utilizes multiple connections for potentially faster downloads (powered by `pypdl`).
- **Cross-Platform:** Built with Electron and Python, aiming for compatibility across major OSes (Windows, macOS, Linux).
- **Modern UI:** React-based interface for a clean user experience.
- **Open Source:** This project is open source and available on GitHub for anyone to contribute.

## 💻 Tech Stack

- **Frontend:** React, Electron, Tailwind, light SCSS/CSS for advanced features
- **Backend:** Python 3.13.3
- **Core Download Logic:** [pypdl](https://github.com/matthewg/pypdl) library
- **Inter-Process Communication (IPC):** Electron IPC

## 🚀 Getting Started (Development)

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- [Node.js](https://nodejs.org/) (includes npm)
- [Python](https://www.python.org/) (Version 3.8+ recommended)
- [pip](https://pip.pypa.io/en/stable/installation/) (Python package installer)
- [Git](https://git-scm.com/)

### Installation & Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Arnob90/DashLoad.git
   cd DashLoad
   ```

2. **Set up the Python Backend:**

   - Navigate to the backend directory (./src/backend/)
   - Activate the virtual environment

     ```bash
     source ./venv/bin/activate.sh
     ```

   - Install Python dependencies:

     ```bash
     pip install -r requirements.txt
     ```

3. **Set up the React Frontend:**

   - Install Node.js dependencies:

     ```bash
     npm install
     ```

### Running the Application

- Make sure you are in the root directory.
- Give the backend run script permissions

  ```bash
  chmod +x ./src/backend/start-backend.fish
  ```

- Run the development script:

  ```bash
  # Using npm
  npm run dev
  ```

- To only start the frontend

```bash
npm run start
```

- To only start the backend

```bash
npm run start:backend
```

- This should compile the React code and launch the Electron application.

### Contributing

- Abide by common sense(don't try to push malware lmao)
- Follow conventions in source
- Try to type as much as possible. Prefer typescript over JS and typed python. No duck typing please unless you absolutely have to.
- Keep PRs focused and readable.
- Please use the issue tracker to report bugs and feature requests. (Testing is very appreciated)
- Feel free to fork if you feel like your PR will do much good.
- Please be nice.

### Roadmap

- [x] Core download logic
- [x] Multi-segmented downloads
- [ ] Performance optimization(maybe move away from electron/python)
- [ ] Bug free and stable
- [ ] Torrenting
- [ ] Extensibility
- [ ] Add tests
