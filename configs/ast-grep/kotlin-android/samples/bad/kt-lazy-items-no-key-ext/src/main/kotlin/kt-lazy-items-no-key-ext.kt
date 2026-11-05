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

@Composable
fun InnerKey(list: List<Item>) {
    LazyRow {
        items(list) { ReusableContent(key = it.id) { Card(it) } } // BAD:key = 在 lambda 裡(代碼審 r1 M15)
    }
}
