package good

@Composable
fun Sensor(mgr: SensorManager, l: SensorEventListener) {
    DisposableEffect(mgr) {
        mgr.registerListener(l, sensor, 0)
        onDispose { mgr.unregisterListener(l) }
    }
    DisposableEffect(Unit) {
        log("enter")
        onDispose { }
    }
}
