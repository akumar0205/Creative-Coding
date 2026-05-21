#!/bin/bash

# Create New Py5 Sketch
# Usage: ./new_sketch.sh <sketch_name>

if [ -z "$1" ]; then
    echo "Usage: ./new_sketch.sh <sketch_name>"
    echo "Example: ./new_sketch.sh my_artwork"
    exit 1
fi

SKETCH_NAME="$1"
SKETCH_DIR="$SKETCH_NAME"
SKETCH_FILE="$SKETCH_DIR/$SKETCH_NAME.py"

# Create sketch directory
mkdir -p "$SKETCH_DIR"

# Create sketch file with template
cat > "$SKETCH_FILE" << 'EOF'
import py5
import numpy as np

# Canvas dimensions
W, H = 900, 900

# Output files
PNG_FILE = "output.png"
SVG_FILE = "output.svg"

# Color palette (HSB: Hue, Saturation, Brightness)
PAPER_PALETTE = [
    (208, 28, 72),
    (204, 34, 66),
]

# Geometry
CX, CY = W / 2, H / 2
R = 75

# Random seeds for reproducibility
BG_SEED = 12345
LINE_SEED = 54321
NOISE_SEED = 11111

def setup():
    py5.size(W, H)
    py5.color_mode(py5.HSB, 360, 100, 100, 100)
    py5.no_loop()
    
    # Draw your artwork here
    py5.background(255)
    
    # Save outputs
    py5.save(PNG_FILE)
    print(f"Saved {PNG_FILE}")

py5.run_sketch()
EOF

echo "Created sketch: $SKETCH_FILE"
echo "Run it with: ./run.sh $SKETCH_FILE"
