package good

@Composable
fun L() {
    LazyColumn {
        item { Title("a") }
        item { Subtitle("b") }
        item { Row1(); HorizontalDivider() }
        item(key = "x") { val t = remember { 1 }; Text("$t") }
        item { Spacer(Modifier.height(8.dp)); Footer() }
    }
}
