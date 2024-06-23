import toolkit
import AngleNodeDef
import AngleRegion

yogaFileDict = {
    "Tree Style": {
        "roi": AngleRegion.TREE,
        "angle_def": AngleNodeDef.TREE_ANGLE,
        "default_image_path" : "image/Tree Style/8.jpg",
    },
    "Warrior2 Style": {
        "roi": AngleRegion.WARRIOR_II,
        "angle_def": AngleNodeDef.WARRIOR_II_ANGLE,
        "default_image_path" : "image/Warrior2 Style/8.jpg"
    },
    "Plank": {
        "roi": AngleRegion.PLANK,
        "angle_def": AngleNodeDef.PLANK_ANGLE,
        "default_image_path" : "image/Plank/10.jpg"
    },
    "Reverse Plank": {
        "roi": AngleRegion.REVERSE_PLANK,
        "angle_def": AngleNodeDef.REVERSE_PLANK_ANGLE,
        "default_image_path" : "image/Reverse Plank/6.jpg"
    },
    "Child's pose": {
        "roi": AngleRegion.CHILDS,
        "angle_def": AngleNodeDef.CHILDS_ANGLE,
        "default_image_path" : "image/Child's pose/5.jpg"
    },
    "Downward dog": {
        "roi": AngleRegion.DOWNWARDDOG,
        "angle_def": AngleNodeDef.DOWNWARDDOG_ANGLE,
        "default_image_path" : "image/Downward dog/6.jpg"
    },
    "Low Lunge": {
        "roi": AngleRegion.LOWLUNGE,
        "angle_def": AngleNodeDef.LOWLUNGE_ANGLE,
        "default_image_path" : "image/Low Lunge/5.jpg"
    },
    "Seated Forward Bend": {
        "roi": AngleRegion.SEATEDFORWARDBEND,
        "angle_def": AngleNodeDef.SEATEDFORWARDBEND_ANGLE,
        "default_image_path" : "image/Seated Forward Bend/5.jpg"
    },
    "Bridge pose": {
        "roi": AngleRegion.BRIDGE,
        "angle_def": AngleNodeDef.BRIDGE_ANGLE,
        "default_image_path" : "image/Bridge pose/5.jpg"
    },
    "Pyramid pose": {
        "roi": AngleRegion.PYRAMID,
        "angle_def": AngleNodeDef.PYRAMID_ANGLE,
        "default_image_path" : "image/Pyramid pose/6.jpg"
    },
    "Mountain pose":{
        "roi": AngleRegion.MOUNTAIN,
        "angle_def": AngleNodeDef.MOUNTAIN_ANGLE,
        "default_image_path" : "image/Mountain pose/1.jpg"
    },
    "Triangle pose":{
        "roi": AngleRegion.TRIANGLE,
        "angle_def": AngleNodeDef.TRIANGLE_ANGLE,
        "default_image_path" : "image/Triangle pose/1.jpg"
    }
}


def get_pose_info(pose):
    if pose in yogaFileDict:
        return yogaFileDict[pose]
    else:
        print("在 Dict 中找不到 ",pose)
        return None

def get_angle_def(pose):
    pose_info = get_pose_info(pose)

    if pose_info is not None:
        return pose_info["angle_def"]
    return None

def get_roi(pose):
    pose_info = get_pose_info(pose)

    if pose_info is not None:
        return pose_info["roi"]
    return {}

def get_sample_angle_dict(pose):
    path = "JsonFile/" + pose + "/sample.json"
    dict = toolkit.readSampleJsonFile(path)
    return dict

def get_sample_socre_angle_dict(pose):
    path = "JsonFile/" + pose + "/sample_score.json"
    dict = toolkit.readSampleJsonFile(path)
    return dict

def get_std_angle_dict(pose):
    path = "JsonFile/" + pose + "/std_angle.json"
    dict = toolkit.readSampleJsonFile(path)
    return dict

def get_weight_angle_dict(pose):
    path = "JsonFile/" + pose + "/weight.json"
    dict = toolkit.readSampleJsonFile(path)
    return dict


def get_image_path(pose):
    return "image/" + pose




