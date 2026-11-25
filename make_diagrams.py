import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch, FancyBboxPatch, Circle, Arc

BODY = "#dfe6ee"
EDGE = "#34495e"
BLUE = "#2874a6"
RED = "#c0392b"
GREEN = "#1e8449"
ORANGE = "#e67e22"
GREY = "#7f8c8d"


def to_global(points, theta_deg, origin=(0.0, 0.0)):
    """Rocket coordinates (s along the rocket, n to its right) -> page coordinates."""
    th = np.deg2rad(theta_deg)
    out = []
    for s, n in points:
        x = s * np.sin(th) + n * np.cos(th)
        y = s * np.cos(th) - n * np.sin(th)
        out.append((origin[0] + x, origin[1] + y))
    return out


def poly(ax, points, theta, origin, color=BODY, z=2):
    ax.add_patch(Polygon(to_global(points, theta, origin), closed=True,
                         facecolor=color, edgecolor=EDGE, linewidth=1.6, zorder=z))


def draw_rocket(ax, theta, origin, fins=False, nozzle_tilt=0.0):
    poly(ax, [(-2, -0.28), (1.6, -0.28), (1.6, 0.28), (-2, 0.28)], theta, origin)
    poly(ax, [(1.6, -0.28), (2.5, 0), (1.6, 0.28)], theta, origin)
    if fins:
        poly(ax, [(-0.9, -0.28), (-2.0, -0.28), (-2.3, -1.0)], theta, origin, color="#aab7c4")
        poly(ax, [(-0.9, 0.28), (-2.0, 0.28), (-2.3, 1.0)], theta, origin, color="#aab7c4")
    # engine nozzle, hinged at the bottom of the rocket
    pivot = np.array([-2.0, 0.0])
    t = np.deg2rad(nozzle_tilt)
    def rot(p):
        d = np.array(p) - pivot
        return (pivot[0] + d[0] * np.cos(t) - d[1] * np.sin(t),
                pivot[1] + d[0] * np.sin(t) + d[1] * np.cos(t))
    bell = [rot(p) for p in [(-2.0, -0.15), (-2.0, 0.15), (-2.55, 0.32), (-2.55, -0.32)]]
    poly(ax, bell, theta, origin, color="#8e9aa6")


def arrow(ax, start, end, color, lw=3, style="-|>", mut=18, z=5):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=mut,
                                 color=color, linewidth=lw, zorder=z))


def dot(ax, xy, color, label, offset, ha="left"):
    ax.add_patch(Circle(xy, 0.14, facecolor=color, edgecolor="white", linewidth=1.5, zorder=6))
    ax.text(xy[0] + offset[0], xy[1] + offset[1], label, color=color, fontsize=11,
            fontweight="bold", ha=ha, va="center", zorder=6)


# ------------------------------------------------------------------ diagram 1
def diagram_stability():
    fig, axes = plt.subplots(1, 2, figsize=(11, 6.4))
    theta = 14
    cases = [
        (axes[0], True, -0.95, "WITH FINS: stable", GREEN,
         "The air pushes the tail sideways,\nswinging the nose back toward straight up."),
        (axes[1], False, 0.95, "NO FINS: unstable", RED,
         "The air pushes the nose further over,\nso the tilt grows faster and faster."),
    ]
    for ax, fins, s_cp, title, color, caption in cases:
        ax.set_aspect("equal")
        ax.set_xlim(-3.6, 3.6)
        ax.set_ylim(-4.6, 4.2)
        ax.axis("off")
        ax.plot([0, 0], [-3.4, 3.6], linestyle="--", color=GREY, linewidth=1.4, zorder=1)
        ax.text(0.12, 3.55, "straight up", color=GREY, fontsize=10, va="top")
        draw_rocket(ax, theta, (0, 0), fins=fins)
        cop = to_global([(s_cp, 0)], theta)[0]
        nhat = np.array([np.cos(np.deg2rad(theta)), -np.sin(np.deg2rad(theta))])
        arrow(ax, cop, cop + 1.6 * nhat, RED, lw=3.5)
        ax.text(cop[0] + 1.7 * nhat[0], cop[1] + 1.7 * nhat[1] + 0.3, "air push",
                color=RED, fontsize=11, fontweight="bold", ha="center")
        dot(ax, cop, RED, "", (0, 0))
        dot(ax, (0, 0), BLUE, "", (0, 0))
        ax.text(-0.35, 0.05, "centre of mass\n(balance point)", color=BLUE, fontsize=10.5,
                fontweight="bold", ha="right", va="center")
        ax.text(-0.75, cop[1],
                "centre of pressure\n(where the air pushes)", color=RED, fontsize=10.5,
                fontweight="bold", ha="right", va="center")
        ax.set_title(title, color=color, fontsize=15, fontweight="bold", pad=6)
        ax.text(0, -4.35, caption, ha="center", va="center", fontsize=11.5, color="#222")
    fig.suptitle("Why a rocket with no fins tips over", fontsize=17, fontweight="bold")
    plt.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig("diagram_stability.png", dpi=200, facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ diagram 2
def diagram_engine_tilt():
    fig, ax = plt.subplots(figsize=(10, 7.4))
    ax.set_aspect("equal")
    ax.set_xlim(-6.4, 4.6)
    ax.set_ylim(-5.6, 5.0)
    ax.axis("off")
    delta = 22   # exaggerated so it is easy to see
    # the engine is tilted so its exhaust goes down and to the right
    draw_rocket(ax, 0, (0, 0), nozzle_tilt=-delta)
    pivot = np.array([0.0, -2.0])
    t = np.deg2rad(delta)
    up_left = np.array([-np.sin(t), np.cos(t)])     # direction the engine pushes the rocket

    # dashed line: where the engine would point if it were not tilted
    ax.plot([0, 0], [-2.0, -4.9], linestyle="--", color=GREY, linewidth=1.3, zorder=1)
    ax.text(-0.15, -4.85, "engine untilted", color=GREY, fontsize=9.5, ha="right", va="center")

    # thrust arrow drawn below the engine, pushing up along the engine axis
    start_pt = pivot - 3.0 * up_left
    arrow(ax, start_pt, pivot - 0.45 * up_left, ORANGE, lw=4.5, mut=22)
    ax.text(start_pt[0] + 0.3, start_pt[1] - 0.1, "thrust (T)", color=ORANGE, fontsize=12.5,
            fontweight="bold", va="center")

    # tilt angle delta
    ax.add_patch(Arc(pivot, 2.4, 2.4, theta1=-90, theta2=-90 + delta, color=ORANGE, linewidth=2.2))
    ax.text(-0.3, -3.35, "δ", color=ORANGE, fontsize=17, fontweight="bold", ha="center", va="center")

    # sideways part of the thrust, acting on the bottom of the rocket
    side = 3.0 * np.sin(t)
    arrow(ax, tuple(pivot), (pivot[0] - side, pivot[1]), RED, lw=4, mut=22)
    ax.text(pivot[0] - side - 0.15, pivot[1] + 0.05, "sideways push\nT × sin(δ)", color=RED,
            fontsize=12, fontweight="bold", ha="right", va="center")

    # centre of mass and lever arm
    dot(ax, (0, 0), BLUE, "", (0, 0))
    ax.text(0.45, 0.35, "centre of mass", color=BLUE, fontsize=11.5, fontweight="bold", va="center")
    ax.annotate("", xy=(1.55, -2.0), xytext=(1.55, 0.0),
                arrowprops=dict(arrowstyle="<->", color=EDGE, linewidth=1.8))
    ax.text(1.75, -1.0, "L\n(lever arm)", color=EDGE, fontsize=12, fontweight="bold", va="center")

    # the result: the rocket twists, nose to the right
    ax.add_patch(FancyArrowPatch((-1.5, 3.1), (1.5, 3.1), connectionstyle="arc3,rad=-0.55",
                                 arrowstyle="-|>", mutation_scale=24, color=GREEN, linewidth=4, zorder=5))
    ax.text(0.0, 4.55, "the nose swings this way", color=GREEN, fontsize=12.5,
            fontweight="bold", ha="center")

    # explanation
    ax.text(-6.2, 2.0,
            "1. The engine tilts by a small\n    angle δ (a few degrees in\n    real rockets).\n\n"
            "2. Part of the thrust now pushes\n    the tail sideways.\n\n"
            "3. That push is far from the\n    centre of mass, so it twists\n    the whole rocket.",
            fontsize=11.5, va="center", ha="left", color="#222", linespacing=1.15)
    ax.text(-6.2, -3.55, "Twisting effect (torque) = T × L × sin(δ)\n≈ T × L × δ for small angles\n"
            "(δ is exaggerated for clarity)",
            fontsize=11.5, color=EDGE, va="center", linespacing=1.3)
    ax.set_title("How tilting the engine steers the rocket", fontsize=17, fontweight="bold")
    fig.savefig("diagram_engine_tilt.png", dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------ diagram 3
def box(ax, xy, w, h, text, color, sub=None, edge=EDGE):
    x, y = xy
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                facecolor=color, edgecolor=edge, linewidth=2, zorder=3))
    ax.text(x, y + (0.16 if sub else 0), text, ha="center", va="center", fontsize=12.5,
            fontweight="bold", zorder=4)
    if sub:
        ax.text(x, y - 0.3, sub, ha="center", va="center", fontsize=10, color="#333", zorder=4)


def diagram_feedback_loop():
    fig, ax = plt.subplots(figsize=(11.5, 6.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.8, 6.6)
    ax.axis("off")
    plain = "#eaf1f8"
    flag = "#fdebd0"
    # top row: controller -> servo -> rocket
    box(ax, (2.0, 4.6), 2.8, 1.5, "Controller", plain, "decides the\nengine angle")
    box(ax, (6.0, 4.6), 2.8, 1.5, "Servo + gimbal", flag, "moves the engine\n(limit: 5 degrees)", edge=ORANGE)
    box(ax, (10.0, 4.6), 2.8, 1.5, "Rocket", plain, "tilts and turns")
    # bottom row: gyroscope -> filter -> controller
    box(ax, (10.0, 1.6), 2.8, 1.5, "Sensors", flag, "gyroscope: measures\nhow fast it turns", edge=ORANGE)
    box(ax, (6.0, 1.6), 2.8, 1.5, "Filter (optional)", flag, "smooths the readings", edge=ORANGE)
    arrow(ax, (3.45, 4.6), (4.55, 4.6), EDGE, lw=2.5)
    arrow(ax, (7.45, 4.6), (8.55, 4.6), EDGE, lw=2.5)
    arrow(ax, (10.0, 3.8), (10.0, 2.4), EDGE, lw=2.5)
    arrow(ax, (8.55, 1.6), (7.45, 1.6), EDGE, lw=2.5)
    arrow(ax, (4.55, 1.6), (2.0, 1.6), EDGE, lw=2.5, style="-")
    arrow(ax, (2.0, 1.6), (2.0, 3.8), EDGE, lw=2.5)
    ax.text(2.0, 2.7, "feedback", fontsize=11, color=EDGE, fontweight="bold", ha="center",
            bbox=dict(facecolor="white", edgecolor="none", pad=2))
    # imperfection tags
    tags = [
        ((6.0, 6.05), "Experiment 1: SERVO LAG\nthe engine arrives late", ORANGE),
        ((10.0, 0.2), "Experiment 2: GYRO NOISE\nthe readings jitter randomly", ORANGE),
        ((6.0, 0.2), "Experiment 3: FILTER\nsmooths jitter but adds delay", ORANGE),
    ]
    for (x, y), text, c in tags:
        ax.text(x, y, text, ha="center", va="center", fontsize=10.5, color=c, fontweight="bold")
    # rule
    ax.text(2.0, 6.05, "engine angle = −(K1 × tilt + K2 × tilt speed)", ha="center",
            fontsize=10.5, color=EDGE, fontweight="bold")
    ax.text(6.0, -0.55, "In this project the tilt angle itself is assumed to be measured perfectly; only the gyroscope is noisy.",
            ha="center", fontsize=10, color=GREY, style="italic")
    ax.set_title("The feedback loop: measure, decide, act, repeat", fontsize=17, fontweight="bold")
    fig.savefig("diagram_feedback_loop.png", dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------ diagram 4
def diagram_tradeoff():
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))
    names = ["PD", "LQR\nheavy damping", "LQR\nmatched"]
    colors = ["#2874a6", "#e67e22", "#1e8449"]
    over = [48.2, 0.0, 17.0]
    jitter = [0.66, 3.71, 0.89]
    for ax, vals, title, ylabel, fmt in [
        (axes[0], over, "Slow motor (100 ms lag)", "Overshoot (%)  lower is better", "{:.1f} %"),
        (axes[1], jitter, "Noisy sensor (5 deg/s)", "Engine twitching (degrees)  lower is better", "{:.2f}"),
    ]:
        bars = ax.bar(names, vals, color=colors, width=0.6)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + max(vals) * 0.02, fmt.format(v),
                    ha="center", va="bottom", fontsize=12, fontweight="bold")
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=10.5)
        ax.set_ylim(0, max(vals) * 1.18)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("No controller wins both tests: the ranking flips", fontsize=16, fontweight="bold")
    plt.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig("diagram_tradeoff.png", dpi=200, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    diagram_stability()
    diagram_engine_tilt()
    diagram_feedback_loop()
    diagram_tradeoff()
    print("Saved: diagram_stability.png, diagram_engine_tilt.png, "
          "diagram_feedback_loop.png, diagram_tradeoff.png")