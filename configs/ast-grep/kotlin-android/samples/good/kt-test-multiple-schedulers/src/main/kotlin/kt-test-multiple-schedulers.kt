class RepoTest {
    private val d1 = StandardTestDispatcher() // GOOD
    private val d2 = UnconfinedTestDispatcher(d1.scheduler) // GOOD
    @Test fun t() = runTest(d1) { assertEquals(d1.scheduler, d2.scheduler) }
}
class LoaderTest {
    private val io = StandardTestDispatcher() // GOOD
    @Before fun setUp() { Dispatchers.setMain(io) }
    @After fun tearDown() { Dispatchers.resetMain() }
    @Test fun loads() = runTest { assertEquals(1, Loader(io).load()) }
}
class InnerTest {
    @Test fun t() = runTest {
        val io = StandardTestDispatcher(testScheduler) // GOOD
        assertEquals(1, Loader(io).load())
    }
}
