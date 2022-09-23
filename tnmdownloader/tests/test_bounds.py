import tnmdownloader
import itertools


def test_good_bounds():
    good_lats = (36, 37, 38, 39, 40, 41)
    good_lons = (-102, -103, -104, -105, -106, -107, -108, -109)

    for lat, lon in itertools.product(good_lats, good_lons):
        assert tnmdownloader.downloader.within_bounding_box(
            lat, lon
        ), f"{lat}, {lon} incorrectly categorized as out of bounds"


def test_bad_bounds():
    bad_lats = (33, 34, 35, 42, 43, 44)
    bad_lons = (-99, -100, -101, -110, -111, -112)

    for lat, lon in itertools.product(bad_lats, bad_lons):
        assert not tnmdownloader.downloader.within_bounding_box(
            lat, lon
        ), f"{lat}, {lon} incorrectly categorized as in bounds"
