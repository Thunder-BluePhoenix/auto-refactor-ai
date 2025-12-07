"""
Test file focused on function length issues (Rule 1).
"""


def tiny_function():
    """Good: Very short function (3 lines)."""
    return 42


def medium_function():
    """Good: Medium-sized function (20 lines, under limit)."""
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
    g = 7
    h = 8
    i = 9
    j = 10
    k = 11
    l = 12
    m = 13
    n = 14
    o = 15
    return a + b + c + d + e + f + g + h + i + j + k + l + m + n + o


def exactly_thirty_lines():
    """Good: Exactly 30 lines (at the limit)."""
    line_1 = 1
    line_2 = 2
    line_3 = 3
    line_4 = 4
    line_5 = 5
    line_6 = 6
    line_7 = 7
    line_8 = 8
    line_9 = 9
    line_10 = 10
    line_11 = 11
    line_12 = 12
    line_13 = 13
    line_14 = 14
    line_15 = 15
    line_16 = 16
    line_17 = 17
    line_18 = 18
    line_19 = 19
    line_20 = 20
    line_21 = 21
    line_22 = 22
    line_23 = 23
    line_24 = 24
    line_25 = 25
    line_26 = 26
    line_27 = 27
    line_28 = 28
    return sum([line_1, line_2, line_3, line_4, line_5, line_6, line_7,
                line_8, line_9, line_10, line_11, line_12, line_13, line_14])


def thirty_five_lines():
    """INFO severity: 35 lines (1.17x over limit)."""
    line_1 = 1
    line_2 = 2
    line_3 = 3
    line_4 = 4
    line_5 = 5
    line_6 = 6
    line_7 = 7
    line_8 = 8
    line_9 = 9
    line_10 = 10
    line_11 = 11
    line_12 = 12
    line_13 = 13
    line_14 = 14
    line_15 = 15
    line_16 = 16
    line_17 = 17
    line_18 = 18
    line_19 = 19
    line_20 = 20
    line_21 = 21
    line_22 = 22
    line_23 = 23
    line_24 = 24
    line_25 = 25
    line_26 = 26
    line_27 = 27
    line_28 = 28
    line_29 = 29
    line_30 = 30
    line_31 = 31
    line_32 = 32
    line_33 = 33
    return sum([line_1, line_2, line_3])


def fifty_lines():
    """WARN severity: 50 lines (1.67x over limit)."""
    line_1 = 1
    line_2 = 2
    line_3 = 3
    line_4 = 4
    line_5 = 5
    line_6 = 6
    line_7 = 7
    line_8 = 8
    line_9 = 9
    line_10 = 10
    line_11 = 11
    line_12 = 12
    line_13 = 13
    line_14 = 14
    line_15 = 15
    line_16 = 16
    line_17 = 17
    line_18 = 18
    line_19 = 19
    line_20 = 20
    line_21 = 21
    line_22 = 22
    line_23 = 23
    line_24 = 24
    line_25 = 25
    line_26 = 26
    line_27 = 27
    line_28 = 28
    line_29 = 29
    line_30 = 30
    line_31 = 31
    line_32 = 32
    line_33 = 33
    line_34 = 34
    line_35 = 35
    line_36 = 36
    line_37 = 37
    line_38 = 38
    line_39 = 39
    line_40 = 40
    line_41 = 41
    line_42 = 42
    line_43 = 43
    line_44 = 44
    line_45 = 45
    line_46 = 46
    line_47 = 47
    line_48 = 48
    return sum([line_1, line_2])


def seventy_lines():
    """CRITICAL severity: 70 lines (2.33x over limit)."""
    line_1 = 1
    line_2 = 2
    line_3 = 3
    line_4 = 4
    line_5 = 5
    line_6 = 6
    line_7 = 7
    line_8 = 8
    line_9 = 9
    line_10 = 10
    line_11 = 11
    line_12 = 12
    line_13 = 13
    line_14 = 14
    line_15 = 15
    line_16 = 16
    line_17 = 17
    line_18 = 18
    line_19 = 19
    line_20 = 20
    line_21 = 21
    line_22 = 22
    line_23 = 23
    line_24 = 24
    line_25 = 25
    line_26 = 26
    line_27 = 27
    line_28 = 28
    line_29 = 29
    line_30 = 30
    line_31 = 31
    line_32 = 32
    line_33 = 33
    line_34 = 34
    line_35 = 35
    line_36 = 36
    line_37 = 37
    line_38 = 38
    line_39 = 39
    line_40 = 40
    line_41 = 41
    line_42 = 42
    line_43 = 43
    line_44 = 44
    line_45 = 45
    line_46 = 46
    line_47 = 47
    line_48 = 48
    line_49 = 49
    line_50 = 50
    line_51 = 51
    line_52 = 52
    line_53 = 53
    line_54 = 54
    line_55 = 55
    line_56 = 56
    line_57 = 57
    line_58 = 58
    line_59 = 59
    line_60 = 60
    line_61 = 61
    line_62 = 62
    line_63 = 63
    line_64 = 64
    line_65 = 65
    line_66 = 66
    line_67 = 67
    line_68 = 68
    return sum([line_1, line_2])
