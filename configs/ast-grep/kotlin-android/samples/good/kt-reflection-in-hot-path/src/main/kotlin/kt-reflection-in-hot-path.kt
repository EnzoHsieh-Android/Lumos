package good

class App : Application() {
    override fun onCreate() {
        super.onCreate()
        val driver = Class.forName("org.sqlite.JDBC")
    }
}

class Adapter : RecyclerView.Adapter<VH>() {
    private val titleField = Item::class.java.getDeclaredField("title")
    override fun onBindViewHolder(holder: VH, position: Int) {
        holder.bind(items[position])
    }
}

fun dump(model: Any) = model::class.memberProperties
