from app.services.document_processor import DocumentProcessor
import os

def test_text_extraction():
    content = "Patient Name: Jane Doe\nFSH Level: 7.5 mIU/mL\nAMH Level: 2.1 ng/mL"
    filename = "test_report.txt"
    file_bytes = content.encode("utf-8")
    
    result = DocumentProcessor.extract(file_bytes, filename)
    print(f"--- TEXT EXTRACTION TEST ---")
    print(f"Filename: {result['filename']}")
    print(f"Format: {result['format']}")
    print(f"Text Content:\n{result['text']}")
    assert "Jane Doe" in result['text']
    assert result['format'] == "TXT"
    print("SUCCESS\n")

if __name__ == "__main__":
    try:
        test_text_extraction()
    except Exception as e:
        print(f"TEST FAILED: {e}")
