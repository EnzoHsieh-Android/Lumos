package good

@Composable
fun L(all: List<T>) {
    val visible = remember(all) { all.filter { it.visible } }
    LazyColumn {
        items(visible, key = { it.id }) { Row1(it) }
        items(all.size, key = { i -> all[i].id }) { i -> Row1(all[i]) }
        items(all, key = { it.id }) { t -> Row1(t, tags = t.tags.take(3)) }
    }
}
