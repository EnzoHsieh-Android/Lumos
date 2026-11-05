class RepoTest {
    private val testScope = TestScope()
    @Test fun a() = testScope.runTest { assertEquals(1, repo.load()) } // GOOD
}
class Repo2Test {
    @Test fun b() = runTest { assertEquals(1, repo.load()) } // GOOD
}
