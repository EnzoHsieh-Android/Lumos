package bad

@Composable
fun L(all: List<T>) {
    LazyColumn {
        items(all.filter { it.visible }, key = { it.id }) { Row1(it) } // BAD
        itemsIndexed(all.sortedBy { it.rank }) { i, t -> Row1(t) } // BAD
        items(all.filterIsInstance<Ad>()) { Ad(it) } // BAD
    }
}
