package bad

@Immutable // BAD
data class Cart(val items: MutableList<Item>)

@Stable // BAD
class Filter(var query: String)

@Immutable // BAD
class Profile(val name: String) {
    var age: Int = 0
}

@Stable // BAD
class Store {
    val map: HashMap<String, Int> = HashMap()
}
