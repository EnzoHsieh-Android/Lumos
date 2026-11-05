package bad

data class Cart(
    var total: Int, // BAD
    val items: MutableList<Item>, // BAD
)
data class Filter(
    val tags: HashSet<String>?, // BAD
    @SerializedName("q") var query: String, // BAD
)
