package good

// case: removed-in-onCleared
class H3ViewModel(private val repo: Repo) : ViewModel() {
    private val obs = Observer<Int> { }
    init { repo.count.observeForever(obs) }
    override fun onCleared() { repo.count.removeObserver(obs) }
}
// case: test-class-observeForever
class H4Test {
    @Test fun t() { vm.state.observeForever(observer) }
}
// case: switchMap-instead
class H5ViewModel(repo: Repo) : ViewModel() {
    val label = repo.count.map { "n=$it" }
}
