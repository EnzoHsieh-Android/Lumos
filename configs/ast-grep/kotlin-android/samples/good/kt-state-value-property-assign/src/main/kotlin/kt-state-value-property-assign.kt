fun a(x: Item) {
    _state.update { it.copy(items = it.items + x) } // GOOD
    _state.value = UiState(loading = false) // GOOD 整個換新值
    textView.text = state.value.user.name // GOOD
    val n = state.value.items.size // GOOD
}

// 容易誤報:欄位名字以 value 開頭(valueLabel),不是 state.value
fun bind(holder: PriceHolder, item: Item) {
    holder.valueLabel.text = item.price // GOOD
}
