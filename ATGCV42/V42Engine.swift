import Foundation

enum V42Engine {
    static func check(_ input: String) -> String {
        guard let bytes = input.data(using: .utf8),
              let m = (try? JSONSerialization.jsonObject(with: bytes)) as? [String: Any] else { return "ERROR: JSON 格式錯誤" }
        func strings(_ key: String) -> [String]? { m[key] as? [String] }
        func pairs(_ key: String) -> [[String]]? { m[key] as? [[String]] }
        guard let q = strings("Q"), let p = strings("P"), let a = strings("A"),
              let qp = pairs("QP"), let pa = pairs("PA"), let aq = pairs("AQ"),
              let bits = m["bits"] as? String, let sol = m["solution"] as? String,
              !bits.isEmpty, bits.count == sol.count,
              (bits + sol).allSatisfy({ $0 == "0" || $0 == "1" }) else {
            return "ERROR: 缺少必要欄位或位元格式錯誤"
        }
        let alphabet = Array("ATGC")
        let code = String(zip(bits,sol).map { x,y in alphabet[(x == "1" ? 2 : 0) + (y == "1" ? 1 : 0)] })
        let back = code.compactMap { alphabet.firstIndex(of: $0) }
        let roundtrip = back.count == bits.count &&
            String(back.map { $0 & 2 == 0 ? "0" : "1" }.joined()) == bits &&
            String(back.map { $0 & 1 == 0 ? "0" : "1" }.joined()) == sol
        let qs = Set(q), ps = Set(p), as_ = Set(a)
        let wellFormed = qp.allSatisfy { $0.count == 2 && qs.contains($0[0]) && ps.contains($0[1]) } &&
            pa.allSatisfy { $0.count == 2 && ps.contains($0[0]) && as_.contains($0[1]) } &&
            aq.allSatisfy { $0.count == 2 && as_.contains($0[0]) && qs.contains($0[1]) }
        let edgesPA = Set(pa.filter { $0.count == 2 }.map { $0.joined(separator: "\u{001f}") })
        let edgesAQ = Set(aq.filter { $0.count == 2 }.map { $0.joined(separator: "\u{001f}") })
        var cycles: [[String]] = []
        for e in qp where e.count == 2 {
            for f in pa where f.count == 2 && f[0] == e[1] {
                if edgesPA.contains(f.joined(separator: "\u{001f}")) &&
                   edgesAQ.contains([f[1],e[0]].joined(separator: "\u{001f}")) {
                    cycles.append([e[0],e[1],f[1]])
                }
            }
        }
        let cnf = m["CNF"] as? [String: [[String]]] ?? [:]
        let sat = cnf.keys.sorted().map { key -> String in
            let clauses = cnf[key] ?? []
            let atoms = Array(Set(clauses.flatMap { $0 }.map { $0.hasPrefix("!") ? String($0.dropFirst()) : $0 })).sorted()
            guard atoms.count <= 16 else { return "\(key): UNKNOWN (>16 atoms)" }
            let n = 1 << atoms.count
            let found = (0..<n).contains { mask in
                let valuation = Dictionary(uniqueKeysWithValues: atoms.enumerated().map { ($0.element, mask & (1 << $0.offset) != 0) })
                return clauses.allSatisfy { clause in clause.contains { literal in
                    let neg = literal.hasPrefix("!")
                    let atom = neg ? String(literal.dropFirst()) : literal
                    return (valuation[atom] ?? false) != neg
                }}
            }
            return "\(key): \(found ? "SAT" : "UNSAT")"
        }
        let fixed = bits == sol
        let gcHalf = code.filter { $0 == "G" || $0 == "C" }.count * 2 == code.count
        return """
        ATGC: \(code)
        roundtrip: \(roundtrip)
        fixed_point: \(fixed)
        GC_half: \(gcHalf)
        relations_well_formed: \(wellFormed)
        cycles: \(cycles)
        finite_CNF: \(sat.joined(separator: ", "))
        quantum_verified: NOT_IMPLEMENTED
        status: \(wellFormed && roundtrip ? "PARTIAL_CHECK_OK" : "INVALID")
        """
    }
}