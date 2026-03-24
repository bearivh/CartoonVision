import cv2
import numpy as np


def resize_for_display(img, max_width=1400, max_height=800):
    h, w = img.shape[:2]
    scale = min(max_width / w, max_height / h, 1.0)
    return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)


def cartoon_adaptive(image_path, output_path="cartoon_adaptive.png"):
    img = cv2.imread(image_path)

    if img is None:
        raise FileNotFoundError(f"이미지를 불러올 수 없습니다: {image_path}")

    # -----------------------------
    # 1) 색은 너무 뭉개지지 않게 약하게 부드럽게
    # -----------------------------
    color = img.copy()
    for _ in range(2):
        color = cv2.bilateralFilter(color, d=7, sigmaColor=50, sigmaSpace=50)

    # -----------------------------
    # 2) 외곽선 추출용 grayscale
    #    자글자글함 줄이려고 blur를 먼저 줌
    # -----------------------------
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # -----------------------------
    # 3) adaptiveThreshold로 외곽선
    # -----------------------------
    edges = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,   # blockSize
        4     # C
    )

    # -----------------------------
    # 4) 작은 점/잔선 정리
    # -----------------------------
    kernel = np.ones((2, 2), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # 선을 약간 또렷하게
    edges = cv2.erode(edges, kernel, iterations=1)

    # -----------------------------
    # 5) 외곽선만 검정으로 덮어쓰기
    #    edges == 0 인 부분이 선
    # -----------------------------
    cartoon = color.copy()
    cartoon[edges == 0] = (0, 0, 0)

    # -----------------------------
    # 6) 원본 / 결과 붙이기
    # -----------------------------
    result = np.hstack((img, cartoon))

    # 저장
    cv2.imwrite(output_path, result)

    # 화면 표시
    display = resize_for_display(result)
    cv2.namedWindow("AdaptiveThreshold Cartoon", cv2.WINDOW_NORMAL)
    cv2.imshow("AdaptiveThreshold Cartoon", display)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return result


if __name__ == "__main__":
    cartoon_adaptive("puppy2.jpg", "cartoon_adaptive.png")