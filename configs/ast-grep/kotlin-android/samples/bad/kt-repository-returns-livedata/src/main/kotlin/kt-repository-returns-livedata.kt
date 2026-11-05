package bad

// case: repo-fun-livedata
class UserRepository(private val dao: UserDao) {
    fun getUsers(): LiveData<List<User>> = dao.observe().map { heavy(it) }
}
// case: interface-datasource
interface UserDataSource { fun observe(id: String): LiveData<User> }
// case: repo-property-livedata
class FeedRepo { val feed: LiveData<Feed> = MutableLiveData() }
