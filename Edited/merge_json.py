import json

Dir = 'MapsaHR\Excercise Pre\Home_Divar\AmirHossein\TehranHousePrices-development\data\House_data_base.part03\database-bil'
json_files = ['0-1.json','1-47.json','46-49.json','50-99.json','100-199.json','200-299.json','300-999.json']

for i in range(len(json_files)):
    json_files[i] = Dir + json_files[i]

def merge_JsonFiles(filename):
    result = []
    for f1 in filename:
        with open(f1, 'r') as fin:
            result.append(json.load(fin))

    with open('merged_jsons_divar.json','w') as fout:
        json.dump(result, fout)

merge_JsonFiles(json_files)

