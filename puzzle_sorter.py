def sort(filename):
    bins={i: [] for i in range(81)}
    with open(filename,"r") as input:
        input.readline()
        for line in input:
            puzzle, solution = line.split(",")
            key=puzzle.count("0")
            bins[key].append(line)
    for (i, bin) in bins.items():
        if len(bin)>0:
            with open("data/"+str(i)+".csv", "w") as output_file:
                output_file.write("quizzes,solutions\n")
                output_file.writelines(bin)


if __name__ == '__main__':
    sort("data/sudoku.csv")