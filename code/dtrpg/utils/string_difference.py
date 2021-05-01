def difference_with_wildcards(str1: str, str2: str) -> int:
    WILDCARD = '*'
    # assuming only * wildcard for 1:n matching
    dynamic_array = [[None for _ in range(len(str1) + 1)] for _ in range(len(str2) + 1)]

    for i in range(len(str1) + 1):
        dynamic_array[0][i] = i

    for i in range(1, len(str2) + 1):
        dynamic_array[i][0] = i

    for i, e2 in enumerate(str2):
        for j, e1 in enumerate(str1):
            replacement_cost = int(e1 != WILDCARD and e2 != WILDCARD and e1 != e2)
            add1_cost = int(e1 != WILDCARD)
            add2_cost = int(e2 != WILDCARD)

            dynamic_array[i + 1][j + 1] = min(
                dynamic_array[i][j] + replacement_cost,
                dynamic_array[i][j + 1] + add1_cost,
                dynamic_array[i + 1][j] + add2_cost,
            )

    return dynamic_array[-1][-1]


def similarity_with_wildcards(str1: str, str2: str) -> float:
    diff = difference_with_wildcards(str1, str2)
    return 1 - 2 * diff / (len(str1) + len(str2))
