package good

// case: update-copy
fun L4ViewModel.addItem(x: Item) { _state.update { it.copy(items = it.items + x) } }
// case: local-list-add
fun build(x: Item) { val holder = Holder(); holder.items.add(x) }
// case: read-size
fun L5ViewModel.count() = _state.value.items.size
