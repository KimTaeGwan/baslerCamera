from pypylon import pylon
import cv2

# Basler 카메라를 검색
devices = pylon.TlFactory.GetInstance().EnumerateDevices()
if len(devices) == 0:
    print("카메라가 발견되지 않았습니다.")
    exit(1)

# 첫 번째 카메라를 선택
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(devices[0]))
camera.Open()

# 카메라 환경설정
camera.Width.Value = camera.Width.Max
camera.Height.Value = camera.Height.Max
camera.BalanceWhiteAuto.SetValue("Continuous") # 자동 WB 설정
camera.GainAuto.SetValue('Off')
camera.GainRaw.Value = 200

# 카메라에서 영상 캡처
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed

# 화면에 영상 표시
while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult)
        frame = image.GetArray()
        frame_resized = cv2.resize(frame, None, fx=0.1, fy=0.1) # 0.9배 축소
        cv2.imshow("Camera", frame_resized)
    grabResult.Release()
    
    if cv2.waitKey(1) == ord('q'):
        break

# 정리
camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()
