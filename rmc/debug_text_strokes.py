#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, 'src')

from rmscene import read_tree
from rmscene import scene_items as si

def debug_text_strokes_file():
    try:
        with open('tests/rm/text_and_strokes.rm', 'rb') as f:
            tree = read_tree(f)
            
        print("=== Text and Strokes File Analysis ===")
        print(f"Root children: {list(tree.root.children.keys())}")
        
        # Count different types of items
        stroke_count = 0
        text_count = 0
        group_count = 0
        
        def analyze_group(group, indent=0):
            nonlocal stroke_count, text_count, group_count
            prefix = "  " * indent
            group_count += 1
            print(f"{prefix}Group {group.node_id}")
            
            for child_id in group.children:
                child = group.children[child_id]
                if isinstance(child, si.Group):
                    analyze_group(child, indent + 1)
                elif isinstance(child, si.Line):
                    stroke_count += 1
                    print(f"{prefix}  Line {child_id}: {len(child.points)} points, tool={child.tool.name}, color={child.color.name}")
                elif isinstance(child, si.Text):
                    text_count += 1
                    print(f"{prefix}  Text {child_id}: {len(child.text)} characters")
                else:
                    print(f"{prefix}  Other {child_id}: {type(child)}")
        
        analyze_group(tree.root)
        
        print(f"\nSummary:")
        print(f"  Groups: {group_count}")
        print(f"  Strokes: {stroke_count}")
        print(f"  Text items: {text_count}")
        
        # Check if there are any problematic items
        print(f"\nRoot text: {tree.root_text}")
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_text_strokes_file()
