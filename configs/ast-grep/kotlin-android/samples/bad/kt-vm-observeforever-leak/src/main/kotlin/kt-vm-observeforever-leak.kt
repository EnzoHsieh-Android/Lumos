package bad

// case: observeForever-in-init
class H1ViewModel(repo: Repo) : ViewModel() {
    private val obs = Observer<Int> { }
    init { repo.count.observeForever(obs) }
}
// case: observeForever-lambda
class H2ViewModel(repo: Repo) : ViewModel() {
    fun start() { repo.count.observeForever { n -> handle(n) } }
    override fun onCleared() { super.onCleared() }
}
