class MainActivity : AppCompatActivity() {
    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        val user = runBlocking { repo.load() } // BAD
    }
}
class Vm : ViewModel() {
    fun read() = runBlocking(Dispatchers.IO) { dao.all() } // BAD
}
