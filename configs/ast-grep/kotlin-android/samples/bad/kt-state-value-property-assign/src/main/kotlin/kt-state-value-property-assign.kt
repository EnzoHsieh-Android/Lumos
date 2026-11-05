fun a(x: Item) {
    _state.value.items += x // BAD
    state.value.user.name = "n" // BAD
    _uiState.value!!.count -= 1 // BAD
}
// 漏報補上:++ 與 /=
fun b() {
    _state.value.count++ // BAD
    _state.value.ratio /= 2 // BAD
}
