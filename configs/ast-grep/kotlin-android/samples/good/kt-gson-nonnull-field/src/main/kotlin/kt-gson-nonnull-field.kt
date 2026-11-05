data class UserDto(
    @SerializedName("name") val name: String?, // GOOD 可空
    @SerializedName("age") val age: Int, // GOOD 基本型別拿到 0 不會 NPE
    val nick: String, // GOOD 沒有 Gson 註解
)
@Serializable
data class UserJson(@SerialName("name") val name: String) // GOOD kotlinx 的註解
// 容易誤報:每個參數都有預設值,Kotlin 會生無參建構子,Gson 用它,預設值有效
class GModel(
    @SerializedName("n") val n: String = "", // GOOD
    @SerializedName("tags") val tags: List<String> = emptyList(), // GOOD
)
