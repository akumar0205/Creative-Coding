#!/bin/bash

# Py5 Sketch Runner
# Usage: ./run.sh <sketch_file.py>

# Activate virtual environment
source .venv/bin/activate

# Set Java 17 (required for py5)
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH="$JAVA_HOME/bin:$PATH"

# Run the sketch
python "$@"
