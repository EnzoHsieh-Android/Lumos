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
