import sudoku
import os
import statistics

from functools import reduce

def test():
    files = os.listdir("data/sorted")
    for file in sorted(files):
        with open("data/sorted/"+file,"r") as input:
            input.readline()
            print("FILENAME: "+file)
            results=[]
            i=0
            solved_by_ac=0
            t = sudoku.Sudoku(None)
            for line in input:
                #SETUP
                steps = [0, 0, 0, 0, 0, 0, 0, 0]
                (puzzle, solution)=line.split(",")
                s=sudoku.Sudoku(puzzle)

                #TEST EFFECTIVENESS OF AC vs DEFAULT BACKTRACKING
                p=s.to_problem()
                sudoku.Solver.counter=0
                if sudoku.Solver.AC_1(p):
                    solved_by_ac += 1
                else:
                    if not sudoku.Solver.backtracking(p):
                        raise Exception
                    steps[1]=sudoku.Solver.counter
                    sudoku.Solver.counter=0
                t.from_problem(p)
                if t.__repr__() != solution[:-1]:
                    raise Exception
                p=s.to_problem()

                sudoku.Solver.backtracking(p)
                steps[0] = sudoku.Solver.counter
                sudoku.Solver.counter = 0
                t.from_problem(p)
                if t.__repr__() != solution[:-1]:
                    raise Exception

                #TEST FORWARD CHECKING
                p = s.to_problem()
                sudoku.Solver.forward_checking(p)
                steps[2] = sudoku.Solver.counter
                t.from_problem(p)
                if t.__repr__() != solution[:-1]:
                    raise Exception

                #TEST FORWARD CHECKING WITH FIRST FAIL
                p = s.to_problem()
                sudoku.Solver.forward_checking(p, True)
                steps[3] = sudoku.Solver.counter
                t.from_problem(p)
                if t.__repr__() != solution[:-1]:
                    raise Exception

                #TEST FORWARD CHECKING WITH MIN CONFLICT
                p = s.to_problem()
                sudoku.Solver.forward_checking(p, least_conflict_heuristic=True)
                steps[4] = sudoku.Solver.counter
                steps[5] = sudoku.Solver.aux_counter
                t.from_problem(p)
                if t.__repr__() != solution[:-1]:
                    raise Exception

                # TEST FORWARD CHECKING WITH both
                p = s.to_problem()
                sudoku.Solver.forward_checking(p, True, True)
                steps[6] = sudoku.Solver.counter
                steps[7] = sudoku.Solver.aux_counter
                t.from_problem(p)
                if t.__repr__() != solution[:-1]:
                    raise Exception

                #FINALIZE
                results.append(steps)
                i += 1
                if i > 4999:
                    break
            # with open("results/"+file, "w") as output:
            #     output.write("BT,BT+AC,FC,FCFF,FCMC\n")
            #     for r in results:
            #         output.write(str(r)[1:-1])
            #         output.write("\n")
            print(f"Number of puzzles: {i}")
            print(f"Solved by AC only: {solved_by_ac} ({solved_by_ac/i*100:.2f}%)")
            backtracking=get_col(results,0)
            withAC=get_col(results,1)
            FC=get_col(results,2)
            FCFF=get_col(results,3)
            FCMC = get_col(results, 4)
            FCMCAUX = get_col(results,5)
            FCB= get_col(results,6)
            FCBAUX= get_col(results,7)
            print(f"Backtraking: min {min(backtracking)}, avg {statistics.mean(backtracking):.2f}, max {max(backtracking)}  values tested")
            print([round(q, 1) for q in statistics.quantiles(backtracking, n=10)])
            print(f"Backtraking with AC: min {min(withAC)}, avg {statistics.mean(withAC):.2f}, max {max(withAC)}  values tested")
            print([round(q, 1) for q in statistics.quantiles(withAC, n=10)])
            print(f"Forward checking: min {min(FC)}, avg {statistics.mean(FC):.2f}, max {max(FC)}  values tested")
            print([round(q, 1) for q in statistics.quantiles(FC, n=10)])
            print(f"Forward checking with FF: min {min(FCFF)}, avg {statistics.mean(FCFF):.2f}, max {max(FCFF)}  values tested")
            print([round(q, 1) for q in statistics.quantiles(FCFF, n=10)])
            print(f"Forward checking with MC: min {min(FCMC)}, avg {statistics.mean(FCMC):.2f}, max {max(FCMC)}  values tested")
            print([round(q, 1) for q in statistics.quantiles(FCMC, n=10)])
            print(f"using the results of other: min {min(FCMCAUX)}, avg {statistics.mean(FCMCAUX):.2f}, max {max(FCMCAUX)}  values tested")
            print([round(q, 1) for q in statistics.quantiles(FCMCAUX, n=10)])
            print(
                f"Forward checking with both: min {min(FCB)}, avg {statistics.mean(FCB):.2f}, max {max(FCB)}  values tested")
            print([round(q, 1) for q in statistics.quantiles(FCB, n=10)])
            print(
                f"using the results of other: min {min(FCBAUX)}, avg {statistics.mean(FCBAUX):.2f}, max {max(FCBAUX)}  values tested")
            print([round(q, 1) for q in statistics.quantiles(FCBAUX, n=10)])
            print()


def get_col(list,col):
    return [row[col] for row in list]


if __name__ == "__main__":
    test()