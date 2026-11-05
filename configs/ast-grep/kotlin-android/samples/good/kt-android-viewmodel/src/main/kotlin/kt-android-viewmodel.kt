package good

// case: plain-viewmodel
class F4ViewModel(private val repo: TitleRepository) : ViewModel()
// case: application-subclass
class MyApp : Application() { override fun onCreate() { super.onCreate() } }
// case: data-layer-takes-context
class TitleRepository(private val app: Application, private val res: Resources) {
    fun title() = res.getString(R.string.title)
}
