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
