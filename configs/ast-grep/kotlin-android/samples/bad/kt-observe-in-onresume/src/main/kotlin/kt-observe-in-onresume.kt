package bad

// case: onResume-observe-trailing
class S1Activity : AppCompatActivity() {
    override fun onResume() { super.onResume(); vm.data.observe(this) { render(it) } }
}
// case: onStart-observe-observer
class S2Fragment : Fragment() {
    override fun onStart() { super.onStart(); vm.data.observe(viewLifecycleOwner, Observer { render(it) }) }
}
