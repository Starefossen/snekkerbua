// mesh_to_usda.swift
//
// Builds a single .usda stage out of one or more binary STL meshes, giving
// each mesh its own named UsdPreviewSurface material. The result is ready to
// be packaged as .usdz with usdcat + usdzip and passes `usdchecker --arkit`.
//
// The input meshes are expected to be in millimetres and ALREADY Y-up
// (generate_loftbed.py bakes the Z-up -> Y-up rotation into the STL vertex
// data). This tool therefore only:
//   * scales millimetres -> metres (0.001)
//   * moves the origin to the centre of the footprint, floor at Y = 0
// using one bounding box shared by all inputs, so the groups stay aligned.
//
// Usage:
//   swift tools/mesh_to_usda.swift <output.usda> <group> [<group> ...]
// where each <group> is
//   <name>=<r,g,b[,a]>=<path to .stl>
// e.g.
//   posts=0.95,0.94,0.91,1=/tmp/loftbed_groups/loftbed_bed_mode_posts.stl
// The alpha component becomes UsdPreviewSurface's `inputs:opacity`.

import Foundation

// ---------------------------------------------------------------------------
// Arguments
// ---------------------------------------------------------------------------
struct Group {
    let name: String
    let rgba: (Float, Float, Float, Float)
    let url: URL
}

func die(_ message: String) -> Never {
    FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
    exit(1)
}

let args = CommandLine.arguments
guard args.count >= 3 else {
    die("usage: mesh_to_usda <output.usda> <name>=<r,g,b[,a]>=<mesh.stl> ...")
}

let outURL = URL(fileURLWithPath: args[1])

let groups: [Group] = args.dropFirst(2).map { spec in
    // Split on the first two '=' only; a path may not contain '='.
    let fields = spec.split(separator: "=", maxSplits: 2, omittingEmptySubsequences: false)
    guard fields.count == 3 else { die("malformed group argument: \(spec)") }
    let comps = fields[1].split(separator: ",").compactMap { Float($0) }
    guard comps.count == 3 || comps.count == 4 else {
        die("malformed colour in: \(spec)")
    }
    return Group(name: String(fields[0]),
                 rgba: (comps[0], comps[1], comps[2], comps.count == 4 ? comps[3] : 1),
                 url: URL(fileURLWithPath: String(fields[2])))
}

// ---------------------------------------------------------------------------
// Binary STL reader
// ---------------------------------------------------------------------------
struct Mesh {
    var points: [SIMD3<Float>] = []      // de-duplicated vertices
    var indices: [Int] = []              // 3 per triangle
}

func readBinarySTL(_ url: URL) -> Mesh {
    guard let data = try? Data(contentsOf: url) else { die("cannot read \(url.path)") }
    guard data.count >= 84 else { die("\(url.lastPathComponent): too short for a binary STL") }
    if data.prefix(5) == "solid".data(using: .ascii)! && data.count < 84 {
        die("\(url.lastPathComponent): ASCII STL is not supported")
    }

    let count = data.withUnsafeBytes { raw -> UInt32 in
        raw.loadUnaligned(fromByteOffset: 80, as: UInt32.self)
    }
    let expected = 84 + Int(count) * 50
    guard data.count >= expected else {
        die("\(url.lastPathComponent): truncated binary STL "
            + "(\(data.count) bytes, expected \(expected))")
    }

    var mesh = Mesh()
    var lookup: [SIMD3<Float>: Int] = [:]
    mesh.indices.reserveCapacity(Int(count) * 3)

    data.withUnsafeBytes { raw in
        for t in 0..<Int(count) {
            let base = 84 + t * 50 + 12          // skip the face normal
            for v in 0..<3 {
                let o = base + v * 12
                let p = SIMD3<Float>(raw.loadUnaligned(fromByteOffset: o, as: Float.self),
                                     raw.loadUnaligned(fromByteOffset: o + 4, as: Float.self),
                                     raw.loadUnaligned(fromByteOffset: o + 8, as: Float.self))
                if let i = lookup[p] {
                    mesh.indices.append(i)
                } else {
                    let i = mesh.points.count
                    lookup[p] = i
                    mesh.points.append(p)
                    mesh.indices.append(i)
                }
            }
        }
    }
    return mesh
}

var meshes = groups.map { readBinarySTL($0.url) }
guard meshes.contains(where: { !$0.points.isEmpty }) else { die("no geometry found") }

// ---------------------------------------------------------------------------
// Shared placement: mm -> m, centred on the footprint, floor at Y = 0
// ---------------------------------------------------------------------------
var lo = SIMD3<Float>(repeating: .greatestFiniteMagnitude)
var hi = SIMD3<Float>(repeating: -.greatestFiniteMagnitude)
for mesh in meshes {
    for p in mesh.points {
        lo = SIMD3(min(lo.x, p.x), min(lo.y, p.y), min(lo.z, p.z))
        hi = SIMD3(max(hi.x, p.x), max(hi.y, p.y), max(hi.z, p.z))
    }
}

let s: Float = 0.001
let offset = SIMD3<Float>((lo.x + hi.x) / 2, lo.y, (lo.z + hi.z) / 2)

for i in meshes.indices {
    for j in meshes[i].points.indices {
        meshes[i].points[j] = (meshes[i].points[j] - offset) * s
    }
}

// ---------------------------------------------------------------------------
// USDA
// ---------------------------------------------------------------------------
func f(_ v: Float) -> String { String(format: "%.6g", v) }
func triple(_ p: SIMD3<Float>) -> String { "(\(f(p.x)), \(f(p.y)), \(f(p.z)))" }

let root = "LoftBed"
var out = """
#usda 1.0
(
    defaultPrim = "\(root)"
    doc = "Generated by tools/mesh_to_usda.swift"
    metersPerUnit = 1
    upAxis = "Y"
)

def Xform "\(root)" (
    kind = "component"
)
{
    def Scope "Materials"
    {

"""

for g in groups {
    out += """
        def Material "\(g.name)"
        {
            token outputs:surface.connect = </\(root)/Materials/\(g.name)/Surface.outputs:surface>

            def Shader "Surface"
            {
                uniform token info:id = "UsdPreviewSurface"
                color3f inputs:diffuseColor = (\(f(g.rgba.0)), \(f(g.rgba.1)), \(f(g.rgba.2)))
                float inputs:metallic = 0
                float inputs:opacity = \(f(g.rgba.3))
                float inputs:roughness = 0.75
                token outputs:surface
            }
        }


"""
}

out += """
    }


"""

for (g, mesh) in zip(groups, meshes) where !mesh.points.isEmpty {
    var mlo = SIMD3<Float>(repeating: .greatestFiniteMagnitude)
    var mhi = SIMD3<Float>(repeating: -.greatestFiniteMagnitude)
    for p in mesh.points {
        mlo = SIMD3(min(mlo.x, p.x), min(mlo.y, p.y), min(mlo.z, p.z))
        mhi = SIMD3(max(mhi.x, p.x), max(mhi.y, p.y), max(mhi.z, p.z))
    }
    let faces = mesh.indices.count / 3
    let points = mesh.points.map(triple).joined(separator: ", ")
    let counts = Array(repeating: "3", count: faces).joined(separator: ", ")
    let indices = mesh.indices.map(String.init).joined(separator: ", ")

    out += """
    def Mesh "\(g.name)" (
        prepend apiSchemas = ["MaterialBindingAPI"]
    )
    {
        float3[] extent = [\(triple(mlo)), \(triple(mhi))]
        int[] faceVertexCounts = [\(counts)]
        int[] faceVertexIndices = [\(indices)]
        rel material:binding = </\(root)/Materials/\(g.name)>
        point3f[] points = [\(points)]
        uniform token subdivisionScheme = "none"
    }


"""
}

out += "}\n"

do {
    try out.write(to: outURL, atomically: true, encoding: .utf8)
} catch {
    die("write failed: \(error)")
}

let dx = (hi.x - lo.x) * s
let dy = (hi.y - lo.y) * s
let dz = (hi.z - lo.z) * s
let tris = meshes.reduce(0) { $0 + $1.indices.count / 3 }
print(String(format: "  %@  %d groups, %d triangles  (%.3f x %.3f x %.3f m, Y-up)",
             outURL.lastPathComponent, groups.count, tris, dx, dy, dz))
