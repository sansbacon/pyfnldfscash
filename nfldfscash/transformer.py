# transformer.py
# converts projections to Player objects

import logging
import pandas as pd
import numpy as np
from pydfs_lineup_optimizer import Player


class Transformer:
    """Converts various projection files / dataframes to Player objects"""

    DEFAULT_THRESHOLDS = {'QB': 15, 'RB': 8, 'WR': 8, 'TE': 6, 'DST': 5}

    DEFENSE_NAMES = (
        'Las Vegas Raiders',
        'Seattle Seahawks',
        'New Orleans Saints',
        'Los Angeles Chargers',
        'Baltimore Ravens',
        'Indianapolis Colts',
        'Miami Dolphins',
        'New England Patriots',
        'New York Giants',
        'Pittsburgh Steelers',
        'Carolina Panthers',
        'Los Angeles Rams',
        'Chicago Bears',
        'Tennessee Titans',
        'Minnesota Vikings',
        'Washington Football Team',
        'Green Bay Packers',
        'Dallas Cowboys',
        'Kansas City Chiefs',
        'Detroit Lions',
        'Cleveland Browns',
        'Arizona Cardinals',
        'Cincinnati Bengals',
        'Tampa Bay Buccaneers',
        'Jacksonville Jaguars',
        'Denver Broncos',
        'Houston Texans',
        'San Francisco 49ers',
        'Philadelphia Eagles',
        'New York Jets',
        'Buffalo Bills',
        'Atlanta Falcons'
    )

    PLAYER_FIELDS_MAPPING = {
        'player': ['Player', 'PLAYER', 'plyr', 'player_name', 'full_name'], 
        'pos': ['Position', 'POS', 'POSITION', 'playerpos', 'player_position', 'positions'], 
        'team': ['TEAM', 'Team', 'player_team'], 
        'salary': ['sal', 'Salary', 'SALARY', 'SAL', 'Sal'], 
        'proj': ['Projection', 'PROJECTION', 'Proj', 'PROJ', 'fantasy_points', 'FPTS', 'fpts', 'points', 'score']
    }

    SUFFIXES = (', Jr.', 'Jr.', ', Sr.', 'Sr.',
                'II', 'III', 'IV', 'V')        

    def __init__(self):
        """Creates Transformer object"""
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    @property
    def player_fields(self):
        """Converts dict keys to set"""
        return set(self.PLAYER_FIELDS_MAPPING.keys())

    def _fix_dst_name(self, dst_name):
        """Fixes DST name"""
        if 'football team' in dst_name.lower():
            return 'WFT Defense'
        if dst_name in self.DEFENSE_NAMES or ' ' in dst_name:
            return f"{dst_name.split(' ')[-1]} Defense"
        return f"{dst_name} Defense"

    def _first_name(self, s):
        """Converts to first name"""
        try:
            return s.split()[0] if ' ' in s else s
        except IndexError:
            return s

    def _last_name(self, s):
        """Converts to last name"""
        if not ' ' in s:
            return s
        parts = s.split(' ')
        if len(parts) == 2:
            return parts[1]
        elif parts[-1] in self.SUFFIXES:
            return parts[-2].replace(',', '')
        return ' '.join(parts[1:])

    def _remap_columns(self, df):
        """Finds match for columns

        Args:
            df (DataFrame): the dataframe

        Returns:
            dict: old column name: new column name

        """
        remap = {}
        for col in df.columns:
            for k, v in self.PLAYER_FIELDS_MAPPING.items():
                if col in v:
                    remap[col] = k
                    break
        return remap

    def _row_to_player(self, row):
        """Converts dataframe row to Player object

        Args:
            row (namedtuple): dataframe row

        Returns:
            Player
        """
        valid_kwargs = (
            'is_injured', 'max_exposure', 'min_exposure', 
            'projected_ownership', 'game_info', 'roster_order', 
            'min_deviation', 'max_deviation', 'is_confirmed_starter', 
            'fppg_floor', 'fppg_ceil'
        )
        
        kwargs = {field: getattr(row, field) for field in row._fields
                  if field in valid_kwargs}

        return Player (
            player_id=row.player, 
            first_name=self._first_name(row.player),
            last_name=self._last_name(row.player),
            positions=[row.pos],
            team=row.team,
            salary=row.salary,
            fppg=row.proj,
            **kwargs
        )

    def make_players(self, df, thresholds=None):
        """Makes players from projection dataframe
        Canonical form is to have the following columns: player, pos, team, salary, proj
        Will attempt to find comparable columns (within reason)

        Args:
            df (DataFrame): projections dataframe
            thresholds (dict): positional fantasy point thresholds to include player

        Returns:
            list: of Player

        """
        # remap columns if necessary
        if not self.player_fields <= set(df.columns):
            df = df.rename(columns=self._remap_columns(df))

        # standardize position and names for DST
        df['pos'] = df.pos.str.replace('[Dd].*', 'DST')
        fixed = df.loc[df['pos'] == 'DST', 'player'].apply(self._fix_dst_name)
        df.loc[df['pos'] == 'DST', 'player'] = fixed

        # filter for thresholds
        if thresholds:
            df['thresh'] = df['pos'].map(thresholds)
            df = df.loc[df['proj'] >= df['thresh'], :]
            
        # now create players
        return [self._row_to_player(row) for row in df.itertuples()]
        

if __name__ == '__main__':
    pass