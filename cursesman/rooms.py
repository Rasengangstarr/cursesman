from cursesman.entities import Pass, Balloom, Oneil, Doll, Powerup, Minvo, Kondoria, Pontan
rooms = [
    ('1', 20, 14, 1*[Balloom(0,0)], Powerup('powerup_flames',0,0)),
    ('2', 20, 14, 3*[Balloom(0,0)] + 3*[Oneil(0,0)] + 1*[Pontan(0,0)], Powerup('powerup_bombs',0,0)),
    ('3', 20, 14, 2*[Balloom(0,0)] + 2*[Oneil(0,0)] + 2*[Doll(0,0)], Powerup('powerup_detonator',0,0)),
    ('4', 20, 14, 1*[Balloom(0,0)] + 1*[Oneil(0,0)] + 2*[Doll(0,0)] + 2*[Minvo(0,0)], Powerup('powerup_speed', 0, 0)),
    ('5', 20, 14, 4*[Oneil(0,0)] + 3*[Doll(0,0)], Powerup('powerup_bombs',0,0))]

