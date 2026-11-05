class VmTest {
    @get:Rule val mainRule = MainDispatcherRule()
    private val repo = FakeRepo(mainRule.testDispatcher) // GOOD
}
class Vm2Test {
    @get:Rule val mainRule = MainDispatcherRule(StandardTestDispatcher()) // GOOD
    @Test fun t() = runTest {
        val io = StandardTestDispatcher() // GOOD
        assertEquals(1, FakeRepo(io).count)
    }
}
// 容易誤報:dispatcher 交給專案自己命名的 Rule
class Vm3Test {
    private val testDispatcher = UnconfinedTestDispatcher()
    @get:Rule val rule = CoroutineTestRule(testDispatcher)
}
