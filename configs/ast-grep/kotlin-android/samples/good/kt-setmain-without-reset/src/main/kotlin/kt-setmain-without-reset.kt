class MainDispatcherRule(private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()) : TestWatcher() {
    override fun starting(description: Description) = Dispatchers.setMain(dispatcher)
    override fun finished(description: Description) = Dispatchers.resetMain() // GOOD
}

// 容易誤報:setMain 與 resetMain 拆在 @Before 與 @After 兩個函式
class FeedViewModelTest {
    @Before
    fun setUp() {
        Dispatchers.setMain(StandardTestDispatcher())
    }
    @After
    fun tearDown() {
        Dispatchers.resetMain() // GOOD
    }
}
