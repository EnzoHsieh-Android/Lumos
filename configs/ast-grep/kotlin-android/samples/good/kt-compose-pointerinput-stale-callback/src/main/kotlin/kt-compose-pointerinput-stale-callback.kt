package good

@Composable
fun Tap(onTap: () -> Unit) {
    val cb by rememberUpdatedState(onTap)
    Box(Modifier.pointerInput(Unit) { detectTapGestures(onTap = { cb() }) })
    Box(Modifier.pointerInput(onTap) { detectTapGestures(onTap = { onTap() }) })
    Box(Modifier.pointerInput(Unit) { detectDragGestures { change, d -> change.consume() } })
}
