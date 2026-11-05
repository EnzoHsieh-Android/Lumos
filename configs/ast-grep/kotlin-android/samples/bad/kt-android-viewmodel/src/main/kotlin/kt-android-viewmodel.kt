package bad

// case: extends-androidviewmodel
class F1ViewModel(app: Application) : AndroidViewModel(app)
// case: getApplication-getString
class F2ViewModel(application: Application) : AndroidViewModel(application) {
    fun title() = getApplication<Application>().getString(R.string.title)
}
// case: resources-ctor
class F3ViewModel(private val res: Resources) : ViewModel()
