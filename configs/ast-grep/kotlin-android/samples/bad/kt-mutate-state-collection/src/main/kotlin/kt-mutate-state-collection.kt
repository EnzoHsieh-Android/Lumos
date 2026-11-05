class CartViewModel : ViewModel() {
    private val _items = MutableStateFlow(mutableListOf<Item>())
    fun add(item: Item) {
        _items.value.add(item) // BAD:參照沒變,不發新值
    }
}

class TagViewModel : ViewModel() {
    private val _tags = MutableStateFlow(mutableMapOf<String, Tag>())
    fun put(tag: Tag) {
        _tags.value[tag.id] = tag // BAD
    }
}

// 漏報補上:可空與 removeIf
class NullableViewModel : ViewModel() {
    private val _ids = MutableLiveData<MutableList<Int>>()
    fun add() { _ids.value?.add(1) } // BAD
    fun drop() { _items.value.removeIf { it.done } } // BAD
}
