package bad

// case: livedata-with-param
class I1ViewModel(private val repository: Repo) : ViewModel() {
    fun getPostalCode(address: String): LiveData<String> = repository.getPostCode(address)
}
// case: flow-no-param
class I2ViewModel(private val repo: Repo) : ViewModel() {
    fun observeUser(): Flow<User> = repo.user()
}
// case: stateflow-block-body
class I3ViewModel(private val repo: Repo) : ViewModel() {
    fun items(query: String): StateFlow<List<Item>> {
        return repo.search(query)
    }
}
