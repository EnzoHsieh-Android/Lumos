package good

data class Cart(val total: Int, val items: List<Item>)
data class Filter(val tags: Set<String>?, val query: String)
class Counter(var count: Int, val buffer: MutableList<Int>)
// 容易誤報:Room Entity 的 var(自動產生主鍵由 Room 回填)
@Entity(tableName = "user")
data class User(
    @PrimaryKey(autoGenerate = true) var id: Long = 0,
    var name: String,
)
