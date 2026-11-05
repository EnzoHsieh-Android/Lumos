package bad

// case: public-suspend
class M1ViewModel(private val repo: Repo) : ViewModel() {
    suspend fun save() { repo.save() }
}
// case: internal-suspend-with-return
class M2ViewModel(private val repo: Repo) : ViewModel() {
    internal suspend fun load(id: String): User = repo.user(id)
}
