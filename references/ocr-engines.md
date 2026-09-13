# OCR engine selection

Prefer a local engine. Apple Vision is convenient on macOS; PaddleOCR can provide strong multilingual recognition when its models are available; Tesseract is a broad fallback. Capture engine/version and confidence metadata. If a model cannot be downloaded, report the fallback instead of silently claiming a second-engine comparison.
