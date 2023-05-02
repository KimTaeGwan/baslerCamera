from pypylon import pylon
import cv2
import datetime
import asyncio

# 이미지 저장 비동기 함수
async def save_image(frame): 
    filename = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + '.jpg'
    cv2.imwrite(filename, frame)
    await asyncio.sleep(3)
    
async def run_tasks(frame):
    task1 = asyncio.create_task(save_image(frame))  
    await task1  

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
    if grabResult.GrabSucceeded():
        image = converter.Convert(grabResult)
        frame = image.GetArray()
        frame_resized = cv2.resize(frame, None, fx=0.1, fy=0.1) # 0.9배 축소
        
        # 배경 제거
        fgmask = fgbg.apply(frame_resized)
        
        # 객체 탐지
        contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnt = list(filter(lambda x: cv2.contourArea(x) > 500, contours))
        if len(cnt):  
            asyncio.run(run_tasks(frame))
            
        # 영상 표시
        cv2.imshow("Camera", frame_resized)
        
    grabResult.Release()
    if cv2.waitKey(1) == ord('q'):
        break

# 정리
camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()
