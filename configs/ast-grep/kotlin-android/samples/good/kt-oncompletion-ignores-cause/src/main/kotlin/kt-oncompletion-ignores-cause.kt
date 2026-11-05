fun a() {
    flow.onCompletion { cause -> if (cause == null) showDone() }.launchIn(scope) // GOOD
    flow.onCompletion { if (it == null) showDone() else showError(it) }.collect() // GOOD
}

// 容易誤報:參數不叫 cause(叫 e),一樣有看
fun watch(flow: Flow<Item>, scope: CoroutineScope) {
    flow.onCompletion { e -> if (e == null) showDone() else showError(e) }.launchIn(scope) // GOOD
}
