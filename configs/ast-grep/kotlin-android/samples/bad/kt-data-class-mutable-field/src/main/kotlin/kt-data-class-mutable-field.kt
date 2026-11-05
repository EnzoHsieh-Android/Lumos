package bad

data class Cart(
    var total: Int, // BAD
    val items: MutableList<Item>, // BAD
)
data class Filter(
    val tags: HashSet<String>?, // BAD
    @SerializedName("q") var query: String, // BAD
)
// 代碼審 r2(規則B Finding 12):Entity 豁免只涵蓋 var,可變集合欄位照報
@Entity
data class Note(@PrimaryKey(autoGenerate = true) var id: Long = 0, val tags: MutableList<String>, val flow: MutableStateFlow<Int>) // BAD ×2
