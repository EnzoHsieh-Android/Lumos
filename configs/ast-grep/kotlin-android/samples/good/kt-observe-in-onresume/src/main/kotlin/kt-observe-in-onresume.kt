package good

// case: onViewCreated
class S3Fragment : Fragment() {
    override fun onViewCreated(view: View, s: Bundle?) { vm.data.observe(viewLifecycleOwner) { render(it) } }
}
// case: onResume-refresh
class S4Activity : AppCompatActivity() {
    override fun onResume() { super.onResume(); vm.refresh() }
}
// case: similar-name
class S5Activity : AppCompatActivity() {
    fun onStartClicked() { vm.start() }
    override fun onCreate(s: Bundle?) { super.onCreate(s); vm.data.observe(this) { } }
}
