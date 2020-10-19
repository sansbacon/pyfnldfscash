import random

import pytest
import pandas as pd
import numpy as np

from nfldfscash import Transformer
from pydfs_lineup_optimizer import Player


@pytest.fixture
def t():
    return Transformer()


@pytest.fixture
def blitz(test_directory):
    return pd.read_csv(test_directory / 'blitz.csv')


@pytest.fixture
def etr(test_directory):
    return pd.read_csv(test_directory / 'etr.csv')


@pytest.fixture
def ffa(test_directory):
    return pd.read_csv(test_directory / 'ffa.csv')


def test_player_fields(t):
    assert t.player_fields == {'player', 'pos', 'team', 'salary', 'proj'}


def test_fix_dst_name(t):
    """Tests _fix_dst_name"""
    assert t._fix_dst_name('Washington Football Team') == 'WFT Defense'
    assert t._fix_dst_name('New York Giants') == 'Giants Defense'
    assert t._fix_dst_name('San Diego Chargers') == 'Chargers Defense'
    assert t._fix_dst_name('Chargers') == 'Chargers Defense'


def test_first_name(t):
    """Tests _first_name"""
    assert t._first_name('Jared Goff') == 'Jared'
    assert t._first_name('Chargers') == 'Chargers'


def test_last_name(t):
    """Tests _last_name"""
    assert t._last_name('Jared Goff') == 'Goff'
    assert t._last_name('Chargers Defense') == 'Defense'
    assert t._last_name('Will Fuller V') == 'Fuller'
    assert t._last_name('Mohammed Sanu Sr.') == 'Sanu'
    assert t._last_name('Odell Beckham, Jr.') == 'Beckham'
    assert t._last_name('Juan del Potro') == 'del Potro'    


def test_remap_columns_blitz(t, blitz, tprint):
    """Tests _remap_columns with blitz"""
    df = blitz.rename(columns=t._remap_columns(blitz))
    assert t.player_fields <= set(df.columns)    
    

def test_remap_columns_etr(t, etr, tprint):
    """Tests _remap_columns with ETR"""
    df = etr.rename(columns=t._remap_columns(etr))
    assert t.player_fields <= set(df.columns)    


def test_remap_columns_ffa(t, ffa, tprint):
    """Tests _remap_columns with FFA"""
    df = ffa.rename(columns=t._remap_columns(ffa))
    assert t.player_fields <= set(df.columns)    


def test_row_to_player_blitz(t, blitz, tprint):
    """Tests _row_to_player"""
    df = blitz.rename(columns=t._remap_columns(blitz))
    df['fppg_ceil'] = 5
    row = next(df.sample(1).itertuples())
    p = t._row_to_player(row)
    assert p.fppg_ceil == 5


def test_row_to_player_etr(t, etr, tprint):
    """Tests _row_to_player"""
    df = etr.rename(columns=t._remap_columns(etr))
    df['fppg_ceil'] = 5
    row = next(df.sample(1).itertuples())
    p = t._row_to_player(row)
    assert p.fppg_ceil == 5


def test_row_to_player_ffa(t, ffa, tprint):
    """Tests _row_to_player"""
    df = ffa.rename(columns=t._remap_columns(ffa))
    df['salary'] = np.random.randint(30, 90, size=len(df)) * 100 
    df['fppg_ceil'] = 5
    row = next(df.sample(1).itertuples())
    p = t._row_to_player(row)
    assert p.fppg_ceil == 5


def test_make_players(t, etr, blitz):
    """Tests _make_players"""
    players = t.make_players(etr)
    assert isinstance(players, list)
    assert len(players) == len(etr)
    player = random.choice(players)
    assert isinstance(player, Player)
    
    # now test blitz
    players = t.make_players(blitz)
    assert isinstance(players, list)
    assert len(players) == len(blitz)
    player = random.choice(players)
    assert isinstance(player, Player)

    # test thresholds
    players = t.make_players(etr, thresholds=t.DEFAULT_THRESHOLDS)
    assert len(players) < len(etr)

