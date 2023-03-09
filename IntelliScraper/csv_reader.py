import csv

def read(filename):
    columns = []
    data = []
    with open(f"../{filename}", 'r') as file:
      csvreader = csv.reader(file)
      for i, row in enumerate(csvreader):
        if i == 0:
            for item in row:
                columns.append(item)
            continue
        sample = {}
        for j, item in enumerate(row):
          sample[columns[j]] = row[j]
        data.append(sample)
    return data

def pluck(data, column):
  output = []
  for dictionary in data:
      output.append(dictionary[column])
  return output

