class RepoTest {
    private val testScope = TestScope()
    @Test fun a() = runTest { repo.load() } // BAD
}
class Repo2Test {
    @Test fun b() {
        val ts = TestScope(StandardTestDispatcher())
        runTest(timeout = 5.seconds) { work(ts) } // BAD
    }
}
