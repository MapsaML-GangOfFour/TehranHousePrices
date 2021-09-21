import pandas as pd
from pathlib import Path


def base_cleaner(df):
    def choose_floor(txt):
        split = txt.split(' از ')[0]
        if split.isnumeric():
            split = int(split)
        else:
            split = {'زیرهمکف': -1,
                     'همکف'   : 0,
                     '+۳۰'    : 31,
                     '۳۰+'    : 31}[split]
        return split

    df.loc[df['اتاق'] == 'بدون اتاق', 'اتاق'] = '0'
    df.drop(['آژانس املاک', 'آگهی‌دهنده', 'نوع ساختمان', 'تور مجازی ۳۶۰ درجه'], axis=1, inplace=True)
    df.drop_duplicates(subset='token', inplace=True)
    df.dropna(subset=['ناحیه', 'متراژ', 'ساخت', 'اتاق', 'قیمت کل', 'طبقه'], inplace=True)
    for col in ['قیمت کل', 'قیمت هر متر']:
        df.loc[:, col] = df[col].str.replace('٫', '').str.replace('تومان', '').astype('int64')
    df['طبقه واحد'] = df['طبقه'].apply(lambda x: choose_floor(x))
    df.fillna(value={'پارکینگ': False,
                     'آسانسور': 0,
                     'انباری' : 0,
                     }, inplace=True)
    df.reset_index(inplace=True, drop=True)
    df = df.assign(کلنگی=df['ساخت'] == 'قبل از ۱۳۷۰')
    df.loc[df['کلنگی'], 'ساخت'] = 1300
    df = df.astype({'ناحیه'  : 'category',
                    'متراژ'  : 'int16',
                    'ساخت'   : 'int16',
                    'اتاق'   : 'int16',
                    'آسانسور': 'bool',
                    'پارکینگ': 'bool',
                    'انباری' : 'bool',
                    })
    return df


def database_files_concatenate(p: Path):
    df = pd.DataFrame()
    for file in p.glob('*.json'):
        dff = pd.read_json(file)
        df = df.append(dff)
    return df


if __name__ == '__main__':
    folder = Path('../data')
    database = database_files_concatenate(folder)
    database = base_cleaner(database)
    db = database[['ناحیه', 'متراژ', 'ساخت', 'اتاق', 'قیمت کل', 'طبقه واحد', 'آسانسور', 'پارکینگ', 'انباری']]
    db.to_pickle((folder / "concatenated base database.pkl.gzip"), compression="gzip")
    print('Done')
