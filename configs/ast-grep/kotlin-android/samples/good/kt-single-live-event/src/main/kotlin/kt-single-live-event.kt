package good

// case: custom-livedata-subclass
class LocationLiveData(ctx: Context) : LiveData<Location>() {
    override fun onActive() { }
}
// case: plain-mutablelivedata-property
class C1ViewModel : ViewModel() {
    private val _name = MutableLiveData<String>()
    val name: LiveData<String> = _name
}
// case: peekContent
fun peek(e: Wrapper<String>) = e.peekContent()
