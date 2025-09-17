import ezdxf
import os

def create_test_dxf():
    """Create a test DXF file with Chinese text for testing"""

    # Create a new DXF document
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # Add some test layers
    doc.layers.add('TEXT_LAYER', color=2)
    doc.layers.add('DIMENSION_LAYER', color=3)
    doc.layers.add('TITLE_BLOCK', color=1)

    # Add Chinese text entities
    chinese_texts = [
        "图层: 建筑平面图",
        "块: 柱子",
        "标注: 1:100",
        "文字: 测试文本",
        "多行文字: 这是一个测试多行文本示例",
        "插入点: (0,0,0)",
        "旋转: 90度",
        "比例: 1:50",
        "线型: CONTINUOUS",
        "颜色: RED",
        "线宽: 0.5mm"
    ]

    # Add MTEXT entities
    for i, text in enumerate(chinese_texts):
        msp.add_mtext(
            text,
            dxfattribs={
                'insert': (0, i * 10, 0),
                'char_height': 2.5,
                'width': 50,
                'layer': 'TEXT_LAYER',
                'style': 'Standard'
            }
        )

    # Add TEXT entities
    for i, text in enumerate(chinese_texts[:5]):
        msp.add_text(
            text,
            dxfattribs={
                'insert': (60, i * 10, 0),
                'height': 2.0,
                'layer': 'TEXT_LAYER',
                'style': 'Standard'
            }
        )

    # Add some dimensions
    msp.add_linear_dim(
        base=(0, 0, 0),
        p1=(10, 0, 0),
        p2=(50, 0, 0),
        dxfattribs={
            'layer': 'DIMENSION_LAYER',
            'text': "长度: 50mm"
        }
    )

    # Add title block
    title_text = [
        "项目名称: 测试项目",
        "图纸编号: A-001",
        "设计: 工程师",
        "日期: 2024-01-01",
        "比例: 1:100",
        "单位: 毫米"
    ]

    for i, text in enumerate(title_text):
        msp.add_text(
            text,
            dxfattribs={
                'insert': (0, -20 - i * 5, 0),
                'height': 3.0,
                'layer': 'TITLE_BLOCK',
                'style': 'Standard'
            }
        )

    # Save the file
    output_path = os.path.join(os.path.dirname(__file__), 'test_chinese_text.dxf')
    doc.saveas(output_path)
    print(f"Test DXF file created: {output_path}")
    return output_path

if __name__ == "__main__":
    create_test_dxf()