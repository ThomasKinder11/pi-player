"""
This variable is defining the actions when a particualr button is pressed.
Each seleactable element in the GUI has a uniqe ID which is assigned to it
when a Kivy selectable object is created. All the selectable Elements can be
found in isha_kivy.py

Each of the tree elemts contains of multiple child object which are
lists of dicts. These dicts have the follwing keys:

'func' --> this is a method of the selectable gui object which should be executed
'id' --> defines the id of the gui element which shall be used

The last element of the dict list must always be {'nextid':ID} which defines
the id of the next element which shall be selected. FUnctions are executed
in the list from left to right.

Example:

0:{
    "left": [{'func':'enable', 'id':1},{'nextid':1}],
}

In the above example the behaviour of the gui element with id 0 is defined.
If we selected element with ID=0 and we press the 'left' key the method "enable"
of the object with the ID=1 is executed. Then the nextid is set to one,
meaning that this object will gain keyboard control
"""

selectId = {
    'settings':1,
    'settingsMenu':100,

    'videos':2,
    'vFile':20000,

    'music':3,
    'mFiles':30000,

    'playlist':4,
    'pFiles':40000,

    'system':0,
    'systemBtn':50001,
    'systemMsg':50000,

    'osd':200,

}




CONTROL_TREE = {
    selectId['settings']:{
        "left": [
            {'func':'switch', 'id':selectId['playlist']},
            {'nextid':selectId['playlist']}
        ],
        "down":[
            {'func':'enable', 'id':selectId['settingsMenu']},
            {'func':'disable', 'id':selectId['settings']},
            {'nextid':selectId['settingsMenu']}
        ],
    },
    selectId['videos']:{
        "left":  [
            {'func':'switch', 'id':selectId['system']},
            {'nextid':selectId['system']}
        ],
        "right": [
            {'func':'switch', 'id':selectId['music']},
            {'nextid':selectId['music']}
        ],
        "up": [
            {'func':'disable', 'id':selectId['vFile']},
            {'nextid':selectId['videos']}
        ],
        "down": [
            {'func':'enable', 'id':selectId['vFile']},
            {'func':'disable', 'id':selectId['videos']},
            {'nextid':selectId['vFile']}
        ],
        "info":"video menu",
    },
    selectId['music']:{
        "left":  [
            {'func':'switch', 'id':selectId['videos']},
            {'nextid':selectId['videos']}
        ],
        "right": [
            {'func':'switch', 'id':selectId['playlist']},
            {'nextid':selectId['playlist']}
        ],
        "down": [
            {'func':'enable', 'id':selectId['mFiles']},
            {'func':'disable', 'id':selectId['music']},
            {'nextid':selectId['mFiles']}
        ],
        "note":"audio menu",
    },
    selectId['playlist']:{
        "left":  [
            {'func':'switch', 'id':selectId['music']},
            {'nextid':selectId['music']}
        ],
        "right": [
            {'func':'switch', 'id':selectId['settings']},
            {'nextid':selectId['settings']}
        ],
        "down": [
             {'func':'disable', 'id':selectId['playlist']},
             {
                 'func':'enable',
                 'id':selectId['pFiles'],
                 'true':[
                     {'func':'disable', 'id':selectId['pFiles']},
                     {'func':'enable', 'id':selectId['playlist']},
                     {'nextid':selectId['playlist']}
                 ]
             },
             {'nextid':selectId['pFiles']},
        ],
        "note":"pFiles",
    },
    selectId['system']:{
        "right": [
            {'func':'switch', 'id':selectId['videos']},
            {'nextid':selectId['videos']}
        ],
        "down":[
            {'func':'disable', 'id':selectId['system']},
            {'func':'enable', 'id':selectId['systemBtn']},
            {'nextid':selectId['systemBtn']}
        ],
        "note":"power control",
    },
    selectId['settingsMenu']:{
        "up": [
            {
                'func':'disable',
                'id':selectId['settingsMenu'],
                'true':[
                    {'func':'enable', 'id':selectId['settings']},
                    {'nextid':selectId['settings']},
                ],
            },
        ],
        "down":[
            {'func':'enable', 'id':selectId['settingsMenu']},
        ],
        "left":[
            {'func':'left', 'id':selectId['settingsMenu']},
        ],
        "right":[
            {'func':'right', 'id':selectId['settingsMenu']},
        ],
        "enter":[
            {'func':'enter', 'id':selectId['settingsMenu']},
        ],
    },
    selectId['osd']:{
        "left": [{'func':'left', 'id':selectId['osd']}],
        "right":[{'func':'right', 'id':selectId['osd']}],
        "+":[{'func':'enable', 'id':selectId['osd']}],
        "-":[{'func':'enable', 'id':selectId['osd']}],
        "m":[{'func':'enable', 'id':selectId['osd']}],
        "enter":[{'func':'enter', 'id':selectId['osd']}],
        "esc":[{'func':'disable', 'id':selectId['osd']}],
        "browser back":[{'func':'disable', 'id':selectId['osd']}],
        "up":[{'func':'up', 'id':selectId['osd']}],
        "down":[{'func':'down', 'id':selectId['osd']}],
    },
    selectId['vFile']:{
        "up":[{
            'func':'disable',
            'id':selectId['vFile'],
            'true':[
                {'func':'enable', 'id':selectId['videos']},
                {'nextid':selectId['videos']}]
            }],
        "down":[{'func':'enable', 'id':selectId['vFile']}],
        "enter":[{'func':'enter', 'id':selectId['vFile']}],
        },
    selectId['mFiles']:{
        "up":[
            {
                'func':'disable',
                'id':selectId['mFiles'],
                'true':[
                    {'func':'enable', 'id':selectId['music']},
                    {'nextid':selectId['music']}
                ]
            }
        ],
        "down":[{'func':'enable', 'id':selectId['mFiles']}],
        "enter":[
            {'func':'enter', 'id':selectId['mFiles']},
            {'nextid':selectId['mFiles']}
        ],
    },
    selectId['pFiles']:{
        "left":  [
            {'func':'left', 'id':selectId['pFiles']},
        ],
        "down": [
            {'func':'enable', 'id':selectId['pFiles']},
            {'nextid':selectId['pFiles']}
        ],
        "up":[{
            'func':'disable',
            'id':selectId['pFiles'],
            'true':[
                {'func':'enable', 'id':selectId['playlist']},
                {'nextid':selectId['playlist']}
            ]
        }],
        "right": [
            {'func':'right', 'id':selectId['pFiles']},
            {'nextid':selectId['pFiles']}
        ],
        "enter": [
            {'func':'enter', 'id':selectId['pFiles']}
        ],
        "type":"pFiless",
        },
    selectId['systemMsg']:{
        "down":[
            {
                'func':'enable',
                'id':selectId['systemMsg'],
                'true':[
                    {'func':'enable', 'id':selectId['system']},
                    {'nextid':selectId['system']}
                ]
            }

        ],
        "up":[
            {
                'func':'disable',
                'id':selectId['systemMsg'],
                'true':[
                    {'func':'enable', 'id':selectId['systemBtn']},
                    {'nextid':selectId['systemBtn']}
                ]
            }

        ],
        "enter":[
            {
                'func':'enter',
                'id':selectId['systemMsg'],
                'true':[
                    {'func':'enable', 'id':selectId['systemBtn']},
                    {'nextid':selectId['systemBtn']}
                ]
            }
        ],
        "left":[{'func':'left', 'id':selectId['systemMsg']}],
        "right":[{'func':'right', 'id':selectId['systemMsg']}],
    },
    selectId['systemBtn']:{
        "down":[
            {'func':'disable', 'id':selectId['systemBtn']},
            {
                'func':'enable',
                'id':selectId['systemMsg'],
                'true':[
                    {'func':'enable', 'id':selectId['systemBtn']},
                    {'nextid':selectId['systemBtn']}
                ],
                'false':[
                    {'nextid':selectId['systemMsg']}
                ]
            }
        ],
        "left":[{'func':'left', 'id':selectId['systemBtn']}],
        "right":[{'func':'right', 'id':selectId['systemBtn']}],
        "up":[
            {'func':'disable', 'id':selectId['systemBtn']},
            {'func':'enable', 'id':selectId['system']},
            {'nextid':selectId['system']}
        ],
        "enter":[{'func':'enter', 'id':selectId['systemBtn']}]
    },
}
