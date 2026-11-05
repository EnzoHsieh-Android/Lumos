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
