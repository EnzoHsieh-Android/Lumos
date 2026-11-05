package bad

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val user = runBlocking { repo.load() } // BAD
    }
}

class HomeViewModel(private val repo: Repo) : ViewModel() {
    fun load() = runBlocking(Dispatchers.IO) { repo.load() } // BAD
}

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        runBlocking { repo.sync() } // BAD
    }
}

@Composable
fun Profile() {
    val name = runBlocking { repo.name() } // BAD
}
