import sys

import cv2
import aiohttp  # noqa: F401
import aiortc  # noqa: F401
import av  # noqa: F401
import easyocr  # noqa: F401
import ultralytics  # noqa: F401


def main() -> int:
    gui_line = next(
        line.strip()
        for line in cv2.getBuildInformation().splitlines()
        if line.strip().startswith("GUI:")
    )

    print("Ambiente Tello CLI/WebRTC OK")
    print(f"Python: {sys.executable}")
    print(f"OpenCV: {cv2.__version__}")
    print(gui_line)

    if "NONE" in gui_line.upper():
        print("OpenCV sem suporte a janela; cv2.imshow nao vai funcionar.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
