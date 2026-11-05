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

// 容易誤報(代碼審 r1 M3):rememberXxx 的回呼、具名 lambda 引數、繪製區塊、組建內的區域函式都不在組建本體
@Composable
fun PickImage(progress: Int) {
    val imageUri = remember { mutableStateOf<Uri?>(null) }
    val launcher = rememberLauncherForActivityResult(GetContent()) { uri -> imageUri.value = uri }
    val offset = remember { mutableStateOf(0f) }
    val drag = rememberDraggableState { delta -> offset.value += delta }
    val zoom = remember { mutableStateOf(1f) }
    val t = rememberTransformableState { z, _, _ -> zoom.value += z }
    val s = remember { mutableStateOf(0) }
    val dismiss = rememberSwipeToDismissBoxState(confirmValueChange = { s.value = 2; true })
    Canvas(Modifier) { s.value = 3 }
    AndroidView(factory = { Slider(it) }, update = { it.value = progress })
    fun reset() { imageUri.value = null }
}
