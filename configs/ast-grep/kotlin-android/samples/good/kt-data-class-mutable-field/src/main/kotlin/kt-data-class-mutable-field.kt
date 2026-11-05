package good

data class Cart(val total: Int, val items: List<Item>)
data class Filter(val tags: Set<String>?, val query: String)
class Counter(var count: Int, val buffer: MutableList<Int>)
