try:
    from autotask.nodes import Node, GeneratorNode, ConditionalNode, register_node
except ImportError:
    from stub import Node, GeneratorNode, ConditionalNode, register_node

from typing import Dict, Any
import os
from PIL import Image
import io
import struct
import tempfile

def pack_icns(images: Dict[str, bytes]) -> bytes:
    """Pack images into ICNS format"""
    # ICNS 文件头
    header = struct.pack('!4sI', b'icns', 0)  # 大小稍后填充
    
    # 图标类型映射
    icon_types = {
        16: b'icp4',    # 16x16
        32: b'icp5',    # 32x32
        64: b'icp6',    # 64x64
        128: b'ic07',   # 128x128
        256: b'ic08',   # 256x256
        512: b'ic09',   # 512x512
        1024: b'ic10',  # 1024x1024
    }
    
    data = bytearray()
    for size, image_data in images.items():
        icon_type = icon_types.get(size)
        if icon_type:
            size_data = len(image_data) + 8  # 8 bytes for type and length
            data.extend(icon_type)
            data.extend(struct.pack('!I', size_data))
            data.extend(image_data)
    
    # 更新文件大小
    total_size = len(data) + 8  # 8 bytes for header
    header = struct.pack('!4sI', b'icns', total_size)
    
    return header + data

def create_icns(image_path: str, output_dir: str, base_name: str) -> list:
    """Create multiple ICNS files with different sizes"""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        # 标准ICNS尺寸
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        output_files = []
        
        # 为每个尺寸创建单独的ICNS文件
        for size in sizes:
            output_filename = f"{base_name}_{size}.icns"
            output_path = os.path.join(output_dir, output_filename)
            
            # 创建当前尺寸的图标
            resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # 将图像转换为PNG格式的字节数据
            png_buffer = io.BytesIO()
            resized_img.save(png_buffer, format='PNG')
            png_data = png_buffer.getvalue()
            
            # 创建ICNS文件
            icns_data = pack_icns({size: png_data})
            
            # 保存ICNS文件
            with open(output_path, 'wb') as f:
                f.write(icns_data)
            
            output_files.append(output_path)
            
        return output_files
    except Exception as e:
        raise Exception(f"Failed to create ICNS: {str(e)}")

def create_ico(image_path: str, output_dir: str, base_name: str) -> list:
    """Create multiple ICO files with different sizes"""
    try:
        img = Image.open(image_path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
            
        # 标准ICO尺寸
        sizes = [16, 32, 48, 64, 128, 256]
        output_files = []
        
        # 为每个尺寸创建单独的ICO文件
        for size in sizes:
            output_filename = f"{base_name}_{size}.ico"
            output_path = os.path.join(output_dir, output_filename)
            
            # 创建当前尺寸的图标
            resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
            resized_img.save(output_path, format='ICO')
            output_files.append(output_path)
            
        return output_files
    except Exception as e:
        raise Exception(f"Failed to create ICO: {str(e)}")

@register_node
class ImageToIconNode(Node):
    """Convert image to icon formats (ICO/ICNS)"""
    NAME = "Image to Icon Converter"
    DESCRIPTION = """Convert image files to ICO (Windows) or ICNS (macOS) format.
    Note: ICNS format is only supported on macOS systems.
    Requirements: pip install pillow
    """

    INPUTS = {
        "image_file": {
            "label": "Image File Path",
            "description": "Path to the input image file (PNG recommended)",
            "type": "STRING",
            "required": True
        },
        "output_dir": {
            "label": "Output Directory",
            "description": "Directory for the output icon file",
            "type": "STRING",
            "required": True
        },
        "format": {
            "label": "Icon Format",
            "description": "Output icon format (ICO for Windows, ICNS for macOS)",
            "type": "COMBO",  # 改为COMBO类型
            "required": True,
            "options": ["ICO", "ICNS"],
            "default": "ICO"
        }
    }

    OUTPUTS = {
        "output_files": {
            "label": "Output Icon Path",
            "description": "Path to the generated icon file",
            "type": "LIST"
        }
    }

    def execute(self, node_inputs: Dict[str, Any], workflow_logger) -> Dict[str, Any]:
        try:
            image_path = node_inputs["image_file"]
            output_dir = node_inputs["output_dir"]
            format = node_inputs["format"]
            
            workflow_logger.info(f"Converting image to {format}: {image_path}")
            
            # 检查输入文件是否存在
            if not os.path.exists(image_path):
                raise Exception(f"Input file not found: {image_path}")
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 获取基础文件名
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            
            # 根据格式批量生成不同尺寸的图标
            if format == "ICO":
                output_files = create_ico(image_path, output_dir, base_name)
                sizes_str = "16, 32, 48, 64, 128, 256"
            else:  # ICNS
                output_files = create_icns(image_path, output_dir, base_name)
                sizes_str = "16, 32, 64, 128, 256, 512, 1024"

            workflow_logger.info(f"Successfully created {format} files with sizes: {sizes_str}")
            workflow_logger.info(f"Output files: {', '.join(output_files)}")
            
            return  output_files  # 返回所有生成的文件路径列

        except Exception as e:
            error_msg = f"Image to {format} conversion failed: {str(e)}"
            workflow_logger.error(error_msg)
            raise Exception(error_msg)