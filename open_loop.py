import numpy as np 
import matplotlib.pyplot as plt 
from scipy.integrate import solve_ivp 

# Rocket numbers (illustrative) 
T = 30.0         # thrust, newtons 
L = 0.4          # distance from the centre of mass to nozzle, metres
I = 0.125        # how hard the rocket is to spin, kg m^2
mu_c = T * L / I # how strongly the engine tilt twists the rocket
mu_a = 20.0      # how strongly the air pushes the nose over 

def rocket(t, state): 
    theta, omega = state          # tilt angle and how fast its changing 
    delta = 0.0                   # engine tilt: no control yet
    alpha = mu_c * delta + mu_a * theta 
    return [omega, alpha] 

start = [np.deg2rad(1), 0.0]      # 1 degree tilt, not spinning 
result = solve_ivp(rocket, [0, 1.0], start, max_step=0.001)

plt.plot(result.t, np.rad2deg(result.y[0]))
plt.xlabel("Time (s)")
plt.ylabel("Tilt angle (degrees)")
plt.title("rocket with no control: tipping over") 
plt.grid(True)
plt.show()
