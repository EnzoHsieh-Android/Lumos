package good

// case: view-system-activity
class Z3Activity : AppCompatActivity() {
    override fun onCreate(s: Bundle?) { super.onCreate(s); setContentView(R.layout.main) }
    override fun onResume() { super.onResume() }
}
// case: compose-with-effect
class Z4Activity : ComponentActivity() {
    override fun onCreate(s: Bundle?) { super.onCreate(s); setContent { LifecycleResumeEffect(Unit) { startTracking(); onPauseOrDispose { stopTracking() } } } }
}
