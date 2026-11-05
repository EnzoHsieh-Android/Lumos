class FeedViewModelTest {
    @Before
    fun setUp() {
        Dispatchers.setMain(StandardTestDispatcher()) // BAD:沒有 resetMain
    }
}

class LoginViewModelTest {
    private val dispatcher = UnconfinedTestDispatcher()
    @Before
    fun setUp() = Dispatchers.setMain(dispatcher) // BAD
}
