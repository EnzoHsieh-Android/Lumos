package bad

@Composable
fun Contacts(list: List<C>) {
    val sorted = list.sortedBy { it.name } // BAD
    Column {
        val adults = list.filter { it.age >= 18 } // BAD
        Text("${adults.size}")
    }
    val byCity = list.groupBy { it.city } // BAD
    val s2 = list.sortedWith(compareBy { it.name }) // BAD
}
