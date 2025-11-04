"""
步骤：
1.opencv获取视频流
2.在画面上画一个方块
3.通过mediapipe获取手指关键点坐标
4.判断手指是否在方块上
5.如果在方块上.方块跟着手指移动
"""
#导入opencv
import cv2
import numpy as np
import math
#mideapipe相关参数
import mediapipe as mp
mp_drawing=mp.solutions.drawing_utils #提供了一些绘制图像的实用函数，用于在图像上绘制关键点、连接线等。
mp_drawing_styles=mp.solutions.drawing_styles #定义了一些绘制风格，用于在图像上绘制关键点和连接线时的样式设置。
mp_hands=mp.solutions.hands #提供了手部关键点检测的功能。通过使用mp_hands.Hands()函数，可以创建一个手部关键点检测的实例，用于检测图像中的手部关键点。

hands = mp_hands.Hands(
     model_complexity=0, #用于设置模型的复杂度，取值范围为（0~2），较低复杂度可以提高处理速度降低检测准确性，反之同理。
     min_detection_confidence=0.5, #参数用于设置检测手部关键点的最小置信度阈值，表示只有当置信度大于等于0.5时，才会被认为是有效的关键点。
     min_tracking_confidence=0.5) #参数用于设置追踪手部关键点的最小置信度阈值，表示只有当置信度大于等于0.5时，才会进行跟踪。

#获取摄像头视频流
cap = cv2.VideoCapture(0)  #调用打开电脑自带摄像头，如果想使用其他食品可以将参数零改为可读取的视频地址

#获取画面宽度与高度
width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#方块参数设置
square_x=100   #方块位置坐标，方块到视频画面左侧水平距离
square_y=100   #方块位置坐标，方块到视频画面顶层垂直距离
square_width=100 #方块的边长
square_color=(255,0,0)

L1=0
L2=0
on_square=False
while True:
     
     #读取每一帧
     ret,frame=cap.read() #该函数用于读取cv.VideoCaptuare()函数的对象cap的数据并返回两个值
                          #ret,是布尔值若读取到图像帧则值为True否则为False
                          #frame,是一个表示图像帧的多维数组（通常是numpy数组），它包含了摄像头捕捉到图像数据

     #对图像进行处理
     frame=cv2.flip(frame,1)  #此代码用于翻转图像,参数值为1表示正常画面,参数为0时水平与垂直方向均翻转,参数为-1时仅为垂直方向翻转

     #mediapipe处理
     frame.flags.writeable=False #将图像设置为不可写
     frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB) #将图像从BGR颜色空间转换为RGB颜色空间。这是因为mediapipe库处理的图像需要在RGB颜色空间下进行。
     results=hands.process(frame) #对图像进行手部关键点检测，将检测结果保存在results变量中。

     frame.flags.writeable=True #将图像设置为可写
     frame=cv2.cvtColor(frame,cv2.COLOR_RGB2BGR) #将图像从RGB颜色空间转换回BGR颜色空间。这是因为后续的绘制操作需要在BGR颜色空间下进行。
     
     #判断是否出现手
     if results.multi_hand_landmarks:
        
        #解析遍历每一双手
        for hand_landmarks in results.multi_hand_landmarks:

          #绘制21个遍历点
          mp_drawing.draw_landmarks(
              frame,
              hand_landmarks,
              mp_hands.HAND_CONNECTIONS,
              mp_drawing_styles.get_default_hand_landmarks_style(),
              mp_drawing_styles.get_default_hand_connections_style()
          )  
          
          #保存21个x,y坐标
          x_list=[]
          y_list=[]
          for landmark in hand_landmarks.landmark:
              #hand_landmarks.landmark表示手部关键点的列表，其中每个元素代表一个关键点。通过遍历hand_landmarks.landmark，可以依次获取每个关键点的信息。
              #添加X坐标
              x_list.append(landmark.x)
              #添加Y坐标
              y_list.append(landmark.y)
              #通过landmark.x和landmark.y分别获取当前关键点的X坐标和Y坐标，并将它们添加到x_list和y_list列表中。
          #print(len(x_list))
     
          #获取食指指尖
          index_finger_x=int(x_list[8]*width) #x_list[8]与_list[8]是用来保存手部关键点坐标的列表
          index_finger_y=int(y_list[8]*height) #相对坐标是指相对于图像的宽度和高度的比例值。通过将相对坐标乘以图像的宽度和高度，可以将其转换为实际的图像坐标
          #根据MediaPipe库的文档，食指指尖的关键点索引为8。因此，通过x_list[8]可以获取食指指尖的相对X坐标，而y_list[8]可以获取食指指尖的相对Y坐标。

        #获取中指指尖xy坐标
          middle_finger_x=int(x_list[12]*width)
          middle_finger_y=int(y_list[12]*height)
        
         #计算食指与中指指尖的距离
          finger_len=math.hypot((index_finger_x-middle_finger_x),
                                (index_finger_y-middle_finger_y))
          print(finger_len)

          #画一个圆来验证
          #cv2.circle(frame,(index_finger_x,index_finger_y),20,(255,0,255),-1)
          #print(index_finger_x,index_finger_y) #圆心坐标为(index_finger_x, index_finger_y)，半径为20个像素，颜色为(255, 0, 255)，并且填充整个圆形

          #如果食指指尖小于30算激活，否则取消激活
          if finger_len<30:
                #判断食指指尖在不在方块上
                if ((index_finger_x > square_x) and (index_finger_x < 
                (square_x+square_width))) and ((index_finger_y > square_y)
                and (index_finger_y < (square_y+square_width))):
                    if on_square==False:
                        print('在方块上')
                        L1=abs(index_finger_x-square_x)
                        L2=abs(index_finger_y-square_y)
                        on_square=True
                        square_color=(0,0,255)
                else:
                    #print("不在方块上")
                    pass
          else:
               #取消激活
               on_square=False
               square_color=(255,0,0)
          if on_square:
              square_x=index_finger_x-L1
              square_y=index_finger_y-L2
     #画一个方块
     #cv2.rectangle(frame,(square_x,square_y),(square_x +square_width,square_y+square_width),(255,0,0),-1)
    #画一个方块
     overlay=frame.copy() #创建一个视频副本，然后在副本上面进行绘制操作而不会修改原有的frame图像，frame.copy()可以创建一个与frame具有相同像素值的新图像
     cv2.rectangle(frame,(square_x,square_y),(square_x+square_width,square_y+square_width),square_color,-1)
     #参数-1控制整个方块的线宽度，-1也表示填充整个方块，将数值更改为较大的整数会发现方块线条边框变粗了
     frame=cv2.addWeighted(overlay,0.5,frame,0.5,0) #将绘制好的视频副本与原视频图像进行叠加，在本例中两个图像权重均为0.5表示叠加时亮度平均
     #显示
     cv2.imshow('Virtual drag',frame) #cv2.imshow()函数第一个参数是窗口的名称，第二个惨呼是要显示的图像

     #退出条件
     if cv2.waitKey(10) & 0xFF ==27:  #判断语句，ESC按键的ASCII值正好是27，因此以ESC按键作为推出判断条件。
          break  #cv2.waitkey(10)表示等待键盘输入的时间，本例中为10毫秒
     
cap.release() #用于进程结束时释放上面cv2.VideoCapture()函数打开的摄像头资源，以便其他程序进程可以访问它

cv2.destroyAllWindows() #该函数用于关闭所有通过cv2.imshow()函数打开的窗口，在该例子中关闭了一个名为"Virtual drag"的窗口。
