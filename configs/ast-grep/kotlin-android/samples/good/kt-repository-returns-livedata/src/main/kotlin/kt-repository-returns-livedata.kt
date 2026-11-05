package good

// case: repo-flow
class UserRepository2(private val dao: UserDao) { fun getUsers(): Flow<List<User>> = dao.observeFlow() }
// case: vm-livedata
class R1ViewModel(repo: UserRepository2) : ViewModel() {
    val users = repo.getUsers().asLiveData()
}
// case: repo-suspend
class UserRepository3 { suspend fun refresh() { } }
