def file_to_text(uploaded_file) -> str:
    data = uploaded_file.read()
    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return data.decode("latin-1", errors="ignore")
