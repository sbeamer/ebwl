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
  def swap_slot(self, other_game):
    # print 'swapping'
    temp_slot = other_game.slot
    other_game.slot = self.slot
    self.slot = temp_slot


def print_list(l):
  print '\n'.join(map(lambda x: x.__str__(), l))


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
  no_returns = map(lambda s: s.strip(), open(filename).readlines())
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


def on_tuesday(game):
  return 'Tuesday' in game.slot.weekday

def on_gilman(game):
  return 'Gilman' in game.slot.location()

def early_gilman(game):
  return on_gilman(game) and '7' in game.slot.time

def games_for_team(team, games):
  return [g for g in games if (g.t1 == team) or (g.t2 == team)]

def remove_unscheduled(games):
  return [g for g in games if g.slot != None]

def games_excl_teams(games, teams):
  return [g for g in games if (g.t1 not in teams) and (g.t2 not in teams)]

def games_on_day(date, games):
  return [g for g in remove_unscheduled(games) if g.slot.date==date]

def teams_playing_in(games):
  return [t for g in games for t in g.teams()]

def games_free_for_day(games, date):
  unscheduled = [g for g in games if g.slot == None]
  teams_playing = teams_playing_in(games_on_day(date, games))
  return games_excl_teams(unscheduled, teams_playing)

def print_team_schedule(team, games):
  print_list(sorted(games_for_team(team, games),key=lambda g: g.slot.date))

def count_metric(pred, games, num_teams):
  c = Counter(teams_playing_in(filter(pred, games)))
  return c

def metric_total(pred, games):
  return len(filter(pred, games))

def game_total(pred, g, games):
  return metric_total(pred, games_for_team(g.t1, games)) + \
         metric_total(pred, games_for_team(g.t2, games))


def check_balance(pred, games, teams):
  counts = count_metric(pred, games, len(teams)).values()
  total_avail = sum(counts)
  min_per = total_avail / len(teams)
  max_per = (total_avail + len(teams) - 1) / len(teams)
  return min(counts) >= min_per and max(counts) <= max_per


def schedule(games, slots):
  for s in slots:
    available_games = games_free_for_day(games, s.date)
    if len(available_games) == 0:
      return False
    random.shuffle(available_games)
    available_games[0].schedule(s)
  return True

def try_balance(pred, games, teams):
  counts = count_metric(pred, games, len(teams)).values()
  total_avail = sum(counts)
  min_per = total_avail / len(teams)
  max_per = (total_avail + len(teams) - 1) / len(teams)
  if min(counts) >= min_per and max(counts) <= max_per:
    return True
  for t in teams:
    if metric_total(pred, games_for_team(t, games)) < min_per:
      swap_one_for(t, pred, games)
    elif metric_total(pred, games_for_team(t, games)) > max_per:
      swap_one_for(t, lambda g: not(pred), games)
  return False

def swap_one_for(team, pred, games):
  neg_games = filter(lambda g: not(pred(g)), games_for_team(team, games))
  dates_to_swap = map(lambda g: g.slot.date, neg_games)
  games_to_swap = map(lambda d: games_on_day(d,games), dates_to_swap)
  games_to_swap = filter(pred, sum(games_to_swap,[]))
  games_to_swap.sort(key=lambda g: game_total(pred, g, games), reverse=True)
  if len(games_to_swap)>0:
    down_game = games_to_swap[0]
    up_game = games_on_day(down_game.slot.date, games_for_team(team, games))[0]
    down_game.swap_slot(up_game)

def balance(label, pred, games, teams):
  trials = 0
  while not try_balance(pred, games, teams) and trials < 10:
    trials += 1
  if trials == 10:
    print '  unbalanced', label
    return False
  print '  balanced', label
  return True


def main():
  num_teams = 12
  if len(sys.argv) < 2:
    print 'Please give schedule input csv'
    return
  filename = sys.argv[1]
  seed = 6475
  teams = gen_teams(num_teams)
  slots = load_slots(filename)
  while True:
    random.seed(seed)
    seed += 1
    games = gen_games(teams)
    if not schedule(games, slots):
      continue
    print 'seed=%u\n  scheduled' % (seed-1)
    if not check_balance(on_tuesday, games, teams):
      print '  unbalanced tuesdays'
      continue
    print '  balanced tuesdays'
    if not balance('gilman/san pablo', on_gilman, games, teams):
      continue
    if not balance('early gilman', early_gilman, games, teams):
      continue
    break
  for t in teams:
    print '\n**%s**' % t
    print_team_schedule(t, games)


if __name__ == '__main__':
	main()
