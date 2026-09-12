<img width="1901" height="957" alt="image" src="https://github.com/user-attachments/assets/d49bdf14-771e-4ab0-ac3f-4f50d0b5b6d1" />

# Punjabi Transliteration Tools — PySide6

Enhanced desktop version of the supplied Streamlit starter.

## Features

- Modern dark PySide6 interface
- Gurmukhi input and Shahmukhi output
- Shahmukhi input and Gurmukhi output
- Two-way transliteration buttons
- Swap text
- Clear workspace
- Copy buttons
- Open `.txt`, `.md`, and `.srt`
- Save text as UTF-8
- Character counters
- Unicode-friendly editors
- Built-in transparent transliteration mapping
- Separate Tools & Notes tab
- No Streamlit server required

## Install

Windows PowerShell:

```powershell
py -m pip install PySide6
```

## Run

```powershell
py punjabi_transliteration_tools.py
```

## Important

The original Streamlit example used:

```python
gurmukhi_text[::-1]
```

and:

```python
shahmukhi_text[::-1]
```

as dummy processing.

This application replaces that demo behavior with a real, transparent Unicode character mapping. Punjabi transliteration is linguistically complex and can be ambiguous, so the mapping is deliberately kept inside the source code and can later be replaced by a validated Punjabi transliteration engine.

The functions to replace are:

```python
transliterate_g2s()
transliterate_s2g()
```

## Suggested future versions

### v1.1
- Better word-aware Gurmukhi → Shahmukhi rules
- Better Shahmukhi → Gurmukhi disambiguation
- Punjabi spell-checking
- Roman Punjabi input/output
- Search and replace

### v1.2
- Side-by-side synchronized editing
- Transliteration history
- Preset language modes
- Export paired Gurmukhi/Shahmukhi text

### v2.0
- Full validated Punjabi transliteration engine
- Document batch conversion
- SRT-aware transliteration
- DOCX/PDF text extraction
- Drag-and-drop files
