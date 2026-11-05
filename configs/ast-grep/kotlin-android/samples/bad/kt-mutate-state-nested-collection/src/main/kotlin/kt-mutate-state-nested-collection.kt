package bad

// case: nested-add
fun L1ViewModel.addItem(x: Item) { _state.value.items.add(x) }
// case: nested-put
fun L2ViewModel.cache(k: String, v: Int) { _state.value.byId.put(k, v) }
// case: nested-index-set
fun L3ViewModel.set(k: String, v: Int) { _state.value.byId[k] = v }
