import csv

# Write to csv file
def write2csv(table, path):
    with open(path, 'w', newline="") as out:
        csv_out = csv.writer(out)
        csv_out.writerows(table)

def readcsv(path, column_types=None):
    with open(path, 'r') as f:
        table = list(csv.reader(f))
        if not column_types:
            return table
        for i in range(len(table)):
            for j in range(len(column_types)):
                table[i][j] = column_types[j](table[i][j])
        return table