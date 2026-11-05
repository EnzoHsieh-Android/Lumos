package good

@Composable
fun Carousel(list: List<Item>) {
    LazyRow {
        items(list, key = { it.id }) { Card(it) }
    }
    LazyVerticalGrid(columns = GridCells.Fixed(2)) {
        itemsIndexed(list, key = { _, it -> it.id }) { i, it -> Cell(i, it) }
    }
    Column {
        list.forEach { Row(it) }
    }
}

// 容易誤報(代碼審 r1 M15):key 是第二個位置引數
@Composable
fun Positional(list: List<Item>) {
    LazyRow { items(list, { it.id }) { Card(it) } }
    LazyVerticalGrid(columns = GridCells.Fixed(2)) { itemsIndexed(list, { _, it -> it.id }) { i, it -> Cell(i, it) } }
}
