class MainActivity : AppCompatActivity() {
    override fun onCreate(b: Bundle?) {
        super.onCreate(b)
        lifecycleScope.launch { viewModel.load() } // GOOD
    }
}
fun main() = runBlocking { // GOOD
    serve()
}
