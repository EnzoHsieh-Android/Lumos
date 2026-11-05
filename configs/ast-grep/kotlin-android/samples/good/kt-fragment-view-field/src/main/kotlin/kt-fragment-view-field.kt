package good

// case: local-adapter
class Y5Fragment : Fragment() {
    override fun onViewCreated(view: View, s: Bundle?) { val adapter = UserAdapter(); list.adapter = adapter }
}
// case: lateinit-viewmodel-and-inject
class Y6Fragment : Fragment() {
    lateinit var viewModel: DetailViewModel
    @Inject lateinit var analytics: Analytics
}
// case: activity-adapter-field
class Y7Activity : AppCompatActivity() {
    private val adapter = UserAdapter()
}
