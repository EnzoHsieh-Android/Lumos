package good

// case: immutable-state
data class CartUiState2(val total: Int = 0, val items: List<Item> = emptyList())
// case: non-state-data-class-var
data class FormInput(val id: Int) { var text: String = "" }
// case: plain-class-named-state
class SavedState(var position: Int)
