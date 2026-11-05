class VmTest {
    private val repo = FakeRepo(StandardTestDispatcher()) // BAD
    @get:Rule val mainRule = MainDispatcherRule()
}
class Vm2Test {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()
    private val io = UnconfinedTestDispatcher() // BAD
}
