package good

@Composable
fun Feed(rows: List<Row>) {
    LazyColumn {
        items(rows, key = { it.id }, contentType = { it::class }) { row ->
            when (row) {
                is Row.Header -> Header(row)
                is Row.Post -> Post(row)
            }
        }
        items(rows, key = { it.id }) { row ->
            when (row.kind) { 1 -> A(); else -> B() }
        }
    }
}
