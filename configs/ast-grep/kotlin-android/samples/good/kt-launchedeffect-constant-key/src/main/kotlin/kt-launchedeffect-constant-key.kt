@Composable
fun Screen(id: String, onDone: () -> Unit) {
    val current by rememberUpdatedState(onDone)
    LaunchedEffect(id) { load(id) } // GOOD
    LaunchedEffect(Unit) { current() } // GOOD
    LaunchedEffect(Unit) { analytics.screen.id.let { log(it) } } // GOOD
}
