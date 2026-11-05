package bad

// case: lateinit-adapter
class Y1Fragment : Fragment() {
    private lateinit var adapter: UserAdapter
}
// case: lateinit-recyclerview
class Y2Fragment : Fragment(R.layout.y) {
    private lateinit var list: RecyclerView
    private lateinit var binding: FragmentYBinding
}
// case: view-list
class Y3Fragment : Fragment() {
    private val views = mutableListOf<View>()
}
// case: adapter-val
class Y4Fragment : Fragment() {
    private val adapter = UserAdapter()
}
