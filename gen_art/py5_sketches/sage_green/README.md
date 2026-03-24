# Sage Green Eyes - Generative Art

A high-resolution generative artwork featuring seven eyes arranged in an asymmetrical pattern on a textured sage green background. Created with py5 (Python mode for Processing).

![Sage Green Eyes](sage_green_full.png)

## Background Technique

The background is created using a multi-layered approach that simulates the appearance of hand-painted paper or a subtly textured wall surface.

### 1. Grid-Based Rendering

The background is rendered at 2x scale (450x450 for a 900x900 canvas) using an offscreen graphics buffer for performance. This allows us to work with smaller dimensions while still achieving smooth results.

```python
S = 2
rw, rh = W // S, H // S
pg = py5.create_graphics(rw, rh)
```

### 2. Subtle Grid Pattern

A very fine grid is overlaid on the background to create the impression of fine paper texture:

- **Grid spacing**: 10 pixels
- **Wiggle effect**: Grid lines have a subtle sine wave distortion (`np.sin(X / 40.0) * 0.3`) to avoid mechanical regularity
- **Line thickness**: 0.4 pixels (extremely thin)
- **Blend intensity**: Lines are only 6-12% different from the base color

This creates an almost subliminal grid pattern that reads as texture rather than geometry.

### 3. Fractal Brownian Motion (FBM) Noise

The grain/texture of the background uses Fractal Brownian Motion, which creates organic, natural-looking noise:

```python
def fbm(x, y, octaves=5, lacunarity=2.0, gain=0.5):
    amp, freq, s, norm = 0.5, 1.0, 0.0, 0.0
    for _ in range(octaves):
        s += amp * py5.noise(x * freq, y * freq)
        norm += amp
        freq *= lacunarity
        amp *= gain
    return s / norm
```

Parameters:
- **Octaves**: 5 layers of noise
- **Lacunarity**: 2.0 (frequency doubles each octave)
- **Gain**: 0.5 (amplitude halves each octave)

This multi-octave approach creates noise with detail at multiple scales, similar to natural textures like stone, paper, or fabric.

### 4. Color Variation

The base sage green color is modulated by the FBM noise:

```python
h = h_base + (grain - 0.5) * 2      # ±2 hue variation
s = np.clip(s_base + (grain - 0.5) * 3, 0, 100)  # ±3 saturation
b = np.clip(b_base + (grain - 0.5) * 5, 0, 100)  # ±5 brightness
```

This creates very subtle tonal variation across the surface.

## Speckle/Spackling Technique

The background features 1200 irregular speckles that blend with the sage green base:

### Overlapping Blob Clusters

Each speckle is not a single circle but a cluster of 5-12 overlapping circles:

```python
n_blobs = np.random.randint(5, 12)
for i in range(n_blobs):
    angle = np.random.uniform(0, np.pi * 2)
    dist = np.random.uniform(0, base_size * 0.7)
    bx = cx + np.cos(angle) * dist
    by = cy + np.sin(angle) * dist
    bsize = base_size * np.random.uniform(0.5, 1.1)
```

This creates irregular, organic shapes rather than perfect circles.

### Color Palette

The speckles use colors very close to the base sage green for blending:
- Slight hue variations (±1-2 degrees)
- Slight saturation variations (±2-3%)
- Slight brightness variations (±3-4%)

### Alpha Blending

Speckles use low alpha values (8-25) with overlapping blobs, creating soft edges that integrate with the background rather than sitting on top of it.

## Eye Technique

### Almond Shape

The eye white is created using a parametric almond shape:

```python
for i in range(n_points):
    t = i / (n_points - 1)
    angle = np.pi * 2 * t
    base_x = np.cos(angle)
    base_y = np.sin(angle)
    
    # Pinch factor for almond shape
    pinch = 1 - 0.15 * abs(base_x)
    
    x = cx + (width/2) * base_x
    y = cy + (height/2) * base_y * pinch
```

The pinch factor reduces the height at the left and right ends, creating the characteristic almond/football shape.

### Pupil Texture

The pupils use pixel-level Perlin noise for organic texture:

1. **Multi-octave noise**: Three layers of noise at different scales
2. **Soft edges**: Noise-based edge variation prevents perfect circles
3. **Color modulation**: Brightness and saturation vary based on noise values
4. **Alpha blending**: Soft fade at the edges

### Radiating Lines

Lines extend from just outside the pupil to near the edge of the eye, following radial angles with slight randomization.

## Overall Composition

- **7 eyes total**: 3 in the left column, 4 in the right column
- **Asymmetrical balance**: The offset columns create visual interest
- **Scale**: 9600x9600 pixels for high-quality large format printing
- **Color palette**: Monochromatic sage greens with muted brick-red accents

## Running the Code

Requirements:
- Python 3.x
- py5 (`pip install py5`)
- numpy

```bash
python sage_green.py
```

Output:
- `sage_green_full.png` - High resolution PNG (9600x9600 pixels)

## License

This generative artwork is provided as-is for personal use and study.
