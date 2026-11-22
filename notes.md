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