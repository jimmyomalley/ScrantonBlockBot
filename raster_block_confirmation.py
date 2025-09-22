from PIL import Image
import numpy as np
import matplotlib
matplotlib.use("Agg")  # save plots to files
import matplotlib.pyplot as plt
import os

# ---------------- CONFIG ----------------
IMAGE_PATH = "blocks.jpg"   # <-- set your image filename
ROW_INDEX  = 200            # raster line (horizontal slice to analyze)
CROP_HALF_WIDTH = 50        # how many pixels left/right of peak to crop
OUT_DIR    = "raster_outputs_analysis"
# ----------------------------------------

os.makedirs(OUT_DIR, exist_ok=True)

# ---------- Helper Functions ----------
def load_rgb(path):
    """Load image as RGB uint8 NumPy array (H, W, 3)."""
    img = Image.open(path).convert("RGB")
    return np.array(img, dtype=np.uint8)

def yellow_score_line(R_line, G_line, B_line):
    """Yellow score = (R+G)/2 - 0.3*B, clipped."""
    Y = (R_line.astype(float) + G_line.astype(float)) / 2.0 - 0.3 * B_line.astype(float)
    Y = np.clip(Y, 0, 255)
    return Y.astype(np.uint8)

def running_min_max(values):
    """Return min, min_x, max, max_x for a signal array."""
    min_val, max_val = 255, 0
    min_x = max_x = 0
    for x, v in enumerate(values):
        v = int(v)
        if v < min_val:
            min_val, min_x = v, x
        if v > max_val:
            max_val, max_x = v, x
    return min_val, min_x, max_val, max_x

def save_single_plot(x, y, label, line_color, title, out_path):
    """Save a plot for a single color channel."""
    plt.figure(figsize=(10, 4))
    plt.plot(x, y, label=label, color=line_color, linewidth=1.5)
    plt.xlabel("Pixel column (x)")
    plt.ylabel("Intensity (0?255)")
    plt.title(title)
    plt.grid(True, linewidth=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

# -------- Filtering Functions ----------
def low_pass(signal, kernel_size=15):
    """Simple moving average smoothing."""
    kernel = np.ones(kernel_size) / kernel_size
    return np.convolve(signal, kernel, mode='same')

def high_pass(signal, kernel_size=15):
    """High-pass = original ? low-pass."""
    return signal - low_pass(signal, kernel_size)

# -------------- Main -------------------
if __name__ == "__main__":
    # 1) Load image
    rgb = load_rgb(IMAGE_PATH)
    H, W = rgb.shape[:2]
    Image.fromarray(rgb).save(os.path.join(OUT_DIR, "captured_frame_copy.jpg"))

    # 2) Pick raster line
    row = max(0, min(ROW_INDEX, H - 1))
    R = rgb[row, :, 0].astype(float)
    G = rgb[row, :, 1].astype(float)
    B = rgb[row, :, 2].astype(float)
    X = np.arange(W)

    # 3) Yellow score
    Y = yellow_score_line(R, G, B).astype(float)

    # 4) Filtering
    R_lp, G_lp, B_lp, Y_lp = [low_pass(ch) for ch in [R, G, B, Y]]
    R_hp, G_hp, B_hp, Y_hp = [high_pass(ch) for ch in [R, G, B, Y]]

    # 5) Analysis for each channel
    channels = {
        "Red":   (R, R_lp, R_hp, "red"),
        "Green": (G, G_lp, G_hp, "green"),
        "Blue":  (B, B_lp, B_hp, "blue"),
        "Yellow":(Y, Y_lp, Y_hp, "gold")
    }

    print(f"Image: {IMAGE_PATH} | size = {W}x{H} | raster row = {row}")
    print("------ Channel Analysis ------")

    max_values = {}
    peak_positions = {}

    for name, (orig, lp, hp, color) in channels.items():
        c_min, c_xmin, c_max, c_xmax = running_min_max(lp)  # analyze smoothed
        peak_to_peak = c_max - c_min
        max_values[name] = c_max
        peak_positions[name] = c_xmax

        print(f"{name.upper()}: max={c_max:.1f} at x={c_xmax} | "
              f"min={c_min:.1f} at x={c_xmin} | ?={peak_to_peak:.1f}")

        # Save plots
        save_single_plot(X, orig, f"{name} (original)", color,
                         f"{name} Channel ? Original", os.path.join(OUT_DIR, f"{name}_original.png"))
        save_single_plot(X, lp, f"{name} (low-pass)", color,
                         f"{name} Channel ? Low-pass Filtered", os.path.join(OUT_DIR, f"{name}_lowpass.png"))
        save_single_plot(X, hp, f"{name} (high-pass)", color,
                         f"{name} Channel ? High-pass Filtered", os.path.join(OUT_DIR, f"{name}_highpass.png"))
                         

    # 6) Determine dominant color using MAX intensity
    dominant_color = max(max_values, key=max_values.get)
    dominant_value = max_values[dominant_color]
    dominant_x = peak_positions[dominant_color]

    print(f"\n==> Dominant color is {dominant_color} (Max={dominant_value:.1f} at x={dominant_x})")

    # 7) Summary plot with all channels
    plt.figure(figsize=(12, 5))
    plt.plot(X, R_lp, color="red", label="Red (LP)")
    plt.plot(X, G_lp, color="green", label="Green (LP)")
    plt.plot(X, B_lp, color="blue", label="Blue (LP)")
    plt.plot(X, Y_lp, color="gold", label="Yellow (LP)")

    # Highlight dominant peak
    plt.axvline(dominant_x, color="black", linestyle="--", linewidth=1)
    plt.text(dominant_x + 5, dominant_value, f"{dominant_color} Peak",
             color="black", fontsize=10, weight="bold")

    plt.xlabel("Pixel column (x)")
    plt.ylabel("Intensity (0?255)")
    plt.title(f"Raster line (row {row}) ? All Channels\nDominant = {dominant_color}")
    plt.legend()
    plt.grid(True, linewidth=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "summary_all_channels.png"), dpi=150)
    plt.close()

    # 8) Crop image around dominant block
    crop_left = max(0, dominant_x - CROP_HALF_WIDTH)
    crop_right = min(W, dominant_x + CROP_HALF_WIDTH)
    cropped_img = rgb[:, crop_left:crop_right, :]
    Image.fromarray(cropped_img.astype(np.uint8)).save(
        os.path.join(OUT_DIR, "dominant_block_crop.jpg")
    )

    print(f"[OK] Saved plots, summary, and cropped dominant block to: {os.path.abspath(OUT_DIR)}")
