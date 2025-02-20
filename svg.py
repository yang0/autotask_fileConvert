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
        with open(svg_path, 'r') as f:
            svg_content = f.read()
            print(f"SVG Content:\n{svg_content}")

        # 增加缩放因子
        scale_factor = 8
        render_width = width * scale_factor
        render_height = height * scale_factor
        
        print(f"Rendering parameters:")
        print(f"- Original size: {width}x{height}")
        print(f"- Render size: {render_width}x{render_height}")
        print(f"- Scale factor: {scale_factor}")
        
        # 修改SVG内容，添加preserveAspectRatio属性和透明背景
        svg_content = svg_content.replace(
            '<svg ',
            '<svg style="background-color: transparent;" preserveAspectRatio="xMidYMid meet" '
        )
        
        # 使用cairosvg转换，确保透明背景
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=render_width,
            output_height=render_height,
            scale=2.0,
            dpi=300,
            unsafe=True,
            background_color="transparent"  # 确保背景透明
        )
        
        # 设置PIL的解压缩炸弹限制
        original_max_pixels = Image.MAX_IMAGE_PIXELS
        Image.MAX_IMAGE_PIXELS = None
        
        try:
            # 转换为PIL Image并保持透明度
            img = Image.open(BytesIO(png_data))
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            print(f"Intermediate image size: {img.size}")
            print(f"Intermediate image mode: {img.mode}")
            
            # 使用高质量的缩放算法，保持透明度
            if img.size != (width, height):
                print(f"Resizing from {img.size} to {width}x{height}")
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # 保存调试图像，保持透明度
            debug_path = os.path.join(os.path.dirname(svg_path), "debug_output.png")
            img.save(debug_path, 'PNG')  # 移除optimize和transparency参数
            print(f"Debug image saved to: {debug_path}")
            
            return img
            
        finally:
            # 恢复PIL的限制
            Image.MAX_IMAGE_PIXELS = original_max_pixels
            
    except Exception as e:
        print(f"Error details: {str(e)}")
        import traceback
        print(f"Stack trace:\n{traceback.format_exc()}")
        raise Exception(f"Failed to convert SVG: {str(e)}")

@register_node
class SVGToImageNode(Node):
    """Convert SVG file to PNG/JPEG with specified dimensions
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
    NAME = "SVG to Image Converter"
    DESCRIPTION = "Convert SVG file to PNG/JPEG with custom dimension"

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
            
            # 保存图片
            if format == "PNG":
                img.save(output_path, 'PNG')  # 移除optimize和transparency参数
            else:
                # JPEG不支持透明度，使用白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                background.save(output_path, 'JPEG', quality=95, optimize=True)

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
