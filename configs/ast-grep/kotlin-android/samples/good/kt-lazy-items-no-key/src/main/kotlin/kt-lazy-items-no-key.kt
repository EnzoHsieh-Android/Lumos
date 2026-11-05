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

// 容易誤報(代碼審 r2 規則A F11):key 傳函式參照或變數
@Composable
fun KeyRef(list: List<User>, keyFn: (User) -> Any) {
    LazyColumn { items(list, ::key) { } } // GOOD
    LazyColumn { items(list, keyFn) { } } // GOOD
}

// 容易誤報(代碼審 r2 規則A F12):純計數的骨架佔位,清單不會重排(與 kt-lazy-items-no-key-ext 同一份豁免)
@Composable
fun Skeleton() {
    LazyColumn { items(5) { Shimmer() } } // GOOD
}
