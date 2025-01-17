try:
    from autotask.nodes import Node, GeneratorNode, ConditionalNode, register_node
except ImportError:
    from stub import Node, GeneratorNode, ConditionalNode, register_node

from typing import Dict, Any
import os
from PIL import Image
import cairosvg
from io import BytesIO

def svg_to_image(svg_path: str, width: int, height: int) -> Image.Image:
    """Convert SVG to Image using CairoSVG with high quality"""
    try:
        # 使用更大的尺寸进行初始渲染以保证质量
        scale_factor = 2
        render_width = width * scale_factor
        render_height = height * scale_factor
        
        # 使用cairosvg直接转换为PNG
        png_data = cairosvg.svg2png(
            url=svg_path,
            output_width=render_width,
            output_height=render_height,
            scale=1.0
        )
        
        # 转换为PIL Image
        img = Image.open(BytesIO(png_data))
        
        # 缩放到目标尺寸
        if img.size != (width, height):
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        return img
    except Exception as e:
        raise Exception(f"Failed to convert SVG: {str(e)}")

@register_node
class SVGToImageNode(Node):
    """Convert SVG file to PNG/JPEG with specified dimensions"""
    NAME = "SVG to Image Converter"
    DESCRIPTION = """Convert SVG file to PNG/JPEG with custom dimensions
    对于 Windows：
    下载并安装 GTK3 运行时环境：
        访问：https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
        下载最新的 .exe 安装包（如 gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe）
        运行安装程序，按默认选项安装
    安装完成后重启系统
    对于 Linux (Ubuntu/Debian)：
        sudo apt-get update
        sudo apt-get install libcairo2-dev pkg-config python3-dev
    对于 CentOS/RHEL：
        sudo yum install cairo-devel
    对于 MacOS：
        brew install cairo
    安装完系统依赖后，重新安装 Python 包：
        pip install cairosvg
    """

    INPUTS = {
        "svg_file": {
            "label": "SVG File Path",
            "description": "Path to the SVG file to convert",
            "type": "STRING",
            "required": True
        },
        "width": {
            "label": "Width",
            "description": "Output image width in pixels",
            "type": "INT",
            "required": True
        },
        "height": {
            "label": "Height",
            "description": "Output image height in pixels",
            "type": "INT",
            "required": True
        },
        "output_dir": {
            "label": "Output Directory",
            "description": "Directory for the output image file",
            "type": "STRING",
            "required": True
        },
        "format": {
            "label": "Output Format",
            "description": "Output image format (PNG or JPEG)",
            "type": "STRING",
            "required": True,
            "default": "PNG",
            "choices": ["PNG", "JPEG"]
        }
    }

    OUTPUTS = {
        "output_file": {
            "label": "Output Image Path",
            "description": "Path to the generated image file",
            "type": "STRING"
        }
    }

    def execute(self, node_inputs: Dict[str, Any], workflow_logger) -> Dict[str, Any]:
        try:
            svg_path = node_inputs["svg_file"]
            width = int(node_inputs["width"])
            height = int(node_inputs["height"])
            output_dir = node_inputs["output_dir"]
            format = node_inputs.get("format", "PNG").upper()
            
            workflow_logger.info(f"Converting SVG file: {svg_path} to {format}")
            
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(svg_path))[0]
            ext = ".png" if format == "PNG" else ".jpg"
            output_path = os.path.join(output_dir, f"{base_name}{ext}")
            
            # 转换SVG到图片
            img = svg_to_image(svg_path, width, height)
            
            # 处理JPEG格式
            if format == "JPEG":
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
            
            # 保存图片
            if format == "PNG":
                img.save(output_path, 'PNG', optimize=True)
            else:
                img.save(output_path, 'JPEG', quality=95, optimize=True)

            workflow_logger.info(f"Successfully converted SVG to {format}: {output_path}")
            
            return {
                "output_file": output_path
            }

        except Exception as e:
            error_msg = f"SVG to {format} conversion failed: {str(e)}"
            workflow_logger.error(error_msg)
            raise Exception(error_msg)


if __name__ == "__main__":
    # Test code
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    node = SVGToImageNode()
    test_inputs = {
        "svg_file": "test.svg",
        "width": 800,
        "height": 600,
        "output_dir": "output"
    }
    
    try:
        result = node.execute(test_inputs, logger)
        print(f"Conversion successful. Output file: {result['output_file']}")
    except Exception as e:
        print(f"Test failed: {str(e)}")
