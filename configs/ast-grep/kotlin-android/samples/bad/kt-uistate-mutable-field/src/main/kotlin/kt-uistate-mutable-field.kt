package bad

// case: var-field
data class CartUiState(var total: Int = 0, val title: String = "")
// case: mutable-list-field
data class ListState(val items: MutableList<Item> = mutableListOf())
// case: sealed-impl-arraylist
data class Success(val rows: ArrayList<Row>) : FeedUiState
