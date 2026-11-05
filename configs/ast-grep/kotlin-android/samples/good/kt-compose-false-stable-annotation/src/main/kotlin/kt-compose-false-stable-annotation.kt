package good

@Immutable
data class Cart(val items: List<Item>, val total: Int)

@Stable
class Filter {
    var query by mutableStateOf("")
    fun apply(x: MutableList<Int>) { var tmp = 0 }
}

data class Plain(val id: Int) {
    var x: Int = 0
    val y: MutableList<Int> = mutableListOf()
}
