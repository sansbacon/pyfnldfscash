import random

import pytest
import pandas as pd
import numpy as np

from nfldfscash import Transformer, generate_lineups, lineups_to_df, lineup_summary
from pydfs_lineup_optimizer import *


@pytest.fixture
def n():
    return 5


@pytest.fixture
def o():
    return get_optimizer(Site.DRAFTKINGS, Sport.FOOTBALL) 
    

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


def test_generate_lineups(o, n, t, etr, blitz):
    """Tests generate lineups"""
    for df in (etr, blitz):
        players = t.make_players(df)
        o.load_players(players)
        lineups = generate_lineups(o, n)
        assert len(lineups) == n
        lineup = random.choice(lineups)
        assert isinstance(lineup, Lineup)


def test_lineups_to_df(o, n, t, etr, blitz):
    """Tests lineups to df"""
    for df in (etr, blitz):
        players = t.make_players(df)
        o.load_players(players)
        lineups = generate_lineups(o, n)
        ldf = lineups_to_df(lineups)
        assert len(ldf) == len(lineups) * 9
        fields = {'id', 'team', 'salary', 'proj'}
        assert fields <= set(ldf.columns)


def test_lineup_summary(o, n, t, etr, blitz):
    """Tests lineup summary"""
    for df in (etr, blitz):
        players = t.make_players(df)
        o.load_players(players)
        lineups = generate_lineups(o, n)
        ldf = lineups_to_df(lineups)
        summ = lineup_summary(ldf, iterations=n)
        fields = {'id', 'position', 'team'}
        assert fields <= set(summ.columns)
