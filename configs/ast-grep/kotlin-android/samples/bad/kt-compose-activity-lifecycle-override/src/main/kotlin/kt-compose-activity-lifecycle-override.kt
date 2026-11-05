package bad

// case: compose-activity-onResume
class Z1Activity : ComponentActivity() {
    override fun onCreate(s: Bundle?) { super.onCreate(s); setContent { App() } }
    override fun onResume() { super.onResume(); startTracking() }
}
// case: compose-activity-onStop
class Z2Activity : ComponentActivity() {
    override fun onCreate(s: Bundle?) { super.onCreate(s); setContent(null) { App() } }
    override fun onStop() { super.onStop(); player.pause() }
}
