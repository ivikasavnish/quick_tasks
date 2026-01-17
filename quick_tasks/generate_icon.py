"""
Generate a simple icon for Quick Tasks.
Run this to create resources/icon.ico if you don't have one.
"""

import sys
from pathlib import Path

def create_icon():
    """Create a simple checkmark icon."""
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QIcon
        from PySide6.QtCore import Qt
    except ImportError:
        print("PySide6 required. Install with: pip install PySide6")
        return False
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create directory
    resources_dir = Path(__file__).parent / "resources"
    resources_dir.mkdir(exist_ok=True)
    icon_path = resources_dir / "icon.ico"
    
    # Generate icon at multiple sizes
    sizes = [16, 32, 48, 64, 128, 256]
    pixmaps = []
    
    for size in sizes:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background circle
        margin = size * 0.06
        painter.setBrush(QBrush(QColor("#0078d4")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            int(margin), int(margin),
            int(size - margin * 2), int(size - margin * 2)
        )
        
        # Checkmark
        stroke_width = max(2, size // 16)
        pen = QPen(
            QColor("#ffffff"),
            stroke_width,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin
        )
        painter.setPen(pen)
        
        # Checkmark coordinates (proportional)
        x1, y1 = size * 0.28, size * 0.50
        x2, y2 = size * 0.44, size * 0.66
        x3, y3 = size * 0.72, size * 0.34
        
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        painter.drawLine(int(x2), int(y2), int(x3), int(y3))
        
        painter.end()
        pixmaps.append(pixmap)
    
    # Save as .ico (Windows icon format)
    # PySide6/Qt doesn't directly support multi-size .ico writing,
    # so we'll save the largest as PNG and create ICO from it
    
    # For proper .ico, we need pillow
    try:
        from PIL import Image
        import io
        
        images = []
        for pixmap in pixmaps:
            buffer = pixmap.toImage()
            # Convert to PIL Image
            width = buffer.width()
            height = buffer.height()
            ptr = buffer.bits()
            ptr.setsize(buffer.sizeInBytes())
            
            img = Image.frombytes(
                'RGBA',
                (width, height),
                bytes(ptr),
                'raw',
                'BGRA'
            )
            images.append(img)
        
        # Save as ICO with all sizes
        images[0].save(
            str(icon_path),
            format='ICO',
            sizes=[(s, s) for s in sizes]
        )
        
        print(f"Created icon: {icon_path}")
        return True
        
    except ImportError:
        # Fall back to saving as PNG
        png_path = resources_dir / "icon.png"
        pixmaps[-1].save(str(png_path), "PNG")
        print(f"Created PNG icon: {png_path}")
        print("Note: Install Pillow for .ico format: pip install Pillow")
        return True


if __name__ == "__main__":
    create_icon()
