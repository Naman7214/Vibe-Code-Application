import xml.etree.ElementTree as ET

def parse_xml_to_dict(xml_str):
    root = ET.fromstring(xml_str)
    file_data = []

    for file_elem in root.findall('file'):
        file_path = file_elem.find('file_path').text
        code_snippet = file_elem.find('code_snippet').text
        file_data.append({
            'file_path': file_path,
            'code_snippet': code_snippet
        })

    return file_data