package bad

@Composable
fun Tap(onTap: () -> Unit, onLong: (Offset) -> Unit) {
    Box(Modifier.pointerInput(Unit) { // BAD
        detectTapGestures(onTap = { onTap() })
    })
    Box(Modifier.size(4.dp).pointerInput(true) { // BAD
        detectTapGestures(onLongPress = { onLong(it) })
    })
}
