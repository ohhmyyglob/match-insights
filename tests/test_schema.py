import pytest
from engine.schema import MatchEvent
from engine.coords import from_statsbomb

def make_event(**changes):
    """A valid event; pass only the fields you want to change."""
    base = dict(t=0, period=1, team="home", player="A", kind="pass", x=50, y=50)
    base.update(changes)
    return MatchEvent(**base)

def test_centre_spot_maps_to_middle():
    assert from_statsbomb(60, 40) == (50.0, 50.0)


def test_top_left_becomes_top_left():
    assert from_statsbomb(0, 0) == (0.0, 100.0)     # top of pitch = high y


def test_off_pitch_event_is_rejected():
    with pytest.raises(ValueError):
        MatchEvent(t=0, period=1, team="home", player="A", kind="pass", x=120, y=50)

def test_pressure_out_of_range_is_rejected():
    with pytest.raises(ValueError):
        MatchEvent(t=0, period=1, team="home", player="A", kind="pass",
                   x=50, y=50, pressure=7)

def test_pressure_edges_are_allowed():
    assert make_event(pressure=1).pressure == 1
    assert make_event(pressure=5).pressure == 5


def test_ball_on_the_touchline_is_allowed():
    make_event(x=100, y=0)        # no error = pass

def test_bottom_right_corner():
    assert from_statsbomb(120, 80) == (100.0, 0.0)


def test_negative_position_is_rejected():
    with pytest.raises(ValueError):
        make_event(y=-1)

@pytest.mark.parametrize("bad", [0, -1, 6, 99])
def test_bad_pressures_are_rejected(bad):
    with pytest.raises(ValueError):
        make_event(pressure=bad)

def test_to_dict_has_every_field():
    d = make_event(xg=0.3).to_dict()
    assert d["xg"] == 0.3
    assert {"t", "team", "player", "kind", "x", "y", "pressure"} <= d.keys()

def test_unknown_kind_is_rejected():
    with pytest.raises(ValueError):
        make_event(kind="shoot")      # typo

@pytest.mark.parametrize("bad", [0, 6, -2, 9])
def test_difficulty_out_of_range_is_rejected(bad):
    with pytest.raises(ValueError):
        make_event(difficulty=bad)


@pytest.mark.parametrize("ok", [None, 1, 3, 5])
def test_valid_difficulties_are_allowed(ok):
    assert make_event(difficulty=ok).difficulty == ok

