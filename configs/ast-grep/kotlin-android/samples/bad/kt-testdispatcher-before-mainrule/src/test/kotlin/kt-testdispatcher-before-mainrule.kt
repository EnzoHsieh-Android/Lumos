class VmTest {
    private val repo = FakeRepo(StandardTestDispatcher()) // BAD
    @get:Rule val mainRule = MainDispatcherRule()
}
class Vm2Test {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()
    private val io = UnconfinedTestDispatcher() // BAD
}
// 專案自己命名的 Rule,另起的 dispatcher 沒交給它
class Vm4Test {
    private val io = StandardTestDispatcher() // BAD
    @get:Rule val coroutineRule = CoroutineTestRule()
}
