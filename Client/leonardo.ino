#include <Mouse.h>
#include <math.h>

String command = "";       // Lệnh nhận từ Serial
int deltaX = 0, deltaY = 0;  // Tọa độ di chuyển theo X và Y

// Quản lý nhấp chuột
bool isClicking = false;
unsigned long clickStartTime = 0;
unsigned long clickDuration;

const int bezierSteps = 20;  // Số bước di chuyển trên đường cong Bezier

// Hàm tính điểm Bezier quadratic
// P(t) = (1-t)^2 * P0 + 2*(1-t)*t * P1 + t^2 * P2
// Với P0 = (0,0), P1 = (ctrlX, ctrlY) và P2 = (targetX, targetY)
void computeBezierPoint(float t, float targetX, float targetY, float ctrlX, float ctrlY, float &outX, float &outY) {
  float u = 1.0 - t;
  outX = u * u * 0.0 + 2 * u * t * ctrlX + t * t * targetX;
  outY = u * u * 0.0 + 2 * u * t * ctrlY + t * t * targetY;
}

void setup() {
    Serial.begin(115200);
    Serial.setTimeout(1);
    Mouse.begin();
    randomSeed(analogRead(0));
}

void loop() {
    if (Serial.available() > 0) {
        command = Serial.readStringUntil('\n');
        command.trim();

        if (command.startsWith("M")) {
            int commaIndex = command.indexOf(',');
            if (commaIndex != -1) {
                deltaX = command.substring(1, commaIndex).toInt();
                deltaY = command.substring(commaIndex + 1).toInt();

                // Tọa độ mục tiêu
                int targetX = deltaX;
                int targetY = deltaY;

                // Chọn điểm điều khiển: trung điểm cộng với offset ngẫu nhiên
                float ctrlX = targetX / 2.0 + random(-10, 10);  // Offset có thể điều chỉnh
                float ctrlY = targetY / 2.0 + random(-10, 10);

                // Tính toán các điểm trên đường cong Bezier
                float prevX = 0, prevY = 0;
                float currX, currY;
                for (int i = 1; i <= bezierSteps; i++) {
                    float t = (float)i / bezierSteps;
                    computeBezierPoint(t, targetX, targetY, ctrlX, ctrlY, currX, currY);
                    
                    // Tính sự khác biệt di chuyển từ điểm trước đó
                    int moveX = (int)round(currX - prevX);
                    int moveY = (int)round(currY - prevY);
                    
                    // Di chuyển chuột với giới hạn mỗi lần - tránh vượt quá 127/-128
                    while (moveX != 0 || moveY != 0) {
                        int stepX = constrain(moveX, -128, 127);
                        int stepY = constrain(moveY, -128, 127);
                        Mouse.move(stepX, stepY);
                        moveX -= stepX;
                        moveY -= stepY;
                    }
                    
                    // Cập nhật điểm trước cho vòng lặp tiếp theo
                    prevX = currX;
                    prevY = currY;
                    
                    // Delay ngẫu nhiên giữa các bước (10-50ms)
                    delay(random(10, 50));
                }
            }
        }
        else if (command.startsWith("C")) {
            if (!isClicking) {
                Mouse.press(MOUSE_LEFT);
                clickStartTime = millis();
                clickDuration = random(40, 80);
                isClicking = true;
            }
        }
    }
    
    if (isClicking) {
        if (millis() - clickStartTime >= clickDuration) {
            Mouse.release(MOUSE_LEFT);
            isClicking = false;
        }
    }
}
