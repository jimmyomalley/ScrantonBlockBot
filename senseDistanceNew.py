from PIL import Image
import numpy as np
import matplotlib
matplotlib.use("Agg")  # save plots to files
import matplotlib.pyplot as plt
import os

# ---------------- CONFIG ----------------
IMAGE_PATH = "blocks.jpg"   # <-- set your image filename
ROW_INDEX = 200             # raster line (horizontal slice)
OUT_DIR = "raster_outputs_filtered"
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
    """Scan left→right; return (min_val, min_x, max_val, max_x)."""
    min_val, max_val = 255, 0
    min_x = max_x = 0
    for x, v in enumerate(values):
        v = int(v)
        if v < min_val:
            min_val, min_x = v, x
        if v > max_val:
            max_val, max_x = v, x
    return min_val, min_x, max_val, max_x


def save_plot(x, y_arrays, labels, title, out_path):
    plt.figure(figsize=(10, 4))
    for y, lab in zip(y_arrays, labels):
        plt.plot(x, y, label=lab, linewidth=1.5)
    plt.xlabel("Pixel column (x)")
    plt.ylabel("Intensity (0–255)")
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
    return np.convolve(signal, kernel, mode="same")


def high_pass(signal, kernel_size=15):
    """High-pass = original − low-pass."""
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

    # 5) Peak detection (on low-pass for stability)
    R_min, R_xmin, R_max, R_xmax = running_min_max(R_lp)
    G_min, G_xmin, G_max, G_xmax = running_min_max(G_lp)
    B_min, B_xmin, B_max, B_xmax = running_min_max(B_lp)
    Y_min, Y_xmin, Y_max, Y_xmax = running_min_max(Y_lp)

    # 6) Determine dominant peak
    max_values = {
        "Red": R_max,
        "Green": G_max,
        "Blue": B_max,
        "Yellow": Y_max,
    }
    dominant_color = max(max_values, key=max_values.get)
    dominant_value = max_values[dominant_color]

    # 7) Console feedback
    print(f"Image: {IMAGE_PATH} | size = {W}x{H} | raster row = {row}")
    print(f"RED:   max={R_max:.1f} at x={R_xmax}")
    print(f"GREEN: max={G_max:.1f} at x={G_xmax}")
    print(f"BLUE:  max={B_max:.1f} at x={B_xmax}")
    print(f"YELL.: max={Y_max:.1f} at x={Y_xmax}")
    print(f"==> Dominant peak is {dominant_color} with value {dominant_value:.1f}")

    # 8) Save plots
    save_plot(
        X,
        [R, G, B],
        ["Red", "Green", "Blue"],
        f"Raster line (row {row}) — Original RGB",
        os.path.join(OUT_DIR, "rgb_original.png"),
    )

    save_plot(
        X,
        [R_lp, G_lp, B_lp, Y_lp],
        ["Red_LP", "Green_LP", "Blue_LP", "Yellow_LP"],
        f"Raster line (row {row}) — Low-pass filtered",
        os.path.join(OUT_DIR, "rgb_lowpass.png"),
    )

    save_plot(
        X,
        [R_hp, G_hp, B_hp, Y_hp],
        ["Red_HP", "Green_HP", "Blue_HP", "Yellow_HP"],
        f"Raster line (row {row}) — High-pass filtered",
        os.path.join(OUT_DIR, "rgb_highpass.png"),
    )

    print("[OK] Saved filtered plots to:", os.path.abspath(OUT_DIR))
