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


def simulate(k1, k2, tau):
    """tau is the servo lag in seconds. tau = 0 means the engine moves instantly."""
    def rocket(t, state):
        theta, omega, d_actual = state
        d_command = np.clip(-(k1 * theta + k2 * omega), -delta_max, delta_max)
        if tau > 0:
            d_rate = (d_command - d_actual) / tau   # engine chases the command
        else:
            d_actual = d_command                     # engine follows instantly
            d_rate = 0.0
        return [omega, mu_c * d_actual + mu_a * theta, d_rate]

    result = solve_ivp(rocket, [0, 3.0], [np.deg2rad(1), 0.0, 0.0], max_step=0.001)
    theta = result.y[0]
    start_tilt = theta[0]
    overshoot = max(0.0, -np.min(theta)) / start_tilt * 100
    outside = np.where(np.abs(theta) > 0.02 * start_tilt)[0]
    if abs(theta[-1]) > 0.02 * start_tilt:
        settling = "no settle"
    else:
        settling = f"{result.t[outside[-1]]:.2f} s" if len(outside) else "0.00 s"
    return result.t, theta, overshoot, settling


controllers = {
    "PD": (1.0, 0.13),
    "LQR Q=(10,1)": lqr_gains(10, 1, 1),
    "LQR matched": lqr_gains(0.58, 0.01, 1),
}

# Table: overshoot and settling time for different servo lags
for name, (k1, k2) in controllers.items():
    print(name)
    for tau in [0.0, 0.05, 0.10, 0.15]:
        _, _, overshoot, settling = simulate(k1, k2, tau)
        print(f"   lag {tau * 1000:4.0f} ms:  overshoot {overshoot:6.1f} %   settling {settling}")

# Graph: tilt angle with a 100 ms servo lag
plt.figure(figsize=(8, 4))
for name, (k1, k2) in controllers.items():
    t, theta, _, _ = simulate(k1, k2, 0.10)
    plt.plot(t, np.rad2deg(theta), label=name)
plt.xlabel("Time (s)")
plt.ylabel("Tilt angle (deg)")
plt.title("Same rocket, 100 ms servo lag")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("servo_lag.png", dpi=200)
plt.show()