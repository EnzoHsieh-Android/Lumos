fun parseOne(input: InputStream): Document {
    val factory = DocumentBuilderFactory.newInstance() // BAD 沒關 DOCTYPE
    return factory.newDocumentBuilder().parse(input)
}
fun parseTwo(parser: XmlPullParser, input: InputStream) {
    parser.setFeature(XmlPullParser.FEATURE_PROCESS_DOCDECL, true) // BAD 開了 DOCTYPE 處理
    parser.setInput(input, null)
}
