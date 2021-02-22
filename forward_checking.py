import copy
import time
from multiprocessing import Process


class CSP:
    def __init__(self, variables, domains, size):
        self.variables = variables  # variables to be constrained
        self.domains = domains  # domain of each variable
        self.size = size  # domain of each variable
        self.constraints = {}
        self.count = 0
        self.nodes_visited = 0

    def check_neighbours(self, assignment, value):
        # Check if the value is directly neighbouring another variable
        for key in assignment:
            # value is cell number
            # check left cell
            if (value - 1) % self.size != 0:
                if assignment[key] == value - 1:
                    return False
            # check right cell
            if (value + 1) % self.size != 1:
                if assignment[key] == value + 1:
                    return False

            # check top cell, if top most cell don't check as it is out of bound
            if not (value - self.size <= 0):
                if assignment[key] == value - self.size:
                    return False
                # check top left cell if left most cell don't check top left don't check as it is out of bound
                if (value - self.size - 1) % self.size != 0:
                    if assignment[key] == value - self.size - 1:
                        return False
                # check top right cell, if right most don't check as it is out of bound
                if (value - self.size + 1) % self.size != 1:
                    if assignment[key] == value - self.size + 1:
                        return False

            # check bottom cell , if bottom row don't check as it is out of bound
            if (value + self.size) <= (self.size * self.size):
                if assignment[key] == value + self.size:
                    return False

                # check bottom left, if left most cell don't check as it is out of bound
                if (value + self.size - 1) % self.size != 0:
                    if assignment[key] == value + self.size - 1:
                        return False
                # check bottom right, right most cell don't check as it is out of bound
                if (value + self.size + 1) % self.size != 1:
                    if assignment[key] == value + self.size + 1:
                        return False

        return True

    def check_column(self, assignment, value):
        count = 0

        for key in assignment:
            if (assignment[key] % self.size) == (value % self.size):
                count += 1
            if count == 2:
                return False
        return True

    def check_row(self, assignment, value):
        count = 0
        for key in assignment:
            if ((assignment[key] - 1) // self.size) == ((value - 1) // self.size):
                count += 1
            if count == 2:
                return False
        return True

    # need to pass variable for block check
    def consistent(self, value, assignment):
        result = True
        # Check if any variable in the assignment has the same value
        for key in assignment:
            if assignment[key] == value:
                return False

        neighbours_valid = self.check_neighbours(assignment, value)

        if not neighbours_valid:
            return False

        column_valid = self.check_column(assignment, value)
        # check column
        if not column_valid:
            return False

        row_valid = self.check_row(assignment, value)
        # check column
        if not row_valid:
            return False

        return result

    def select_variable(self, assignment, heuristic):
        if heuristic == "most_constrained":
            return self.most_constrained(assignment)
        elif heuristic == "most_constraining":
            return self.most_constraining(assignment)
        elif heuristic == "hybrid":
            return self.hybrid(assignment)

    def reduce_domains(self, assignment):

        reduced_domains = copy.deepcopy(self.domains)

        # for every variable not in assigment. Take each assigned value and remove value from domain
        for var in self.variables:
            if var not in assignment:
                for key in assignment:
                    assigned_value = assignment[key]  # variable
                    if assigned_value in reduced_domains[var]:
                        reduced_domains[var].remove(assigned_value)
                    # checking if assigned values are not neighbours to domain
                    # check and remove right
                    if (assigned_value + 1) % self.size != 1 and assigned_value + 1 in reduced_domains[var]:
                        reduced_domains[var].remove(assigned_value + 1)
                    # check and remove left
                    if (assigned_value - 1) % self.size != 0 and assigned_value - 1 in reduced_domains[var]:
                        reduced_domains[var].remove(assigned_value - 1)
                    # check and remove down
                    if (assigned_value + self.size) <= self.size * self.size and assigned_value + self.size in \
                            reduced_domains[var]:
                        reduced_domains[var].remove(assigned_value + self.size)
                    # check and remove top
                    if (assigned_value - self.size) > 0 and (assigned_value - self.size) in reduced_domains[var]:
                        reduced_domains[var].remove(assigned_value - self.size)
                    # check and remove top left
                    if (assigned_value - self.size - 1) % self.size != 0 and (assigned_value - self.size - 1) in \
                            reduced_domains[var]:
                        reduced_domains[var].remove(assigned_value - self.size - 1)
                    # check and remove top right
                    if (assigned_value - self.size + 1) % self.size != 1 and (assigned_value - self.size + 1) in \
                            reduced_domains[var]:
                        reduced_domains[var].remove(assigned_value - self.size + 1)
                    # check and remove bottom left
                    if (assigned_value + self.size - 1) % self.size != 0 and (assigned_value + self.size - 1) in \
                            reduced_domains[var]:
                        reduced_domains[var].remove(assigned_value + self.size - 1)
                    # check and remove bottom right
                    if (assigned_value + self.size + 1) % self.size != 1 and (assigned_value + self.size + 1) in \
                            reduced_domains[var]:
                        reduced_domains[var].remove(assigned_value + self.size + 1)

        # remove rows
        for var in self.variables:
            if var not in assignment:
                for value in reduced_domains[var]:
                    count_row = 0
                    for key in assignment:
                        assigned_value = assignment[key]  # variable
                        if ((assigned_value - 1) // self.size) == ((value - 1) // self.size):
                            count_row += 1
                        if count_row == 2 and value in reduced_domains[var]:
                            reduced_domains[var].remove(value)
        # remove columns
        for var in self.variables:
            if var not in assignment:
                for value in reduced_domains[var]:
                    count_column = 0
                    for key in assignment:
                        assigned_value = assignment[key]  # variable
                        if (assigned_value % self.size) == (value % self.size):
                            count_column += 1
                        if count_column == 2 and value in reduced_domains[var]:
                            reduced_domains[var].remove(value)

        return reduced_domains

    def most_constrained(self, assignment):
        # count => checking the fewest possible options left.
        count = 2147483647
        most_constrained = -1

        reduced_domains = self.reduce_domains(assignment)

        for key in reduced_domains:
            if key not in assignment:
                if len(reduced_domains[key]) < count:
                    count = len(reduced_domains[key])
                    most_constrained = key

        local_assignment = assignment.copy()
        local_assignment[most_constrained] = self.domains[most_constrained][0]
        reduced_domains = self.reduce_domains(local_assignment)

        return most_constrained, reduced_domains

    def total_length(self, domains):
        result = 0
        for var in domains:
            result += len(domains[var])
        return result

    def get_neighbours(self, value):
        neighbours = [value]

        # right
        if (value + 1) % self.size != 1:
            neighbours.append(value + 1)

        # check and remove left
        if (value - 1) % self.size != 0:
            neighbours.append(value - 1)

        # check and remove down
        if (value + self.size) <= self.size * self.size:
            neighbours.append((value + self.size))

        # check and remove top
        if (value - self.size) > 0:
            neighbours.append((value - self.size))

        # check and remove top left
        if (value - self.size - 1) % self.size != 0:
            neighbours.append((value - self.size - 1))

        # check and remove top right
        if (value - self.size + 1) % self.size != 1:
            neighbours.append((value - self.size + 1))

        # check and remove bottom left
        if (value + self.size - 1) % self.size != 0:
            neighbours.append((value + self.size - 1))

        # check and remove bottom right
        if (value + self.size + 1) % self.size != 1:
            neighbours.append((value + self.size + 1))

        return neighbours

    def most_constraining(self, assignment):
        most_constraining = -1
        max_count = -1

        list_of_lengths = {}

        local_domains = self.reduce_domains(assignment)
        list_of_neighbours = {}
        for variable in self.variables:
            if variable not in assignment:
                local_var = variable
                if len(local_domains[local_var]) != 0:
                    first_val = local_domains[local_var][0]

                    list_of_neighbours[variable] = self.get_neighbours(first_val)

        count = 0
        for variable in list_of_neighbours:
            for value in list_of_neighbours[variable]:
                for var in self.variables:
                    if var not in assignment and var != variable:
                        if value in self.domains[var]:
                            count += 1

            list_of_lengths[variable] = count

        for key in list_of_lengths:
            if list_of_lengths[key] > max_count:
                most_constraining = key
                max_count = list_of_lengths[key]

        list_of_reduced_domains = {}
        local_assignment = assignment.copy()
        if most_constraining == -1:
            return most_constraining, list_of_reduced_domains
        else:
            local_assignment[most_constraining] = self.domains[most_constraining][0]
        list_of_reduced_domains = self.reduce_domains(local_assignment)

        return most_constraining, list_of_reduced_domains

    def most_constrained_hybrid(self, assignment, reduced_domains):
        hybrid = -1
        count = 2147483647
        for key in reduced_domains:
            if key not in assignment:
                if len(reduced_domains[key]) < count:
                    count = len(reduced_domains[key])
                    hybrid = key

        local_assignment = assignment.copy()
        list_of_reduced_domains = {}
        if hybrid == -1:
            return hybrid, list_of_reduced_domains
        else:
            local_assignment[hybrid] = self.domains[hybrid][0]

        list_of_reduced_domains = self.reduce_domains(local_assignment)

        return hybrid, list_of_reduced_domains

    def hybrid(self, assignment):
        hybrid_var = -1
        max_count = -1

        list_of_lengths = {}

        local_domains = self.reduce_domains(assignment)
        list_of_neighbours = {}
        for variable in self.variables:
            if variable not in assignment:
                local_var = variable
                if len(local_domains[local_var]) != 0:
                    first_val = local_domains[local_var][0]

                    list_of_neighbours[variable] = self.get_neighbours(first_val)

        count = 0
        for variable in list_of_neighbours:
            for value in list_of_neighbours[variable]:
                for var in self.variables:
                    if var not in assignment and var != variable:
                        if value in self.domains[var]:
                            count += 1

            list_of_lengths[variable] = count

        most_constrained_length = 2147483647
        for key in list_of_lengths:
            if list_of_lengths[key] > max_count and len(local_domains[key]) < most_constrained_length:
                hybrid_var = key
                max_count = list_of_lengths[key]
                most_constrained_length = len(local_domains[key])

        list_of_reduced_domains = {}
        local_assignment = assignment.copy()
        if hybrid_var == -1:
            return hybrid_var, list_of_reduced_domains
        else:
            local_assignment[hybrid_var] = self.domains[hybrid_var][0]
        list_of_reduced_domains = self.reduce_domains(local_assignment)

        return hybrid_var, list_of_reduced_domains


    def backtracking(self, assignment, heuristic):
        # print(assignment)
        # base case
        if len(assignment) == len(self.variables):
            return assignment
        else:
            # assignment is a dict
            # domain is a dict
            variable, reduced_domains = self.select_variable(assignment, heuristic)
            # d[v] //edit so FC
            if variable == -1:
                return None

            for value in reduced_domains[variable]:
                self.nodes_visited += 1
                if self.consistent(value, assignment):
                    assignment[variable] = value

                    result = self.backtracking(assignment, heuristic)

                    if result is not None:
                        return assignment  # final assignmnet.

                    assignment.pop(variable)
            return None

    # print_output(assignment)
    # print the output of the solution
    #
    # assignment - dictionary containing the final solution to a puzzle
    # returns a string with the appropriate output
    def print_output(self, assignment):
        output = ""
        # check for no solution
        if assignment is None:
            output = "No solution"
        else:
            for num in range(1, self.size * self.size + 1):
                if (num % self.size) == 1:
                    output += "\n|"
                if num in assignment.values():
                    output += "X|"
                else:
                    output += ".|"
        print("Number of Nodes:", self.nodes_visited)
        print(output)


# Returns a list of variables, and domains.
def read_file():
    file = open("input")
    lines = file.readlines()
    # List of variables.
    variables = [x + 1 for x in range(len(lines) * 2)]
    # Dictionary of domains
    domains = {}
    # Keeping track of Variables
    count = 0
    for line in lines:
        str_values = line.split("\\t")[1].rstrip().split(",")
        domain = []
        for value in str_values:
            domain.append(int(value))
        domains[variables[count]] = domain
        domains[variables[count + 1]] = domain
        count += 2
        # CHECK EDGE CASES
    size = int(count / 2)
    return variables, domains, size


def solve_csp():
    variables, domains, size = read_file()
    csp = CSP(variables, domains, size)
    resyi = csp.backtracking({}, "most_constraining")
    csp.print_output(resyi)


if __name__ == '__main__':
    solve = Process(target=solve_csp)
    # Start the process
    solve.start()
    start_time = time.time()
    # time out after 10 min (600 seconds)
    solve.join(timeout=60000)
    # terminate the process.
    print("--- %s seconds ---" % (time.time() - start_time))
    solve.terminate()
