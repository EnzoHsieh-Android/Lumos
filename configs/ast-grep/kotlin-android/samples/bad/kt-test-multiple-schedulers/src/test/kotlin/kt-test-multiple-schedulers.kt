class RepoTest {
    private val d1 = StandardTestDispatcher() // BAD
    private val d2 = UnconfinedTestDispatcher() // BAD
}
class LoaderTest {
    private val io = StandardTestDispatcher() // BAD
    @Test fun loads() = runTest {
        Loader(io).load()
        advanceUntilIdle()
    }
}
