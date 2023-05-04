from pypylon import pylon
import cv2
import datetime
import time

class Camera:
    def __init__(self):
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.camera.Open()
        self.camera.Width.Value = self.camera.Width.Max
        self.camera.Height.Value = self.camera.Height.Max
        self.camera.BalanceWhiteAuto.SetValue("Continuous")
        self.camera.GainAuto.SetValue('Off')
        self.camera.GainRaw.Value = 200
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_BGR8packed

    def start_grabbing(self):
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    def retrieve_result(self, timeout):
        grab_result = self.camera.RetrieveResult(timeout, pylon.TimeoutHandling_ThrowException)
        if grab_result.GrabSucceeded():
            image = self.converter.Convert(grab_result)
            return image.GetArray()
        grab_result.Release()
        return None

    def stop_grabbing(self):
        self.camera.StopGrabbing()
        self.camera.Close()

class BackgroundSubtractor:
    def __init__(self):
        self.fgbg = cv2.createBackgroundSubtractorMOG2()

    def apply(self, frame):
        return self.fgbg.apply(frame)

class ImageSaver:
    def __init__(self):
        self.last_run = 0
        self.interval_time = 10

    def save_image(self, frame):
        current_time = time.time()
        if current_time - self.last_run >= self.interval_time:
            self.last_run = current_time
            filename = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '.jpg'
            cv2.imwrite(filename, frame)

class VideoDisplay:
    def __init__(self):
        cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)

    def show(self, frame):
        frame_resized = cv2.resize(frame, None, fx=0.2, fy=0.2)
        cv2.imshow("Camera", frame_resized)
        return cv2.waitKey(1) == ord('q')

def main():
    camera = Camera()
    camera.start_grabbing()
    background_subtractor = BackgroundSubtractor()
    image_saver = ImageSaver()
    video_display = VideoDisplay()

    while camera.camera.IsGrabbing():
        frame = camera.retrieve_result(5000)
        if frame is not None:
            fgmask = background_subtractor.apply(frame)
            contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnt = list(filter(lambda x: cv2.contourArea(x) > 500, contours))
            if len(cnt):
                image_saver.save_image(frame)
            if video_display.show(frame):
                break

    camera.stop_grabbing()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
