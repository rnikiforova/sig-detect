import os
from collections import defaultdict

import spacy
from rasa.shared.nlu.constants import ENTITY_ATTRIBUTE_START, ENTITY_ATTRIBUTE_VALUE, ENTITY_ATTRIBUTE_END, \
    ENTITY_ATTRIBUTE_TYPE
from spacy.tokens import Token
import pandas as pd
import rasa.train
from rasa.shared.nlu.training_data.entities_parser import find_entities_in_training_example, replace_entities

print("Loading spacy...")
nlp = spacy.load("en_core_web_md")
print("Spacy loaded.")

# import geonamescache
#
# gc = geonamescache.GeonamesCache()
# states = gc.get_us_states_by_names()
# states_short = gc.get_us_states()


with open(r"..\lookup\first_names.txt") as f_first:
    first_names = f_first.readlines()
    first_names = set(x.lower().strip() for x in first_names)

with open(r"..\lookup\last_names.txt") as f_last:
    last_names = f_last.readlines()
    last_names = set(x.lower().strip() for x in last_names)

with open(r"..\lookup\job_titles.txt") as f_jobs:
    job_titles = f_jobs.readlines()
    job_titles = set(x.lower().strip() for x in job_titles)
    job_titles_parts = set([word.lower().strip() for title in job_titles for word in title.split(" ")])


def entities_by_position(ents):
    return {(ent[ENTITY_ATTRIBUTE_START], ent[ENTITY_ATTRIBUTE_END]): ent[ENTITY_ATTRIBUTE_TYPE] for ent in ents}


def get_label(start, text, ents):
    end = start + len(text)
    by_position = entities_by_position(ents)
    for (start_ent, end_ent), label in by_position.items():
        if start >= start_ent and end <= end_ent: # contained
            return label
    return "no_entity"


dir_path = r"F:\Documents\stopansko\masters\thesis\sig-detect\data\clean\enron_random_clean_signatures"
full_d = []
for root, dirs, filenames in os.walk(dir_path):
    if ".idea" in root:
        continue
    for i, filename in enumerate(filenames):
        # d = defaultdict(list)
        file_features = []
        print(f"{i}. {filename} ...")
        with open(os.path.join(root, filename), encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            entities = find_entities_in_training_example(line)
            plain_text = replace_entities(line)
            doc = nlp(plain_text)
            for t in doc:
                low = t.orth_.lower()
                curr_d = {
                    "token": t.orth_,
                    "filename": filename,
                    "label": get_label(t.idx, t.orth_, entities),

                    "email": t.like_email,
                    "url": t.like_url,
                    "num": t.like_num,
                    "stop": t.is_stop,
                    "alpha": t.is_alpha,
                    "title": t.is_title,
                    "first": low in first_names,
                    "last": low in last_names,
                    "job": low in job_titles,
                    "job_part": low in job_titles_parts,
                    "spacy": t.ent_type_ or "no_entity",
                    "prefix3": t.orth_[:3],
                    "line_prefix3": plain_text[:3],
                    "line_suffix3": plain_text[-3:],
                    "shape": t.shape_,

                }
                file_features.append(curr_d)
                # if plain_text.strip() and t.orth_.strip():
                #     file_features.append(curr_d)
        full_d.append(file_features)

# df = pd.DataFrame(d)

import pickle
# with open(r"../../sig-detect/prep/df_ner.pkl", "wb") as f:
#     pickle.dump(df, f)

with open(r"../../sig-detect/prep/list_ner.pkl", "wb") as f:
    pickle.dump(full_d, f)

print("Saved to df_ner.pkl")


# THEN
# - analyze for sufixes, prefixes

# THEN
# - sender, from, cc, headers
