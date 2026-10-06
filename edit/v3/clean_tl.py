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
    # red titles: white letters (inpaint) + additive red glow (subtract)
    y0, y1 = 1100, 1390
    band = f[y0:y1]
    b = band.astype(np.int16)
    core = (b[..., 2] - (b[..., 0] + b[..., 1]) // 2) > 45
    if np.count_nonzero(core) > 2500:
        hsv = cv2.cvtColor(band, cv2.COLOR_BGR2HSV)
        white = cv2.inRange(hsv, (0, 0, 175), (180, 120, 255))
        near = cv2.dilate(core.astype(np.uint8) * 255, np.ones((31, 31), np.uint8))
        m = cv2.bitwise_and(white, near)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        m = cv2.dilate(m, np.ones((13, 13), np.uint8))
        fb = band.astype(np.float32)
        gmax = np.maximum(fb[..., 0], fb[..., 1])
        exc = np.clip(fb[..., 2] - gmax, 0, None)
        sel = cv2.dilate(core.astype(np.uint8), np.ones((61, 61), np.uint8)).astype(np.float32)
        sel = cv2.GaussianBlur(sel, (0, 0), 10)
        glow = exc * sel
        fb[..., 2] -= glow
        fb[..., 1] -= glow * 0.18
        fb[..., 0] -= glow * 0.18
        band = np.clip(fb, 0, 255).astype(np.uint8)
        band = fast_inpaint(band, m, 2, 5)
        # soften the filled letter zone so it reads as motion blur, not shapes
        zone = cv2.GaussianBlur(cv2.dilate(m, np.ones((15, 15), np.uint8)), (0, 0), 7)
        zone = zone[..., None].astype(np.float32) / 255
        soft = cv2.GaussianBlur(band, (0, 0), 7).astype(np.float32)
        f[y0:y1] = (soft * zone + band.astype(np.float32) * (1 - zone)).astype(np.uint8)
    return f
