package good

@Composable
fun L() {
    val state = rememberLazyListState()
    val s2 = rememberScrollState()
    LazyVerticalGrid(GridCells.Fixed(2), state = rememberLazyGridState()) { }
}

class FeedHolder {
    val listState = LazyListState(firstVisibleItemIndex = 3)
}
