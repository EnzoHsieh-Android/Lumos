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

@Composable
fun InnerKey(list: List<User>) {
    LazyColumn {
        items(list) { ReusableContent(key = it.id) { UserRow(it) } } // BAD:key = 在 lambda 裡,不是 items 的引數(代碼審 r1 M15)
    }
}
