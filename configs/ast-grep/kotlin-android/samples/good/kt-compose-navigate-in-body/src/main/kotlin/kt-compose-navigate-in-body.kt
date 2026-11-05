package good

@Composable
fun Login(state: UiState, onDone: () -> Unit) {
    LaunchedEffect(state.done) { if (state.done) onDone() }
    Button(onClick = dropUnlessResumed { nav.navigate("home") }) { Text("go") }
    BackHandler { nav.popBackStack() }
    LaunchedEffect(state.err) { if (state.err) nav.popBackStack() }
}

fun NavGraphBuilder.graph(nav: NavController) {
    composable("a") { }
    nav.navigate("b")
}
