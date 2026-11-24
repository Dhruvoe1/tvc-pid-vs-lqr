# Intuition notes
## 1. Why does a finless rocket tip over ? 
Fins move the centre of pressure behind the centre of mass. If the rocket tilts, the air pushes the tail back into line, like the feather on an arrow. Without fins, any tilts gets made worse by the air, so the rocket is unstable, like a broom balanced on a hand. 

## 2. What does tilting the engine do?
Tilting the engine by a small engle pushes the tall sideways. The tail is far from the centre of mass, so this creates a torque that rotates the rocket. Tilting the engine steers the rocket's angle rather than changing its direction completely. 

## 3. What does the controller need to know? 
It needs to know how far the rocket is tilted (the angle error), so it can push back the other way. This is proportional (p) part. It also needs to know how fast the angle is changing (measured by a gyroscope), so it can push harder when the tilt is growing quickly. This is the derivative (D) part. 

## 4. Torque 
Torque = force x distance from the pivot. For the rocket, torque = T x L x sin(delta), where T is thrust, L is the distance from the centre of mass to the nozzle, and delta is the gimbal angle. Doubling the thrsut doubles the torque, a longer L gives more torque, and a bigger delta gives more torque (for small angles). 

## 5. Controller tuning results (Kp = 1.0)

| Kd | Overshoot | Settling time | Peak engine angle |
|---|---|---|---|
| 0.05 | 40.7 % | 1.59 s | 1.00 deg |
| 0.13 | 4.0 % | 0.68 s | 1.00 deg |
| 0.30 | 0.0 % | 1.37 s | 1.00 deg |

Too little damping (Kd = 0.05) makes the rocket wobble. Too much (Kd = 0.30) removes overshoot but makes it slow to settle. Kd = 0.13 gives a damping ratio of about 0.7 and the fastest settling. The simulated overshoot values match the values predicted by theory.

## 6. LQR results

| Setting | K1 | K2 | Overshoot | Settling time | Peak engine angle |
|---|---|---|---|---|---|
| Q = diag(10, 1), R = 1 | 3.38 | 1.03 | 0.0 % | 1.25 s | 3.38 deg |
| Q = diag(10, 1), R = 10 | 1.23 | 0.354 | 0.0 % | 1.26 s | 1.23 deg |
| Q = diag(1000, 1), R = 1 | 31.83 | 1.29 | 0.0 % | 0.15 s | 5.00 deg (saturated) |

A larger R makes LQR use the engine more gently. A very large Q asks for roughly 32 degrees of engine tilt per degree of rocket tilt, which hits the 5 degree gimbal limit (saturation), but gives the fastest recovery. The Q = 10 baseline is overdamped, so it is slower than the hand-tuned PD controller (0.68 s) even though it uses more engine movement. To compare PD and LQR fairly, both should be tuned to the same peak engine angle.

## 7. Servo lag results

| Servo lag | PD | LQR Q=(10,1) | LQR matched |
|---|---|---|---|
| 0 ms | 4.0 % overshoot, 0.68 s | 0.0 %, 1.25 s | 0.0 %, 0.63 s |
| 50 ms | 16.7 %, 0.81 s | 0.0 %, 1.24 s | 0.0 %, 0.68 s |
| 100 ms | 48.2 %, no settle in 3 s | 0.0 %, 1.21 s | 17.0 %, 1.63 s |
| 150 ms | 186 %, unstable (growing) | 0.3 %, 1.36 s | 41.7 %, no settle |

PD, tuned for speed, is the most sensitive to servo lag and becomes unstable at 150 ms. The heavily damped LQR is barely affected.

## 8. Gyro noise results

Engine jitter in degrees (standard deviation, average of 10 runs) after the rocket has settled.

| Gyro noise | PD | LQR Q=(10,1) | LQR matched |
|---|---|---|---|
| 0 deg/s | 0.00 | 0.00 | 0.00 |
| 1 deg/s | 0.13 | 1.09 | 0.18 |
| 5 deg/s | 0.66 | 3.71 | 0.89 |
| 10 deg/s | 1.32 | 4.35 | 1.77 |

The ranking is the reverse of the servo lag result. The heavily damped LQR has a gain on tilt speed (K2 about 1.03) roughly 8 times larger than PD (Kd = 0.13), so it amplifies gyro noise about 8 times more. At 5 deg/s its engine command repeatedly hits the 5 degree gimbal limit. The same large gain that protects against servo lag makes it vulnerable to sensor noise: no controller wins both tests.

## 9. Gyro filter results

A first-order low-pass filter on the gyro reading (5 deg/s noise, jitter = engine standard deviation in degrees).

| Servo lag | Filter | PD jitter | LQR Q=(10,1) jitter | LQR matched jitter |
|---|---|---|---|---|
| 0 ms | none | 0.66 | 3.71 | 0.89 |
| 0 ms | 10 ms | 0.22 | 1.75 | 0.30 |
| 0 ms | 20 ms | 0.16 | 1.23 | 0.21 |
| 30 ms | none | 0.14 | 0.69 | 0.17 |
| 30 ms | 10 ms | 0.13 | 1.39 | 0.16 |
| 30 ms | 20 ms | 0.13 | 2.64 (sustained wobble) | 0.16 |

With a perfect servo, the filter cuts jitter a lot. With a 30 ms servo, the servo already smooths the engine motion, so the filter adds little and costs extra lag. For the heavily damped LQR, a 20 ms filter plus a 30 ms servo gives a sustained limit-cycle oscillation: the tilt stays within about 0.2 degrees, but the engine swings by almost 4 degrees to hold it, because the command saturates at the 5 degree limit. Lag from the servo and from the filter add together, and high-gain controllers have the least margin for it.