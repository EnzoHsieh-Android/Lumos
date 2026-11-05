package good

@Composable
fun Screen(s: ScrollState) {
    LazyColumn {
        item { Header() }
        items(xs, key = { it }) { Text(it) }
    }
    Column(Modifier.verticalScroll(s)) {
        LazyRow { items(ys, key = { it }) { Text(it) } }
    }
    Column(Modifier.fillMaxSize()) {
        LazyColumn { items(xs, key = { it }) { Text(it) } }
    }
}
