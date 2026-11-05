class MainActivity : AppCompatActivity() {
    override fun onCreate(b: Bundle?) {
        val r = client.newCall(req).execute() // BAD
        val s = URL("https://x").openStream() // BAD
    }
}
class ListFragment : Fragment() {
    fun load() { api.list().execute() } // BAD
}
