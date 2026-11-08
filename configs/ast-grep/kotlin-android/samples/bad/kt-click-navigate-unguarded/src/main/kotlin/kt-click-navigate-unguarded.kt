package bad

// case: compose-onclick-lambda
@Composable
fun Home(nav: NavController) {
    Button(onClick = { nav.navigate("help") }) { Text("Help") }
}
// case: modifier-clickable
@Composable
fun Row1(nav: NavController) {
    Box(Modifier.clickable { nav.navigate("detail/1") })
}
