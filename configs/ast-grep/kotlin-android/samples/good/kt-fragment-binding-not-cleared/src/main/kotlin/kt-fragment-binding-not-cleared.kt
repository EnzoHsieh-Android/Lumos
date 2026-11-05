class ProfileFragment : Fragment() {
    private var _binding: FragmentProfileBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, state: Bundle?): View {
        _binding = FragmentProfileBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null // GOOD
    }
}

// 容易誤報:binding 只當區域變數用,沒有 _binding 欄位,不需要清
class FeedFragment : Fragment(R.layout.fragment_feed) {
    override fun onViewCreated(view: View, state: Bundle?) {
        val binding = FragmentFeedBinding.bind(view)
        binding.title.text = "feed"
    }
}

// 容易誤報(代碼審 r1 m4):this._binding = null 一樣是清掉
class SearchFragment : Fragment() {
    private var _binding: FragmentSearchBinding? = null
    override fun onDestroyView() {
        super.onDestroyView()
        this._binding = null // GOOD
    }
}
