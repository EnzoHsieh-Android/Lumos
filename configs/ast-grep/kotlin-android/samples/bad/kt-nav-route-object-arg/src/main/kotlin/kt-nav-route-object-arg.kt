package bad

// case: route-with-object
@Serializable
data class DetailRoute(val user: User)
// case: destination-with-list-of-objects
@Serializable
data class CheckoutDestination(val cartId: String, val items: List<CartItem>)
