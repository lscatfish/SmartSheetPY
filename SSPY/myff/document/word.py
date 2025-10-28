"""word文件docx"""
import zipfile
from typing import List

import xml.etree.ElementTree as ET

from .base import ParasSheets


class DirectDocxParser:
    """直接解析docx的XML结构，避免依赖python-docx，解析产生自cpp原始逻辑"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.namespace = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
        }

    def parse_tables_from_xml(self) -> List[List[List[str]]]:
        """直接从document.xml解析表格数据"""
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                # 读取document.xml
                with zip_ref.open('word/document.xml') as xml_file:
                    xml_content = xml_file.read()

                return self._parse_xml_tables(xml_content)

        except (zipfile.BadZipFile, KeyError, ET.ParseError) as e:
            print(f"XML解析错误: {e}")
            return []

    def _parse_xml_tables(self, xml_content: bytes) -> List[List[List[str]]]:
        """解析XML中的表格结构"""
        root = ET.fromstring(xml_content)
        all_tables = []

        # 查找所有表格元素
        for tbl_elem in root.findall('.//w:tbl', self.namespace):
            table_data = []

            # 处理每一行
            for tr_elem in tbl_elem.findall('w:tr', self.namespace):
                row_data = []

                # 处理每个单元格
                for tc_elem in tr_elem.findall('w:tc', self.namespace):
                    cell_text = self._extract_cell_text(tc_elem)
                    row_data.append(cell_text.strip())

                if row_data:  # 只添加非空行
                    table_data.append(row_data)

            if table_data:  # 只添加非空表格
                all_tables.append(table_data)

        return all_tables

    def _extract_cell_text(self, cell_element) -> str:
        """提取单元格内的文本内容"""
        text_parts = []

        # 提取段落文本
        for p_elem in cell_element.findall('.//w:p', self.namespace):
            para_text = []
            for t_elem in p_elem.findall('.//w:t', self.namespace):
                if t_elem.text:
                    para_text.append(t_elem.text)

            if para_text:
                text_parts.append(''.join(para_text))

        return ' '.join(text_parts)

    def parse_paragraphs_from_xml(self) -> List[str]:
        """直接从XML解析段落文本"""
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                with zip_ref.open('word/document.xml') as xml_file:
                    xml_content = xml_file.read()

                return self._parse_xml_paragraphs(xml_content)

        except Exception as e:
            print(f"段落解析错误: {e}")
            return []

    def _parse_xml_paragraphs(self, xml_content: bytes) -> List[str]:
        """解析XML中的段落文本"""
        root = ET.fromstring(xml_content)
        paragraphs = []

        for p_elem in root.findall('.//w:p', self.namespace):
            para_text = []
            for t_elem in p_elem.findall('.//w:t', self.namespace):
                if t_elem.text:
                    para_text.append(t_elem.text)

            if para_text:
                paragraph = ''.join(para_text).strip()
                if paragraph:
                    paragraphs.append(paragraph)

        return paragraphs


class Word(ParasSheets):
    """word文件的解析，只实现读取方法"""

    def __init__(self, path, if_print = False):
        super().__init__(path)
        d = DirectDocxParser(self._absolute_path)
        self._paragraphs = d.parse_paragraphs_from_xml()

    def __parse_sheets(self,d):
        self._sheets = d.parse_tables_from_xml()

