fun dir(ctx: Context) = ctx.getExternalFilesDir(null) // GOOD
val msg = "files are not stored under /sdcard any more" // GOOD 只是說明文字
val state = Environment.getExternalStorageState() // GOOD 沒淘汰
