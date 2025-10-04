#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, 'src')

from rmscene import read_tree
from rmscene import scene_items as si
from rmc.exporters.svg import build_anchor_pos, get_anchor, xx, yy

def debug_yaxis_positioning():
    with open('tests/rm/abcd.strokes.rm', 'rb') as f:
        tree = read_tree(f)
        
    print("=== Y-Axis Positioning Analysis ===")
    
    # Build anchor positions
    anchor_pos = build_anchor_pos(tree.root_text)
    print(f"Anchor positions: {anchor_pos}")
    
    def analyze_group(group, indent=0):
        prefix = "  " * indent
        print(f"{prefix}Group {group.node_id}")
        
        # Get anchor info
        anchor_x, anchor_y = get_anchor(group, anchor_pos)
        print(f"{prefix}  Anchor: ({anchor_x}, {anchor_y})")
        
        for child_id in group.children:
            child = group.children[child_id]
            if isinstance(child, si.Group):
                analyze_group(child, indent + 1)
            elif isinstance(child, si.Line):
                print(f"{prefix}  Line {child_id}: {len(child.points)} points")
                if child.points:
                    first_point = child.points[0]
                    last_point = child.points[-1]
                    
                    # Original coordinates
                    orig_first_x, orig_first_y = first_point.x, first_point.y
                    orig_last_x, orig_last_y = last_point.x, last_point.y
                    
                    # After anchor transformation
                    trans_first_x = orig_first_x + anchor_x
                    trans_first_y = orig_first_y + anchor_y
                    trans_last_x = orig_last_x + anchor_x
                    trans_last_y = orig_last_y + anchor_y
                    
                    # After SVG scaling
                    svg_first_x, svg_first_y = xx(trans_first_x), yy(trans_first_y)
                    svg_last_x, svg_last_y = xx(trans_last_x), yy(trans_last_y)
                    
                    print(f"{prefix}    Original: ({orig_first_x:.1f}, {orig_first_y:.1f}) -> ({orig_last_x:.1f}, {orig_last_y:.1f})")
                    print(f"{prefix}    Transformed: ({trans_first_x:.1f}, {trans_first_y:.1f}) -> ({trans_last_x:.1f}, {trans_last_y:.1f})")
                    print(f"{prefix}    SVG Scaled: ({svg_first_x:.1f}, {svg_first_y:.1f}) -> ({svg_last_x:.1f}, {svg_last_y:.1f})")
                    print(f"{prefix}    Tool: {child.tool.name}, Color: {child.color.name}")
    
    analyze_group(tree.root)

if __name__ == "__main__":
    debug_yaxis_positioning()
