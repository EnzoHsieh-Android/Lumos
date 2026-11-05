package good

@Composable
fun Counter(state: MutableState<Int>, scope: CoroutineScope) {
    Button(onClick = { state.value = state.value + 1 }) { Text("+") }
    LaunchedEffect(state) { state.value = 0 }
    SideEffect { state.value++ }
    Box(Modifier.clickable(role = Role.Button) { state.value-- })
    IconButton(onClick = { scope.launch { state.value = 3 } }) { }
}

class Vm {
    fun inc() { state.update { it + 1 } }
}
