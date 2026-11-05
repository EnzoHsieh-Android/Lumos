package bad

// case: nested-add
fun L1ViewModel.addItem(x: Item) { _state.value.items.add(x) }
// case: nested-put
fun L2ViewModel.cache(k: String, v: Int) { _state.value.byId.put(k, v) }
// case: nested-index-set
fun L3ViewModel.set(k: String, v: Int) { _state.value.byId[k] = v }
// case: nested-putAll / removeIf / set(漏報補上)
fun L6ViewModel.merge(m: Map<String, Int>) { _state.value.byId.putAll(m) }
fun L7ViewModel.prune() { _state.value.items.removeIf { it.done } }
fun L8ViewModel.replace(x: Item) { _state.value.items.set(0, x) }
