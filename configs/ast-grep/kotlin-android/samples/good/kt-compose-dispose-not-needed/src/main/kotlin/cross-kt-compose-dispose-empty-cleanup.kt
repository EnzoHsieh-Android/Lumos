// 跨規則邊界案例(檔名以 cross- 開頭):這段是 kt-compose-dispose-empty-cleanup(UI-32)與 kt-compose-lifecycle-observer-leak(ARCH-35)的壞寫法,
// 放在這裡是證明 kt-compose-dispose-not-needed 不重複報,免得兩條給相反的建議;好例的跨規則檢查略過這種檔
@Composable
fun Leaky(owner: LifecycleOwner, observer: LifecycleObserver) {
    DisposableEffect(owner) {
        owner.lifecycle.addObserver(observer)
        onDispose { }
    }
}
