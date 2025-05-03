# BGTANK
### Bulk Background Remover
![image](https://github.com/user-attachments/assets/828bf099-4a9c-47c7-99f8-f341b4ebc61e)


## Installation

### Automatic (Recommended)

Download [Setup](https://github.com/verlorengest/BGTANK/releases/download/BGTANK1.0/BGTANK.Setup.exe) and launch.

OR,
Clone the repo,
```bash
python launcher.py
```

This will:
- Create the `.venv` folder
- Install all required packages
- Launch the application

Requires Python 3.7 or higher and internet connection on first run.

---

### Manual

1. Clone the repository:

```bash
git clone https://github.com/verlorengest/bgtank.git
cd bgtank
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Then activate it:

- On Windows:
  ```bash
  .venv\Scripts\activate
  ```

- On macOS/Linux:
  ```bash
  source .venv/bin/activate
  ```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Launch the application:

```bash
python main.py
```

If app doesn't start, try fix.bat
