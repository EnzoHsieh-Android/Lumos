@Composable
fun Users(users: List<User>) {
    LazyColumn {
        items(users, key = { it.id }) { UserRow(it) } // GOOD
    }
}

// 容易誤報:Paging 的 items 用 itemKey 給 key
@Composable
fun Orders(orders: LazyPagingItems<Order>) {
    LazyColumn {
        items(count = orders.itemCount, key = orders.itemKey { it.id }) { OrderRow(orders[it]) } // GOOD
    }
}

// 容易誤報(代碼審 r1 M15):key 是第二個位置引數
@Composable
fun Positional(list: List<User>) {
    LazyColumn { items(list, { it.id }) { UserRow(it) } } // GOOD
}
