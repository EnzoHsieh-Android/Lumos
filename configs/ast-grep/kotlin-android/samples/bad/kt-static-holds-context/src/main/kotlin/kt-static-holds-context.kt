package bad

object Repo {
    lateinit var context: Context // BAD
    fun init(c: Context) { context = c }
}

class Prefs {
    companion object {
        private var ctx: Context? = null // BAD
    }
}
