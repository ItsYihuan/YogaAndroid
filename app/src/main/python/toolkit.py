import json
from os.path import dirname, join
import math as m
import AngleNodeDef
from yogaFileGetter import get_image_path

MIN_DETECT_VISIBILITY = 0.7
DISPLACEMENT_DISTANCE = 0.15

def readSampleJsonFile(path):
    """read joint angle sample json file


    Args:
        path (str): json file path


    Returns:
        sample angle in json(dict) format
        (if process error return None)
    """
    try:
        filename=join(dirname(__file__),path)
        with open(filename, 'r') as file:
            sample_angle = json.load(file)
            return sample_angle
    except:
        return None


def writeSampleJsonFile(angle_array, angle_def, path):
    """write sample joint angle in json file


    Args:
        angle_array (numpy array): sample angle array
        angle_def (list): joint points defined by AngleNodeDef.py
        path (str): json file storage path


    Returns:
        No return
    """
    data = {}
    index = 0
    for key,_ in angle_def.items():
        data[key] = angle_array[index]
        index+=1
    # print(data)
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)


def computeAngle(point1, centerPoint, point2):
    """compute joint points angle


    Args:
       point1 (list): joint points contains x,y,z
       centerPoint (list): joint points contains x,y,z
       point2 (list): joint points contains x,y,z


       centerPoint--->point1 = vector1
       centerPoint--->point2 = vector2
       use vector1 & vector2 compute angle


    Returns:
       degree (float)
    """

    p1_x, pc_x, p2_x = point1[0], centerPoint[0], point2[0]
    p1_y, pc_y, p2_y = point1[1], centerPoint[1], point2[1]


    if len(point1) == len(centerPoint) == len(point2) == 3:
        p1_z, pc_z, p2_z = point1[2], centerPoint[2], point2[2]
    else:
        # 2 dim
        p1_z, pc_z, p2_z = 0,0,0


    # vector
    x1,y1,z1 = (p1_x-pc_x),(p1_y-pc_y),(p1_z-pc_z)
    x2,y2,z2 = (p2_x-pc_x),(p2_y-pc_y),(p2_z-pc_z)

    # angle
    cos_b = (x1*x2 + y1*y2 + z1*z2) / (m.sqrt(x1**2 + y1**2 + z1**2) *(m.sqrt(x2**2 + y2**2 + z2**2)))
    B = round(m.degrees(m.acos(cos_b)),3)
    return B

def treePoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    """
    tree pose rule


    Args:
       roi (list): region of interesting joint for tree pose
       tips (str): tips
       sample_angle_dict (dict): sample angle dict
       angle_dict (dict): angle dict
       point3d (mediapipe): mediapipe detect result


    Returns:
       roi (dict)
       tips (str)
       pointsOut (list)
    """
    pointsOut = []# (a,b): a -> b
    for key, _ in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        """if mat.point_count == 0:
           tips = "請將腳踩到瑜珈墊中" if tip_flag else tips
           imagePath = f"{imageFolder}/8.jpg" if tip_flag else imagePath
        elif mat.point_count >= 2:
           tips = "請將右腳抬起" if tip_flag else tips
           imagePath = f"{imageFolder}/8.jpg" if tip_flag else imagePath
        """
        #if angle_dict[key] == -1:
        #    continue
        if key == 'RIGHT_KNEE':
            min_angle = 170
            max_angle = 180
            if angle_dict[key] == -1:
                continue
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi[key] = True
                pointsOut=[] if tip_flag else pointsOut
            elif angle_dict[key]<min_angle:
                roi[key] = False
                tips = "將左腳打直平均分配雙腳重量，勿將右腳重量全放在左腳大腿" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi= point3d[AngleNodeDef.RIGHT_KNEE]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x, pointStart_y+DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
            else:
                roi[key] = False
                tips = "請勿將右腳重量全放在左腳大腿，避免傾斜造成左腳負擔" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi= point3d[AngleNodeDef.RIGHT_KNEE]
                pointsOut = [pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y, pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key == 'LEFT_FOOT_INDEX':
            _,foot_y,_ ,foot_vi= point3d[AngleNodeDef.LEFT_FOOT_INDEX]
            _,knee_y,_ ,knee_vi= point3d[AngleNodeDef.RIGHT_KNEE]
            if foot_vi <MIN_DETECT_VISIBILITY and knee_vi < MIN_DETECT_VISIBILITY :
                continue
            if foot_y <= knee_y:
                roi[key] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi[key] = False
                tips = "請將右腳抬至高於左腳膝蓋的位置，勿將右腳放在左腳膝蓋上，避免造成膝蓋負擔"
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_FOOT_INDEX]
                pointsOut = [pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y, pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key == 'LEFT_KNEE':
            _,_,knee_z,_ = point3d[AngleNodeDef.LEFT_KNEE]
            _,_,hip_z,_ = point3d[AngleNodeDef.LEFT_HIP]
            if angle_dict[key] == -1:
                continue
            if angle_dict['LEFT_KNEE']<=60 and ((hip_z-knee_z)*100)<=17:
                roi[key] = True
                pointsOut=[]
            elif angle_dict['LEFT_KNEE']>60:
                roi[key] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi= point3d[AngleNodeDef.LEFT_KNEE]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
                print("toolkit: ",pointsOut, "Point3d:",point3d[AngleNodeDef.LEFT_KNEE])
                tips = "請將右腳再抬高一些，不可壓到左腳膝蓋" if tip_flag else tips
            elif ((hip_z-knee_z)*100)>17:
                roi[key] = False
                tips = "將臂部往前推，打開左右骨盆，右腳膝蓋不可向前傾" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi= point3d[AngleNodeDef.LEFT_HIP]
                pointsOut = [pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y-DISPLACEMENT_DISTANCE, pointStart_x, pointStart_y] if tip_flag else pointsOut
                print("toolkit: ",pointsOut, "Point3d:",point3d[AngleNodeDef.LEFT_HIP])
            else:
                roi[key] = False
                tips = "右腳膝蓋不可向前傾，須與髖關節保持同一平面" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi= point3d[AngleNodeDef.LEFT_KNEE]
                pointsOut = [pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y-DISPLACEMENT_DISTANCE, pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key == 'LEFT_HIP':
            if angle_dict[key] == -1:
                continue
            if angle_dict[key]>=100:
                roi[key] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi[key] = False
                tips = "請確認右腳膝蓋是否已經抬至左腳膝蓋以上" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi= point3d[AngleNodeDef.LEFT_KNEE]
                pointsOut = [pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y-DISPLACEMENT_DISTANCE, pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key == 'LEFT_SHOULDER' or key == 'RIGHT_SHOULDER':
            if angle_dict[key] == -1:
                continue
            if angle_dict[key]>=120:
                roi[key] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi[key] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi= point3d[AngleNodeDef.LEFT_SHOULDER] if key=='LEFT_SHOULDER' else point3d[AngleNodeDef.RIGHT_SHOULDER]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
                tips = "請將雙手合掌並互相施力，往上伸展至頭頂正上方" if tip_flag else tips
        elif key == 'LEFT_ELBOW' or key == 'RIGHT_ELBOW':
            if angle_dict[key] == -1:
                continue
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            if angle_dict[key]>=min_angle:
                roi[key] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi[key] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi= point3d[AngleNodeDef.LEFT_ELBOW] if key=='LEFT_ELBOW' else point3d[AngleNodeDef.RIGHT_ELBOW]
                if key=='LEFT_ELBOW':
                    pointsOut = [pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y, pointStart_x, pointStart_y] if tip_flag else pointsOut
                else:
                    pointsOut = [pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y, pointStart_x, pointStart_y] if tip_flag else pointsOut
                tips = "請將雙手再往上伸展，使手軸貼近耳朵" if tip_flag else tips
        elif key == 'LEFT_INDEX' or key == 'RIGHT_INDEX':
            index_x,_,_,index_vi = point3d[AngleNodeDef.LEFT_INDEX] if key == 'LEFT_INDEX' else point3d[AngleNodeDef.RIGHT_INDEX]
            left_shoulder_x,_,_,left_shoulder_vi = point3d[AngleNodeDef.LEFT_SHOULDER]
            right_shoulder_x,_,_,right_shoulder_vi = point3d[AngleNodeDef.RIGHT_SHOULDER]
            if index_x>=right_shoulder_x and index_x<=left_shoulder_x:
                roi[key] = True
                pointsOut=[] if tip_flag else pointsOut
            elif index_x<right_shoulder_x:
                roi[key] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi= point3d[AngleNodeDef.LEFT_INDEX] if key=='LEFT_INDEX' else point3d[AngleNodeDef.RIGHT_INDEX]
                pointsOut = [pointStart_x, pointStart_y, (pointStart_x+DISPLACEMENT_DISTANCE), pointStart_y] if tip_flag else pointsOut
                tips = "請將雙手往右移動，保持在頭頂正上方" if tip_flag else tips
            elif index_x>left_shoulder_x:
                roi[key] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi= point3d[AngleNodeDef.LEFT_INDEX] if key=='LEFT_INDEX' else point3d[AngleNodeDef.RIGHT_INDEX]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                tips = "請將雙手往左移動，保持在頭頂正上方" if tip_flag else tips
    if tips == "":
        tips = "動作正確"
        pointsOut=[]
    return roi, tips, pointsOut


def warriorIIPoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    """warriorII pose rule


    Args:
       roi (list): region of interesting joint for warriorII pose
       tips (str): tips
       sample_angle_dict (dict): sample angle dict
       angle_dict (dict): angle dict
       point3d (mediapipe): mediapipe detect result


    Returns:
       roi (dict)
       tips (str)
       pointsOut (list)
    """
    pointsOut = [] # (a,b): a -> b
    for key, _ in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        if key == 'LEFT_ANKLE': #1
            hip_x,_,_,hip_vi, =  point3d[AngleNodeDef.LEFT_HIP]
            knee_x,_,_,knee_vi =  point3d[AngleNodeDef.LEFT_KNEE]
            if knee_vi  < MIN_DETECT_VISIBILITY and hip_vi < MIN_DETECT_VISIBILITY:
                continue
            if hip_x<=knee_x:
                roi[key] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi[key] = False
                tips = "請將右腳腳尖朝向右手邊" if tip_flag else tips
                pointStart_x, pointStart_y, _, _= point3d[AngleNodeDef.LEFT_FOOT_INDEX]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
        elif key == 'LEFT_KNEE': #2
            ankle_x,_,_ ,ankle_vi=  (point3d[AngleNodeDef.LEFT_ANKLE])
            knee_x,_,_ ,knee_vi=  (point3d[AngleNodeDef.LEFT_KNEE])
            if angle_dict[key] == -1 :
                continue
            if ankle_vi <MIN_DETECT_VISIBILITY and knee_vi  < MIN_DETECT_VISIBILITY:
                continue
            if angle_dict[key]>=90 and angle_dict[key]<=150 and abs((ankle_x-knee_x))<=0.08:
                roi[key] = True
                pointsOut=[] if tip_flag else pointsOut
            elif abs((ankle_x-knee_x))>0.08:
                roi[key] = False
                tips = "請將右腳膝蓋往右腳腳踝的方向移動，直到小腿與地面呈垂直" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_KNEE]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
            elif angle_dict[key]<90:
                roi[key] = False
                tips = "臀部不可低於右腳膝蓋，請將左腳往內收回使臀部高於右腳膝蓋" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_KNEE]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
            elif angle_dict[key]>150:
                roi[key] = False
                tips = "請將左腳再往後一些，讓臀部有空間可以下壓" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_KNEE]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
        elif key == 'RIGHT_KNEE': #3
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=165:
                roi[key] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi[key] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_KNEE]
                pointStart_x_end, pointStart_y_end, pointStart_z_end, _= point3d[AngleNodeDef.RIGHT_ANKLE]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x_end, pointStart_y_end] if tip_flag else pointsOut
                tips = "請將左腳膝蓋打直，並將左腳腳尖朝向前方" if tip_flag else tips
        elif key == 'LEFT_HIP' or key == 'RIGHT_HIP': #4
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=100:
                roi[key] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi[key] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_KNEE] if key == 'RIGHT_HIP' else point3d[AngleNodeDef.LEFT_KNEE]
                if key == 'RIGHT_HIP':
                    pointsOut = [pointStart_x, pointStart_y, pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                else:
                    pointsOut = [pointStart_x, pointStart_y, pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                tips = "請將雙腳再拉開一些距離，臀部向前推並挺胸" if tip_flag else tips
        elif key == 'NOSE': #5
            nose_x,_,_,nose_vi =  (point3d[AngleNodeDef.NOSE])
            left_hip_x,_,_,left_hip_vi =  (point3d[AngleNodeDef.LEFT_HIP])
            right_hip_x,_,_,right_hip_vi =  (point3d[AngleNodeDef.RIGHT_HIP])
            if left_hip_vi <MIN_DETECT_VISIBILITY and right_hip_vi <MIN_DETECT_VISIBILITY and nose_vi <MIN_DETECT_VISIBILITY :
                continue
            if abs(nose_x-left_hip_x)<abs(nose_x-right_hip_x):
                roi[key] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi[key] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.NOSE]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                tips = "請將頭轉向彎曲腳的方向並直視前方" if tip_flag else tips
        elif key == 'LEFT_SHOULDER': #6
            _,left_shoulder_y,_,left_shoulder_vi =  (point3d[AngleNodeDef.LEFT_SHOULDER])
            _,left_elbow_y,_,left_elbow_vi =  (point3d[AngleNodeDef.LEFT_ELBOW])
            if angle_dict[key]==-1:
                continue
            if angle_dict[key]>=150:
                roi[key] = True
                pointsOut=[] if tip_flag else pointsOut
            elif angle_dict[key]<150 and (left_elbow_y-left_shoulder_y)>0.05:
                roi[key] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
                tips = f"請將右手抬高，與肩膀呈水平，並將身體挺直朝向前方" if tip_flag else tips
            else:
                roi[key] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x, pointStart_y+DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
                tips = f"請將右手放低 ，與肩膀呈水平，並將身體挺直朝向前方" if tip_flag else tips
        elif key == 'RIGHT_SHOULDER': #6
            _,right_shoulder_y,_,right_shoulder_vi =  (point3d[AngleNodeDef.RIGHT_SHOULDER])
            _,right_elbow_y,_,right_elbow_vi =  (point3d[AngleNodeDef.RIGHT_ELBOW])
            if angle_dict[key]==-1:
                continue
            if angle_dict[key]>=150:
                roi[key] = True
                pointsOut=[]
            elif angle_dict[key]<150 and (right_elbow_y-right_shoulder_y)>0.05:
                roi[key] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_ELBOW]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
                tips = f"請將左手抬高，與肩膀呈水平，並將身體挺直朝向前方" if tip_flag else tips
            else:
                roi[key] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_ELBOW]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x, pointStart_y+DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
                tips = f"請將左手放低，與肩膀呈水平，並將身體挺直朝向前方" if tip_flag else tips
        elif key == 'LEFT_ELBOW' or key == 'RIGHT_ELBOW': #7
            if angle_dict[key] == -1 :
                continue
            direction = "右" if key == 'LEFT_ELBOW' else "左"
            if angle_dict[key]>=160:
                roi[key] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi[key] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW] if key == 'LEFT_ELBOW' else point3d[AngleNodeDef.RIGHT_ELBOW]
                pointStart_x_end, pointStart_y_end, pointStart_z_end, _= point3d[AngleNodeDef.LEFT_WRIST]  if key == 'LEFT_ELBOW' else point3d[AngleNodeDef.RIGHT_WRIST]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x_end, pointStart_y_end] if tip_flag else pointsOut
                tips = f"請將{direction}手手心朝下平放並打直{direction}手" if tip_flag else tips
    if tips == "":
        tips = "動作正確 ! "
        pointsOut=[]
    return roi, tips, pointsOut


def plankPoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    """plank pose rule


    Args:
        roi (list): region of interesting joint for plank pose
        tips (str): tips
        sample_angle_dict (dict): sample angle dict
        angle_dict (dict): angle dict
        point3d (mediapipe): mediapipe detect result


    Returns:
       roi (dict)
       tips (str)
       pointsOut (list)
    """
    side = ''
    pointsOut = [] # (a,b): a -> b
    for key, value in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        if key == 'NOSE':
            if point3d[AngleNodeDef.NOSE][0] > point3d[AngleNodeDef.LEFT_HIP][0] and point3d[AngleNodeDef.NOSE][0] > point3d[AngleNodeDef.RIGHT_HIP][0]:
                roi['NOSE'] = True
                side = 'RIGHT_'
            elif point3d[AngleNodeDef.NOSE][0] < point3d[AngleNodeDef.LEFT_HIP][0] and point3d[AngleNodeDef.NOSE][0] < point3d[AngleNodeDef.RIGHT_HIP][0]:
                roi['NOSE'] = True
                side = 'LEFT_'
            else:
                roi[key] = False
                tips = "請將身體朝左方或右方趴下，並將雙手撐在肩膀下方，將身體撐起，使身體呈現一斜線"
                break
        if key == side + 'ANKLE':
            min_angle = 30
            ankle_x, ankle_y, _, ankle_vi=point3d[AngleNodeDef.LEFT_ANKLE] if key=='LEFT_ANKLE' else point3d[AngleNodeDef.RIGHT_ANKLE]
            foot_index_x, foot_index_y, _, foot_index_vi=point3d[AngleNodeDef.LEFT_FOOT_INDEX] if key=='LEFT_ANKLE' else point3d[AngleNodeDef.RIGHT_FOOT_INDEX]
            
            if ankle_vi >MIN_DETECT_VISIBILITY :
                continue
            if ankle_y<=foot_index_y and abs(ankle_y-foot_index_y)>0.08:
                roi['RIGHT_ANKLE'] = True
                roi['LEFT_ANKLE'] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                roi['RIGHT_ANKLE'] = False
                roi['LEFT_ANKLE'] = False
                tips = "請用前腳掌將身體撐起"
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_FOOT_INDEX] if key=='RIGHT_ANKLE' else point3d[AngleNodeDef.LEFT_FOOT_INDEX]
                pointsOut = [pointStart_x, pointStart_y,pointStart_x,pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
        elif key == side + 'KNEE':
            min_angle = 160
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=min_angle:
                roi['RIGHT_KNEE'] = True
                roi['LEFT_KNEE'] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                roi['RIGHT_KNEE'] = False
                roi['LEFT_KNEE'] = False
                tips = "請將雙腿伸直並讓大腿到腳踝成一直線"
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_KNEE] if key=='RIGHT_KNEE' else point3d[AngleNodeDef.LEFT_KNEE]
                pointsOut=[pointStart_x,pointStart_y,pointStart_x,pointStart_y+DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
        elif key == side + 'EYE':
            if side == 'LEFT_':
                if point3d[AngleNodeDef.RIGHT_SHOULDER][3] <MIN_DETECT_VISIBILITY and point3d[AngleNodeDef.RIGHT_EYE][3] < MIN_DETECT_VISIBILITY:
                    continue
                eye_shoulder_distance = abs(point3d[AngleNodeDef.RIGHT_SHOULDER][1] - point3d[AngleNodeDef.RIGHT_EYE][1])
                forearm_distance = abs(point3d[AngleNodeDef.RIGHT_SHOULDER][1] - point3d[AngleNodeDef.RIGHT_ELBOW][1])
            else:
                if point3d[AngleNodeDef.LEFT_SHOULDER][3] <MIN_DETECT_VISIBILITY and point3d[AngleNodeDef.LEFT_EYE][3] < MIN_DETECT_VISIBILITY:
                    continue
                eye_shoulder_distance = abs(point3d[AngleNodeDef.LEFT_SHOULDER][1] - point3d[AngleNodeDef.LEFT_EYE][1])
                forearm_distance = abs(point3d[AngleNodeDef.LEFT_SHOULDER][1] - point3d[AngleNodeDef.LEFT_ELBOW][1])
            if eye_shoulder_distance >= forearm_distance * 0.05:
                roi['LEFT_EYE'] = True
                roi['RIGHT_EYE'] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                tips = "請將頭抬起，保持頸椎平行於地面"
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_EYE] if key=='LEFT_EYE' else point3d[AngleNodeDef.RIGHT_EYE]
                pointsOut=[pointStart_x, pointStart_y,pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOuth
        elif key == side + 'ELBOW':
            if side == 'RIGHT_':
                elbow_x,_,_,elbow_vi =  (point3d[AngleNodeDef.RIGHT_ELBOW])
                shoulder_x,_,_,shoulder_vi =  (point3d[AngleNodeDef.RIGHT_SHOULDER])
            else:
                elbow_x,_,_,elbow_vi =  (point3d[AngleNodeDef.LEFT_ELBOW])
                shoulder_x,_,_,shoulder_vi =  (point3d[AngleNodeDef.LEFT_SHOULDER])
            if abs(elbow_x - shoulder_x) < 0.1 and angle_dict[key]>150:
                roi['RIGHT_ELBOW'] = True
                roi['LEFT_ELBOW'] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                roi['RIGHT_ELBOW'] = False
                roi['LEFT_ELBOW'] = False
                if side == 'RIGHT_' and elbow_x > shoulder_x:
                    tips = "請將手臂打直，並將手肘向後縮並確認手肘位置在肩關節下方"
                    pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_ELBOW]
                    pointsOut=[pointStart_x, pointStart_y, pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                elif side == 'LEFT_' and elbow_x < shoulder_x:
                    tips = "請將手臂打直，手肘向後縮並確認手肘位置在肩關節下方"
                    pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW]
                    pointsOut=[pointStart_x, pointStart_y, pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                elif side == 'LEFT_' and elbow_x > shoulder_x:
                    tips = "請將手臂打直，手肘向前移並確認手肘位置在肩關節下方"
                    pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW]
                    pointsOut=[pointStart_x, pointStart_y, pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                else:
                    tips = "請將手臂打直，手肘向前移並確認手肘位置在肩關節下方"
                    pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_ELBOW]
                    pointsOut=[pointStart_x, pointStart_y, pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
        elif key == side + 'SHOULDER':
            min_angle = 60
            max_angle = 85
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi['RIGHT_SHOULDER'] = True
                roi['LEFT_SHOULDER'] = True
                pointsOut = [] if tip_flag else pointsOut
            elif tip_flag == True:
                roi['RIGHT_SHOULDER'] = False
                roi['LEFT_SHOULDER'] = False
                if angle_dict[key] < min_angle:
                    tips = "請將身體向後移並確認手軸於肩膀下方，維持頸椎、胸椎、腰椎維持一直線平行於地面"
                    pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_ELBOW] if key=='RIGHT_SHOULDER' else point3d[AngleNodeDef.LEFT_ELBOW]
                    if key=='RIGHT_ELBOW':
                        pointsOut=[pointStart_x, pointStart_y, pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                    else:
                        pointsOut=[pointStart_x, pointStart_y, pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                else:
                    tips = "請將身體向前移並確認手軸於肩膀下方，維持頸椎、胸椎、腰椎維持一直線平行於地面"
                    pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_ELBOW] if key=='RIGHT_SHOULDER' else point3d[AngleNodeDef.LEFT_ELBOW]
                    if key=='RIGHT_ELBOW':
                        pointsOut=[pointStart_x, pointStart_y, pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y]  if tip_flag else pointsOut
                    else:
                        pointsOut=[pointStart_x, pointStart_y, pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y]  if tip_flag else pointsOut
        elif key == side + 'HIP':
            min_angle = 165
            _,nose_y,_,_ =  (point3d[AngleNodeDef.NOSE])
            _,left_hip_y,_,_ =  (point3d[AngleNodeDef.LEFT_HIP])
            _,right_hip_y,_,_ =  (point3d[AngleNodeDef.RIGHT_HIP])
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=min_angle and ((side=="RIGHT_"and (left_hip_y-nose_y)<=0.2) or (side=="LEFT_"and (right_hip_y-nose_y)<=0.2)):
                roi['RIGHT_HIP'] = True
                roi['LEFT_HIP'] = True
                pointsOut = [] if tip_flag else pointsOut
            elif angle_dict[key] < min_angle and tip_flag == True:
                roi['RIGHT_HIP'] = False
                roi['LEFT_HIP'] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_HIP] if key=='RIGHT_HIP' else point3d[AngleNodeDef.LEFT_HIP]
                pointsOut=[pointStart_x,pointStart_y,pointStart_x,pointStart_y+DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
                tips = "請將屁股稍微放下"
            elif ((side=="RIGHT_"and left_hip_y-nose_y>0.2) or (side=="LEFT_"and right_hip_y-nose_y>0.2)) and tip_flag == True:
                roi['RIGHT_HIP'] = False
                roi['LEFT_HIP'] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_HIP] if key=='RIGHT_HIP' else point3d[AngleNodeDef.LEFT_HIP]
                pointsOut=[pointStart_x,pointStart_y,pointStart_x,pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
                tips = "請將屁股稍微抬起"
        
    if tips == "":
        tips = "動作正確"
        pointsOut = []
    return roi, tips, pointsOut


def reversePlankPoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    """reverse plank pose rule


    Args:
        roi (list): region of interesting joint for reverse plank pose
        tips (str): tips
        sample_angle_dict (dict): sample angle dict
        angle_dict (dict): angle dict
        point3d (mediapipe): mediapipe detect result


    Returns:
        roi (dict)
        tips (str)
        pointsOut (list)
    """
    side = ""
    pointsOut = [] # (a,b): a -> b
    for key, _ in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        if key == 'NOSE':
            node_x,_,_,node_vi =  (point3d[AngleNodeDef.NOSE])
            left_hip_x,_,_,left_hip_vi =  (point3d[AngleNodeDef.LEFT_HIP])
            right_hip_x,_,_,right_hip_vi =  (point3d[AngleNodeDef.RIGHT_HIP])
            if node_vi < MIN_DETECT_VISIBILITY:
                roi[key] = False
                tips = "請將身體面向右方或左方坐下，並將雙手撐在肩膀下方，使上半身呈現斜線" if tip_flag else tips
                break
            if node_x>left_hip_x and node_x>right_hip_x:
                roi[key] = True
                side = "LEFT"
            elif node_x<left_hip_x and node_x<right_hip_x:
                roi[key] = True
                side = "RIGHT"
            else:
                roi[key] = False
                tips = "請將身體面向右方或左方坐下，並將雙手撐在肩膀下方，使上半身呈現斜線" if tip_flag else tips
                break
        if key == f"{side}_ELBOW":
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=min_angle:
                roi["LEFT_ELBOW"] = True
                roi["RIGHT_ELBOW"] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                roi["LEFT_ELBOW"] = False
                roi["RIGHT_ELBOW"] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW] if key=="LEFT_ELBOW" else point3d[AngleNodeDef.RIGHT_ELBOW]
                pointsOut=[pointStart_x, pointStart_y,pointStart_x, pointStart_y+DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
                tips = "請將雙手向後伸，指尖朝前，將手軸打直" if tip_flag else tips
        elif key == f"{side}_INDEX":
            tolerance_val=0.01
            index_x,_,_,index_vi =  (point3d[AngleNodeDef.RIGHT_INDEX])
            shoulder_x,_,_,shoulder_vi =  (point3d[AngleNodeDef.RIGHT_SHOULDER])
            if side == "LEFT":
                index_x,_,_,index_vi =  (point3d[AngleNodeDef.LEFT_INDEX])
                shoulder_x,_,_,shoulder_vi =  (point3d[AngleNodeDef.LEFT_SHOULDER])
            if index_x < shoulder_x+tolerance_val and side == "LEFT":
                roi["LEFT_INDEX"] = True
                roi["RIGHT_INDEX"] = True
                pointsOut = [] if tip_flag else pointsOut
            elif index_x+tolerance_val > shoulder_x and side == "RIGHT":
                roi["LEFT_INDEX"] = True
                roi["RIGHT_INDEX"] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                roi["LEFT_INDEX"] = False
                roi["RIGHT_INDEX"] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_WRIST] if key=="LEFT_INDEX" else point3d[AngleNodeDef.RIGHT_WRIST]
                if key=="LEFT_INDEX":
                    pointsOut=[pointStart_x, pointStart_y,pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y]  if tip_flag else pointsOut
                else:
                    pointsOut=[pointStart_x, pointStart_y,pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                tips = "請將雙手手指朝向臀部，並將手臂打直，垂直於地面" if tip_flag else tips
        elif key == f"{side}_WRIST":
            if(side=='RIGHT'):
                wrist_x,_,_,wrist_vi =  (point3d[AngleNodeDef.RIGHT_WRIST])
                elbow_x,_,_,elbow_x_vi =  (point3d[AngleNodeDef.RIGHT_ELBOW])
            else:
                wrist_x,_,_,wrist_vi =  (point3d[AngleNodeDef.LEFT_WRIST])
                elbow_x,_,_,elbow_x_vi =  (point3d[AngleNodeDef.LEFT_ELBOW])
            if wrist_vi< MIN_DETECT_VISIBILITY or  elbow_x_vi< MIN_DETECT_VISIBILITY:
                continue
            if abs(elbow_x-wrist_x)<0.15:
                roi["LEFT_WRIST"] = True
                roi["RIGHT_WRIST"] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                roi["LEFT_WRIST"] = False
                roi["RIGHT_WRIST"] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW] if key=="LEFT_WRIST" else point3d[AngleNodeDef.RIGHT_ELBOW]
                pointsOut=[pointStart_x, pointStart_y,pointStart_x, pointStart_y+DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
                tips = "請將手掌平貼於地面，讓肩膀、手軸、手腕成一直線垂直於地面" if tip_flag else tips
        elif key == f"{side}_SHOULDER":
            min_angle = 60
            max_angle = 80
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi["LEFT_SHOULDER"] = True
                roi["RIGHT_SHOULDER"] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                roi["LEFT_SHOULDER"] = False
                roi["RIGHT_SHOULDER"] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_HIP] if key=="LEFT_SHOULDER" else point3d[AngleNodeDef.RIGHT_HIP]
                pointsOut=[pointStart_x, pointStart_y,pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
                tips = "將臀部抬起，胸往前挺，使脊椎保持一直線" if tip_flag else tips
        elif key == f"{side}_HIP":
            tolerance_val = 5
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=min_angle:
                roi["LEFT_HIP"] = True
                roi["RIGHT_HIP"] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                roi["LEFT_HIP"] = False
                roi["RIGHT_HIP"] = False
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_HIP] if key=="LEFT_HIP" else point3d[AngleNodeDef.RIGHT_HIP]
                pointsOut=[pointStart_x, pointStart_y,pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
                tips = "請將臀部抬高一些，使身體保持一直線" if tip_flag else tips
        elif key == f"{side}_KNEE":
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=min_angle:
                roi["LEFT_KNEE"] = True
                roi["RIGHT_KNEE"] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                roi["LEFT_KNEE"] = False
                roi["RIGHT_KNEE"] = False
                tips = "請將雙腳膝蓋打直，使身體保持一直線" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_KNEE] if key=="LEFT_KNEE" else point3d[AngleNodeDef.RIGHT_KNEE]
                pointStart_x_end, pointStart_y_end, pointStart_z_end, _ = point3d[AngleNodeDef.LEFT_ANKLE] if key=="LEFT_KNEE" else point3d[AngleNodeDef.RIGHT_ANKLE]
                pointsOut=[pointStart_x, pointStart_y,pointStart_x_end, pointStart_y_end] if tip_flag else pointsOut
    if tips == "":
        tips = "動作正確"
        pointsOut = []
    return roi, tips, pointsOut


def ChildsPoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    """child's pose rule


    Args:
        roi (list): region of interesting joint for child's pose
        tips (str): tips
        sample_angle_dict (dict): sample angle dict
        angle_dict (dict): angle dict
        point3d (mediapipe): mediapipe detect result
    
    
    Returns:
        roi (dict)
        tips (str)
        pointsOut (list)
    """
    side = ""
    pointsOut=[]
    for key, _ in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        #detect the side for the pose
        if key == 'NOSE':
            nose_x,_,_,nose_vi =  (point3d[AngleNodeDef.NOSE])
            left_hip_x,_,left_hip_z,left_hip_vi =  (point3d[AngleNodeDef.LEFT_HIP])
            left_knee_x,_,left_knee_y,left_knee_vi =  (point3d[AngleNodeDef.LEFT_KNEE])
            right_hip_x,_,right_hip_z,right_hip_vi =  (point3d[AngleNodeDef.RIGHT_HIP])
            right_knee_x,_,right_knee_y,right_knee_vi =  (point3d[AngleNodeDef.RIGHT_KNEE])
            if  (nose_x<right_hip_x and nose_x<left_hip_x) or (right_knee_x<right_hip_x and abs(right_knee_x-right_hip_x)>0.2):
                roi[key] = True
                side = "RIGHT"
            elif (left_hip_x<nose_x and right_hip_x<nose_x) or (left_knee_x>left_hip_x and abs(left_hip_x-left_knee_x)>0.2):
                roi[key] = True
                side = "LEFT"
            else:
                roi[key] = False
                tips = "請將身體面向右方或左方以跪姿坐下" if tip_flag else tips
                break

        if key == f'{side}_KNEE':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]<=40:
                roi["LEFT_KNEE"] = True
                roi["RIGHT_KNEE"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_KNEE"] = False
                roi["RIGHT_KNEE"] = False
                tips = "請確認雙腿是否已經屈膝" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_KNEE] if key=="LEFT_KNEE" else point3d[AngleNodeDef.RIGHT_KNEE]
                pointsOut = [pointStart_x, pointStart_y+DISPLACEMENT_DISTANCE, pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key == f'{side}_HIP':
            tolerance_val = 10
            max_angle = sample_angle_dict[key] + tolerance_val
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]<=60:
                roi["LEFT_HIP"] = True
                roi["RIGHT_HIP"] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                roi["LEFT_HIP"] = False
                roi["RIGHT_HIP"] = False
                tips = "請確認是否已經將身體向前趴下" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_HIP] if key=="LEFT_HIP" else point3d[AngleNodeDef.LEFT_HIP]
                pointsOut = [pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE, pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key == f'{side}_SHOULDER':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=120:
                roi["LEFT_SHOULDER"] = True
                roi["RIGHT_SHOULDER"] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                roi["LEFT_SHOULDER"] = False
                roi["RIGHT_SHOULDER"] = False
                tips = "請確認是否已經將手臂向上舉直" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW] if key=="LEFT_SHOULDER" else point3d[AngleNodeDef.RIGHT_ELBOW]
                if key=="LEFT_SHOULDER":
                    pointsOut = [pointStart_x, pointStart_y,pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                else:
                    pointsOut = [pointStart_x, pointStart_y,pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
        elif key == f'{side}_ELBOW':
            if(side=='LEFT'):
                _,knee_y,_,knee_vi =  (point3d[AngleNodeDef.LEFT_KNEE])
                _,elbow_y,_,elbow_vi =  (point3d[AngleNodeDef.LEFT_ELBOW])
            else:
                _,knee_y,_,knee_vi =  (point3d[AngleNodeDef.RIGHT_KNEE])
                _,elbow_y,_,elbow_vi =  (point3d[AngleNodeDef.RIGHT_ELBOW])

            if angle_dict[key] == -1 or knee_vi<0.7 or elbow_vi<0.7:
                continue
            if angle_dict[key]>=130 and abs(knee_y-elbow_y)<0.2:
                roi["LEFT_ELBOW"] = True
                roi["RIGHT_ELBOW"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_ELBOW"] = False
                roi["RIGHT_ELBOW"] = False
                tips = "請確認是否已經將手臂向前伸直"   if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW] if key=="LEFT_ELBOW" else point3d[AngleNodeDef.RIGHT_ELBOW]
                pointsOut = [pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE,pointStart_x, pointStart_y] if tip_flag else pointsOut
    if tips == "":
        tips = "動作正確 ! "
        pointsOut=[] if tip_flag else pointsOut
    return roi, tips, pointsOut


def DownwardDogRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    """Downward dog's pose rule
    
    
    Args:
        roi (list): region of interesting joint for DownwardDog's pose
        tips (str): tips
        sample_angle_dict (dict): sample angle dict
        angle_dict (dict): angle dict
        point3d (mediapipe): mediapipe detect result
    
    
    Returns:
        roi (dict)
        tips (str)
        pointsOut (list)
    """
    side = ""
    pointsOut=[]
    for key, _ in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        #detect the side for the pose
        if key == 'NOSE':
            node_x,_,_,node_vi =  (point3d[AngleNodeDef.NOSE])
            left_hip_x,_,_,left_hip_vi =  (point3d[AngleNodeDef.LEFT_HIP])
            right_hip_x,_,_,right_hip_vi =  (point3d[AngleNodeDef.RIGHT_HIP])
            if node_vi < MIN_DETECT_VISIBILITY :
                roi[key] = False
                tips = "請將身體面向右方或左方雙膝跪地，再用雙手撐地將臀部向上撐起成倒V字型" if tip_flag else tips
                break
            else:
                if node_x>left_hip_x and node_x>right_hip_x:
                    roi[key] = True
                    side = "RIGHT"
                elif node_x<left_hip_x and node_x<right_hip_x:
                    roi[key] = True
                    side = "LEFT"
                else:
                    roi[key] = False
                    tips = "請將身體面向右方或左方雙膝跪地，再用雙手撐地將臀部向上撐起成倒V字型" if tip_flag else tips
                    break
        if key == f'{side}_SHOULDER':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=120:
                roi["LEFT_SHOULDER"] = True
                roi["RIGHT_SHOULDER"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_SHOULDER"] = False
                roi["RIGHT_SHOULDER"] = False
                tips = "請確認是否已經將手臂打直，並將臀部向上撐起" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_SHOULDER] if key=="LEFT_SHOULDER" else point3d[AngleNodeDef.RIGHT_SHOULDER]
                if key=="LEFT_SHOULDER":
                    pointsOut= [pointStart_x, pointStart_y,pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y+DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
                else:
                    pointsOut= [pointStart_x, pointStart_y,pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y+DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
        elif key == f'{side}_ELBOW':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=100:
                roi["LEFT_ELBOW"] = True
                roi["RIGHT_ELBOW"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_ELBOW"] = False
                roi["RIGHT_ELBOW"] = False
                tips = "請確認手掌是否已經貼至地面"   if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_WRIST] if key=="LEFT_ELBOW" else point3d[AngleNodeDef.RIGHT_WRIST]
                pointsOut = [pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE ,pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key == f'{side}_HIP':
            tolerance_val = 10
            min_angle = sample_angle_dict[key]-tolerance_val
            max_angle = sample_angle_dict[key]+tolerance_val
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=min_angle and angle_dict[key]<=max_angle:
                roi["LEFT_HIP"] = True
                roi["RIGHT_HIP"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_HIP"] = False
                roi["RIGHT_HIP"] = False
                tips = "請確認是否已經將身體向下伸展且把背打直, 呈現倒v字型" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_SHOULDER] if key=="LEFT_HIP" else point3d[AngleNodeDef.RIGHT_SHOULDER]
                pointsOut = [pointStart_x, pointStart_y ,pointStart_x, pointStart_y+DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
        elif key == f'{side}_KNEE':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=150:
                roi["LEFT_KNEE"] = True
                roi["RIGHT_KNEE"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_KNEE"] = False
                roi["RIGHT_KNEE"] = False
                tips = "請確認雙腿是否已經打直" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_HIP] if key=="LEFT_KNEE" else point3d[AngleNodeDef.RIGHT_HIP]
                pointStart_x_end, pointStart_y_end, pointStart_z_end, _= point3d[AngleNodeDef.LEFT_ANKLE] if key=="LEFT_KNEE" else point3d[AngleNodeDef.RIGHT_ANKLE]
                pointsOut = [pointStart_x, pointStart_y ,pointStart_x_end, pointStart_y_end] if tip_flag else pointsOut
        elif key == f'{side}_ANKLE':
            if(side=='LEFT'):
                _,index_y,_,index_vi =  (point3d[AngleNodeDef.LEFT_FOOT_INDEX])
                _,heel_y,_,heel_vi = (point3d[AngleNodeDef.LEFT_HEEL])
            else:
                _,index_y,_,index_vi =  (point3d[AngleNodeDef.RIGHT_FOOT_INDEX])
                _,heel_y,_,heel_vi = (point3d[AngleNodeDef.RIGHT_HEEL])
            if heel_vi<MIN_DETECT_VISIBILITY or index_vi<MIN_DETECT_VISIBILITY:
                continue
            if abs(index_y-heel_y)<0.1:
                roi["LEFT_ANKLE"] = True
                roi["RIGHT_ANKLE"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_ANKLE"] = False
                roi["RIGHT_ANKLE"] = False
                tips = "請確認腳跟是否已經貼地" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ANKLE] if key=="LEFT_ANKLE" else point3d[AngleNodeDef.RIGHT_ANKLE]
                pointsOut = [pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE ,pointStart_x, pointStart_y] if tip_flag else pointsOut
    if tips == "":
        tips = "動作正確 ! "
        pointsOut=[] if tip_flag else pointsOut
    return roi, tips, pointsOut


def LowLungeRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    """Low Lunge pose rule


    Args:
        roi (list): region of interesting joint for Low Lunge pose
        tips (str): tips
        sample_angle_dict (dict): sample angle dict
        angle_dict (dict): angle dict
        point3d (mediapipe): mediapipe detect result


    Returns:
        roi (dict)
        tips (str)
        pointsOut (list)
    """
    side = ""
    side_back = ""
    pointsOut=[]
    direction=""
    direction_back=""
    for key, _ in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        #detect the side for the pose
        if key == 'NOSE':
            nose_x,_,_,left_knee_vi = point3d[AngleNodeDef.NOSE]
            left_knee_x,left_knee_y,_,left_knee_vi = point3d[AngleNodeDef.LEFT_SHOULDER]
            right_knee_x,right_knee_y,_,right_knee_vi = point3d[AngleNodeDef.RIGHT_SHOULDER]
            if left_knee_vi <MIN_DETECT_VISIBILITY or right_knee_vi <MIN_DETECT_VISIBILITY:
                roi[key] = False
                tips = "請將身體面向右方或左方成低弓箭步姿，並將雙手向上舉起" if tip_flag else tips
                break
            else:
                if right_knee_x>nose_x and left_knee_x>nose_x:
                    roi[key] = True
                    side = "RIGHT"
                    side_back = "LEFT"
                    direction="左"
                    direction_back="右"
                elif right_knee_x<nose_x and left_knee_x<nose_x:
                    roi[key] = True
                    side = "LEFT"
                    side_back = "RIGHT"
                    direction="右"
                    direction_back="左"
                else:
                    roi[key] = False
                    tips = "請將身體面向右方或左方成低弓箭步姿，並將雙手向上舉起" if tip_flag else tips
                    break
        if key == f'{side}_KNEE':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=100:
                roi[f"{side}_KNEE"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi[f"{side}_KNEE"] = False
                tips = f"請確認是否將{direction}腳向後伸" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_KNEE] if key=="LEFT_KNEE" else point3d[AngleNodeDef.RIGHT_KNEE]
                pointsOut = [pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE ,pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key == f"{side_back}_KNEE":
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]<=90:
                roi[f"{side_back}_KNEE"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi[f"{side_back}_KNEE"] = False
                tips = f"請確認是否已經將{direction_back}腳屈膝" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_KNEE] if key=="LEFT_KNEE" else point3d[AngleNodeDef.RIGHT_KNEE]
                pointsOut = [pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE ,pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key == f'{side}_HIP':
            if(side=='LEFT'):
                _,hip_y,_,hip_vi = point3d[AngleNodeDef.LEFT_HIP]
            else:
                _,hip_y,_,hip_vi = point3d[AngleNodeDef.RIGHT_HIP]
            _,knee_l_y,_,knee_vi = point3d[AngleNodeDef.LEFT_KNEE]
            _,knee_r_y,_,knee_vi = point3d[AngleNodeDef.RIGHT_KNEE]
            if hip_vi<MIN_DETECT_VISIBILITY or knee_vi<MIN_DETECT_VISIBILITY:
                continue
            if (knee_l_y<=hip_y and hip_y<=knee_r_y) or ((knee_l_y>=hip_y and hip_y>=knee_r_y)):
                roi[f"{side}_HIP"] = True
                roi[f"{side_back}_HIP"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi[f"{side}_HIP"] = False
                roi[f"{side_back}_HIP"] = False
                tips = f"請確認是否已經將{direction}腳向後伸，上半身向下壓低" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_HIP] if key=="LEFT_HIP" else point3d[AngleNodeDef.RIGHT_HIP]
                pointsOut = [pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE ,pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key == f'{side}_SHOULDER':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=130:
                roi["LEFT_SHOULDER"] = True
                roi["RIGHT_SHOULDER"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_SHOULDER"] = False
                roi["RIGHT_SHOULDER"] = False
                tips = "請確認是否已經將手臂向上打直" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_SHOULDER] if key=="LEFT_SHOULDER" else point3d[AngleNodeDef.RIGHT_SHOULDER]
                pointStart_x_end, pointStart_y_end, pointStart_z_end, _= point3d[AngleNodeDef.LEFT_WRIST] if key=="LEFT_WRIST" else point3d[AngleNodeDef.RIGHT_WRIST]
                pointsOut = [pointStart_x, pointStart_y ,pointStart_x_end, pointStart_y_end] if tip_flag else pointsOut
        elif key == f'{side}_ELBOW':
            _,nose_y,_,nose_vi = point3d[AngleNodeDef.NOSE]
            _,r_elbow_y,_,r_elbow_vi = point3d[AngleNodeDef.RIGHT_ELBOW]
            _,l_elbow_y,_,l_elbow_vi = point3d[AngleNodeDef.LEFT_ELBOW]
            if nose_vi < MIN_DETECT_VISIBILITY:
                continue
            if r_elbow_y<=nose_y or l_elbow_y<=nose_y:
                roi["LEFT_ELBOW"] = True
                roi["RIGHT_ELBOW"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_ELBOW"] = False
                roi["RIGHT_ELBOW"] = False
                tips = "請確認手掌是否已經將手臂打直且舉高過頭"   if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW] if key=="LEFT_ELBOW" else point3d[AngleNodeDef.RIGHT_ELBOW]
                pointsOut = [pointStart_x, pointStart_y ,pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
    if tips == "":
        tips = "動作正確"
        pointsOut=[]
    return roi, tips, pointsOut


def SeatedForwardBendRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    """Seated Forward Bend pose rule


    Args:
        roi (list): region of interesting joint for Seated Forward Bend pose
        tips (str): tips
        sample_angle_dict (dict): sample angle dict
        angle_dict (dict): angle dict
        point3d (mediapipe): mediapipe detect result


    Returns:
        roi (dict)
        tips (str)
        pointsOut (list)
    """
    side = "LEFT"
    pointsOut=[]
    for key, _ in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        #detect the side for the pose
        if key == 'NOSE':
            node_x,_,_,node_vi =  (point3d[AngleNodeDef.NOSE])
            left_shoulder_x,_,_,left_shoulder_vi =  (point3d[AngleNodeDef.LEFT_SHOULDER])
            right_shoulder_x,_,_,right_shoulder_vi =  (point3d[AngleNodeDef.RIGHT_SHOULDER])
            if node_vi < MIN_DETECT_VISIBILITY:
                roi[key] = False
                tips = "請將身體面向右方或左方坐下，並將腳伸直" if tip_flag else tips
                break
            else:
                if node_x>left_shoulder_x and node_x>right_shoulder_x:
                    roi[key] = True
                    side = "RIGHT"
                elif node_x<left_shoulder_x and node_x<right_shoulder_x:
                    roi[key] = True
                    side = "LEFT"
                else:
                    roi[key] = False
                    tips = "請將身體面向右方或左方坐下，並將腳伸直" if tip_flag else tips
                    break
        if key == f'{side}_KNEE':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=150:
                roi["LEFT_KNEE"] = True
                roi["RIGHT_KNEE"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_KNEE"] = False
                roi["RIGHT_KNEE"] = False
                tips = "請確認是否已經將雙腳向前伸直" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_KNEE] if key=="LEFT_KNEE" else point3d[AngleNodeDef.RIGHT_KNEE]
                if key=="LEFT_KNEE":
                    pointsOut = [pointStart_x, pointStart_y ,pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                else:
                    pointsOut = [pointStart_x, pointStart_y ,pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
        elif key == f'{side}_SHOULDER':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=80 and angle_dict[key]<100:
                roi["LEFT_SHOULDER"] = True
                roi["RIGHT_SHOULDER"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_SHOULDER"] = False
                roi["RIGHT_SHOULDER"] = False
                tips = "請確認是否已經將身體向前彎曲，並將手臂向前伸" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW] if key=="LEFT_SHOULDER" else point3d[AngleNodeDef.RIGHT_ELBOW]
                if key=="LEFT_SHOULDER":
                    pointsOut = [pointStart_x, pointStart_y ,pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y]  if tip_flag else pointsOut
                else:
                    pointsOut = [pointStart_x, pointStart_y ,pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y]  if tip_flag else pointsOut
        elif key == f'{side}_ELBOW':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=150:
                roi["LEFT_ELBOW"] = True
                roi["RIGHT_ELBOW"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_ELBOW"] = False
                roi["RIGHT_ELBOW"] = False
                tips = "請確認是否已經將手臂打直" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW] if key=="LEFT_ELBOW" else point3d[AngleNodeDef.RIGHT_ELBOW]
                if key=="LEFT_ELBOW":
                    pointsOut = [pointStart_x, pointStart_y ,pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y]  if tip_flag else pointsOut
                else:
                    pointsOut = [pointStart_x, pointStart_y ,pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y]  if tip_flag else pointsOut
        elif key == f'{side}_HIP':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]<=75:
                roi["LEFT_HIP"] = True
                roi["RIGHT_HIP"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_HIP"] = False
                roi["RIGHT_HIP"] = False
                tips = "請確認是否已經將身體向前彎，盡量碰觸到腳板" if tip_flag else tips
                pointStart_x_1, pointStart_y_1, _, _ = point3d[AngleNodeDef.LEFT_HIP] if key=="LEFT_HIP" else point3d[AngleNodeDef.RIGHT_HIP]
                pointStart_x_2, pointStart_y_2, _, _ = point3d[AngleNodeDef.LEFT_SHOULDER] if key=="LEFT_HIP" else point3d[AngleNodeDef.RIGHT_SHOULDER]
                pointStart_x = (pointStart_x_1+pointStart_x_2)/2.0
                pointStart_y = (pointStart_y_1+pointStart_y_2)/2.0
                if key=="LEFT_HIP":
                    pointsOut = [pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y+DISPLACEMENT_DISTANCE ,pointStart_x, pointStart_y] if tip_flag else pointsOut
                else:
                    pointsOut = [pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y-DISPLACEMENT_DISTANCE ,pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key == f'{side}_KNEE':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=150:
                roi["LEFT_KNEE"] = True
                roi["RIGHT_KNEE"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_KNEE"] = False
                roi["RIGHT_KNEE"] = False
                tips = "請確認是否已經將雙腳向前伸直" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_KNEE] if key=="LEFT_KNEE" else point3d[AngleNodeDef.RIGHT_KNEE]

                if key=="LEFT_KNEE":
                    pointsOut = [pointStart_x, pointStart_y ,pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                else:
                    pointsOut = [pointStart_x, pointStart_y ,pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
        elif key == f"{side}_ANKLE":
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]<=145:
                roi["LEFT_ANKLE"] = True
                roi["RIGHT_ANKLE"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_ANKLE"] = False
                roi["RIGHT_ANKLE"] = False
                tips = "請確認是否將腳踝輕微勾回" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_FOOT_INDEX] if key=="LEFT_ANKLE" else point3d[AngleNodeDef.RIGHT_FOOT_INDEX]
                if key=="LEFT_ANKLE":
                    pointsOut = [pointStart_x, pointStart_y ,pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y]  if tip_flag else pointsOut
                else:
                    pointsOut = [pointStart_x, pointStart_y ,pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y]  if tip_flag else pointsOut
    if tips == "":
        tips = "動作正確"
        pointsOut=[]
    return roi, tips, pointsOut

def BridgeRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    """Bridge pose rule


    Args:
        roi (list): region of interesting joint for Bridge pose
        tips (str): tips
        sample_angle_dict (dict): sample angle dict
        angle_dict (dict): angle dict
        point3d (mediapipe): mediapipe detect result


    Returns:
        roi (dict)
        tips (str)
        pointsOut (list)
    """
    side = ""
    pointsOut=[]
    for key, _ in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        #detect the side for the pose
        if key == 'NOSE':
            node_x,_,_,node_vi =  (point3d[AngleNodeDef.NOSE])
            left_shoulder_x,_,_,left_shoulder_vi  =  (point3d[AngleNodeDef.LEFT_SHOULDER])
            right_shoulder_x,_,_,right_shoulder_vi =  (point3d[AngleNodeDef.RIGHT_SHOULDER])
            if node_vi < MIN_DETECT_VISIBILITY:
                roi[key] = False
                tips = "請將身體平躺下，並將雙手放置於身體兩側" if tip_flag else tips
                break
            else:
                if node_x>left_shoulder_x and node_x>right_shoulder_x:
                    roi[key] = True
                    side = "LEFT"
                elif node_x<left_shoulder_x and node_x<right_shoulder_x:
                    roi[key] = True
                    side = "RIGHT"
                else:
                    roi[key] = False
                    tips = "請將身體平躺下，並將雙手放置於身體兩側" if tip_flag else tips
                    break
        if key == f'{side}_KNEE':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]<=80:
                roi["LEFT_KNEE"] = True
                roi["RIGHT_KNEE"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_KNEE"] = False
                roi["RIGHT_KNEE"] = False
                tips = "請確認是否已經將雙腳屈膝" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_KNEE] if key=="LEFT_KNEE" else point3d[AngleNodeDef.RIGHT_KNEE]
                pointsOut = [pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE ,pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key == f'{side}_ELBOW':
            tolerance_val = 25
            min_angle = sample_angle_dict[key]-tolerance_val
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=min_angle:
                roi["LEFT_ELBOW"] = True
                roi["RIGHT_ELBOW"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_ELBOW"] = False
                roi["RIGHT_ELBOW"] = False
                tips = "請確認手掌是否已經貼至地面"   if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_WRIST] if key=="LEFT_ELBOW" else point3d[AngleNodeDef.RIGHT_WRIST]
                pointsOut = [pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE ,pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key == f'{side}_SHOULDER':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]<=45:
                roi["LEFT_SHOULDER"] = True
                roi["RIGHT_SHOULDER"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_SHOULDER"] = False
                roi["RIGHT_SHOULDER"] = False
                tips = "請利用核心力量將臀部撐起" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_HIP] if key=="LEFT_SHOULDER" else point3d[AngleNodeDef.RIGHT_HIP]
                pointsOut = [pointStart_x, pointStart_y ,pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
        elif key == f'{side}_HIP':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=150:
                roi["LEFT_HIP"] = True
                roi["RIGHT_HIP"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_HIP"] = False
                roi["RIGHT_HIP"] = False
                tips = "請確認是否已經將身體挺直，並與大腿形成一條直線" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_SHOULDER] if key=="LEFT_HIP" else point3d[AngleNodeDef.RIGHT_SHOULDER]
                pointStart_x_end, pointStart_y_end,_,_= point3d[AngleNodeDef.LEFT_KNEE] if key=="LEFT_HIP" else point3d[AngleNodeDef.RIGHT_KNEE]
                pointsOut = [pointStart_x, pointStart_y ,pointStart_x_end, pointStart_y_end] if tip_flag else pointsOut
    if tips == "":
        tips = "動作正確"
        pointsOut=[]
    return roi, tips, pointsOut

def PyramidRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    """Pyramid pose rule


    Args:
        roi (list): region of interesting joint for Pyramid pose
        tips (str): tips
        sample_angle_dict (dict): sample angle dict
        angle_dict (dict): angle dict
        point3d (mediapipe): mediapipe detect result

        
    Returns:
        roi (dict)
        tips (str)
        pointsOut (list)
    """
    side = ""
    pointsOut=[]
    for key, _ in roi.items():
        tip_flag = False
        if tips == "":
            tip_flag = True
        #detect the side for the pose
        if key == 'NOSE':
            node_x,_,_,node_vi =  (point3d[AngleNodeDef.NOSE])
            left_shoulder_x,_,_,left_shoulder_vi  =  (point3d[AngleNodeDef.LEFT_SHOULDER])
            right_shoulder_x,_,_,right_shoulder_vi =  (point3d[AngleNodeDef.RIGHT_SHOULDER])
            if node_vi < MIN_DETECT_VISIBILITY:
                roi[key] = False
                tips = "請將身體面向左方或右方，將其中一隻腳向前跨，並將雙腿打直" if tip_flag else tips
                break
            else:
                if node_x>left_shoulder_x and node_x>right_shoulder_x:
                    roi[key] = True
                    side = "RIGHT"
                elif node_x<left_shoulder_x and node_x<right_shoulder_x:
                    roi[key] = True
                    side = "LEFT"
                else:
                    roi[key] = False
                    tips = "請將身體面向左方或右方，將其中一隻腳向前跨，並將雙腿打直" if tip_flag else tips
                    break
        if key == 'LEG_ANKLE':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]<=90:
                roi["LEG"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEG"] = False
                tips = "請確認是否已經將其中一隻腳向前跨" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_KNEE] if side=="LEFT" else point3d[AngleNodeDef.RIGHT_KNEE]
                if key=="LEFT_KNEE":
                    pointsOut = [pointStart_x, pointStart_y ,pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
                else:
                    pointsOut = [pointStart_x, pointStart_y ,pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
        elif key == f'{side}_HIP':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]<=110:
                roi["LEFT_HIP"] = True
                roi["RIGHT_HIP"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_HIP"] = False
                roi["RIGHT_HIP"] = False
                tips = "請確認是否已經將身體向前腳彎曲" if tip_flag else tips
                pointStart_x_1, pointStart_y_1, _, _ = point3d[AngleNodeDef.LEFT_HIP] if key=="LEFT_HIP" else point3d[AngleNodeDef.RIGHT_HIP]
                pointStart_x_2, pointStart_y_2, _, _ = point3d[AngleNodeDef.LEFT_SHOULDER] if key=="LEFT_HIP" else point3d[AngleNodeDef.RIGHT_SHOULDER]
                pointStart_x = (pointStart_x_1+pointStart_x_2)/2.0
                pointStart_y = (pointStart_y_1+pointStart_y_2)/2.0
                if key=="LEFT_HIP":
                    pointsOut = [pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y-DISPLACEMENT_DISTANCE ,pointStart_x, pointStart_y] if tip_flag else pointsOut
                else:
                    pointsOut = [pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
        elif key == f'{side}_KNEE':
            tolerance_val = 20
            min_angle = sample_angle_dict[key]-tolerance_val
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=min_angle:
                roi["LEFT_KNEE"] = True
                roi["RIGHT_KNEE"] = True
                pointsOut=[]  if tip_flag else pointsOut
            else:
                roi["LEFT_KNEE"] = False
                roi["RIGHT_KNEE"] = False
                tips = "請確認是否已經將雙腳打直" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_HIP] if key=="LEFT_KNEE" else point3d[AngleNodeDef.RIGHT_HIP]
                pointStart_x_end, pointStart_y_end,_,_= point3d[AngleNodeDef.LEFT_ANKLE] if key=="LEFT_KNEE" else point3d[AngleNodeDef.RIGHT_ANKLE]
                pointsOut = [pointStart_x, pointStart_y ,pointStart_x_end, pointStart_y_end] if tip_flag else pointsOut
        elif key == f'{side}_SHOULDER':
            if(side=='LEFT'):
                _,index_y,_,index_vi =  (point3d[AngleNodeDef.LEFT_INDEX])
                _,ankle_y,_,ankle_vi = (point3d[AngleNodeDef.LEFT_ANKLE])
            else:
                _,index_y,_,index_vi =  (point3d[AngleNodeDef.RIGHT_INDEX])
                _,ankle_y,_,ankle_vi = (point3d[AngleNodeDef.RIGHT_ANKLE])

            if index_vi<0.7 or ankle_vi<0.7:
                continue
            if ankle_y<=index_y+0.2:
                roi["LEFT_SHOULDER"] = True
                roi["RIGHT_SHOULDER"] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                roi["LEFT_SHOULDER"] = False
                roi["RIGHT_SHOULDER"] = False
                tips = "請確認是否已經將手臂放置於前腳兩側，小心不要遮擋到腳踝視線" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_SHOULDER] if key=="LEFT_SHOULDER" else point3d[AngleNodeDef.RIGHT_SHOULDER]
                pointStart_x_end, pointStart_y_end,_,_= point3d[AngleNodeDef.LEFT_WRIST] if key=="LEFT_SHOULDER" else point3d[AngleNodeDef.RIGHT_WRIST]
                pointsOut = [pointStart_x, pointStart_y ,pointStart_x_end, pointStart_y_end] if tip_flag else pointsOut
        elif key == f'{side}_ELBOW':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=90:
                roi["LEFT_ELBOW"] = True
                roi["RIGHT_ELBOW"] = True
                pointsOut = [] if tip_flag else pointsOut
            else:
                roi["LEFT_ELBOW"] = False
                roi["RIGHT_ELBOW"] = False
                tips = "請確認手臂是否已經向下伸直"   if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_SHOULDER] if key=="LEFT_SHOULDER" else point3d[AngleNodeDef.RIGHT_SHOULDER]
                pointStart_x_end, pointStart_y_end,_,_= point3d[AngleNodeDef.LEFT_WRIST] if key=="LEFT_SHOULDER" else point3d[AngleNodeDef.RIGHT_WRIST]
                pointsOut = [pointStart_x, pointStart_y ,pointStart_x_end, pointStart_y_end] if tip_flag else pointsOut
    if tips == "":
        tips = "動作正確"
        pointsOut = []
    return roi, tips, pointsOut

def MountainPoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    """Mountain pose rule

    Args:
        roi (list): region of interesting joint for Mountain pose
        tips (str): tips
        sample_angle_dict (dict): sample angle dict
        angle_dict (dict): angle dict
        point3d (mediapipe): mediapipe detect result

    Returns:
        roi (dict)
        tips (str)
        pointsOut (list)
    """
    pointsOut = []
    tip_flag = False

    if tips == "":
        tip_flag = True

    for key, _ in roi.items():
        if key == 'NOSE':
            nose_y, _, _, nose_vi = (point3d[AngleNodeDef.NOSE])
            left_hip_y, _, _, left_hip_vi = (point3d[AngleNodeDef.LEFT_HIP])
            right_hip_y, _, _, right_hip_vi = (point3d[AngleNodeDef.RIGHT_HIP])

            if nose_vi < MIN_DETECT_VISIBILITY:
                roi[key] = False
                tips = "請確保頭部正直且面向前方" if tip_flag else tips
                break
            else:
                if abs(nose_y - (left_hip_y + right_hip_y) / 2.0) <= 0.1:
                    roi[key] = True
                else:
                    roi[key] = False
                    tips = "請確保頭部正直且面向前方" if tip_flag else tips

        if key == 'LEFT_SHOULDER' or key == 'RIGHT_SHOULDER':
            if angle_dict[key] == -1:
                continue
            if 80 <= angle_dict[key] <= 100:
                roi[key] = True
            else:
                roi[key] = False
                tips = "請保持雙肩平行放置" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_SHOULDER] if key=="LEFT_SHOULDER" else point3d[AngleNodeDef.RIGHT_SHOULDER]
                pointsOut = [pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y, pointStart_x, pointStart_y] if key=="LEFT_SHOULDER" else [pointStart_x, pointStart_y, pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] 

        if key == 'LEFT_ELBOW' or key == 'RIGHT_ELBOW':
            if angle_dict[key] == -1:
                continue
            if angle_dict[key] >= 160:
                roi[key] = True
            else:
                roi[key] = False
                tips = "請將雙臂伸直，放置身體兩側，並將手掌朝向前方" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW] if key=="LEFT_ELBOW" else point3d[AngleNodeDef.RIGHT_ELBOW]
                pointsOut = [pointStart_x, pointStart_y, pointStart_x, pointStart_y+DISPLACEMENT_DISTANCE]

        if key == 'LEFT_HIP' or key == 'RIGHT_HIP':
            if angle_dict[key] == -1:
                continue
            if 80 <= angle_dict[key] <= 100:
                roi[key] = True
            else:
                roi[key] = False
                tips = "請將身體保持直立" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_HIP] if key=="LEFT_HIP" else point3d[AngleNodeDef.RIGHT_HIP]
                pointsOut = [pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE, pointStart_x, pointStart_y+DISPLACEMENT_DISTANCE]

        if key == 'LEFT_KNEE' or key == 'RIGHT_KNEE':
            if angle_dict[key] == -1:
                continue
            if angle_dict[key] >= 160:
                roi[key] = True
            else:
                roi[key] = False
                tips = "請將雙腿伸直併攏" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_KNEE] if key=="LEFT_KNEE" else point3d[AngleNodeDef.RIGHT_KNEE]
                pointsOut = [pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE, pointStart_x, pointStart_y+DISPLACEMENT_DISTANCE]

        if key == 'LEFT_ANKLE' or key == 'RIGHT_ANKLE':
            left_ankle_y, _, _, left_ankle_vi = (point3d[AngleNodeDef.LEFT_ANKLE])
            right_ankle_y, _, _, right_ankle_vi = (point3d[AngleNodeDef.RIGHT_ANKLE])

            if left_ankle_vi < MIN_DETECT_VISIBILITY or right_ankle_vi < MIN_DETECT_VISIBILITY:
                roi[key] = False
                tips = "請確保腳踝仍在鏡頭範圍內" if tip_flag else tips
                break
            else:
                if abs(left_ankle_y - right_ankle_y) <= 0.05:
                    roi[key] = True
                else:
                    roi[key] = False
                    tips = "請保持雙腳平行且腳後跟接觸地面" if tip_flag else tips
                    pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ANKLE] if key=="LEFT_ANKLE" else point3d[AngleNodeDef.RIGHT_ANKLE]
                    pointsOut = [pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y, pointStart_x, pointStart_y] if key=="LEFT_ANKLE" else [pointStart_x, pointStart_y, pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] 

    if tips == "":
        tips = "動作正確"
        pointsOut = []

    return roi, tips, pointsOut

def TrianglePoseRule(roi, tips, sample_angle_dict, angle_dict, point3d):
    """Triangle pose rule

    Args:
        roi (list): region of interesting joint for Triangle pose
        tips (str): tips
        sample_angle_dict (dict): sample angle dict
        angle_dict (dict): angle dict
        point3d (mediapipe): mediapipe detect result

    Returns:
        roi (dict)
        tips (str)
        pointsOut (list)
    """
    side = ""
    pointsOut = []
    tip_flag = False

    if tips == "":
        tip_flag = True

    for key, _ in roi.items():
        if key == 'LEFT_HIP':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=45 and angle_dict[key]<=100:
                roi["LEFT_HIP"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_HIP"] = False
                tips = "請確認是否已經將右腳向右跨，使雙腳呈現大字型" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_KNEE] 
                pointsOut = [pointStart_x, pointStart_y,pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut       
        if key == 'LEFT_SHOULDER':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=150:
                roi["LEFT_SHOULDER"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                tips = "請將雙手手臂平舉打直" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.LEFT_ELBOW] 
                pointsOut = [pointStart_x, pointStart_y,pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
        elif key == 'RIGHT_SHOULDER':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]>=150:
                roi["RIGHT_SHOULDER"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                tips = "請將雙手手臂平舉打直" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_ELBOW] 
                pointsOut = [pointStart_x, pointStart_y,pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
        elif key == 'RIGHT_FOOT_INDEX':
            right_foot_index_x,_,_,right_foot_index_vi  =  (point3d[AngleNodeDef.RIGHT_FOOT_INDEX])
            right_heel_x,_,_,right_heel_vi =  (point3d[AngleNodeDef.RIGHT_HEEL])
            
            if right_foot_index_vi < MIN_DETECT_VISIBILITY or  right_heel_vi< MIN_DETECT_VISIBILITY:
                tips = "請確認腳踝是否位於鏡頭範圍之內" if tip_flag else tips
                continue
            if right_foot_index_x < right_heel_x:
                roi["RIGHT_FOOT_INDEX"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["RIGHT_FOOT_INDEX"] = False
                tips = "請確認是否已經將左腳向左轉" if tip_flag else tips
                pointStart_x, pointStart_y, pointStart_z, pointStart_vi = point3d[AngleNodeDef.RIGHT_FOOT_INDEX] 
                pointsOut = [pointStart_x, pointStart_y,pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y] if tip_flag else pointsOut
        elif key == 'RIGHT_HIP':
            if angle_dict[key] == -1 :
                continue
            if angle_dict[key]<=90:
                roi["RIGHT_HIP"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["RIGHT_HIP"] = False
                tips = "請確認是否已經將身體向左腳下彎，" if tip_flag else tips
                point1_x, point1_y, _, _ = point3d[AngleNodeDef.RIGHT_HIP] 
                point2_x, point2_y, _, _ = point3d[AngleNodeDef.RIGHT_SHOULDER] 
                pointStart_x = (point1_x+point2_x)/2
                pointStart_y = (point1_y+point2_y)/2
                pointsOut = [pointStart_x, pointStart_y,pointStart_x, pointStart_y+DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
        elif key == 'LEFT_ELBOW':
            _,left_elbow_y,_,left_elbow_vi  =  (point3d[AngleNodeDef.LEFT_ELBOW])
            _,left_wrist_y,_,left_wrist_vi =  (point3d[AngleNodeDef.LEFT_WRIST])
            if left_wrist_vi< MIN_DETECT_VISIBILITY:
                tips = "請確認右手腕是否位於鏡頭範圍內"
                continue
            if left_wrist_y<left_elbow_y and angle_dict[key]>=150:
                roi["LEFT_ELBOW"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_ELBOW"] = False
                tips = "請確認是否已經將右手舉直並向上拉高" if tip_flag else tips
                pointStart_x, pointStart_y, _, _ = point3d[AngleNodeDef.LEFT_ELBOW] 
                pointsOut = [pointStart_x, pointStart_y,pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
        elif key == 'RIGHT_ELBOW':
            _,right_elbow_y,_,right_elbow_vi  =  (point3d[AngleNodeDef.RIGHT_ELBOW])
            _,right_wrist_y,_,right_wrist_vi =  (point3d[AngleNodeDef.RIGHT_WRIST])
            if right_wrist_vi< MIN_DETECT_VISIBILITY:
                tips = "請確認左手腕是否位於鏡頭範圍內"
                continue
            if right_elbow_y<right_wrist_y and angle_dict[key]>=150:
                roi["RIGHT_ELBOW"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["RIGHT_ELBOW"] = False
                tips = "請確認是否已經將左手向下舉直" if tip_flag else tips
                pointStart_x, pointStart_y, _, _ = point3d[AngleNodeDef.RIGHT_ELBOW] 
                pointsOut = [pointStart_x, pointStart_y,pointStart_x, pointStart_y+DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
        
        elif key =='RIGHT_EYE':
            _,right_eye_y,_,right_eye_vi  =  (point3d[AngleNodeDef.RIGHT_EYE])
            _,nose_y,_,nose_vi =  (point3d[AngleNodeDef.NOSE])
            if nose_y< MIN_DETECT_VISIBILITY:
                continue
            if nose_y<right_eye_y:
                roi["RIGHT_EYE"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["RIGHT_EYE"] = False
                tips = "請確認是否已經將眼睛向上看" if tip_flag else tips
                pointStart_x, pointStart_y, _, _ = point3d[AngleNodeDef.RIGHT_EYE] 
                pointsOut = [pointStart_x, pointStart_y,pointStart_x, pointStart_y-DISPLACEMENT_DISTANCE] if tip_flag else pointsOut
        elif key =='RIGHT_KNEE':
            if angle_dict[key]==-1:
                continue
            if angle_dict[key]>=150:
                roi["RIGHT_KNEE"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["RIGHT_KNEE"] = False
                tips = "請確認是否已經將左腳打直" if tip_flag else tips
                pointStart_x, pointStart_y, _, _ = point3d[AngleNodeDef.RIGHT_KNEE] 
                pointsOut = [pointStart_x-DISPLACEMENT_DISTANCE, pointStart_y-DISPLACEMENT_DISTANCE,pointStart_x, pointStart_y] if tip_flag else pointsOut
        elif key =='LEFT_KNEE':
            if angle_dict[key]==-1:
                continue
            if angle_dict[key]>=150:
                roi["LEFT_KNEE"] = True
                pointsOut=[] if tip_flag else pointsOut
            else:
                roi["LEFT_KNEE"] = False
                tips = "請確認是否已經將右腳打直" if tip_flag else tips
                pointStart_x, pointStart_y, _, _ = point3d[AngleNodeDef.LEFT_KNEE] 
                pointsOut = [pointStart_x+DISPLACEMENT_DISTANCE, pointStart_y-DISPLACEMENT_DISTANCE,pointStart_x, pointStart_y] if tip_flag else pointsOut
    if tips == "":
        tips = "動作正確"
        pointsOut = []

    return roi, tips, pointsOut