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

// 容易誤報:有註冊卻留空 onDispose 歸會擋的 UI-32(kt-compose-dispose-empty-cleanup),這條不報,免得兩條給相反的建議
@Composable
fun Leaky(owner: LifecycleOwner, observer: LifecycleObserver) {
    DisposableEffect(owner) {
        owner.lifecycle.addObserver(observer)
        onDispose { }
    }
}
