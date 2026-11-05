package good

@Composable
fun Track(owner: LifecycleOwner, o: LifecycleObserver) {
    DisposableEffect(owner) {
        owner.lifecycle.addObserver(o)
        onDispose { owner.lifecycle.removeObserver(o) }
    }
    LifecycleEventEffect(Lifecycle.Event.ON_RESUME) { refresh() }
}

class MainActivity : ComponentActivity() {
    override fun onCreate(s: Bundle?) { lifecycle.addObserver(o) }
}
