@Composable
fun Users(users: List<User>) {
    LazyColumn {
        items(users) { UserRow(it) } // BAD:沒有 key
    }
}

@Composable
fun Orders(orders: List<Order>) {
    LazyColumn {
        item { Header() }
        items(items = orders, contentType = { "order" }) { OrderRow(it) } // BAD
    }
}
