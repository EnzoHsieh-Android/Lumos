@Composable
fun Screen(id: String, onDone: () -> Unit) {
    LaunchedEffect(Unit) {
        load(id) // BAD
        onDone() // BAD
    }
}
@Composable
fun Other(userId: Int) {
    LaunchedEffect(true) { vm.fetch(userId) } // BAD
}
