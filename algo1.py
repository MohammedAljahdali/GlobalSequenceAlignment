def update(grid, i, j, gap, match, mismatch):
    left = grid[i, j - 1] + gap
    up = grid[i - 1, j] + gap
    ismatch = seq1[i-1] == seq2[j-1]
    dig = grid[i - 1, j - 1] + match if ismatch else grid[i - 1, j - 1] + mismatch
    grid[i, j] = max(left, up, dig)

def init(grid, i, j, gaph):
    if i == 0 and j == 0:
        grid[i, j] = 0
    elif i == 0:
        grid[i, j] = grid[i, j-1] + gap
    elif j == 0:
        grid[i, j] = grid[i-1, j] + gap
    else:
        raise("error")
    
def algo1(seq1, seq2, gap=-2, match=1, mismatch=-1, debug=False):
    grid = np.zeros(
        (len(seq1)+1, len(seq2)+1)
    )
    if debug:
        print(grid)
        print(grid.shape)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if i == 0 or j == 0:
                init(grid, i, j, gap)
            else:
                update(grid, i, j,  gap, match, mismatch)
    if debug:
        print(grid)
        print(i, j)
    result1 = ""
    result2 = ""
    while i > 0 and j > 0:
        ismatch = seq1[i-1] == seq2[j-1]
        if ismatch:
            i -= 1
            j -= 1
            result1 += seq1[i]
            result2 += seq2[j]
            if debug:
                print(result1[::-1])
                print(result2[::-1])
        else:
            left = grid[i, j - 1]
            up = grid[i - 1, j]
            dig = grid[i - 1, j - 1]
            values = [left, up, dig]
            max_value = max(values)
            for idx, value in enumerate(values):
                if value == max_value:
                    if idx == 0:
                        j -= 1
                        result1 += "-"
                        result2 += seq2[j]
                        if debug:
                            print(result1[::-1])
                            print(result2[::-1])
                    elif idx ==1:
                        i -= 1
                        result1 += seq1[i]
                        result2 += "-"
                        if debug:
                            print(result1[::-1])
                            print(result2[::-1])
                    else:
                        i -= 1
                        j -= 1
                        result1 += seq1[i]
                        result2 += seq2[j]
                        if debug:
                            print(result1[::-1])
                            print(result2[::-1])
    if i == 1:
        i -= 1
        result1 += seq1[i]
        result2 += "-"
    elif j == 1:
        j -= 1
        result1 += "-"
        result2 += seq2[j]
    if debug:
        print(i, j, grid[i,j])
        print(result1[::-1])
        print(result2[::-1])
    return result1[::-1], result2[::-1]

# TODO: define a main with argparser to execute function 1
# TODO: create a function to read data and execture the algorithm on them, and add option in the main to use it instated of a single input