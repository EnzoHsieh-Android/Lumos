package good

// case: repository-param
class AB4ViewModel(private val repo: UserRepository, private val getUser: GetUserUseCase) : ViewModel()
// case: repository-owns-dao
class UserRepository4(private val dao: UserDao, private val api: UserApi)
// case: vm-handle
class AB5ViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel()
