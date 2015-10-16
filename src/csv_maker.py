import csv

def doCSV(csv_file_path, raw_data):
    def reduce_item(key, value):
        #Reduction Condition 1
        if type(value) is list:
            if type(value[0]) is str:
                reduced_item[str(key)] = ', '.join(value)
            elif type(value[0]) is dict:
                reduced_item[str(key)] = ""
                for sub_item in value[:-1]:
                    reduced_item[str(key)] += ', '.join(sub_item.values()) + ', '
                reduced_item[str(key)] += ', '.join(value[-1].values())

        #Reduction Condition 2
        elif type(value) is dict:
            sub_keys = value.keys()
            for sub_key in sub_keys:
                reduce_item(key+'_'+str(sub_key), value[sub_key])

        #Base Condition
        else:
            reduced_item[str(key)] = value
    processed_data = []
    header = []
    for item in raw_data:
        reduced_item = {}
        reduce_item('', item)

        header += reduced_item.keys()

        processed_data.append(reduced_item)

    header = list(set(header))
    header.sort()

    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, header, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in processed_data:
            writer.writerow(row)
