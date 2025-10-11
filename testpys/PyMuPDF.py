import fitz  # PyMuPDF


def extract_text_blocks(pdf_path):
    """
    提取PDF中每个页面的文本块信息，包括内容、位置和字体样式。
    """
    doc = fitz.open(pdf_path)
    text_blocks_info = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # 关键步骤：以字典形式获取页面中的所有块信息
        blocks_dict = page.get_text("dict")

        for block in blocks_dict["blocks"]:
            if block["type"] == 0:  # 类型为0表示文本块
                block_text = ""
                font_sizes = []
                fonts_used = set()

                # 遍历块中的每一行和每一个span
                for line in block["lines"]:
                    for span in line["spans"]:
                        # 拼接文本内容
                        block_text += span["text"]
                        print(span["text"])
                        # 记录字体大小和字体名称
                        font_sizes.append(span["size"])
                        fonts_used.add(span["font"])

                # 汇总该文本块的信息
                block_info = {
                    "page"     : page_num + 1,
                    "bbox"     : block["bbox"],  # 边界框坐标 [x0, y0, x1, y1]
                    "text"     : block_text.strip(),
                    "font_size": max(font_sizes) if font_sizes else 0,  # 取最大字体作为代表
                    "font"     : list(fonts_used)[0] if fonts_used else None,  # 取第一种字体
                }
                text_blocks_info.append(block_info)

    doc.close()
    return text_blocks_info


if __name__ == "__main__":
    # 使用示例
    pdf_path = "组织推荐班委-刘禹初.pdf"  # 替换为你的PDF文件路径
    blocks = extract_text_blocks(pdf_path)

    # 打印结果
    for i, block in enumerate(blocks):
        print(f"块 {i + 1} (第{block['page']}页):")
        print(f"  位置: {block['bbox']}")
        print(f"  字体: {block['font']}, 大小: {block['font_size']:.1f}")
        print(f"  内容: {block['text']}")  # 只打印前100个字符
        print("-" * 50)

    # from SSPY.mypdf import PdfLoad
    # a = PdfLoad(pdf_path, table_only = False)
    # print(a.pages)
