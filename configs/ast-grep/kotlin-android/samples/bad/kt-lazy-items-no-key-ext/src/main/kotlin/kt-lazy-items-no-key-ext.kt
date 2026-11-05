package bad

@Composable
fun Carousel(list: List<Item>) {
    LazyRow {
        items(list) { Card(it) } // BAD
    }
    LazyVerticalGrid(columns = GridCells.Fixed(2)) {
        itemsIndexed(list) { i, it -> Cell(i, it) } // BAD
    }
    LazyColumn(modifier = Modifier.fillMaxSize()) {
        items(list) { Row(it) } // BAD
    }
}
