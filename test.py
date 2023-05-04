from pypylon import pylon
import cv2
import datetime
import time
import os

# 이미지 저장 비동기 함수
def save_image(frame): 
    today = datetime.datetime.now()
    folderName = today.strftime("%Y-%m-%d")

    imgName = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '.jpg'
    if not os.path.exists(folderName):
        os.makedirs(folderName)
        
    cv2.imwrite(os.path.join(folderName, imgName), frame)
    
# 카메라 초기화
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

# 카메라 환경설정
camera.Width.Value = camera.Width.Max
camera.Height.Value = camera.Height.Max
camera.BalanceWhiteAuto.SetValue("Continuous") # 자동 WB 설정
camera.GainAuto.SetValue('Off')
camera.GainRaw.Value = 200

# 배경 제거 객체 초기화
fgbg = cv2.createBackgroundSubtractorMOG2()

# 카메라에서 영상 캡처
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed

# 화면에 영상 표시
while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    ratio = 0.2 # 카메라 앵글 비율
    wholeArea = 20172145.5 # 전체 화면 영역
    objectSize = (wholeArea * ratio * ratio) / 10 # 찾고자 하는 객체 사이즈
    
    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult)
        frame = image.GetArray()
        frame_resized = cv2.resize(frame, None, fx=1*ratio, fy=1*ratio) # 0.9배 축소
        
        # 배경 제거
        fgmask = fgbg.apply(frame_resized)
        
        # 현재 시간
        current_time = time.time()
        # 객체 탐지
        contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnt = list(filter(lambda x: cv2.contourArea(x) > objectSize, contours))
        if len(cnt):
            for c in cnt:
                area = cv2.contourArea(c)
                print(f"Detected object area: {area}")
            save_image(frame_resized)
            
        # 영상 표시
        # 그리드 그리기
        grid_size = 3 # 3x3 그리드
        rows, cols, _ = frame_resized.shape
        for i in range(1, grid_size):
            cv2.line(frame_resized, (0, i*rows//grid_size), (cols, i*rows//grid_size), (128,128,128), thickness=1)
            cv2.line(frame_resized, (i*cols//grid_size, 0), (i*cols//grid_size, rows), (128,128,128), thickness=1)
        
        cv2.imshow("Camera2", frame_resized)
        
    grabResult.Release()
    if cv2.waitKey(1) == ord('q'):
        break

# 정리
camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()
