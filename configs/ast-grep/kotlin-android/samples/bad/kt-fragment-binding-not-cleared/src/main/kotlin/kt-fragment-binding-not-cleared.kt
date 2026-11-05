class ProfileFragment : Fragment() {
    private var _binding: FragmentProfileBinding? = null // BAD:onDestroyView 沒清
    private val binding get() = _binding!!

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, state: Bundle?): View {
        _binding = FragmentProfileBinding.inflate(inflater, container, false)
        return binding.root
    }
}

class FeedFragment : Fragment() {
    private var _binding: FragmentFeedBinding? = null // BAD:有 onDestroyView 但沒設回 null
    override fun onDestroyView() {
        super.onDestroyView()
    }
}
