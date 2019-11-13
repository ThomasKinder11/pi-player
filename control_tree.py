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

CONTROL_TREE = {
    0:{
        "left": [
            {'func':'switch', 'id':3},
            {'nextid':3}
        ],
        "up": None,
        "down":[
            {'func':'enable', 'id':100},
            {'func':'disable', 'id':0},
            {'nextid':100}
        ],
        "info":"settings menu"
    },
    1:{
        "left":  [
            {'func':'switch', 'id':4},
            {'nextid':4}
        ],
        "right": [
            {'func':'switch', 'id':2},
            {'nextid':2}
        ],
        "up": [
            {'func':'disable', 'id':20000},
            {'nextid':1}
        ],
        "down": [
            {'func':'enable', 'id':20000},
            {'func':'disable', 'id':1},
            {'nextid':20000}
        ],
        "info":"video menu",
    },
    2:{
        "left":  [
            {'func':'switch', 'id':1},
            {'nextid':1}
        ],
        "right": [
            {'func':'switch', 'id':3},
            {'nextid':3}
        ],
        "down": [
            {'func':'enable', 'id':30000},
            {'func':'disable', 'id':2},
            {'nextid':30000}
        ],
        "note":"audio menu",
    },
    3:{
        "left":  [
            {'func':'switch', 'id':2},
            {'nextid':2}
        ],
        "right": [
            {'func':'switch', 'id':0},
            {'nextid':0}
        ],
        "down": [
             {'func':'disable', 'id':3},
             {
                 'func':'enable',
                 'id':40000,
                 'true':[
                     {'func':'disable', 'id':40000},
                     {'func':'enable', 'id':3},
                     {'nextid':3}
                 ]
             },
        ],
        "note":"playlist",
    },
    4:{
        "right": [
            {'func':'switch', 'id':1},
            {'nextid':1}
        ],
        "down":[
            {'func':'disable', 'id':4},
            {'func':'enable', 'id':50001},
            {'nextid':50001}
        ],
        "note":"power control",
    },
    100:{
        "left":[{'func':'decrement', 'id':100}],
        "right":[{'func':'increment', 'id':100}],
        "up":[
            {'func':'disable', 'id':100},
            {'func':'enable', 'id':0},
            {'nextid':0}
        ],
        "down":[
            {'func':'enable', 'id':101},
            {'func':'disable', 'id':100},
            {'nextid':101}
        ]
    },
    101:{
        "left":[{'func':'decrement', 'id':101}],
        "right":[{'func':'increment', 'id':101}],
        "up": [
            {'func':'enable', 'id':100},
            {'func':'disable', 'id':101},
            {'nextid':100}
        ],
        "down":[
            {'func':'enable', 'id':102},
            {'func':'disable', 'id':101},
            {'nextid':102}
        ],
    },
    102:{
        "left":None,
        "right":None,
        "up": [
            {'func':'enable', 'id':101},
            {'func':'disable', 'id':102},
            {'nextid':101}
        ],
        "down": [
            {'func':'enable', 'id':103},
            {'func':'disable', 'id':102},
            {'nextid':103}
        ],
        "enter": [
            {'func':'on_press', 'id':102},
            {'nextid':102}
        ],
    },
    103:{
        "up": [
            {'func':'enable', 'id':102},
            {'func':'disable', 'id':103},
            {'nextid':102}
        ],
        "enter": [
            {'func':'on_press', 'id':103},
            {'nextid':103}
        ],
    },
    200:{
        "left": [{'func':'left', 'id':200}],
        "right":[{'func':'right', 'id':200}],
        "enter":[{'func':'enter', 'id':200}],
        "browser back": [{'func':'disable', 'id':200}],
        "volume up": [{'func':'volumeUp', 'id':200}],
        "volume down": [{'func':'volumeDown', 'id':200}],
        "volume mute": [{'func':'muteToggle', 'id':200}],
    },
    20000:{
        "up":[{
            'func':'disable',
            'id':20000,
            'true':[
                {'func':'enable', 'id':1},
                {'nextid':1}]
            }],
        "down":[{'func':'enable', 'id':20000}],
        "enter":[{'func':'enter', 'id':20000}],
        },
    30000:{
        "up":[
            {
                'func':'disable',
                'id':30000,
                'true':[
                    {'func':'enable', 'id':2},
                    {'nextid':2}
                ]
            }
        ],
        "down":[{'func':'enable', 'id':30000}],
        "enter":[
            {'func':'enter', 'id':30000},
            {'nextid':30000}
        ],
    },
    40000:{
        "left":  [
            {'func':'left', 'id':40000},
        ],
        "down": [
            {'func':'enable', 'id':40000},
            {'nextid':40000}
        ],
        "up":[{
            'func':'disable',
            'id':40000,
            'true':[
                {'func':'enable', 'id':3},
                {'nextid':3}
            ]
        }],
        "right": [
            {'func':'right', 'id':40000},
            {'nextid':40000}
        ],
        "enter": [
            {'func':'enter', 'id':40000}
        ],
        "type":"playlists",
        },
    50000:{
        "down":[
            {
                'func':'enable',
                'id':50000,
                'true':[
                    {'func':'enable', 'id':4},
                    {'nextid':4}
                ]
            }

        ],
        "up":[
            {
                'func':'disable',
                'id':50000,
                'true':[
                    {'func':'enable', 'id':50001},
                    {'nextid':50001}
                ]
            }

        ],
        "enter":[
            {
                'func':'enter',
                'id':50000,
                'true':[
                    {'func':'enable', 'id':50001},
                    {'nextid':50001}
                ]
            }
        ],
        "left":[{'func':'left', 'id':50000}],
        "right":[{'func':'right', 'id':50000}],
    },
    50001:{
        "down":[
            {'func':'disable', 'id':50001},
            {
                'func':'enable',
                'id':50000,
                'true':[
                    {'func':'enable', 'id':50001},
                    {'nextid':50001}
                ],
                'false':[
                    {'nextid':50000}
                ]
            }
        ],
        "left":[{'func':'left', 'id':50001}],
        "right":[{'func':'right', 'id':50001}],
        "up":[
            {'func':'disable', 'id':50001},
            {'func':'enable', 'id':4},
            {'nextid':4}
        ],
        "enter":[{'func':'enter', 'id':50001}]
    },
}
