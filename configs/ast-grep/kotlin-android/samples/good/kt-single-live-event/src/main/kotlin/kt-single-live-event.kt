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
// 容易誤報:MutableLiveData 子類但不是事件包裝
class NonNullLiveData<T : Any>(init: T) : MutableLiveData<T>(init)
class Debounced<T> : MutableLiveData<T>()
