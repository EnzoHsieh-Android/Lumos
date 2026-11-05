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

// 容易誤報(代碼審 r1 M5):rememberSaveable 加 Saver 就是 rememberScrollState 的做法
@Composable
fun Saved() {
    val s = rememberSaveable(saver = ScrollState.Saver) { ScrollState(0) }
    val l = rememberSaveable(saver = LazyListState.Saver) { LazyListState() }
}
