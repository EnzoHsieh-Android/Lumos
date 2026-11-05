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
// 代碼審 r2(規則B Finding 7):mainActivityRule 是 Activity 的 Rule,不是換 Main 派發器的 Rule
class VmCTest {
    @get:Rule val mainActivityRule = ActivityScenarioRule(MainActivity::class.java)
    val d1 = StandardTestDispatcher() // BAD
    val d2 = StandardTestDispatcher() // BAD
}
