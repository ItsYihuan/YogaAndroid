package com.example.yoga.View

import android.content.Intent
import android.graphics.Color
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import androidx.lifecycle.lifecycleScope
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.example.yoga.Model.GlobalVariable
import com.example.yoga.databinding.ActivityMenuBinding
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class Menu : AppCompatActivity() {
    private lateinit var menuBinding: ActivityMenuBinding
    private var global=GlobalVariable.getInstance()
    private lateinit var currentSelect:Button  //call by reference

    // yogaMat function
    private lateinit var python : Python
    private lateinit var yogaMat : PyObject
    private var yogaMatFunctionThread: Thread? = null
    private var threadFlag : Boolean = true
    private var functionNumber: Int = 0

    fun lastpage(){
        threadFlag = false // to stop thread

        val intent = Intent(this, MainActivity::class.java).apply {
            putExtra("playMusic",false)
        }
        startActivity(intent)
        finish()
    }
    fun nextpage(){
        nextpage(currentSelect.text.toString())
    }
    fun nextpage(posename:String){
        threadFlag = false // to stop thread

        val intent = Intent(this, VideoGuide::class.java).apply {
            putExtra("poseName",posename)
        }
        startActivity(intent)
        finish()
    }
    fun select(){
        currentSelect.setBackgroundColor(Color.rgb(10,240,5))
        currentSelect.setTextColor(Color.rgb(60,60,0))
        currentSelect.setShadowLayer(15f,5f,5f,Color.WHITE)
    }
    fun unselect(){
        currentSelect.setBackgroundColor(Color.BLUE)
        currentSelect.setTextColor(Color.WHITE)
        currentSelect.setShadowLayer(0f,0f,0f,0)
    }
    fun selectTo(btn: Button){
        unselect()
        currentSelect = btn
        select()
    }
    fun up(){
        var next = when(currentSelect){
            menuBinding.button3 -> menuBinding.button1
            menuBinding.button4 -> menuBinding.button2
            menuBinding.button5 -> menuBinding.button3
            menuBinding.button6 -> menuBinding.button4
            menuBinding.button7 -> menuBinding.button5
            menuBinding.button8 -> menuBinding.button6
            menuBinding.button9 -> menuBinding.button7
            menuBinding.button10-> menuBinding.button8
            menuBinding.button11-> menuBinding.button9
            menuBinding.button12-> menuBinding.button10
            else -> currentSelect
        }
        selectTo(next)
    }
    fun down(){
        var next = when(currentSelect){
            menuBinding.button1-> menuBinding.button3
            menuBinding.button2-> menuBinding.button4
            menuBinding.button3-> menuBinding.button5
            menuBinding.button4-> menuBinding.button6
            menuBinding.button5-> menuBinding.button7
            menuBinding.button6-> menuBinding.button8
            menuBinding.button7-> menuBinding.button9
            menuBinding.button8-> menuBinding.button10
            menuBinding.button9-> menuBinding.button11
            menuBinding.button10-> menuBinding.button12
            else -> currentSelect
        }
        selectTo(next)
    }
    fun left(){
        var next = when(currentSelect){
            menuBinding.button2-> menuBinding.button1
            menuBinding.button4-> menuBinding.button3
            menuBinding.button6-> menuBinding.button5
            menuBinding.button8-> menuBinding.button7
            menuBinding.button10-> menuBinding.button9
            menuBinding.button12-> menuBinding.button11
            else -> currentSelect
        }
        selectTo(next)
    }
    fun right(){
        var next = when(currentSelect){
            menuBinding.button1-> menuBinding.button2
            menuBinding.button3-> menuBinding.button4
            menuBinding.button5-> menuBinding.button6
            menuBinding.button7-> menuBinding.button8
            menuBinding.button9-> menuBinding.button10
            menuBinding.button11-> menuBinding.button12
            else -> currentSelect
        }
        selectTo(next)
    }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        menuBinding = ActivityMenuBinding.inflate(layoutInflater)
        setContentView(menuBinding.root)
        supportActionBar?.hide() // 隐藏title bar

        currentSelect = menuBinding.button1

        menuBinding.back.setOnClickListener {
            lastpage()
        }
        menuBinding.button1.setBackgroundColor(Color.BLUE)
        menuBinding.button1.setOnClickListener {
            selectTo(menuBinding.button1)
            nextpage("Tree Style")
        }
        menuBinding.button2.setBackgroundColor(Color.BLUE)
        menuBinding.button2.setOnClickListener {
            selectTo(menuBinding.button2)
            nextpage("Warrior2 Style")
        }
        menuBinding.button3.setBackgroundColor(Color.BLUE)
        menuBinding.button3.setOnClickListener {
            selectTo(menuBinding.button3)
            nextpage("Plank")
        }
        menuBinding.button4.setBackgroundColor(Color.BLUE)
        menuBinding.button4.setOnClickListener {
            selectTo(menuBinding.button4)
            nextpage("Reverse Plank")
        }
        menuBinding.button5.setBackgroundColor(Color.BLUE)
        menuBinding.button5.setOnClickListener {
            selectTo(menuBinding.button5)
            nextpage("Child\'s pose")
        }
        menuBinding.button6.setBackgroundColor(Color.BLUE)
        menuBinding.button6.setOnClickListener {
            selectTo(menuBinding.button6)
            nextpage("Seated Forward Bend")
        }
        menuBinding.button7.setBackgroundColor(Color.BLUE)
        menuBinding.button7.setOnClickListener {
            selectTo(menuBinding.button7)
            nextpage("Low Lunge")
        }
        menuBinding.button8.setBackgroundColor(Color.BLUE)
        menuBinding.button8.setOnClickListener {
            selectTo(menuBinding.button8)
            nextpage("Downward dog")
        }
        menuBinding.button9.setBackgroundColor(Color.BLUE)
        menuBinding.button9.setOnClickListener {
            selectTo(menuBinding.button9)
            nextpage("Pyramid pose")
        }
        menuBinding.button10.setBackgroundColor(Color.BLUE)
        menuBinding.button10.setOnClickListener {
            selectTo(menuBinding.button10)
            nextpage("Bridge pose")
        }
        menuBinding.button11.setBackgroundColor(Color.BLUE)
        menuBinding.button11.setOnClickListener {
            selectTo(menuBinding.button11)
            nextpage("Mountain pose")
        }
        menuBinding.button12.setBackgroundColor(Color.BLUE)
        menuBinding.button12.setOnClickListener {
            selectTo(menuBinding.button12)
            nextpage("Triangle pose")
        }
        select()

        // python start
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        python = Python.getInstance()

        // get yogaMat python module
        yogaMat = python.getModule("heatmap")

        // using yogaMat select and nextPage
        yogaMatFunctionThread = Thread {
            try {
                Thread.sleep(1000)
                while (threadFlag) {
                    functionNumber = yogaMat.callAttr("checkFunction").toInt()
                    runOnUiThread {
                        if (functionNumber == 1) {
                            right()
                        } else if (functionNumber == 2) {
                            up()
                        } else if (functionNumber == 3) {
                            left()
                        } else if (functionNumber == 4) {
                            down()
                        }
                    }
                    if (yogaMat.callAttr("checkReturn").toBoolean()) {
                        nextpage()
                        break
                    }
                    Thread.sleep(750)
                }
            } catch (e: InterruptedException) {
                e.printStackTrace()
            }
            println("!!! Menu Done !!!")
        }

        yogaMatFunctionThread?.start()
    }

    override fun onStart() {
        super.onStart()
        lifecycleScope.launch {
            delay(800)
            global.backgroundMusic.play()
        }
    }
    override fun onPause() {
        super.onPause()
        global.backgroundMusic.pause()
    }

    override fun onResume() {
        super.onResume()
        global.backgroundMusic.play()
    }

    override fun onDestroy() {
        super.onDestroy()
        global.backgroundMusic.pause()
    }
}