from collections import Counter
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

def gen_teams(num_teams):
  return map(lambda x: 'T' + str(x), range(1,num_teams+1))

def gen_games(teams):
  all_games = []
  for t1 in teams:
    for t2 in teams[teams.index(t1):]:
      if t1 != t2:
        all_games += [Game(t1,t2)]
  return all_games


def main():
  num_teams = 12
  if len(sys.argv) < 2:
    print 'Please give schedule input csv'
    return
  filename = sys.argv[1]
  slots = load_slots(filename)
  # for s in slots:
  #   print s
  # slot_stats(slots)
  teams = gen_teams(num_teams)
  games = gen_games(teams)
  # for g in games:
  #   print g


if __name__ == '__main__':
	main()
