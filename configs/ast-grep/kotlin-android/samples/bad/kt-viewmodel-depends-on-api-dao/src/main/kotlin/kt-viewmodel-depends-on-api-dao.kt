class VM(private val api: ApiService) : ViewModel() // BAD 寫在同一行
class VM2(
    private val dao: UserDao, // BAD
    private val repo: UserRepository,
) : AndroidViewModel(app)
