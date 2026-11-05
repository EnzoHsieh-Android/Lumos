package good

// case: route-with-id
@Serializable
data class DetailIdRoute(val userId: String, val tab: Int = 0)
// case: serializable-model-not-route
@Serializable
data class User(val profile: Profile)
// case: route-list-of-ids
@Serializable
data class CompareRoute(val ids: List<Long>, val note: String? = null)
