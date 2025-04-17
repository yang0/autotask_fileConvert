# autotask_fileConvert

A powerful AutoTask plugin for file format conversion, supporting SVG to image conversion and image to icon formats.

## Features

- **SVG to Image Converter**: Convert SVG files to high-quality PNG or JPEG images with custom dimensions
- **Image to Icon Converter**: Transform images into ICO (Windows) or ICNS (macOS) icon formats with multiple size variants

## Installation

1. Install the plugin through AutoTask's plugin manager
2. Ensure you have the required dependencies:
   - For SVG conversion: `pip install cairosvg pillow`
   - For icon conversion: `pip install pillow`

### System Dependencies

#### For SVG Conversion:
- **Windows**: Install GTK3 runtime environment
- **Linux (Ubuntu/Debian)**: `sudo apt-get install libcairo2-dev pkg-config python3-dev`
- **CentOS/RHEL**: `sudo yum install cairo-devel`
- **MacOS**: `brew install cairo`

## Usage

### SVG to Image Conversion
Convert SVG files to PNG or JPEG with specified dimensions:
- Input: SVG file
- Output: PNG or JPEG image with custom dimensions
- Options: Width, height, output format, output directory

### Image to Icon Conversion
Transform images into icon formats:
- Input: Image file (PNG recommended)
- Output: ICO (Windows) or ICNS (macOS) files with multiple size variants
- Options: Output format, output directory

## License

MIT

---

AutoTask.dev User Id: buKkhpRSxA9LT4zZ6GDKH9
