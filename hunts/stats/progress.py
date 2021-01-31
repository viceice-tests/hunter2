# Copyright (C) 2021 The Hunter2 Contributors.
#
# This file is part of Hunter2.
#
# Hunter2 is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Hunter2 is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with Hunter2.  If not, see <http://www.gnu.org/licenses/>.

import json
from datetime import datetime

from django.db.models import Min
from django.utils.html import escape
from django.utils.safestring import mark_safe
from schema import And, Schema

from teams.models import TeamRole
from .abstract import AbstractGenerator
from ..models import Episode, Guess, TeamPuzzleData


class ProgressGenerator(AbstractGenerator):
    """
    Generates a graph showing progress through the hunt

    There is a graph per episode showing the number of puzzles completed against time.
    """
    id = 'progress'
    title = 'Progress Graph'
    version = 1

    template = 'hunts/stats/progress.html'

    schema = Schema({
        'episode_progress': [
            {
                'id': int,
                'name': str,
                'data': {
                    'puzzle_names': [str],
                    'teams': [{
                        'team_id': int,
                        'team_name': And(str, len),
                        'puzzle_times': [{
                            'puzzle': int,
                            'date': datetime,
                        }],
                    }],
                },
            },
        ],
    })

    def __init__(self, number=10, **kwargs):
        super().__init__(**kwargs)
        self.number = number

    def generate(self):
        episodes = [self.episode] if self.episode is not None else Episode.objects.all()

        results = []

        for episode in episodes:
            tp_datas = TeamPuzzleData.objects.filter(
                puzzle__episode=episode, start_time__isnull=False,
            ).order_by('start_time')

            by_team = {}

            for tp_data in tp_datas:
                if tp_data.team.id not in by_team:
                    by_team[tp_data.team.id] = {
                        'team_id': tp_data.team.id,
                        # We have to escape team names here since they are encoded in JSON which is marked safe later
                        'team_name': escape(tp_data.team.get_display_name()),
                        'puzzle_times': [{
                            'puzzle_name': '',
                            'date': tp_data.start_time.isoformat(),
                        }]
                    }

            correct_guesses = Guess.objects.filter(
                correct_current=True, correct_for__isnull=False, for_puzzle__episode=episode, by_team__role=TeamRole.PLAYER,
            ).select_related(
                'by_team',
                'for_puzzle',
            ).values(
                'by_team', 'for_puzzle__title', 'given',
            ).annotate(
                min_given=Min('given'),
            ).order_by('min_given')

            for guess in correct_guesses:
                by_team[guess['by_team']]['puzzle_times'].append({
                    'puzzle_name': guess['for_puzzle__title'],
                    'date': guess['given'].isoformat(),
                })

            data = {
                'teams': [team for team in by_team.values() if len(team['puzzle_times']) > 1],
            }

            if not episode.parallel:
                data['puzzle_names'] = [puzzle.title for puzzle in episode.puzzle_set.all()]

            results.append({
                'id': episode.id,
                'name': mark_safe(episode.name),
                'data': mark_safe(json.dumps(data)),
            })

        return {
            'episode_progress': results,
        }
