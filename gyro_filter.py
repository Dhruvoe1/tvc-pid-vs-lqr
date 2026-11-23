import numpy as np
import matplotlib.pyplot as plt
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


def simulate(k1, k2, noise_dps, servo_lag, filter_time, seed=0):
    """Fixed time steps. The gyro reading is smoothed by a filter before the
    controller uses it. filter_time = 0 means no filter."""
    rng = np.random.default_rng(seed)
    dt = 0.002
    steps = int(4.0 / dt)
    theta, omega = np.deg2rad(1), 0.0
    d_actual, omega_filtered = 0.0, 0.0
    noise = np.deg2rad(noise_dps)
    t = np.arange(steps) * dt
    tilt = np.zeros(steps)
    engine = np.zeros(steps)
    for i in range(steps):
        omega_measured = omega + rng.normal(0.0, noise)
        if filter_time > 0:
            omega_filtered += (omega_measured - omega_filtered) / filter_time * dt
        else:
            omega_filtered = omega_measured
        d_command = np.clip(-(k1 * theta + k2 * omega_filtered), -delta_max, delta_max)
        if servo_lag > 0:
            d_actual += (d_command - d_actual) / servo_lag * dt
        else:
            d_actual = d_command
        omega += (mu_c * d_actual + mu_a * theta) * dt
        theta += omega * dt
        tilt[i] = theta
        engine[i] = d_actual
    return t, np.rad2deg(tilt), np.rad2deg(engine)


def judge(k1, k2, servo_lag, filter_time):
    """Overshoot with a perfect gyro, and engine jitter with 5 deg/s of gyro noise."""
    t, tilt, _ = simulate(k1, k2, 0, servo_lag, filter_time)
    overshoot = max(0.0, -np.min(tilt)) / tilt[0] * 100
    settled = abs(tilt[-1]) < 0.02 * tilt[0]
    jitter = np.mean([np.std(simulate(k1, k2, 5, servo_lag, filter_time, s)[2][t > 2.0])
                      for s in range(10)])
    return overshoot, settled, jitter


controllers = {
    "PD": (1.0, 0.13),
    "LQR Q=(10,1)": lqr_gains(10, 1, 1),
    "LQR matched": lqr_gains(0.58, 0.01, 1),
}

print("5 deg/s gyro noise. Jitter = how much the engine twitches (degrees).")
for name, (k1, k2) in controllers.items():
    print(name)
    for servo_lag in [0.0, 0.03]:
        for filter_time in [0.0, 0.01, 0.02]:
            overshoot, settled, jitter = judge(k1, k2, servo_lag, filter_time)
            status = "settles" if settled else "WOBBLES"
            print(f"   servo {servo_lag * 1000:3.0f} ms, filter {filter_time * 1000:3.0f} ms:"
                  f"  overshoot {overshoot:5.1f} %  jitter {jitter:5.2f}  {status}")

# Graph: the heavily damped LQR with a 30 ms servo, at three filter settings
plt.figure(figsize=(8, 4))
k1, k2 = controllers["LQR Q=(10,1)"]
for filter_time in [0.0, 0.01, 0.02]:
    t, tilt, _ = simulate(k1, k2, 0, 0.03, filter_time)
    plt.plot(t, tilt, label=f"filter {filter_time * 1000:.0f} ms")
plt.xlabel("Time (s)")
plt.ylabel("Tilt angle (deg)")
plt.title("LQR Q=(10,1), 30 ms servo lag, perfect gyro")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("gyro_filter.png", dpi=200)
plt.show()