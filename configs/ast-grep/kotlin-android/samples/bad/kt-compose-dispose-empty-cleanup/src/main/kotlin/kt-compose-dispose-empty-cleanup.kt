package bad

@Composable
fun Sensor(mgr: SensorManager, l: SensorEventListener, view: View) {
    DisposableEffect(mgr) { // BAD
        mgr.registerListener(l, sensor, 0)
        onDispose { }
    }
    DisposableEffect(view) { // BAD
        view.addOnLayoutChangeListener(cb)
        onDispose {}
    }
}
