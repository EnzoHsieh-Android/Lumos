fun a() {
    flow.onEach { show(it) }.catch { e -> _state.value = Error(e) }.collect() // GOOD
    flow.catch { log(it) }.launchIn(scope) // GOOD
    flow.catch { emit(Empty) }.collect() // GOOD
}

// 容易誤報:catch 有本體,把錯誤轉成錯誤狀態
fun watch(flow: Flow<Item>, scope: CoroutineScope) {
    flow.catch { e -> _state.value = UiState.Error(e) }.launchIn(scope) // GOOD
}
