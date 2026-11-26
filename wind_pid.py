import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.linalg import solve_continuous_are

# Rocket numbers (same as before)
T = 30.0
L = 0.4
I = 0.125
mu_c = T * L / I
mu_a = 20.0
delta_max = np.deg2rad(5)


def lqr_gains(q1, q2, r):
    A = np.array([[0.0, 1.0], [mu_a, 0.0]])
    B = np.array([[0.0], [mu_c]])
    P = solve_continuous_are(A, B, np.diag([q1, q2]), np.array([[r]]))
    K = np.linalg.solve(np.array([[r]]), B.T @ P)
    return K[0, 0], K[0, 1]


def simulate(kp, kd, ki, wind, start_tilt=0.0, servo_lag=0.0, t_end=8.0):
    """Engine angle = -(kp * tilt + kd * tilt speed + ki * total tilt so far).
    wind(t) is an extra twisting push from the air, in the same units as mu_a."""
    def rocket(t, state):
        theta, omega, total_tilt, d_actual = state
        d_command = np.clip(-(kp * theta + kd * omega + ki * total_tilt), -delta_max, delta_max)
        if servo_lag > 0:
            d_rate = (d_command - d_actual) / servo_lag
        else:
            d_actual = d_command
            d_rate = 0.0
        return [omega, mu_c * d_actual + mu_a * theta + wind(t), theta, d_rate]

    result = solve_ivp(rocket, [0, t_end], [np.deg2rad(start_tilt), 0.0, 0.0, 0.0], max_step=0.002)
    return result.t, np.rad2deg(result.y[0])


def time_back(t, tilt, limit, after=1.0):
    """How long after the wind starts until the tilt stays within the limit (degrees)."""
    late = t >= after
    if abs(tilt[-1]) > limit:
        return "never"
    outside = np.where(np.abs(tilt[late]) > limit)[0]
    return f"{t[late][outside[-1]] - after:.2f} s" if len(outside) else "0.00 s"


steady_wind = lambda t: 3.0 if t >= 1.0 else 0.0           # a steady crosswind from 1 s onwards
short_gust = lambda t: 6.0 if 1.0 <= t < 1.3 else 0.0      # a 0.3 second shove
no_wind = lambda t: 0.0

controllers = {
    "PD": (1.0, 0.13, 0.0),
    "LQR matched": (*lqr_gains(0.58, 0.01, 1), 0.0),
    "PID Ki=1": (1.0, 0.13, 1.0),
    "PID Ki=3": (1.0, 0.13, 3.0),
}

print("STEADY CROSSWIND from 1 s (the rocket starts upright)")
print(f"{'':14s}{'peak tilt':>11s}{'final lean':>12s}{'back within 0.1 deg':>22s}")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7))
for name, gains in controllers.items():
    t, tilt = simulate(*gains, steady_wind)
    peak = np.max(np.abs(tilt))
    final = np.mean(tilt[t > t[-1] - 0.5])
    print(f"{name:14s}{peak:8.2f} deg{final:9.3f} deg{time_back(t, tilt, 0.1):>22s}")
    ax1.plot(t, tilt, label=name)

print()
print("SHORT GUST (0.3 s shove at 1 s)")
print(f"{'':14s}{'peak tilt':>11s}{'back within 0.05 deg':>23s}")
for name, gains in controllers.items():
    t, tilt = simulate(*gains, short_gust, t_end=6.0)
    print(f"{name:14s}{np.max(np.abs(tilt)):8.2f} deg{time_back(t, tilt, 0.05):>23s}")
    ax2.plot(t, tilt, label=name)

print()
print("THE COST: overshoot when starting from a 1 degree tilt (no wind)")
print(f"{'':14s}{'perfect servo':>15s}{'50 ms servo lag':>17s}")
for name in ["PD", "PID Ki=1", "PID Ki=3"]:
    row = f"{name:14s}"
    for lag in [0.0, 0.05]:
        t, tilt = simulate(*controllers[name], no_wind, start_tilt=1.0, servo_lag=lag, t_end=6.0)
        overshoot = max(0.0, -np.min(tilt)) / tilt[0] * 100
        row += f"{overshoot:13.1f} % " if lag == 0 else f"{overshoot:15.1f} %"
    print(row)

ax1.set_title("Steady crosswind from 1 s: PD and LQR stay leaning, PID recovers")
ax2.set_title("Short gust: every controller recovers")
for ax in (ax1, ax2):
    ax.axvline(1.0, color="grey", linestyle="--", linewidth=1)
    ax.set_ylabel("Tilt angle (deg)")
    ax.grid(True)
    ax.legend()
ax2.set_xlabel("Time (s)")
plt.tight_layout()
plt.savefig("wind_pid.png", dpi=200)
plt.show()