from cursesman.entities import Pass, Balloom, Oneil, Doll, Powerup, Minvo, Kondoria, Pontan
rooms = [
    ('2345', 20, 14, [], Powerup('powerup_flames',0,0)),
    ('DEBUG', 20, 14, 1*[Minvo(0,0)] + 1*[Kondoria(0,0)] + 1*[Pontan(0,0)], Powerup('powerup_flames',0,0)),
    ('2345', 20, 14, 6*[Balloom(0,0)], Powerup('powerup_flames',0,0)),
    ('1234', 20, 14, 3*[Oneil(0,0)] + 3*[Balloom(0,0)], Powerup('powerup_bombs', 0, 0)),
    ('1234', 20, 14, (2*[Oneil(0,0)] + 2*[Balloom(0,0)] + 2*[Doll(0,0)]), Powerup('powerup_bombs',0,0))

]
