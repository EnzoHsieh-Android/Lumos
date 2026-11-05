class BatteryMonitor(private val context: Context) : DefaultLifecycleObserver {
    override fun onStart(owner: LifecycleOwner) {
        context.registerReceiver(receiver, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
    }
    override fun onStop(owner: LifecycleOwner) {
        context.unregisterReceiver(receiver) // GOOD:對稱解除
    }
}

// 容易誤報:解除寫在另一個回呼裡,不在註冊的同一個函式
class StepCounter(private val sensors: SensorManager) {
    fun onResume() {
        sensors.registerListener(listener, stepSensor, SensorManager.SENSOR_DELAY_UI)
    }
    fun onPause() {
        sensors.unregisterListener(listener) // GOOD
    }
}
