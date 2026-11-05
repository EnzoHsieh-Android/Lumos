package bad

@Composable
fun L() {
    val state = LazyListState() // BAD
    val s2 = remember { ScrollState(0) } // BAD
    LazyVerticalGrid(GridCells.Fixed(2), state = LazyGridState()) { } // BAD
}

// 代碼審 r2(規則A F9):rememberSaveable 沒給 saver,ScrollState 沒有預設 saver
@Composable
fun NoSaver() {
    val s = rememberSaveable { ScrollState(0) } // BAD
}
