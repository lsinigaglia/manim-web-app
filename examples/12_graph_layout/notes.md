# Graph Layout Algorithms Notes

Key patterns:
- `graph.animate.change_layout("layout_name")` smoothly transitions layouts
- Available layouts: "circular", "spring", "kamada_kawai", "planar", "spectral", "shell"
- `seed` parameter makes spring layout deterministic
- The Graph class handles vertex repositioning and edge redrawing automatically
