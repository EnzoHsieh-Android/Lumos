package bad

@Composable
fun Counter(state: MutableState<Int>, f: MutableFloatState) {
    Text("${state.value}")
    state.value = state.value + 1 // BAD
    Column {
        state.value++ // BAD
    }
    if (f.floatValue < 0f) f.floatValue = 0f // BAD
}
