import cv2, numpy as np


def fast_inpaint(band, mask, scale, radius):
    """Inpaint at reduced resolution, paste back only the masked pixels."""
    h, w = band.shape[:2]
    sb = cv2.resize(band, (w // scale, h // scale), interpolation=cv2.INTER_AREA)
    sm = cv2.resize(mask, (w // scale, h // scale), interpolation=cv2.INTER_NEAREST)
    sm = cv2.dilate(sm, np.ones((3, 3), np.uint8))
    fill = cv2.inpaint(sb, sm, radius, cv2.INPAINT_TELEA)
    fill = cv2.resize(fill, (w, h), interpolation=cv2.INTER_LINEAR)
    a = cv2.GaussianBlur(mask, (0, 0), 2)[..., None].astype(np.float32) / 255
    return (fill * a + band * (1 - a)).astype(np.uint8)


def clean(f):
    f = f.copy()
    # yellow subtitles (hue ~25, strongly saturated)
    y0, y1 = 1515, 1625
    band = f[y0:y1]
    hsv = cv2.cvtColor(band, cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, (19, 110, 110), (32, 255, 255))
    if cv2.countNonZero(m) > 40:
        m = cv2.dilate(m, np.ones((9, 9), np.uint8))
        f[y0:y1] = fast_inpaint(band, m, 2, 4)
    # red titles: white letters + red/pink glow (sits under the frosted strip)
    y0, y1 = 1130, 1330
    band = f[y0:y1]
    b = band.astype(np.int16)
    core = (b[..., 2] - (b[..., 0] + b[..., 1]) // 2) > 45
    if np.count_nonzero(core) > 2500:
        soft = (b[..., 2] - b[..., 1]) > 18
        hsv = cv2.cvtColor(band, cv2.COLOR_BGR2HSV)
        white = cv2.inRange(hsv, (0, 0, 200), (180, 90, 255)) > 0
        near = cv2.dilate(core.astype(np.uint8), np.ones((41, 41), np.uint8)) > 0
        m = ((core | soft | white) & near).astype(np.uint8) * 255
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
        m = cv2.dilate(m, np.ones((11, 11), np.uint8))
        f[y0:y1] = fast_inpaint(band, m, 4, 4)
    return f
