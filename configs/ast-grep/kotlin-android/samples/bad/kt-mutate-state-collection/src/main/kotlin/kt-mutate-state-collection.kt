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
