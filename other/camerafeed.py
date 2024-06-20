import cv2, time, math

capture_device = cv2.VideoCapture(0)

SD_W, SD_H = 1024, 1024

def crop_frame(frame):
    h, w, ch = frame.shape

    left, right = 0, w
    delta = w - SD_W
    if delta > 0:
        shift = math.ceil(delta/2)
        left = shift - 1
        right = left + SD_W

    bottom, top = 0, h
    delta = h - SD_H
    if delta > 0:
        shift = math.ceil(delta/2)
        bottom = shift - 1
        top = bottom + SD_H

    crop = frame[bottom:top, left:right, :]
    print(F"+++ frame shape: {frame.shape}, crop shape: {crop.shape}")

    return crop

run_cond = True
then = time.perf_counter()
while run_cond:
    print("in a loop")
    ret, frame = capture_device.read()
    if ret:
        now = time.perf_counter()
        frame_time = now - then
        then = now
        crop = crop_frame(frame)
        cv2.imshow("webcam", crop)
        print(frame.shape)
    # print(frame)
    elo = cv2.waitKey(1)
    print(elo)
    if cv2.waitKey(1) == ord("q"):
        run_cond = False
