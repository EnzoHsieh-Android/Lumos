package bad

class Adapter : RecyclerView.Adapter<VH>() {
    override fun onBindViewHolder(holder: VH, position: Int) {
        val cls = Class.forName(items[position].type) // BAD
        val f = items[position].javaClass.getDeclaredField("title") // BAD
    }
}

class Chart(ctx: Context) : View(ctx) {
    override fun onDraw(canvas: Canvas) {
        val props = model::class.memberProperties // BAD
    }
}
