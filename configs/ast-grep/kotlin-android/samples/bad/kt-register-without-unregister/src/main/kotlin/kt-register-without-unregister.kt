package bad

class BatteryActivity : AppCompatActivity() {
    override fun onStart() {
        super.onStart()
        registerReceiver(receiver, IntentFilter(Intent.ACTION_BATTERY_CHANGED)) // BAD
    }
}

class StepFragment : Fragment() {
    override fun onResume() {
        super.onResume()
        sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_UI) // BAD
        ContextCompat.registerReceiver(requireContext(), r, f, ContextCompat.RECEIVER_NOT_EXPORTED) // BAD
        connectivity.registerNetworkCallback(request, callback) // BAD
    }
}

// (併自 kt-register-pair-missing)一般類別註冊了沒解除
class BatteryMonitor(private val context: Context) {
    fun start() {
        context.registerReceiver(receiver, IntentFilter(Intent.ACTION_BATTERY_CHANGED)) // BAD
    }
}

class StepCounter(private val sensors: SensorManager) {
    fun onResume() {
        sensors.registerListener(listener, stepSensor, SensorManager.SENSOR_DELAY_UI) // BAD
    }
}
