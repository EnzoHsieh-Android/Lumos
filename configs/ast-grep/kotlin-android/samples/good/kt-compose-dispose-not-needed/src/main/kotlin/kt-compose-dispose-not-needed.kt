package good

@Composable
fun Screen(id: String) {
    LaunchedEffect(id) {
        analytics.log("open $id")
    }
}

@Composable
fun Observe(owner: LifecycleOwner, observer: LifecycleObserver) {
    DisposableEffect(owner) {
        owner.lifecycle.addObserver(observer)
        onDispose { owner.lifecycle.removeObserver(observer) }
    }
}
