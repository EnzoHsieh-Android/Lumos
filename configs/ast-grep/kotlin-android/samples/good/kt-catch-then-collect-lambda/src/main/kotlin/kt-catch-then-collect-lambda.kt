suspend fun a() {
    flow.onEach { parse(it) }.catch { log(it) }.collect() // GOOD
    flow.catch { log(it) }.collect() // GOOD
    flow.catch { log(it) }.launchIn(scope) // GOOD
}

// 容易誤報:會丟例外的 render 寫在 onEach,catch 在它後面,collect 不帶 lambda
fun CoroutineScope.watch(flow: Flow<Item>) = launch {
    flow.onEach { render(it) }.catch { showError(it) }.collect() // GOOD
}
