"""Convert .rm SceneTree to TLDRaw JSON format.

TLDRaw is a raw stroke data format compatible with tldraw applications.
This exporter extracts stroke data from reMarkable files and converts it
to the TLDRaw JSON structure.
"""

import json
import logging
import base64
import secrets
from typing import Dict, List, Any, Tuple
from rmscene import SceneTree
from rmscene import scene_items as si
from rmscene.text import TextDocument
from .svg import build_anchor_pos, get_anchor, get_bounding_box, xx, yy, LINE_HEIGHTS, TEXT_TOP_Y
from .writing_tools import Pen, RM_PALETTE

_logger = logging.getLogger(__name__)

# TLDRaw format constants
TLDRAW_FILE_FORMAT_VERSION = 1
TLDRAW_SCHEMA_VERSION = 2

# Color mapping from reMarkable to TLDRaw color names
COLOR_MAP = {
    si.PenColor.BLACK: "black",
    si.PenColor.GRAY: "gray",
    si.PenColor.WHITE: "white",
    si.PenColor.YELLOW: "yellow",
    si.PenColor.GREEN: "green",
    si.PenColor.PINK: "pink",
    si.PenColor.BLUE: "blue",
    si.PenColor.RED: "red",
    si.PenColor.GRAY_OVERLAP: "gray",
    si.PenColor.HIGHLIGHT: "yellow",  # Yellow for highlighter
    si.PenColor.GREEN_2: "green",
    si.PenColor.CYAN: "cyan",
    si.PenColor.MAGENTA: "magenta",
    si.PenColor.YELLOW_2: "yellow",
}

# Size mapping from reMarkable to TLDRaw size names
SIZE_MAP = {
    "thin": "s",
    "medium": "m", 
    "thick": "l",
    "very_thick": "xl",
}


def generate_tldraw_index() -> str:
    """
    Generate a proper TLDRaw index key matching the working demo format.
    
    Returns:
        A valid TLDRaw index string (e.g., "a5SrRBsV")
    """
    # Generate 6 random bytes and encode with URL-safe base64
    random_bytes = secrets.token_bytes(6)
    base64_bytes = base64.urlsafe_b64encode(random_bytes)
    # Remove padding and underscores, convert to proper format
    encoded = base64_bytes.decode('ascii').rstrip('=').replace('_', '').replace('-', '')
    
    # Ensure we have exactly 7 characters after the 'a' prefix
    if len(encoded) > 7:
        encoded = encoded[:7]
    elif len(encoded) < 7:
        # Pad with additional random characters if needed
        while len(encoded) < 7:
            encoded += secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
    
    return 'a' + encoded


def tree_to_tldraw(tree: SceneTree, output) -> None:
    """
    Convert a SceneTree to TLDRaw JSON format based on the reference implementation.
    
    Args:
        tree: The SceneTree extracted from the .rm file
        output: IO stream to write the JSON output
    """
    _logger.debug("Exporting %d items to TLDRaw format", len(list(tree.walk())))
    
    # Get anchor positions for proper coordinate transformation
    anchor_pos = build_anchor_pos(tree.root_text)
    
    # Build TLDRaw document structure based on working demo format
    tldraw_doc = {
        "tldrawFileFormatVersion": 1,
        "schema": {
            "schemaVersion": 2,
            "sequences": {
                "com.tldraw.store": 5,
                "com.tldraw.asset": 1,
                "com.tldraw.camera": 1,
                "com.tldraw.document": 2,
                "com.tldraw.instance": 25,
                "com.tldraw.instance_page_state": 5,
                "com.tldraw.page": 1,
                "com.tldraw.instance_presence": 6,
                "com.tldraw.pointer": 1,
                "com.tldraw.shape": 4,
                "com.tldraw.asset.bookmark": 2,
                "com.tldraw.asset.image": 5,
                "com.tldraw.asset.video": 5,
                "com.tldraw.shape.group": 0,
                "com.tldraw.shape.text": 3,
                "com.tldraw.shape.bookmark": 2,
                "com.tldraw.shape.draw": 2,
                "com.tldraw.shape.geo": 10,
                "com.tldraw.shape.note": 9,
                "com.tldraw.shape.line": 5,
                "com.tldraw.shape.frame": 1,
                "com.tldraw.shape.arrow": 7,
                "com.tldraw.shape.highlight": 1,
                "com.tldraw.shape.embed": 4,
                "com.tldraw.shape.image": 5,
                "com.tldraw.shape.video": 4,
                "com.tldraw.binding.arrow": 1
            }
        },
        "records": [
            {
                "gridSize": 10,
                "name": "",
                "meta": {},
                "id": "document:document",
                "typeName": "document",
            },
            {
                "id": "pointer:pointer",
                "typeName": "pointer",
                "x": 0,
                "y": 0,
                "lastActivityTimestamp": 1759583342499,
                "meta": {},
            },
            {
                "meta": {},
                "id": "page:page",
                "name": "Page 1",
                "index": "a1",
                "typeName": "page",
            },
            {
                "followingUserId": None,
                "opacityForNextShape": 1,
                "stylesForNextShape": {
                    "tldraw:geo": "rectangle",
                },
                "brush": None,
                "scribbles": [],
                "cursor": {
                    "type": "default",
                    "rotation": 0,
                },
                "isFocusMode": False,
                "exportBackground": True,
                "isDebugMode": False,
                "isToolLocked": False,
                "screenBounds": {
                    "x": 0,
                    "y": 0,
                    "w": 1502,
                    "h": 809,
                },
                "insets": [False, False, False, False],
                "zoomBrush": None,
                "isGridMode": False,
                "isPenMode": False,
                "chatMessage": "",
                "isChatting": False,
                "highlightedUserIds": [],
                "isFocused": True,
                "devicePixelRatio": 2,
                "isCoarsePointer": False,
                "isHoveringCanvas": True,
                "openMenus": [],
                "isChangingStyle": False,
                "isReadonly": False,
                "meta": {},
                "duplicateProps": None,
                "id": "instance:instance",
                "currentPageId": "page:page",
                "typeName": "instance",
            },
            {
                "editingShapeId": None,
                "croppingShapeId": None,
                "selectedShapeIds": [],
                "hoveredShapeId": None,
                "erasingShapeIds": [],
                "hintingShapeIds": [],
                "focusedGroupId": None,
                "meta": {},
                "id": "instance_page_state:page:page",
                "pageId": "page:page",
                "typeName": "instance_page_state",
            },
            {
                "x": 0,
                "y": 0,
                "z": 1,
                "meta": {},
                "id": "camera:page:page",
                "typeName": "camera",
            },
        ]
    }
    
    # Process root text if present
    shape_index = 1
    if tree.root_text is not None:
        shape_index = process_root_text_for_tldraw(tree.root_text, tldraw_doc["records"], shape_index)
    
    # Process all strokes and convert to shape records
    shape_index = process_group_for_tldraw(tree.root, tldraw_doc["records"], anchor_pos, shape_index)
    
    # Write JSON output
    json.dump(tldraw_doc, output, indent=2)
    _logger.debug("Finished TLDRaw export with %d shapes", shape_index - 1)


def convert_stroke_to_shape_record(
    stroke: si.Line, 
    shape_index: int, 
    anchor_pos: Dict
) -> Dict[str, Any]:
    """
    Convert a reMarkable stroke to a TLDRaw shape record.
    
    Args:
        stroke: The reMarkable line/stroke
        shape_index: Index for the shape (used for ordering)
        anchor_pos: Anchor position mapping
        
    Returns:
        TLDRaw shape record dictionary or None if conversion fails
    """
    try:
        # Get pen properties
        color = COLOR_MAP.get(stroke.color, "black")
        
        # Convert reMarkable thickness to TLDRaw size
        size = get_tldraw_size(stroke.thickness_scale)
        
        # Convert points to TLDRaw format
        points = []
        for point in stroke.points:
            # TLDRaw points have x, y, z (pressure) format
            x = point.x
            y = point.y
            z = 0.5  # Default pressure, can be calculated from point.pressure if needed
            points.append({"x": x, "y": y, "z": z})
        
        if not points:
            return None
        
        # Create TLDRaw shape record based on reference format
        shape_record = {
            "x": points[0]["x"],
            "y": points[0]["y"],
            "rotation": 0,
            "isLocked": False,
            "opacity": 1,
            "meta": {},
            "id": f"shape:{shape_index:02d}",  # Generate unique ID
            "type": "draw",
            "props": {
                "segments": [
                    {
                        "type": "free",
                        "points": points
                    }
                ],
                "color": color,
                "fill": "none",
                "dash": "draw",
                "size": size,
                "isComplete": True,
                "isClosed": False,
                "isPen": False,
                "scale": 1
            },
            "parentId": "page:page",
            "index": generate_tldraw_index(),
            "typeName": "shape"
        }
        
        return shape_record
        
    except Exception as e:
        _logger.error("Failed to convert stroke %s: %s", shape_index, e)
        return None


def process_group_for_tldraw(
    group: si.Group, 
    records: List[Dict], 
    anchor_pos: Dict, 
    shape_index: int
) -> int:
    """
    Process a group and all its children, converting strokes to TLDRaw shape records
    with proper coordinate transformation.
    
    Args:
        group: The group to process
        records: List to add shape records to
        anchor_pos: Anchor position mapping
        shape_index: Starting shape index
        
    Returns:
        Next available shape index
    """
    current_index = shape_index
    
    # Get anchor position for this group
    anchor_x, anchor_y = get_anchor(group, anchor_pos)
    _logger.debug(f"Group {group.node_id}: anchor_x={anchor_x}, anchor_y={anchor_y}")
    
    for child_id in group.children:
        child = group.children[child_id]
        _logger.debug("Processing child: %s %s", child_id, type(child))
        
        if isinstance(child, si.Group):
            # Process nested groups recursively
            current_index = process_group_for_tldraw(child, records, anchor_pos, current_index)
            
        elif isinstance(child, si.Line):
            # Convert stroke to TLDRaw shape with coordinate transformation
            shape_record = convert_stroke_to_shape_record_with_transform(
                child, current_index, anchor_x, anchor_y
            )
            if shape_record:
                records.append(shape_record)
                current_index += 1
    
    return current_index


def convert_stroke_to_shape_record_with_transform(
    stroke: si.Line, 
    shape_index: int, 
    anchor_x: float,
    anchor_y: float
) -> Dict[str, Any]:
    """
    Convert a reMarkable stroke to a TLDRaw shape record with coordinate transformation.
    
    Args:
        stroke: The reMarkable line/stroke
        shape_index: Index for the shape (used for ordering)
        anchor_x: X coordinate offset from anchor
        anchor_y: Y coordinate offset from anchor
        
    Returns:
        TLDRaw shape record dictionary or None if conversion fails
    """
    try:
        # Get pen properties
        color = COLOR_MAP.get(stroke.color, "black")
        
        # Convert reMarkable thickness to TLDRaw size
        size = get_tldraw_size(stroke.thickness_scale)
        
        # Convert points to TLDRaw format with coordinate transformation
        points = []
        for point in stroke.points:
            # Apply anchor transformation (no scaling for now)
            x = point.x + anchor_x
            y = point.y + anchor_y
            z = 0.5  # Default pressure, can be calculated from point.pressure if needed
            points.append({"x": x, "y": y, "z": z})
        
        if not points:
            return None
        
        # Create TLDRaw shape record based on reference format
        shape_record = {
            "x": points[0]["x"],
            "y": points[0]["y"],
            "rotation": 0,
            "isLocked": False,
            "opacity": 1,
            "meta": {},
            "id": f"shape:{shape_index:02d}",  # Generate unique ID
            "type": "draw",
            "props": {
                "segments": [
                    {
                        "type": "free",
                        "points": points
                    }
                ],
                "color": color,
                "fill": "none",
                "dash": "draw",
                "size": size,
                "isComplete": True,
                "isClosed": False,
                "isPen": False,
                "scale": 1
            },
            "parentId": "page:page",
            "index": generate_tldraw_index(),
            "typeName": "shape"
        }
        
        return shape_record
        
    except Exception as e:
        _logger.error("Failed to convert stroke %s: %s", shape_index, e)
        return None


def process_root_text_for_tldraw(
    text: si.Text, 
    records: List[Dict], 
    shape_index: int
) -> int:
    """
    Process root text and convert it to TLDRaw text shape records.
    
    Args:
        text: The root text from the reMarkable file
        records: List to add shape records to
        shape_index: Starting shape index
        
    Returns:
        Next available shape index
    """
    current_index = shape_index
    
    try:
        doc = TextDocument.from_scene_item(text)
        y_offset = TEXT_TOP_Y
        
        for paragraph in doc.contents:
            y_offset += LINE_HEIGHTS.get(paragraph.style.value, 70)
            
            if str(paragraph).strip():  # Only process non-empty paragraphs
                # Calculate position using same scaling as SVG
                x_pos = xx(text.pos_x)
                y_pos = yy(text.pos_y + y_offset)
                
                # Determine text style based on paragraph style
                font_size = get_tldraw_font_size(paragraph.style.value)
                font_style = get_tldraw_font_style(paragraph.style.value)
                
                # Create TLDRaw text shape record with correct richText format
                text_shape = {
                    "x": x_pos,
                    "y": y_pos,
                    "rotation": 0,
                    "isLocked": False,
                    "opacity": 1,
                    "meta": {},
                    "id": f"shape:{current_index:02d}",
                    "type": "text",
                    "props": {
                        "color": "black",
                        "size": "m",
                        "w": len(str(paragraph)) * 10,  # Approximate width
                        "font": "draw",
                        "textAlign": "start",
                        "autoSize": True,
                        "scale": 1,
                        "richText": {
                            "type": "doc",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "attrs": {"dir": "auto"},
                                    "content": [
                                        {"type": "text", "text": str(paragraph).strip()}
                                    ]
                                }
                            ]
                        }
                    },
                    "parentId": "page:page",
                    "index": generate_tldraw_index(),
                    "typeName": "shape"
                }
                
                records.append(text_shape)
                current_index += 1
                _logger.debug(f"Added text shape: '{str(paragraph).strip()}' at ({x_pos}, {y_pos})")
                
    except Exception as e:
        _logger.error(f"Failed to process root text: {e}")
        import traceback
        traceback.print_exc()
    
    return current_index


def get_tldraw_font_size(paragraph_style: str) -> int:
    """
    Convert reMarkable paragraph style to TLDRaw font size.
    
    Args:
        paragraph_style: The reMarkable paragraph style value
        
    Returns:
        TLDRaw font size in pixels
    """
    style_sizes = {
        "PLAIN": 16,
        "BOLD": 18,
        "HEADING": 24,
        "BULLET": 16,
        "BULLET2": 14,
        "CHECKBOX": 16,
        "CHECKBOX_CHECKED": 16,
    }
    return style_sizes.get(paragraph_style, 16)


def get_tldraw_font_style(paragraph_style: str) -> str:
    """
    Convert reMarkable paragraph style to TLDRaw font style.
    
    Args:
        paragraph_style: The reMarkable paragraph style value
        
    Returns:
        TLDRaw font style string
    """
    if paragraph_style == "BOLD":
        return "bold"
    elif paragraph_style == "HEADING":
        return "bold"
    else:
        return "normal"


def get_tldraw_size(thickness_scale: float) -> str:
    """
    Convert reMarkable thickness scale to TLDRaw size.
    
    Args:
        thickness_scale: The reMarkable thickness scale value
        
    Returns:
        TLDRaw size string
    """
    if thickness_scale <= 1.0:
        return "s"
    elif thickness_scale <= 2.0:
        return "m"
    elif thickness_scale <= 3.0:
        return "l"
    else:
        return "xl"


def tree_to_tldraw_raw(tree: SceneTree, output) -> None:
    """
    Convert a SceneTree to TLDRaw format with minimal processing.
    This version preserves more of the original stroke data.
    
    Args:
        tree: The SceneTree extracted from the .rm file
        output: IO stream to write the JSON output
    """
    _logger.debug("Exporting %d items to TLDRaw raw format", len(list(tree.walk())))
    
    # Get anchor positions
    anchor_pos = build_anchor_pos(tree.root_text)
    
    # Build raw stroke data
    raw_data = {
        "version": "2.0.0",
        "source": "rmc-raw",
        "strokes": [],
        "metadata": {
            "total_strokes": 0,
            "pen_types": set(),
            "colors": set(),
        }
    }
    
    # Extract raw stroke data
    stroke_id = 0
    for item in tree.walk():
        if isinstance(item, si.Line):
            stroke_data = extract_raw_stroke_data(item, stroke_id, anchor_pos)
            if stroke_data:
                raw_data["strokes"].append(stroke_data)
                raw_data["metadata"]["pen_types"].add(item.tool.name)
                raw_data["metadata"]["colors"].add(item.color.name)
                stroke_id += 1
    
    # Convert sets to lists for JSON serialization
    raw_data["metadata"]["pen_types"] = list(raw_data["metadata"]["pen_types"])
    raw_data["metadata"]["colors"] = list(raw_data["metadata"]["colors"])
    raw_data["metadata"]["total_strokes"] = stroke_id
    
    # Write JSON output
    json.dump(raw_data, output, indent=2)
    _logger.debug("Finished TLDRaw raw export with %d strokes", stroke_id)


def extract_raw_stroke_data(
    stroke: si.Line, 
    stroke_id: int, 
    anchor_pos: Dict
) -> Dict[str, Any]:
    """
    Extract raw stroke data from a reMarkable line.
    
    Args:
        stroke: The reMarkable line/stroke
        stroke_id: ID for the stroke
        anchor_pos: Anchor position mapping
        
    Returns:
        Raw stroke data dictionary
    """
    points_data = []
    for point in stroke.points:
        point_data = {
            "x": point.x,
            "y": point.y,
            "speed": point.speed,
            "direction": point.direction,
            "width": point.width,
            "pressure": point.pressure,
        }
        points_data.append(point_data)
    
    stroke_data = {
        "id": stroke_id,
        "tool": {
            "type": stroke.tool.name,
            "value": stroke.tool.value,
        },
        "color": {
            "type": stroke.color.name,
            "value": stroke.color.value,
        },
        "thickness_scale": stroke.thickness_scale,
        "starting_length": stroke.starting_length,
        "points": points_data,
        "move_id": stroke.move_id,
    }
    
    return stroke_data
