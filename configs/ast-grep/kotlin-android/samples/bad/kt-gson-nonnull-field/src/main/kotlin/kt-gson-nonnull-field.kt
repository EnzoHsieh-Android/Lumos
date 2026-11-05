data class UserDto(
    @SerializedName("name") val name: String, // BAD
    @SerializedName("tags") val tags: List<String> = emptyList(), // BAD 預設值 Gson 也不管
)
