package bad

@Composable
fun Feed(rows: List<Row>) {
    LazyColumn {
        items(rows, key = { it.id }) { row -> // BAD
            when (row) {
                is Row.Header -> Header(row)
                is Row.Post -> Post(row)
            }
        }
        itemsIndexed(rows) { i, r -> // BAD
            when (r) { is Row.Ad -> Ad(r); else -> Post(r) }
        }
    }
}
