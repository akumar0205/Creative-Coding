PY5 GENERATIVE ART SETUP — MACOS (APPLE SILICON)

This document contains every step required to:
- Use Homebrew Python (not system Python)
- Install and configure Java 17
- Install py5 inside a virtual environment
- Run sketches reliably
- Debug PATH / JVM / Python issues
- Completely reset everything if needed

This assumes:
- macOS (Apple Silicon)
- zsh shell (default on macOS)
- Homebrew installed


============================================================
FULL MACHINE SETUP (DO THIS ONCE PER LAPTOP)
============================================================

1) Confirm Homebrew is installed

Run:
brew --version
brew --prefix

Expected prefix:
/opt/homebrew

If Homebrew is not installed, install from:
https://brew.sh


2) Install Python 3.11 via Homebrew

Run:
brew install python@3.11

Verify:
ls -la /opt/homebrew/bin/python3.11
/opt/homebrew/bin/python3.11 --version

You should see Python 3.11.x


3) Force macOS to use Homebrew Python (NOT system Python)

Add Homebrew Python to PATH permanently:

echo 'export PATH="/opt/homebrew/opt/python@3.11/libexec/bin:$PATH"' >> ~/.zprofile
echo 'export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH"' >> ~/.zprofile
source ~/.zprofile
hash -r

Verify:
which python
python --version

Expected:
Python 3.11.x
Path should begin with:
/opt/homebrew/opt/python@3.11/libexec/bin/python

If you still see /usr/bin/python3, check:
echo $PATH
which -a python

Homebrew paths must appear BEFORE /usr/bin.


4) Install Java 17 (Temurin recommended for py5)

Run:
brew install --cask temurin@17

Verify Java:
 /usr/libexec/java_home -V
 java -version

You must see version 17.x.


============================================================
PROJECT SETUP (DO THIS ONCE PER PROJECT FOLDER)
============================================================

1) Create project folder

mkdir -p ~/Projects/gen_art/py5_tester
cd ~/Projects/gen_art/py5_tester


2) Create virtual environment

python -m venv .venv
source .venv/bin/activate

Verify:
which python
python --version

Expected:
.../py5_tester/.venv/bin/python
Python 3.11.x

Note:
.venv is hidden. Use:
ls -a
to see it.


3) Install py5 inside the venv

python -m pip install -U pip
pip install py5


4) Set Java 17 (REQUIRED EVERY NEW TERMINAL SESSION)

export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH="$JAVA_HOME/bin:$PATH"

Verify:
echo $JAVA_HOME
java -version
python -c "import py5; print('py5 ok')"

If it prints "py5 ok", setup is complete.


============================================================
DAILY WORKFLOW
============================================================

Every time you open a new terminal:

cd ~/Projects/gen_art/py5_tester
source .venv/bin/activate
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH="$JAVA_HOME/bin:$PATH"
python your_sketch.py

When finished:
deactivate


============================================================
RECOMMENDED FOLDER STRUCTURE
============================================================

py5_tester/
│
├── .venv/
├── SETUP.txt
├── sketches/
│   ├── sketch_001.py
│   ├── sketch_002.py
│
└── exports/

All sketches share the same .venv.


============================================================
DEBUGGING CHECKLIST
============================================================

1) Verify Python

which python
python --version
python -c "import platform; print(platform.machine())"

Must show:
- Inside .venv
- Python 3.11.x
- arm64


2) Verify Java

echo $JAVA_HOME
/usr/libexec/java_home -V
java -version

Must show Java 17.x.


3) If you see:
"py5 is unable to start Java 17 Virtual Machine"

Run:

export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH="$JAVA_HOME/bin:$PATH"
export DYLD_LIBRARY_PATH="$JAVA_HOME/lib:$JAVA_HOME/lib/server:$DYLD_LIBRARY_PATH"
python -c "import py5"


4) If wrong Python is being used

which python
which -a python
echo $PATH

Homebrew Python must appear before /usr/bin.


============================================================
FULL NUCLEAR RESET
============================================================

If everything becomes unstable:

deactivate 2>/dev/null || true
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install py5
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH="$JAVA_HOME/bin:$PATH"
python -c "import py5; print('py5 ok')"

If Java is broken:

brew reinstall --cask temurin@17


============================================================
RULES TO NEVER BREAK
============================================================

- Never install py5 globally
- Never use /usr/bin/python3
- Always use a virtual environment
- Always use Java 17
- One project = one .venv


============================================================
MINIMAL PY5 TEMPLATE
============================================================

import py5

def setup():
    py5.size(600, 600)

def draw():
    py5.background(255)
    py5.circle(300, 300, 200)

py5.run_sketch()

Run:
python sketch.py


============================================================
END OF FILE
============================================================

Happy generating.