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

// 容易誤報(代碼審 r1 M7):Lazy 清單自己給了固定高度,量測不會拿到無限長度
@Composable
fun Fixed(list: List<Item>) {
    Column(Modifier.verticalScroll(rememberScrollState())) {
        LazyColumn(Modifier.height(300.dp)) { items(list, key = { it.id }) { Text("") } }
    }
    Row(Modifier.horizontalScroll(rememberScrollState())) {
        LazyRow(modifier = Modifier.width(200.dp)) { items(list, key = { it.id }) { Text("") } }
    }
}
