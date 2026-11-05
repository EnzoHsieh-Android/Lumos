// 語意覆核級已知誤報(代碼審 r2 規則B Finding 4):理由寫在屬性上一行,形狀分不出是不是這一行的理由,交盲判看
class WarmCacheRepository(scope: CoroutineScope, source: Flow<Int>) {
    // 理由: app-scope cache must warm up before first screen
    val cache = source.stateIn(scope, SharingStarted.Eagerly, 0)
    val other = source.stateIn(scope, SharingStarted.Eagerly, 1) // 理由: 開機就要預熱
}
