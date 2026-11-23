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
    """Ask LQR for the best gains, given the costs q1, q2 and r."""
    A = np.array([[0.0, 1.0], [mu_a, 0.0]])
    B = np.array([[0.0], [mu_c]])
    Q = np.diag([q1, q2])
    R = np.array([[r]])
    P = solve_continuous_are(A, B, Q, R)
    K = np.linalg.solve(R, B.T @ P)
    return K[0, 0], K[0, 1]


def simulate(k1, k2):
    """Run the rocket with engine tilt = -(k1 * tilt + k2 * tilt speed)."""
    def tilt(theta, omega):
        return np.clip(-(k1 * theta + k2 * omega), -delta_max, delta_max)

    def rocket(t, state):
        theta, omega = state
        return [omega, mu_c * tilt(theta, omega) + mu_a * theta]

    result = solve_ivp(rocket, [0, 2.0], [np.deg2rad(1), 0.0], max_step=0.001)
    theta, omega = result.y
    delta = tilt(theta, omega)

    start_tilt = theta[0]
    overshoot = max(0.0, -np.min(theta)) / start_tilt * 100
    outside = np.where(np.abs(theta) > 0.02 * start_tilt)[0]
    if abs(theta[-1]) > 0.02 * start_tilt:
        settling = "did not settle"
    else:
        settling = f"{result.t[outside[-1]]:.2f} s" if len(outside) else "0.00 s"
    peak = np.max(np.abs(np.rad2deg(delta)))
    return result.t, theta, delta, overshoot, settling, peak


# The controllers to compare: name -> (k1, k2)
controllers = {
    "PD (Kp=1.0, Kd=0.13)": (1.0, 0.13),
    "LQR, Q=(10, 1)": lqr_gains(10, 1, 1),
    "LQR matched, Q=(0.58, 0.01)": lqr_gains(0.58, 0.01, 1),
}

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 6))

print(f"{'Controller':30s} {'Overshoot':>10s} {'Settling':>15s} {'Peak engine':>12s}")
for name, (k1, k2) in controllers.items():
    t, theta, delta, overshoot, settling, peak = simulate(k1, k2)
    print(f"{name:30s} {overshoot:9.1f}% {settling:>15s} {peak:10.2f} deg")
    ax1.plot(t, np.rad2deg(theta), label=name)
    ax2.plot(t, np.rad2deg(delta), label=name)

ax1.set_ylabel("Tilt angle (deg)")
ax1.set_title("PD vs LQR: rocket recovering from a 1 degree tilt")
ax1.legend()
ax1.grid(True)
ax2.set_ylabel("Engine angle (deg)")
ax2.set_xlabel("Time (s)")
ax2.grid(True)
plt.tight_layout()
plt.savefig("comparison.png", dpi=200)
plt.show()