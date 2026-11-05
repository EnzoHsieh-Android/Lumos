package good

object Repo {
    lateinit var appContext: Context
    fun init(c: Context) { appContext = c.applicationContext }
}

object Prefs {
    private val context: Context = App.instance.applicationContext
}

class Holder(private val context: Context)
