package bad

// case: dao-param
class AB1ViewModel(private val userDao: UserDao) : ViewModel()
// case: api-and-prefs
class AB2ViewModel @Inject constructor(private val api: UserApi, private val prefs: SharedPreferences) : ViewModel()
// case: datastore-generic
class AB3ViewModel(private val store: DataStore<Preferences>) : ViewModel()
