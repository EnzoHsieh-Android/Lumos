package good

class BatteryActivity : AppCompatActivity() {
    override fun onStart() {
        super.onStart()
        registerReceiver(receiver, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
    }

    override fun onStop() {
        unregisterReceiver(receiver)
        super.onStop()
    }
}

class StepFragment : Fragment() {
    override fun onResume() {
        super.onResume()
        sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_UI)
        connectivity.registerNetworkCallback(request, callback)
    }

    override fun onPause() {
        sensorManager.unregisterListener(this)
        connectivity.unregisterNetworkCallback(callback)
        super.onPause()
    }
}

// 容易誤報(代碼審 r1 m4):Application 跟整個程序同壽命,永久註冊不會洩漏
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        registerReceiver(receiver, IntentFilter(Intent.ACTION_LOCALE_CHANGED))
        sensors.registerListener(listener, stepSensor, SensorManager.SENSOR_DELAY_UI)
    }
}

// (併自 kt-register-pair-missing)解除寫在另一個回呼裡
class StepCounter(private val sensors: SensorManager) {
    fun onResume() {
        sensors.registerListener(listener, stepSensor, SensorManager.SENSOR_DELAY_UI)
    }
    fun onPause() {
        sensors.unregisterListener(listener) // GOOD
    }
}
