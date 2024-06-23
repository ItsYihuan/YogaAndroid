import toolkit
from FeetData import FeetData
from yogaFileGetter import *


class YogaPose:
    '''
    type: WarriorII, Tree, ReversePlank, Plank ...etc
    '''
    def __init__(self, type):
        self.type = type
        self.tips = ""
        self.roi = get_roi(type)
        self.angle_def = get_angle_def(type)

        self.angle_dict = self.initialAngleDict()
        self.sample_angle_dict = {}#initialAngleDict
        self.initialDetect()
        self.angle_show = ""
        self.pointsOut=[]


    def initialAngleDict(self, dict={}):
        index = 0
        for key,_ in self.angle_def.items():
            dict[key] = 0
            index+=1
        return dict

    def initialDetect(self):
        self.sample_angle_dict = get_sample_angle_dict(self.type)

    def detect(self, point, rect , center, feet_data_json):
        self.tips = ""
        self.angle_show = ""
        self.pointsOut = []
        point3d = []

        feet_data = FeetData.from_dict(feet_data_json)

        feet_count = feet_data.get_feet_count_on_mat()
        # print("feet : 瑜珈墊上的腳數量:", feet_count)

        closer_foot = feet_data.get_closer_foot_to_center(center)
        # print("feet : 靠近重心的腳:", closer_foot)

        for i in range(point.size()):
            ang = []
            for j in range(4):
                ang.append(point.get(i).get(j))
            point3d.append(ang)

        con = sum(1 for i in point3d if i[3] < toolkit.MIN_DETECT_VISIBILITY)

        if(con>16):  #half of all node
            self.tips="無法偵測到完整骨架"
            self.angle_show = "無法偵測到完整骨架"
            self.pointsOut=[]
            return [self.angle_show, self.tips,  self.pointsOut]


        for key,value in self.angle_def.items():
            if float(point3d[value[0]][3]) < toolkit.MIN_DETECT_VISIBILITY and float(point3d[value[1]][3]) <toolkit.MIN_DETECT_VISIBILITY and float(point3d[value[2]][3]) <toolkit.MIN_DETECT_VISIBILITY :
                self.angle_dict[key] = -1
                self.angle_show = self.angle_show + f"{key}:-1\n"
            else:
                if (self.type == 'Reverse Plank')  or (self.type == 'Plank') or (self.type == "Child's pose"):
                    angle = toolkit.computeAngle(point3d[value[0]][:2], point3d[value[1]][:2], point3d[value[2]][:2])
                else:
                    angle = toolkit.computeAngle(point3d[value[0]], point3d[value[1]], point3d[value[2]])
                self.angle_dict[key] = angle
                self.angle_show = self.angle_show + f"{key}:{angle}\n"

        if(self.type == 'Tree Style'):
            self.roi, self.tips, self.pointsOut = toolkit.treePoseRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        elif(self.type == 'Warrior2 Style'):
            self.roi, self.tips, self.pointsOut = toolkit.warriorIIPoseRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        elif(self.type == 'Reverse Plank'):
            self.roi, self.tips, self.pointsOut = toolkit.reversePlankPoseRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        elif(self.type == 'Plank'):
            self.roi, self.tips, self.pointsOut = toolkit.plankPoseRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        elif(self.type == "Child's pose"):
            self.roi, self.tips, self.pointsOut = toolkit.ChildsPoseRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        elif(self.type == 'Downward dog'):
            self.roi, self.tips, self.pointsOut = toolkit.DownwardDogRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        elif(self.type == 'Low Lunge'):
            self.roi, self.tips, self.pointsOut = toolkit.LowLungeRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        elif(self.type == "Seated Forward Bend"):
            self.roi, self.tips, self.pointsOut = toolkit.SeatedForwardBendRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        elif(self.type == 'Bridge pose'):
            self.roi, self.tips, self.pointsOut = toolkit.BridgeRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        elif(self.type == 'Pyramid pose'):
            self.roi, self.tips, self.pointsOut = toolkit.PyramidRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        elif(self.type == 'Mountain pose'):
            self.roi, self.tips, self.pointsOut = toolkit.PyramidRule(self.roi, self.tips, self.sample_angle_dict, self.angle_dict, point3d)
        # if(self.pointsOut!=[]):
        #     self.pointsOut=self.normalize( point3d,self.pointsOut)

        print("pointsOut: ",self.pointsOut)
        return [self.angle_show, self.tips,  self.pointsOut]


if __name__ == "__main__":
    landmark  = [[-0.04195899, -0.45470068, -0.49800783], [-0.03318192, -0.49662837, -0.4922224], [-0.032739207, -0.4973393, -0.49164993], [-0.033388793, -0.497507, -0.49159402], [-0.06492008, -0.49036375, -0.48721924], [-0.06476935, -0.4911882, -0.4887974], [-0.06557713, -0.49282837, -0.48756254], [0.028702015, -0.51032495, -0.38913843], [-0.11468751, -0.49356246, -0.3765228], [-0.012957713, -0.44161838, -0.45839038], [-0.055624127, -0.43527463, -0.4538186], [0.11355136, -0.38072678, -0.2867345], [-0.15001108, -0.3640738, -0.2830636], [0.105660625, -0.38897547, -0.2670021], [-0.16315629, -0.30791038, -0.28597853], [0.028729225, -0.490607, -0.20702372], [-0.1065853, -0.43440008, -0.32455036], [0.012279185, -0.49882388, -0.19516961], [-0.072593324, -0.46145716, -0.32724383], [0.015803024, -0.5043777, -0.18922848], [-0.0710453, -0.4755236, -0.304786], [0.024810823, -0.4902709, -0.19758111], [-0.09388401, -0.44077945, -0.3161253], [0.11446194, 9.667E-4, -0.011351924], [-0.11425122, -0.022955116, 0.014334617], [0.08581746, -0.3953731, -0.06520676], [-0.13826358, -0.432663, -0.019005297], [0.119602785, -0.3428142, 0.25228384], [-0.0027126078, -0.38588876, 0.25816008], [0.11135201, -0.30023316, 0.30899766], [0.0032428917, -0.35206273, 0.33343795], [0.20238611, -0.6161823, 0.10663971], [0.0078034527, -0.5411762, 0.16228935]]
    yoga  = YogaPose("Tree")
    print(yoga.detect(landmark,None))