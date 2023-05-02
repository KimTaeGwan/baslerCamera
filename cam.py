from pypylon import pylon
import cv2

# Basler 카메라를 검색합니다.
devices = pylon.TlFactory.GetInstance().EnumerateDevices()
if len(devices) == 0:
    print("카메라가 발견되지 않았습니다.")
    exit(1)

# 첫 번째 카메라를 선택합니다.
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(devices[0]))

# 카메라의 속성을 설정합니다.
camera.Open()
camera.Width.Value = camera.Width.Max
camera.Height.Value = camera.Height.Max
camera.BalanceWhiteAuto.SetValue("Continuous") # 자동 WB 설정
camera.GainAuto.SetValue('Off')
camera.GainRaw.Value = 200

# 이미지를 취득합니다.
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
while camera.IsGrabbing():
    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    if grab_result.GrabSucceeded():
        # 이미지를 OpenCV 형식으로 변환합니다.
        image = converter.Convert(grab_result)
        img = image.GetArray()
        # 이미지를 축소합니다.
        img_resized = cv2.resize(img, None, fx=0.1, fy=0.1) # 0.5배 축소
        # 이미지를 표시합니다.
        cv2.imshow("Basler Camera", img_resized)
        cv2.waitKey(1)
    grab_result.Release()
    
# 카메라를 정리합니다.
camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()
