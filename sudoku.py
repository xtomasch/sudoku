from timeit import timeit


class Sudoku:

    def __init__(self, repr_string):
        if repr_string is None:
            self.data=list(range(81))
        else:
            self.data = list(repr_string)

    def to_problem(self):
        problem = []
        for i in range(len(self.data)):
            if self.data[i] == '0':
                problem.append(Variable(i))
            else:
                # noinspection PyTypeChecker
                problem.append(Variable(i, [ord(self.data[i]) - 48]))
        # row rules
        for row in range(9):
            for col in range(9):
                for i in range(col+1, 9):
                    NotEqual.new(problem[row * 9 + col], problem[row * 9 + i])
        # col rules
        for col in range(9):
            for row in range(9):
                for i in range(row+1, 9):
                    NotEqual.new(problem[row * 9 + col], problem[i * 9 + col])
        # square rules
        for s_row in range(3):
            for s_col in range(3):
                for i in range(9):
                    for j in range(i+1, 9):
                        NotEqual.new(problem[(s_row * 3 + i // 3) * 9 + s_col * 3 + i % 3],
                                     problem[(s_row * 3 + j // 3) * 9 + s_col * 3 + j % 3])
        return problem

    def from_problem(self, problem):
        for var in problem:
            self.data[var.name] = var.assignment

    def print(self, pretty=False):
        if pretty:

            def print_sudoku_line():
                nonlocal current_position
                print('│', end='')
                for i in range(3):
                    for j in range(3):
                        print(' '+str(self.data[current_position])+' ', end='')
                        current_position += 1
                    print('│', end='')
                print()

            current_position = 0
            print('┌' + 9 * '─' + "┬" + 9 * '─' + "┬" + 9 * '─' + '┐')
            print_sudoku_line()
            print_sudoku_line()
            print_sudoku_line()
            print('├' + 9 * '─' + "┼" + 9 * '─' + "┼" + 9 * '─' + '┤ ')
            print_sudoku_line()
            print_sudoku_line()
            print_sudoku_line()
            print('├' + 9 * '─' + "┼" + 9 * '─' + "┼" + 9 * '─' + '┤ ')
            print_sudoku_line()
            print_sudoku_line()
            print_sudoku_line()
            print('└' + 9 * '─' + "┴" + 9 * '─' + "┴" + 9 * '─' + '┘')

        else:
            for row in range(9):
                print(self.data[row*9:(row+1)*9])

    def __repr__(self):
        result = ""
        for field in self.data:
            result += str(field)
        return result


class Variable:
    def __init__(self, name, domain=range(1, 10)):
        self.domain = set(domain)
        self.constraints_from = []
        self.constraints_to = []
        self.assignment = None
        self.name = name

    def __repr__(self):
        assigned = self.assignment if self.assignment else "-"
        domain = self.domain if self.domain else "{}"
        return f"{self.name:>2}: {assigned} {domain} "


class InconsistentProblem(Exception):
    def __init__(self):
        pass


class NotEqual:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @staticmethod
    def new(a, b):
        c_from = NotEqual(a, b)
        c_to = NotEqual(b, a)
        a.constraints_from.append(c_from)
        b.constraints_from.append(c_to)
        a.constraints_to.append(c_to)
        b.constraints_to.append(c_from)

    @staticmethod
    def check_values(a_value, b_value):
        return a_value != b_value

    def check_value(self, a_value):
        for b_value in self.b.domain:
            if a_value != b_value:
                return True
        return False

    def propagate(self):
        to_delete = set()
        for a_value in self.a.domain:
            if not self.check_value(a_value):
                to_delete.add(a_value)
        if len(to_delete) == 0:
            return False
        self.a.domain -= to_delete
        if len(self.a.domain) == 0:
            raise InconsistentProblem
        return True

    def propagate_against_value(self, b_value):
        self.a.domain.discard(b_value)
        if len(self.a.domain) == 0:
            raise InconsistentProblem


class Solver:
    counter = 0
    @staticmethod
    def AC_1(problem):
        changed = True
        while changed:
            changed = False
            for variable in problem:
                for constraint in variable.constraints_from:
                    changed = constraint.propagate() or changed
        solved=True
        for variable in problem:
            if len(variable.domain) == 1:
                (variable.assignment,) = variable.domain
            else:
                solved=False
        return solved

    @staticmethod
    def first_conflict(problem):
        if len(problem) < 2:
            return
        min_domain_size=min(problem,key=lambda var: len(var.domain))
        i=problem.index(min_domain_size)
        problem[i], problem[-1] = problem[-1], problem[i]



    @staticmethod
    def least_constrained_first(problem):
        problem.sort(key = lambda var : len(var.domain))


    @staticmethod
    def most_constrained_first(problem):
        problem.sort(key=lambda var: len(var.domain), reverse=True)

    @staticmethod
    def backtracking(problem,heuristic=None):

        def backtracking_step(unassigned):
            if len(unassigned) == 0:
                return True
            variable = unassigned.pop()
            for value in variable.domain:
                Solver.counter += 1
                value_consistent = True
                for constraint in variable.constraints_to:
                    if constraint.a.assignment and not constraint.check_values(constraint.a.assignment, value):
                        value_consistent = False
                        break
                if value_consistent:
                    variable.assignment = value
                    if backtracking_step(unassigned):
                        return True
            unassigned.append(variable)
            variable.assignment=None
            return False

        Solver.counter = 0
        unassigned = []
        for var in problem:
            if len(var.domain) == 0:
                raise InconsistentProblem
            if not var.assignment:
                if len(var.domain) == 1:
                    (var.assignment,) = var.domain
                else:
                    unassigned.append(var)
        # TODO these heuristic do not make a lot sense for plain backtracking - it would be better to implement Forward checking or Real Full Look Ahead
        # TODO apply static order heuristics here
        if heuristic is not None:
            heuristic(unassigned)
        return backtracking_step(unassigned)

    @staticmethod
    def forward_checking(problem, first_fail_heuristic=False):

        def backtracking_step(unassigned, first_fail_heuristic):
            if len(unassigned) == 0:
                return True
            if first_fail_heuristic:
                Solver.first_conflict(unassigned)
            variable = unassigned.pop()
            saved_state = [(var.name, var.domain.copy())for var in unassigned]
            for value in variable.domain: # TODO apply min conflict heuristic here
                value_consistent = True
                Solver.counter += 1
                for constraint in variable.constraints_to:
                    if constraint.a.assignment and not constraint.check_values(constraint.a.assignment, value):
                        value_consistent = False
                        break
                    elif not constraint.a.assignment:
                        try:
                            constraint.propagate_against_value(value)
                        except InconsistentProblem:
                            value_consistent = False
                            break
                if value_consistent:
                    variable.assignment = value
                    if backtracking_step(unassigned, first_fail_heuristic):
                        return True

                for (var_name, var_domain) in saved_state:
                    nonlocal  problem
                    problem[var_name].domain=var_domain.copy()
            unassigned.append(variable)
            variable.assignment = None
            return False

        Solver.counter = 0
        unassigned = []
        for var in problem:
            if len(var.domain) == 0:
                raise InconsistentProblem
            if not var.assignment:
                if len(var.domain) == 1:
                    (var.assignment,) = var.domain
                else:
                    unassigned.append(var)
        return backtracking_step(unassigned, first_fail_heuristic)


# USAGE
# create new sudoku from string
s = Sudoku("004300209005009001070060043006002087190007400050083000600000105003508690042910300")
# convert the sudoku to CSP
p = s.to_problem()
# use methods to solve
# if not Solver.AC_1(p):
#     Solver.backtracking(p) # now it is possible to use AC if sufficient
Solver.backtracking(p)
# update the sudoku with the solved problem
s.from_problem(p)
# u can check the state of variables of the problem
for var in p:
    print(var)
# print the sudoku
s.print(pretty=True)
# compare the result with groundtruth
print("Solution is correct? " +
      str(s.__repr__() == "864371259325849761971265843436192587198657432257483916689734125713528694542916378"))
