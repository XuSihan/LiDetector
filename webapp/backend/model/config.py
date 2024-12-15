config = {

    'attiLabel_type': {
        0: 'NOmentioned',
        1: 'can',
        2: 'cannot',
        3: 'must',
        4: 'conflict',
    },
    'attiType_label':{
        'NOmentioned': 0,
        'can': 1,
        'cannot': 2,
        'must': 3,
        'conflict': 4,
    },

    'atti_moreStrictTable': [
        [1, 2, 3, 4],
        [2, 2, 4, 4],
        [3, 4, 3, 4],
        [4, 4, 4, 4],
    ],


    'absentAtti' : [2,2,2,2,1, 1,2,2,2,1, 1,2,1,1,1, 2,1,2,1,1, 1,2,1], # 对权利/义务的划分

    'absent' : [2, 1],

    'instance_size' : 212, # 0-211

    'term_list' : ['Distribute', #0
                   'Modify', #1
                   'Commercial Use', #2
                   'Hold Liable', #3
                   'Include Copyright',#4
                   'Include License', #5
                   'Sublicense', #6
                   'Use Trademark', #7
                   'Private Use', #8
                   'Disclose Source', #9
                   'State Changes', #10
                   'Place Warranty', #11
                   'Include Notice', #12
                   'Include Original', #13
                   'Give Credit',#14
                   'Use Patent Claims', #15
                   'Rename', #16
                   'Relicense', #17
                   'Contact Author', #18
                   'Include Install Instructions', #19
                   'Compensate for Damages', #20
                   'Statically Link', #21
                   'Pay Above Use Threshold', #22
                   ''],
    'termList_size' : 24

}
