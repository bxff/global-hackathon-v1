#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, 'src')

from rmscene import read_tree
from rmscene import scene_items as si
from rmc.exporters.svg import build_anchor_pos, get_anchor

def debug_tree_structure():
    with open('tests/rm/abcd.strokes.rm', 'rb') as f:
        tree = read_tree(f)
        
    print("=== Tree Structure ===")
    print(f"Root children: {list(tree.root.children.keys())}")
    
    # Build anchor positions
    anchor_pos = build_anchor_pos(tree.root_text)
    print(f"Anchor positions: {anchor_pos}")
    
    def print_group(group, indent=0):
        prefix = "  " * indent
        print(f"{prefix}Group {group.node_id}")
        
        # Get anchor info
        anchor_x, anchor_y = get_anchor(group, anchor_pos)
        print(f"{prefix}  Anchor: ({anchor_x}, {anchor_y})")
        
        for child_id in group.children:
            child = group.children[child_id]
            if isinstance(child, si.Group):
                print_group(child, indent + 1)
            elif isinstance(child, si.Line):
                print(f"{prefix}  Line {child_id}: {len(child.points)} points")
                if child.points:
                    first_point = child.points[0]
                    print(f"{prefix}    First point: ({first_point.x}, {first_point.y})")
                    print(f"{prefix}    Tool: {child.tool.name}, Color: {child.color.name}")
    
    print_group(tree.root)

if __name__ == "__main__":
    debug_tree_structure()
