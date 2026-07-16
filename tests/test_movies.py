"""
Unit tests สำหรับโมดูล Movie & Showtime (M2)
รันด้วยคำสั่ง: pytest tests/test_movies.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from movies import Movie, Theater, Showtime, ShowtimeCatalog


class TestMovie:
    def test_create_movie_success(self):
        movie = Movie("Avengers: New Dawn", "Action", 140, "PG-13")
        assert movie.title == "Avengers: New Dawn"

    def test_invalid_duration_raises_error(self):
        with pytest.raises(ValueError):
            Movie("Bad Movie", "Drama", 0)

    def test_invalid_rating_raises_error(self):
        with pytest.raises(ValueError):
            Movie("Bad Movie", "Drama", 100, rating="XXX")

    def test_matches_search_by_title(self):
        movie = Movie("Avengers: New Dawn", "Action", 140)
        assert movie.matches_search("avengers") is True

    def test_matches_search_by_genre(self):
        movie = Movie("Avengers: New Dawn", "Action", 140)
        assert movie.matches_search("action") is True

    def test_matches_search_no_match(self):
        movie = Movie("Avengers: New Dawn", "Action", 140)
        assert movie.matches_search("comedy") is False


class TestTheater:
    def test_capacity_calculation(self):
        theater = Theater("Theater 1", rows=7, seats_per_row=10)
        assert theater.capacity == 70

    def test_invalid_rows_raises_error(self):
        with pytest.raises(ValueError):
            Theater("Bad Theater", rows=0, seats_per_row=10)


class TestShowtime:
    def _make_showtime(self, rows=2, seats_per_row=5, price=180):
        movie = Movie("Test Movie", "Drama", 100)
        theater = Theater("Theater 1", rows=rows, seats_per_row=seats_per_row)
        return Showtime(movie, theater, "2026-08-01", "18:30", price)

    def test_available_seats_count_initial(self):
        showtime = self._make_showtime()
        assert showtime.available_seats_count == 10

    def test_reserve_seats_reduces_availability(self):
        showtime = self._make_showtime()
        showtime.reserve_seats(3)
        assert showtime.available_seats_count == 7
        assert showtime.booked_seat_count == 3

    def test_reserve_more_than_available_raises_error(self):
        showtime = self._make_showtime()
        with pytest.raises(ValueError):
            showtime.reserve_seats(100)

    def test_release_seats(self):
        showtime = self._make_showtime()
        showtime.reserve_seats(5)
        showtime.release_seats(2)
        assert showtime.booked_seat_count == 3

    def test_is_available_true_when_seats_left(self):
        showtime = self._make_showtime()
        assert showtime.is_available() is True

    def test_is_available_false_when_full(self):
        showtime = self._make_showtime()
        showtime.reserve_seats(10)
        assert showtime.is_available() is False

    def test_invalid_price_raises_error(self):
        movie = Movie("Test Movie", "Drama", 100)
        theater = Theater("Theater 1")
        with pytest.raises(ValueError):
            Showtime(movie, theater, "2026-08-01", "18:30", -10)


class TestShowtimeCatalog:
    def test_add_and_search_movie(self):
        catalog = ShowtimeCatalog()
        movie = Movie("Avengers: New Dawn", "Action", 140)
        catalog.add_movie(movie)
        results = catalog.search_movies("avengers")
        assert len(results) == 1

    def test_get_available_showtimes_excludes_full(self):
        catalog = ShowtimeCatalog()
        movie = Movie("Test Movie", "Drama", 100)
        theater = Theater("Theater 1", rows=1, seats_per_row=1)
        showtime_full = Showtime(movie, theater, "2026-08-01", "18:30", 180)
        showtime_full.reserve_seats(1)
        showtime_open = Showtime(movie, Theater("Theater 2", rows=2, seats_per_row=2),
                                  "2026-08-01", "20:00", 180)

        catalog.add_showtime(showtime_full)
        catalog.add_showtime(showtime_open)

        available = catalog.get_available_showtimes()
        assert showtime_full not in available
        assert showtime_open in available
