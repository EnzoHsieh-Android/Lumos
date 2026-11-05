class CartViewModel : ViewModel() {
    private val _state = MutableStateFlow(CartState())
    fun add(item: Item) {
        _state.update { it.copy(items = it.items + item) } // GOOD
    }
}

// 容易誤報:改的是函式裡自己的區域集合,不是狀態的 .value
fun buildTags(source: List<Tag>): Map<String, Tag> {
    val result = mutableMapOf<String, Tag>()
    source.forEach { result[it.id] = it }
    result.remove("")
    return result
}
