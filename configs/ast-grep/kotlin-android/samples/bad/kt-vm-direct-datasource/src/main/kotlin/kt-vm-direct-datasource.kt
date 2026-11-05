package bad

// case: dao-param
class AB1ViewModel(private val userDao: UserDao) : ViewModel()
// case: api-and-prefs
class AB2ViewModel @Inject constructor(private val api: UserApi, private val prefs: SharedPreferences) : ViewModel()
// case: datastore-generic
class AB3ViewModel(private val store: DataStore<Preferences>) : ViewModel()

// case: api-service-oneline(併自 kt-viewmodel-depends-on-api-dao)
class AB8ViewModel(private val api: ApiService) : ViewModel()
// case: android-vm-dao(併自 kt-viewmodel-depends-on-api-dao)
class AB9ViewModel(
    private val dao: UserDao,
    private val repo: UserRepository,
) : AndroidViewModel(app)
