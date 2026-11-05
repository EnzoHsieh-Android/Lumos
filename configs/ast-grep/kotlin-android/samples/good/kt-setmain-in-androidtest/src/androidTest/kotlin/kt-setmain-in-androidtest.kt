// 儀器測試用真的 UI 執行緒;要控制的 dispatcher 以建構參數注入,不換 Main
class FeedScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun showsItems() {
        val vm = FeedViewModel(repo = FakeRepo(), io = StandardTestDispatcher()) // GOOD:注入,不 setMain
        composeTestRule.setContent { FeedScreen(vm) }
        composeTestRule.onNodeWithTag("feed").assertIsDisplayed()
    }
}

// 容易誤報:名字開頭是 setMain 的一般方法(切主分頁),不是 Dispatchers.setMain
class HomeTabTest {
    @Test
    fun switchesTab() {
        val nav = FakeNavigator()
        nav.setMainTab(Tab.Feed) // GOOD
        assertEquals(Tab.Feed, nav.current)
    }
}
