import xml.etree.ElementTree as ET

def parse_xml_to_dict(xml_str):
    root = ET.fromstring(xml_str)
    file_data = []

    for file_elem in root.findall('FILE'):
        file_path = file_elem.find('FILE_PATH').text
        code_snippet = file_elem.find('CODE_SNIPPET').text
        file_data.append({
            'file_path': file_path,
            'code_snippet': code_snippet
        })

    return file_data