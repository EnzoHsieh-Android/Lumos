package bad

@Composable
fun Track(owner: LifecycleOwner, o: LifecycleObserver) {
    owner.lifecycle.addObserver(o) // BAD
    LaunchedEffect(owner) {
        owner.lifecycle.addObserver(o) // BAD
    }
    DisposableEffect(owner) {
        owner.lifecycle.addObserver(o) // BAD
        onDispose { }
    }
}
