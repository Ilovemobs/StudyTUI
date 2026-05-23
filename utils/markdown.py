def markdown_to_text(md: str) -> str:
    import re
    text = re.sub(r'#{1,6}\s+', '', md)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'[-*+]\s+', '', text)
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
    return text.strip()
