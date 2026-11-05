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

// 容易誤報(代碼審 r1 m4):var 有自訂 getter/setter 接到 State;方法內的區域變數不是欄位
@Stable
class Counter {
    private val state = mutableStateOf(0)
    var count: Int
        get() = state.value
        set(v) { state.value = v }
    fun snapshot(): List<Int> {
        val out: MutableList<Int> = mutableListOf()
        return out
    }
}
