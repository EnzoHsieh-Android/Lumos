data class UserDto(
    @SerializedName("name") val name: String?, // GOOD 可空
    @SerializedName("age") val age: Int, // GOOD 基本型別拿到 0 不會 NPE
    val nick: String, // GOOD 沒有 Gson 註解
)
@Serializable
data class UserJson(@SerialName("name") val name: String) // GOOD kotlinx 的註解
