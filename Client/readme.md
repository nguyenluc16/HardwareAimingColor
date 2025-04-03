# [leonardo.ino]– Enhanced Human-Like Mouse Movement

This Arduino sketch has been modified to simulate more natural mouse movements using a quadratic Bezier curve. The improvements aim to mimic human behavior and help evade detection by anti-cheat systems that monitor for overly precise, mechanical motions.

## Key Enhancements

- **Quadratic Bezier Curve Movement:**  
  Instead of moving in a straight line, the sketch calculates a smooth curved trajectory from the starting position to the target coordinates. A control point is used to add a small random offset, creating an unpredictable path.

- **Randomized Delay Between Steps:**  
  Between each incremental movement along the Bezier curve, a small random delay (between 10 and 50 ms) is introduced. This delay simulates natural reaction time variability, reducing the risk of detection.

- **Incremental Movement with Step Constraints:**  
  The movement is broken into a predefined number of steps (default 20 steps). Each incremental move is constrained to avoid sending excessively large values at once, ensuring compatibility with the Arduino Mouse library.

- **Mouse Click Simulation:**  
  A separate section handles mouse click commands by randomly determining a click duration (between 40 and 80 ms), further imitating the nuances of human clicking behavior.

## How It Works

1. **Receiving Commands:**  
   - The sketch listens for serial commands.  
   - A command starting with `M` (e.g., `M100,50`) triggers mouse movement, while a command starting with `C` triggers a mouse click.

2. **Bezier Curve Calculation:**  
   - The target coordinates (`deltaX` and `deltaY`) are parsed from the command.  
   - A control point is computed as the midpoint between the origin and target with a random offset.  
   - The sketch divides the trajectory into 20 steps and computes each intermediate point using the quadratic Bezier formula:
     \[
     P(t) = (1-t)^2 \times P_0 + 2(1-t)t \times P_1 + t^2 \times P_2 \quad \text{for } t \in [0,1]
     \]
     where \(P_0 = (0, 0)\) is the starting point, \(P_1\) is the control point, and \(P_2\) is the target.

3. **Executing Movement:**  
   - For each computed point, the sketch calculates the difference from the previous point and moves the mouse accordingly using `Mouse.move()`.  
   - After each movement step, a random delay is applied to emulate natural motion.

4. **Click Handling:**  
   - When a click command is received, the sketch simulates a mouse press for a random duration before releasing the button.

## Usage

- **Movement Command:**  
  Send a command in the format:  
  `M<deltaX>,<deltaY>\n`  
  *Example:* `M100,50` will move the mouse 100 units on the X-axis and 50 units on the Y-axis following a smooth Bezier curve.

- **Click Command:**  
  Send the command:  
  `C\n`  
  to simulate a left mouse click with a randomized press duration.

This enhanced version of the Arduino sketch is designed specifically to create mouse movements that are harder for anti-cheat systems to flag as robotic or non-human.


Hàm computeBezierPoint:
Hàm này tính toán tọa độ (x, y) tại điểm trên đường cong Bezier theo tham số t, với:
P0 = (0,0) là điểm xuất phát của chuột.
P1 = (ctrlX, ctrlY) là điểm điều khiển, giúp tạo ra đường cong mềm mại.
P2 = (targetX, targetY) là tọa độ mục tiêu cần di chuyển đến.

Px = (1-t)^2 * P0x + 2(1-t)t * P1x + t^2 * P2x
Py = (1-t)^2 * P0y + 2(1-t)t * P1y + t^2 * P2y


Điểm điều khiển P1 được đặt ở giữa P0 và P2, với một độ lệch ngẫu nhiên để tạo ra chuyển động tự nhiên hơn.
Chuột sẽ di chuyển theo đường cong Bezier bậc 2 dựa vào công thức nội suy:(targetX,targetY) là tọa độ mục tiêu.

Chọn điểm điều khiển:
Điểm điều khiển được tính từ trung điểm của đường nối từ (0,0) đến (targetX, targetY) với một offset ngẫu nhiên nhỏ, giúp tạo ra đường cong cong tự nhiên.

Di chuyển theo đường cong:
Ta chia đường cong thành bezierSteps (20 bước). Với mỗi bước, tính toán điểm hiện tại, sau đó di chuyển chuột theo hiệu số giữa điểm hiện tại và điểm trước đó, kèm theo delay ngẫu nhiên giữa các bước để mô phỏng chuyển động tự nhiên.

Quản lý click chuột:
Phần click chuột giữ nguyên như phiên bản trước.