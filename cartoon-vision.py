import cv2
import numpy as np


def resize_for_display(img, max_width=1400, max_height=800):
    h, w = img.shape[:2]
    scale = min(max_width / w, max_height / h, 1.0)
    return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)


def cartoon_vision(image_path, output_path="cartoon_vision.png"):
    img = cv2.imread(image_path)

    if img is None:
        raise FileNotFoundError(f"이미지를 불러올 수 없습니다: {image_path}")

    color = img.copy()
    for _ in range(2):
        color = cv2.bilateralFilter(color, d=7, sigmaColor=50, sigmaSpace=50)

    # 채도 강조
    hsv = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    s = np.clip(s * 1.3, 0, 255).astype(np.uint8)
    color = cv2.merge([h, s, v])
    color = cv2.cvtColor(color, cv2.COLOR_HSV2BGR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        4
    )

    kernel = np.ones((2, 2), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    edges = cv2.erode(edges, kernel, iterations=1)

    cartoon = color.copy()
    cartoon[edges == 0] = (0, 0, 0)

    result = np.hstack((img, cartoon))

    cv2.imwrite(output_path, result)

    display = resize_for_display(result)
    cv2.namedWindow("Cartoon", cv2.WINDOW_NORMAL)
    cv2.imshow("Cartoon", display)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return result


if __name__ == "__main__":
    cartoon_vision("lego.jpg", "cartoon_vision.png")
