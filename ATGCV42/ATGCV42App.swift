import SwiftUI

@main struct ATGCV42App: App {
    var body: some Scene { WindowGroup { ContentView() } }
}

struct ContentView: View {
    @State private var source = (try? String(contentsOf: Bundle.main.url(forResource: "example", withExtension: "json")!, encoding: .utf8)) ?? "{}"
    @State private var report = "點選「執行有限驗證」開始。"
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    Text("ATGC UQTM v42").font(.title.bold())
                    Text("iPhone 原生運算實驗室 · 無 SHA").foregroundStyle(.secondary)
                    Text("輸入 JSON 規格").font(.headline)
                    TextEditor(text: $source)
                        .font(.system(.footnote, design: .monospaced))
                        .frame(height: 260).padding(6)
                        .overlay(RoundedRectangle(cornerRadius: 8).stroke(.gray.opacity(0.4)))
                    Button("執行有限驗證") { report = V42Engine.check(source) }
                        .buttonStyle(.borderedProminent)
                    Text("檢查報告").font(.headline)
                    Text(report).font(.system(.footnote, design: .monospaced))
                        .textSelection(.enabled)
                    Text("量子酉性：此 Swift 版本尚未移植 v37 的精確 Q(i) 驗證，因此不宣稱 quantum_verified。Python 參考模組附於專案。")
                        .font(.caption).foregroundStyle(.secondary)
                }.padding()
            }.navigationTitle("ATGC v42")
        }
    }
}