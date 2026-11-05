package bad

@Composable
fun Login(state: UiState, nav: NavController) {
    if (state.done) nav.navigate("home") // BAD
    when (state.err) {
        true -> nav.popBackStack() // BAD
        else -> {}
    }
    Column {
        if (state.logout) { nav.navigate("login") { popUpTo(0) } } // BAD
    }
}
