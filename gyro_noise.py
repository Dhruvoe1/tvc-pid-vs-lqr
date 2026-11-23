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


def simulate(k1, k2, noise_dps, seed=0):
    """Fixed time steps, because the random noise changes at every step.
    noise_dps is the gyro noise in degrees per second."""
    rng = np.random.default_rng(seed)
    dt = 0.002
    steps = int(4.0 / dt)
    theta, omega = np.deg2rad(1), 0.0
    noise = np.deg2rad(noise_dps)
    t = np.arange(steps) * dt
    tilt = np.zeros(steps)
    engine = np.zeros(steps)
    for i in range(steps):
        omega_measured = omega + rng.normal(0.0, noise)    # the gyro is not perfect
        delta = np.clip(-(k1 * theta + k2 * omega_measured), -delta_max, delta_max)
        alpha = mu_c * delta + mu_a * theta
        omega += alpha * dt
        theta += omega * dt
        tilt[i] = theta
        engine[i] = delta
    return t, np.rad2deg(tilt), np.rad2deg(engine)


controllers = {
    "PD": (1.0, 0.13),
    "LQR Q=(10,1)": lqr_gains(10, 1, 1),
    "LQR matched": lqr_gains(0.58, 0.01, 1),
}

# Table: how much does the engine jitter once the rocket has settled (after 2 s)?
print("Engine jitter (degrees, average of 10 runs) after the rocket has settled")
print(f"{'Gyro noise':>12s}" + "".join(f"{name:>16s}" for name in controllers))
for noise_dps in [0, 1, 5, 10]:
    row = f"{noise_dps:>8d} deg/s"
    for name, (k1, k2) in controllers.items():
        jitter = []
        for seed in range(10):
            t, tilt, engine = simulate(k1, k2, noise_dps, seed)
            jitter.append(np.std(engine[t > 2.0]))
        row += f"{np.mean(jitter):16.2f}"
    print(row)

# Graph: engine angle with 5 deg/s of gyro noise
fig, axes = plt.subplots(3, 1, sharex=True, sharey=True, figsize=(8, 7))
for ax, (name, (k1, k2)) in zip(axes, controllers.items()):
    t, tilt, engine = simulate(k1, k2, 5)
    ax.plot(t, engine)
    ax.set_ylabel("Engine (deg)")
    ax.set_title(name, fontsize=10)
    ax.grid(True)
axes[-1].set_xlabel("Time (s)")
fig.suptitle("Engine movement with 5 deg/s of gyro noise")
plt.tight_layout()
plt.savefig("gyro_noise.png", dpi=200)
plt.show()