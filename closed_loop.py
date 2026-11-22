import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Rocket numbers (illustrative)
T = 30.0
L = 0.4
I = 0.125
mu_c = T * L / I
mu_a = 20.0
delta_max = np.deg2rad(5)    # the engine can tilt 5 degrees at most

# Controller settings: change these and re-run to see what happens
Kp = 1.0      # reacts to how far the rocket is tilted
Kd = 0.13     # reacts to how fast the tilt is changing

def engine_tilt(theta, omega):
    delta = -(Kp * theta + Kd * omega)
    return np.clip(delta, -delta_max, delta_max)

def rocket(t, state):
    theta, omega = state
    delta = engine_tilt(theta, omega)
    alpha = mu_c * delta + mu_a * theta
    return [omega, alpha]

start = [np.deg2rad(1), 0.0]
result = solve_ivp(rocket, [0, 2.0], start, max_step=0.001)

theta = result.y[0]
omega = result.y[1]
delta = engine_tilt(theta, omega)

# Two graphs, one above the other
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
ax1.plot(result.t, np.rad2deg(theta))
ax1.set_ylabel("Tilt angle (deg)")
ax1.grid(True)
ax2.plot(result.t, np.rad2deg(delta))
ax2.set_ylabel("Engine angle (deg)")
ax2.set_xlabel("Time (s)")
ax2.grid(True)
plt.show()