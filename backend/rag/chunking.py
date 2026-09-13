CHUNK_SIZE = 900
CHUNK_OVERLAP = 120


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks while preferring paragraph boundaries."""
    if not text.strip():
        return []

    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n")]
    paragraphs = [paragraph for paragraph in paragraphs if paragraph]

    chunks = []
    current = ""

    for paragraph in paragraphs:
        if len(paragraph) > CHUNK_SIZE:
            if current:
                chunks.append(current)
                current = ""

            start = 0
            while start < len(paragraph):
                end = start + CHUNK_SIZE
                chunks.append(paragraph[start:end])

                if end >= len(paragraph):
                    break

                start = end - CHUNK_OVERLAP

            continue

        candidate = f"{current}\n\n{paragraph}" if current else paragraph

        if len(candidate) <= CHUNK_SIZE:
            current = candidate
        else:
            chunks.append(current)

            overlap = current[-CHUNK_OVERLAP:]
            current = f"{overlap}\n\n{paragraph}"

    if current:
        chunks.append(current)

    return chunks