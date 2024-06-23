package com.example.yoga.Model

import android.content.Context
import com.example.yoga.R

class fileNameGetter {
    //獲取影片檔案
     fun getfile(context: Context, filename: String): Int {
        return when (filename) {
            "Tree Style" -> R.raw.tree_style
            "Warrior2 Style" -> R.raw.warrior2_style
            "Plank" -> R.raw.plank
            "Reverse Plank" -> R.raw.reverse_plank
            "Child's pose" -> R.raw.childspose_teacher
            "Seated Forward Bend" -> R.raw.seatedforwardbend_teacher
            "Low Lunge" -> R.raw.lowlunge_teacher
            "Downward dog" -> R.raw.downwarddog_teacher
            "Pyramid pose" -> R.raw.pyramid_teacher
            "Bridge pose" -> R.raw.bridge_teacher
            "Mountain pose" -> R.raw.mountain_teacher
            else -> R.raw.tree_style
        }
    }
    // Function to get image resource based on poseName
    fun getDefaultPic(filename: String?): String {
        return when (filename) {
            "Tree Style" -> "Tree Style/8"
            "Warrior2 Style" -> "Warrior2 Style/8"
            "Plank" -> "Plank/10"
            "Reverse Plank" -> "Reverse Plank/6"
            "Child's pose" -> "Child's pose/5"
            "Seated Forward Bend" -> "Seated Forward Bend/5"
            "Low Lunge" -> "Low Lunge/5"
            "Downward dog" -> "Downward dog/6"
            "Pyramid pose" -> "Pyramid pose/6"
            "Bridge pose" -> "Bridge pose/5"
            else -> "Tree Style/8"
        }
    }
    // Function to get image resource based on poseName
    fun getPoseFolder(filename: String?): String {
        return when (filename) {
            "Tree Style" -> "Tree Style"
            "Warrior2 Style" -> "Warrior2 Style"
            "Plank" -> "Plank"
            "Reverse Plank" -> "Reverse Plank"
            "Child's pose" -> "Child's pose"
            "Seated Forward Bend" -> "Seated Forward Bend"
            "Low Lunge" -> "Low Lunge"
            "Downward dog" -> "Downward dog"
            "Pyramid pose" -> "Pyramid pose"
            "Bridge pose" -> "Bridge pose"
            else -> "Tree Style"
        }
    }
}