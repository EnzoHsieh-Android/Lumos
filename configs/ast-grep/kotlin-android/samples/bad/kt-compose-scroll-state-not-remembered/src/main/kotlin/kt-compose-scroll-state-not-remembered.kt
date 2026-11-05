package bad

@Composable
fun L() {
    val state = LazyListState() // BAD
    val s2 = remember { ScrollState(0) } // BAD
    LazyVerticalGrid(GridCells.Fixed(2), state = LazyGridState()) { } // BAD
}
