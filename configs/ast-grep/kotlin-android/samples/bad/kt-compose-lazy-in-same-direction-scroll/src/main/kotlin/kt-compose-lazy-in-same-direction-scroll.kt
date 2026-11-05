package bad

@Composable
fun Screen(s: ScrollState) {
    Column(Modifier.fillMaxSize().verticalScroll(s)) {
        Header()
        LazyColumn { items(xs, key = { it }) { Text(it) } } // BAD
    }
    Row(modifier = Modifier.horizontalScroll(rememberScrollState())) {
        LazyRow(Modifier.height(80.dp)) { item { A() } } // BAD
    }
}
