// 正式碼不歸測試規則管
class DebugApp {
    fun swap(d: CoroutineDispatcher) { Dispatchers.setMain(d) }
}
