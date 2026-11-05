class MainActivity : AppCompatActivity() {
    override fun onCreate(b: Bundle?) {
        lifecycleScope.launch {
            val r = withContext(Dispatchers.IO) { client.newCall(req).execute().use { it.code } } // GOOD
        }
        thread { URL("https://x").openStream() } // GOOD
        LoadTask().execute() // GOOD AsyncTask 舊寫法自己在背景
    }
}
class Repo {
    fun load() = api.list().execute() // GOOD 不在 Activity/Fragment
}
