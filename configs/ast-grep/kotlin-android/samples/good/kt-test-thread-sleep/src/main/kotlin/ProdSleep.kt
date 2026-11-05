// 正式碼不歸測試規則管
class Poller(private val composeTestRule: Any) {
    fun poll() { Thread.sleep(100) }
}
