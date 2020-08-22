import os
import numpy as np
import pandas as pd
from prep.utils import remove_blanks, line_to_entity, get_signature_length, strip_blank_lines

if __name__ == "__main__":
    files_path = r"F:\Documents\stopansko\masters\thesis\sig-detect\data\clean"
    filenames = [f for f in os.listdir(files_path) if os.path.isfile(os.path.join(files_path, f))]
    files = list()
    entities = list()
    for filename in filenames:
        with open(os.path.join(files_path, filename), mode="r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            lines = strip_blank_lines(lines)
            non_blanks = remove_blanks(lines)
            if len(non_blanks) > 0:
                lengths = [len(line) for line in lines]
                file_entities = [line_to_entity(line, filename, i) for i, line in enumerate(non_blanks)]
                entities.extend(file_entities)
                files.append({
                    "filename": filename,
                    "nlines": len(lines),
                    "len_avg": np.ceil(np.mean(lengths)),
                    "len_min": min(lengths),
                    "len_max": max(lengths),
                    "nBlanks": len(lines) - len(non_blanks),
                    "nNonBlanks": len(non_blanks),
                    "nSig": get_signature_length(file_entities)
                })

    df_files = pd.DataFrame(files)
    entities = pd.DataFrame(entities)