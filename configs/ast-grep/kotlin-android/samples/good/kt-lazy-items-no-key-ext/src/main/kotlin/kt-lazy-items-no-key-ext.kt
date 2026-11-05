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
