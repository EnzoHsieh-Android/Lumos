class BatteryMonitor(private val context: Context) {
    fun start() {
        context.registerReceiver(receiver, IntentFilter(Intent.ACTION_BATTERY_CHANGED)) // BAD:沒有 unregisterReceiver
    }
}

class StepCounter(private val sensors: SensorManager) {
    fun onResume() {
        sensors.registerListener(listener, stepSensor, SensorManager.SENSOR_DELAY_UI) // BAD:沒有 unregisterListener
    }
}
