from collections import Counter
import random
import sys

class Slot:
  def __init__(self, s):
    date, weekday, time, field = map(lambda s: s.strip(), s.split(','))
    self.date = date
    self.weekday = weekday
    self.time = time
    self.field = field
  def __str__(self):
    year, month, day = map(lambda s: int(s), self.date.split('/'))
    pretty_date = '%u/%u/%u' % (month, day, year)
    return '%s @ %s, %s' % (pretty_date, self.time, self.field)
  def location(self):
    s = self.field
    return s[:s.find(' #')] if '#' in s else s


class Game:
  def __init__(self, t1, t2):
    self.t1 = t1
    self.t2 = t2
    self.slot = None
  def __str__(self):
    field = self.slot if self.slot != None else 'unscheduled'
    return '%s v %s @ %s' % (self.t1, self.t2, field)
  def schedule(self, slot):
    self.slot = slot
  def teams(self):
    return [self.t1, self.t2]
  def sum_scheduled(self, games):
    scheduled = remove_unscheduled(games)
    return len(games_for_team(self.t1, scheduled) + \
               games_for_team(self.t2, scheduled))


def print_list(l):
  print '\n'.join(map(lambda x: x.__str__(), l))

def flat_map(f,l):
  return [item for sublist in map(f,l) for item in sublist]


def gen_teams(num_teams):
  return map(lambda x: 'T' + str(x), range(1,num_teams+1))

def gen_games(teams):
  all_games = []
  for t1 in teams:
    for t2 in teams[teams.index(t1):]:
      if t1 != t2:
        all_games += [Game(t1,t2)]
  return all_games

def load_slots(filename):
  f = open(filename)
  lines = f.readlines()
  no_returns = map(lambda s: s.strip(), lines)
  no_blanks = filter(lambda s: s!='', no_returns)
  return map(Slot, no_blanks)

def slot_stats(slots):
  print '%u total slots' % len(slots)
  field_counts = Counter(map(lambda slot: slot.location(), slots))
  print '  Fieilds: ', field_counts.items()
  year_counts = Counter(map(lambda s: s.date[:s.date.find('/')], slots))
  print '  Years: ', year_counts.items()
  day_counts = Counter(map(lambda slot: slot.weekday, slots))
  print '  Day: ', day_counts.items()
  time_counts = Counter(map(lambda slot: slot.time, slots))
  print '  Time: ', time_counts.items()


def games_for_team(team, games):
  return filter(lambda g: g.t1 == team or g.t2 == team, games)

def remove_unscheduled(games):
  return filter(lambda g: g.slot != None, games)

def games_excl_teams(games, teams):
  return filter(lambda g: (g.t1 not in teams) and (g.t2 not in teams), games)

def games_on_day(games, date):
  scheduled = remove_unscheduled(games)
  return filter(lambda g: g.slot.date==date, scheduled)

def games_free_for_day(games, date):
  unscheduled = filter(lambda g: g.slot == None, games)
  teams_playing = flat_map(lambda g: g.teams(), games_on_day(games, date))
  return games_excl_teams(unscheduled, teams_playing)

def print_team_schedule(team, games):
  print_list(games_for_team(team, games))


def schedule(games, slots):
  for s in slots:
    available_games = games_free_for_day(games, s.date)
    if len(available_games) == 0:
      return False
    random.shuffle(available_games)
    available_games[0].schedule(s)
  return True



def main():
  num_teams = 12
  if len(sys.argv) < 2:
    print 'Please give schedule input csv'
    return
  filename = sys.argv[1]
  scheduled = False
  seed = 65
  while not scheduled:
    random.seed(seed)
    teams = gen_teams(num_teams)
    games = gen_games(teams)
    slots = load_slots(filename)
    if not schedule(games, slots):
      print seed, 'got ', len(remove_unscheduled(games)), '/', len(games)
    else:
      print seed, 'succeeded'
      break
    seed += 1
  print_team_schedule('T1', games)


if __name__ == '__main__':
	main()
