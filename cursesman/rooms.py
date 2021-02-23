from cursesman.entities import Balloom, Oneil
rooms = [
    ('2345', 20, 14, 1*[Balloom(0,0)]),
    ('2345', 20, 14, 1*[Oneil(0,0)] + 5*[Balloom(0,0)]),
    ('1234', 20, 14, 3*[Oneil(0,0)] + 3*[Balloom(0,0)])
]
