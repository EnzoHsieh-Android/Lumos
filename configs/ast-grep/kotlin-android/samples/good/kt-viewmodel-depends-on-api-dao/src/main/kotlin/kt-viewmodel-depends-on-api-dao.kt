class VM(private val repo: UserRepository) : ViewModel() // GOOD
class Repo(private val api: ApiService, private val dao: UserDao) // GOOD 不是 ViewModel
class VM2(private val apiary: Apiary) : ViewModel() // GOOD 名字只是像
