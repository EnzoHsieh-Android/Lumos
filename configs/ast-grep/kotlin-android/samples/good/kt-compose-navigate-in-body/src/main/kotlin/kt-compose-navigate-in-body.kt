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

// 容易誤報(代碼審 r1 M3):結果回呼與組建內的區域函式裡導航
@Composable
fun PickThenGo(navController: NavController) {
    val l2 = rememberLauncherForActivityResult(GetContent()) { navController.navigate("y") }
    fun goHome() { navController.navigate("home") }
    Button(onClick = { goHome() }) { }
}
