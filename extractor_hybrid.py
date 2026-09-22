import re
import sys

# Month abbreviations, CPU codes, and ciphers to ignore in Alphanumeric Sub-Docs
IGNORE_PREFIXES = [
    "AES", "SEED", "GOST", "DES", "RSA", "SHA", "MD5",
    "JAN", "FEB", "MAR", "APR", "MAY", "JUN", 
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC",
    "JANUARY", "FEBRUARY", "MARCH", "APRIL", "JUNE", 
    "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
    "CPU", "CPUOCT", "CPUJUL", "CPUAPR", "CPUJAN",
    "ORA", "PLS", "JDK", "SLES", "RHEL", "LNX", "BP", "UEK", "ORACORE",
    "BUG", "XMS", "XMX", "XMN", "XSS"
]

def extract_hybrid(text, min_doc_digits=3, max_doc_digits=8):
    """
    HYBRID EXTRACTOR (Option 2 - Categorized)
    
    1. Main Doc:
       - Identifies the primary main document ID at the top of the advisory (e.g. KB873521, KB111315, NEWS20).
       
    2. Patches:
       - Pure 7 to 8 digits, handles prefixes (Patch:, PATCH, *PATCH, <Patch...>, BUG:)
       - Strips trailing footnotes/suffixes (*, +, PM, P+, +E, C, EC, P, D, I, MP, etc.)
       - Excludes version strings (e.g. 11.2.0.4.250415), build dates (build=170814, BP:170718), error codes, dates, and alphanumeric doc prefixes.
       
    3. Sub Docs (KB / Alphanumeric):
       - Alphanumeric doc IDs (e.g. FAQ1948, KB106822, KB866924, KB407227, NEWS20).
       - Cleans glued prefixes (e.g. inKB866924 -> KB866924, inKB407227 -> KB407227).
       - Filters out months, ciphers, error codes, and main doc header.
       - Formatted with 2 spaces.
       
    4. Sub Docs (MOS / .1 to .9):
       - MOS Doc IDs ending with .1 through .9 (e.g. 1067455.1, 32126974.8, 1935285.1, 888.1).
       - Strips trailing footnotes/suffixes (P*, *D, *, +, MP, K+, etc.).
       - Excludes multi-dot version numbers (11.2.0.4.9, 19.3.0.1).
       - Tracks occurrence counts: doc(count).
    """
    if not text or not text.strip():
        return None, [], [], {}

    # --- Step 1: Detect Main Document Header ---
    # Finds the very first alphanumeric doc code near the top of text (supports KB12345, NEWS20, etc.)
    main_doc = None
    first_kb_match = re.search(r'(?<!\d\.)(?<![A-Za-z0-9_])([A-Za-z]{2,10}\d{2,10})(?!\.\d)(?![A-Za-z0-9_])', text[:500])
    if first_kb_match:
        cand = first_kb_match.group(1).upper()
        if not any(cand.startswith(p) for p in IGNORE_PREFIXES):
            main_doc = cand

    # --- Step 2: Extract Sub Docs (MOS - .1 to .9) ---
    # Lookbehind ensures no preceding version dot (blocks 11.2.0.4.9) and no attached letters/underscores
    # Discards trailing suffixes like P*, *D, *, +, MP, K+, etc.
    mos_pattern = rf'(?<!\d\.)(?<![A-Za-z0-9_])(\d{{{min_doc_digits},{max_doc_digits}}}\.[1-9])(?:[A-Za-z*+!#~%^&|/\\?-]+)?(?!\.\d)'
    
    mos_subdocs_counts = {}
    for doc in re.findall(mos_pattern, text):
        mos_subdocs_counts[doc] = mos_subdocs_counts.get(doc, 0) + 1

    # --- Step 3: Extract Sub Docs (KB / Alphanumeric) ---
    # Matches tokens like KB866924, FAQ1948, KB106822, KI72728E, KI98374PE, NEWS20, inKB866924, inKB407227
    # Strips trailing footnote/status suffixes (e.g. KI72728E -> KI72728, KI98374PE -> KI98374)
    kb_pattern = r'(?<!\d\.)(?<![A-Za-z0-9_])([A-Za-z]{2,12}\d{2,10})(?:[A-Za-z*+!#~%^&|/\\?-]+)?(?!\.\d)(?![0-9_])'
    kb_subdocs = []
    
    for match in re.findall(kb_pattern, text):
        token = match.upper()
        
        # Clean glued prepositions (e.g. INKB866924 -> KB866924, INKB407227 -> KB407227)
        for prep in ["IN", "TO", "OF", "IS", "ON", "FOR"]:
            if token.startswith(prep + "KB") or token.startswith(prep + "FAQ") or token.startswith(prep + "DOC") or token.startswith(prep + "KI") or token.startswith(prep + "NEWS"):
                token = token[len(prep):]
                break
                
        # Filter out months, ciphers, error codes
        if any(token.startswith(prefix) for prefix in IGNORE_PREFIXES):
            continue
            
        # Ignore main doc header
        if main_doc and token == main_doc:
            continue
            
        if token not in kb_subdocs:
            kb_subdocs.append(token)

    # --- Step 4: Extract Patches ---
    # Lookbehind (?<![A-Za-z0-9_.-]) ensures patch does NOT start with letters (e.g. KB182654 is blocked)
    # Exclude build dates like build=170814 or BP:170718 or B204P:171017
    # (\d{7,8}) captures the 7 to 8 digit patch number
    # (?:[A-Za-z*+!#~%^&|/\\?-]+)? strips trailing suffixes (*, +, PM, P+, +E, MP, etc.)
    patch_pattern = r'(?<!build=)(?<!BP:)(?<!B204P:)(?:(?<![A-Za-z0-9_.-])|(?<=\bBUG)|(?<=\bbug))(\d{7,8})(?:[A-Za-z*+!#~%^&|/\\?-]+)?(?!\.\d)(?![0-9_])'
    
    patches = []
    for num in re.findall(patch_pattern, text):
        # Exclude if it's the main doc numeric portion (e.g. 873521 in KB873521)
        if main_doc and main_doc.endswith(num):
            continue
            
        # Exclude if it's part of an alphanumeric sub-doc
        if any(kb.endswith(num) for kb in kb_subdocs):
            continue
            
        # Exclude if it's a version date (YYMMDD like 170718, 160719 when attached to BP)
        if num in patches:
            continue
            
        patches.append(num)

    return main_doc, patches, kb_subdocs, mos_subdocs_counts

def format_hybrid_output(main_doc, patches, kb_subdocs, mos_subdocs_counts):
    main_doc_str = main_doc if main_doc else "None identified"
    patches_str = ", ".join(patches) if patches else "None found"
    kb_str = "  ".join(kb_subdocs) if kb_subdocs else "None found"
    
    mos_formatted = [f"{doc}({count})" for doc, count in mos_subdocs_counts.items()]
    mos_str = ", ".join(mos_formatted) if mos_formatted else "None found"
    
    patches_count = len(patches)
    kb_count = len(kb_subdocs)
    
    mos_unique_count = len(mos_subdocs_counts)
    mos_total_count = sum(mos_subdocs_counts.values())
    mos_count_display = f"{mos_unique_count}({mos_total_count})"
    
    output = (
        f"Main Doc:\t{main_doc_str}\n"
        f"Patches:\t{patches_str}\n"
        f"Sub Docs (KB):\t{kb_str}\n"
        f"Sub Docs (MOS):\t{mos_str}\n\n"
        f"Patches Count:\t\t{patches_count}\n"
        f"Sub Docs (KB) Count:\t{kb_count}\n"
        f"Sub Docs (MOS) Count:\t{mos_count_display}"
    )
    return output

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            m, p, kb, mos = extract_hybrid(content)
            print(format_hybrid_output(m, p, kb, mos))
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    else:
        print("--- Hybrid Mode (Paste text, then press Ctrl+Z and Enter on Windows) ---")
        try:
            content = sys.stdin.read()
            m, p, kb, mos = extract_hybrid(content)
            print("\n=== HYBRID EXTRACTION RESULTS ===")
            print(format_hybrid_output(m, p, kb, mos))
        except Exception as e:
            print(f"Error: {e}")
            
        print("\n" + "-" * 50)
        input("Press Enter to close window...")
