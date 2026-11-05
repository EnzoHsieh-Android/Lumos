package good

// case: repository-param
class AB4ViewModel(private val repo: UserRepository, private val getUser: GetUserUseCase) : ViewModel()
// case: repository-owns-dao
class UserRepository4(private val dao: UserDao, private val api: UserApi)
// case: vm-handle
class AB5ViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel()

// case: analytics-service(代碼審 r1 m4:名稱帶 Service 但不是資料來源)
class AB6ViewModel(private val analytics: AnalyticsService, private val repo: UserRepository) : ViewModel()
// case: apiary(併自 kt-viewmodel-depends-on-api-dao:名字只是像)
class AB7ViewModel(private val apiary: Apiary) : ViewModel()
