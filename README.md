# Gimbaled rocket attitude control: PD vs LQR in Python

A first-year aerospace engineering project (Nov 2026). It simulates a small finless rocket that keeps itself upright by tilting its engine, designs two controllers (PD and LQR), and tests how each one copes with imperfect hardware: a slow servo, a noisy gyroscope, and a filter on the gyro signal.

![PD vs LQR with a 100 ms servo lag](servo_lag.png)

*Same rocket, same 1 degree starting tilt, 100 ms servo lag. Blue: PD. Orange: LQR with heavy damping. Green: LQR tuned to use the same engine effort as PD.*

## The short version

No controller won every test. The one that handled a slow servo best handled sensor noise worst, and the reverse. Adding a noise filter helped only when nothing else in the loop was already adding lag.

## What I found

| Test | PD | LQR, heavy damping | LQR, matched to PD |
|---|---|---|---|
| Ideal conditions (overshoot, settling time) | 4.0 %, 0.68 s | 0.0 %, 1.25 s | 0.0 %, 0.63 s |
| 100 ms servo lag | 48 % overshoot, not settled after 3 s | 0.0 %, 1.21 s | 17 %, 1.63 s |
| 150 ms servo lag | 186 % overshoot, growing | 0.3 %, 1.36 s | 42 %, not settled |
| Engine jitter, 5 deg/s gyro noise | 0.66 deg | 3.71 deg | 0.89 deg |

1. **Matched on engine effort, PD and LQR performed almost the same** in ideal conditions (0.68 s against 0.63 s). My first LQR looked slow only because of the weights I chose.
2. **Speed and robustness trade off.** With servo lag, the fastest-tuned controller (PD) went wrong first, and the heavily damped LQR barely noticed.
3. **Noise reverses the ranking.** The heavily damped LQR uses about 8 times the gain on tilt speed, so it amplifies gyro noise about 8 times more, and its engine command repeatedly hits the 5 degree limit.
4. **A gyro filter is not free.** With a perfect servo, a 20 ms filter cut PD jitter from 0.66 to 0.16 degrees. With a 30 ms servo already in the loop, the same filter added almost nothing for PD, and pushed the heavy LQR into a sustained oscillation (tilt within about 0.2 degrees, but the engine swinging almost 4 degrees).

## The model

A two-state, small-angle model of pitch motion:

    tilt acceleration = mu_c * engine angle + mu_a * tilt angle

- `mu_c = T * L / I` is how strongly the engine twists the rocket (thrust 30 N, lever arm 0.4 m, moment of inertia 0.125 kg m^2, giving 96 per s^2).
- `mu_a = 20 per s^2` is the destabilising push from the air on a finless body (centre of pressure ahead of the centre of mass).
- The engine can tilt at most 5 degrees. Every run starts with a 1 degree tilt.

The parameters are illustrative, not a real vehicle.

## The controllers

- **PD:** engine angle = -(Kp * tilt + Kd * tilt speed), with Kp = 1.0 and Kd = 0.13 (damping ratio about 0.7).
- **LQR:** gains from the algebraic Riccati equation, with cost weights Q on tilt and tilt speed and R on engine use. "Heavy damping" uses Q = diag(10, 1). "Matched" uses Q = diag(0.58, 0.01), chosen so its peak engine angle is the same 1.0 degree as PD, which makes the comparison fair.

## Imperfections tested

- **Servo lag:** the engine chases the commanded angle with a first-order time constant of 0 to 150 ms.
- **Gyro noise:** Gaussian noise added to the measured tilt speed (0 to 10 deg/s), averaged over 10 runs with fixed random seeds.
- **Gyro filter:** a first-order low-pass filter on the gyro reading (10 and 20 ms).

## Limitations

- Two states only: no lateral motion, no wind, no changing mass or thrust curve.
- The aerodynamic term is held constant, though on a real rocket it grows with speed.
- Only the gyro is noisy; the tilt angle is assumed to be measured perfectly.
- The controller is PD, not full PID, because this model has no steady drift for an integral term to correct.
- Simulation only. Nothing here has been validated on hardware.

## Run it

Install Python 3.11 or newer, then:

    python -m pip install numpy scipy matplotlib
    python compare.py

| File | What it does |
|---|---|
| `open_loop.py` | The rocket with no control, tipping over |
| `closed_loop.py` | PD controller with performance metrics |
| `lqr.py` | LQR controller with adjustable weights |
| `compare.py` | PD and both LQR versions on one graph |
| `servo_lag.py` | Servo lag experiment |
| `gyro_noise.py` | Gyro noise experiment |
| `gyro_filter.py` | Gyro filter experiment (takes about 30 seconds) |
| `notes.md` | Working notes and full result tables |

## Next steps

Add wind gusts and centre-of-mass shifts, add an integral term for a full PID, use a nonlinear model without the small-angle approximation, and validate on a 3D-printed gimbal.

## References

- Comparison of LQR, LQG and PID control for a finless rocket, *Machines* 11(3), 394 (2023): https://mdpi.com/2075-1702/11/3/394
- Sutton and Biblarz, *Rocket Propulsion Elements*, thrust vector control chapter.