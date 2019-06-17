from observation import Observation

sc_flags = {'CI': 38432,
            'CX': 2367,
            'DM': 4219,
            'ER': 1240,
            'HC': 2113,
            'HO': 22,
            'LW': 25108,
            'NR': 482,
            'OM': 468,
            'OO': 342,
            'OT': 2200,
            'OX': 178,
            'total': 441707}
lc_flags = {'DM': 3, 'ER': 4, 'LW': 123, 'total': 3510}
th_flags = {'DM': 216, 'ER': 1, 'LW': 94, 'total': 4308}
mm_flags = {'DM': 6, 'ER': 30, 'LW': 450, 'MR': 48, 'total': 12431}

for group in [lc_flags, mm_flags]:
    for k, v in group.items():
        print("{}  {}  {:.2%}".format(k, v, v / group["total"]))
