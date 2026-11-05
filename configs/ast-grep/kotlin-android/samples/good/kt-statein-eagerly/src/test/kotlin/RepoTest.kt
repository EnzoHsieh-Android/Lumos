// 容易誤報:官方測試寫法,在 runTest 裡用 backgroundScope stateIn
class RepoTest {
    @Test fun t() = runTest {
        val state = repo.flow.stateIn(backgroundScope, SharingStarted.Eagerly, 0)
        assertEquals(0, state.value)
    }
}
