def edit_distance(s1: str, s2: str, n: int, m: int, dp: list[list[int]]) -> int:
    if n == 0:
        return m
    if m == 0:
        return n

    if dp[n][m] != -1:
        return dp[n][m]

    if s1[n - 1] == s2[m - 1]:
        dp[n][m] = edit_distance(s1, s2, n - 1, m - 1, dp)
        return dp[n][m]

    delete_cost = dp[n - 1][m] if dp[n - 1][m] != -1 else edit_distance(s1, s2, n - 1, m, dp)
    insert_cost = dp[n][m - 1] if dp[n][m - 1] != -1 else edit_distance(s1, s2, n, m - 1, dp)
    replace_cost = dp[n - 1][m - 1] if dp[n - 1][m - 1] != -1 else edit_distance(s1, s2, n - 1, m - 1, dp)

    dp[n][m] = 1 + min(delete_cost, insert_cost, replace_cost)
    return dp[n][m]


def levenshtein_ratio(str1: str, str2: str) -> float:
    n = len(str1)
    m = len(str2)
    dp = [[-1 for _ in range(m + 1)] for _ in range(n + 1)]

    lev = edit_distance(str1, str2, n, m, dp)
    return ((n + m) - lev) / (n + m)