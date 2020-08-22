import pandas as pd
import json


def row_to_dict(row, prefix=""):
    features = {
        # prefix+'blank': row.blank,
        prefix+'len': row.len,
        prefix+'lineNo': row.lineNo,
        prefix+'email': row.email,
        # prefix+'url': row.url,
        # prefix+'phone': row.phone,
        # prefix+'sigdelimiter': row.sigdelimiter,
        # prefix+'special': row.special,
        # prefix+'words': row.words,
        # prefix+'name': row.name,
        # prefix+'endquote': row.endquote,
        # prefix+'tabs1': row.tabs1,
        # prefix+'tabs2': row.tabs2,
        # prefix+'tabs3': row.tabs3,
        # prefix+'punct20': row.punct20,
        # prefix+'punct50': row.punct50,
        # prefix+'punct90': row.punct90,
        # prefix+'reply': row.reply,
        # prefix+'startpunct': row.startpunct,
        # prefix+'firstchar': row.firstchar,
        # prefix+'replypunct': row.replypunct,
        # prefix+'wrote': row.wrote,
        # prefix+'alphanum90': row.alphanum90,
        # prefix+'alphanum50': row.alphanum50,
        # prefix+'alphanum10': row.alphanum10,
        # prefix+'title': row.title,
        # prefix+'posFromEnd': row.posFromEnd,
        # prefix+'last': row["last"], # last is a pd function
        # prefix+'prevlast': row.prevlast,
        # prefix+'last5': row.last5,
        # prefix+'last11': row.last11,
        # prefix+'lenRatio': row.lenRatio,
        # prefix+'less_avg_len': row.less_avg_len,
        # prefix+'more_avg_len': row.more_avg_len,
        # prefix+'less_avg_len75': row.less_avg_len75,
        # prefix+'less_avg_len50': row.less_avg_len50
    }
    return features


def line2features(index, row, source):
    features = row_to_dict(row)

    # There is a previous one
    if row.lineNo > 1:
        prev_line = source.shift(1)
        features.update(row_to_dict(prev_line, "-1:"))
    else:
        features['BOS'] = True

    if (row.posFromEnd > 0) and (index < len(source.index) - 1):
        next_line = source.iloc[index + 1]
        features.update(row_to_dict(next_line, "+1:"))
    else:
        features['EOS'] = True
    return features


def df2features(df):
    new_df = df.copy()
    cols = df.columns
    for col in cols:
        new_df[f"-1:{col}"] = new_df[col].shift(1)
        new_df[f"+1:{col}"] = new_df[col].shift(-1)

    features = [row.dropna().to_dict() for idx, row in new_df.iterrows()]
    return features


def get_features(df):
    return [[line2features(index, row, df) for index, row in df.iterrows()]]


if __name__ == "__main__":
    # s = """
    # 5 Lorem ipsum
    # 7 Dolor sit
    # 2 Other
    # """
    #
    # data = {
    #     "starts": [5, 7, 2],
    #     "ends": ["m", "t", "r"],
    #     "lineNo": [0, 1, 2],
    #     "posFromEnd": [2, 1, 0]
    # }
    # master = pd.DataFrame(data)
    master = pd.read_pickle("master.pkl")

    # columns: Index(['line', 'filename', 'entity', 'len', 'lineNo', 'email', 'url', 'phone',
    #        'sigdelimiter', 'special', 'words', 'name', 'endquote', 'tabs1',
    #        'tabs2', 'tabs3', 'punct20', 'punct50', 'punct90', 'reply',
    #        'startpunct', 'firstchar', 'replypunct', 'wrote', 'alphanum90',
    #        'alphanum50', 'alphanum10', 'title', 'nlines', 'len_avg', 'len_min',
    #        'len_max', 'nBlanks', 'nNonBlanks', 'nSig', 'posFromEnd', 'last',
    #        'prevlast', 'last5', 'last11', 'posRatio', 'posRatioNB', 'lenRatio',
    #        'less_avg_len', 'more_avg_len', 'less_avg_len75', 'less_avg_len50'],
    #       dtype='object')

    # print(master.filename.unique())
    first = master[(master.filename == "0.txt") | (master.filename == "1.txt")]
    first = first.loc[:, ["line", "len", "lineNo", "email"]]

    X_train = df2features(first)
    print(X_train.loc[:, ["lineNo", "lineNo_prev", "lineNo_next"]])
