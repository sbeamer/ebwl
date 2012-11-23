import random

class Team:
  def __init__(self, name):
    self.name = name
    self.schedule = []
  def __str__(self):
    return self.name
  def played(self, opp):
    t1 = map(lambda x: x.t1, self.schedule)
    t2 = map(lambda x: x.t2, self.schedule)
    return (opp in t1) or (opp in t2)
  def free_on(self, d):
    def grab_day(g):
      if g.slot != None:
        return g.slot.day
    days = map(grab_day, self.schedule)
    return not d in days
  def conflicting_games(self):
    days = map(lambda x: x.slot.day, self.schedule)
    dupe_days = []
    for d in days:
      if days.count(d) > 1:
        dupe_days += [d]
    dupe_days = list(set(dupe_days))
    dupe_games = []
    for d in dupe_days:
      dupe_games += filter(lambda x: x.slot.day == d, self.schedule)[:1]
    return dupe_games
  def print_schedule(self):
    self.schedule.sort()
    print self.name
    for g in self.schedule:
      print ' ', g

class Site:
  san_pablo, gilman = 'San Pablo', 'Gilman'

class Time:
  early, late, full = '7-9p', '9-11p', '7-10p'

class Slot:
  def __init__(self, d, s, t, f):
    self.day = d
    self.site = s
    self.time = t
    self.field = f  
  def __str__(self):
    return '%s @ %s, %s #%u' % (self.day, self.time, self.site, self.field)

class Game:
  def __init__(self, t1, t2, slot=None):
    self.t1 = t1
    self.t2 = t2
    self.t1.schedule += [self]
    self.t2.schedule += [self]
    self.slot = slot
  def schedule(self, slot):
    self.slot = slot
  def swap_slot(self, other):
    temp = self.slot
    self.slot = other.slot
    other.slot = temp
  def ok_to_swap(self, other):
    my_day = self.slot.day
    other_day = other.slot.day
    return self.t1.free_on(other_day) and self.t2.free_on(other_day) and \
      other.t1.free_on(my_day) and other.t2.free_on(my_day) and \
      (self.t1 != other.t1 and self.t1 != other.t2) and \
      (self.t2 != other.t1 and self.t2 != other.t2)
  def __str__(self):
    return '%s v %s, %s' % (self.t1, self.t2, self.slot)

tuesdays = ['11/27','12/4','12/11','12/18','1/8','1/15','1/22','1/29','2/5']
thursdays = ['11/29','12/6','12/13','12/20','1/10','1/17','1/24','1/31','2/7']

def tues(d):
  return d in tuesdays

def thurs(d):
  return d in thursdays

def f_san_pablo_first_week(s):
  return s.site == Site.san_pablo and (s.day == '11/27' or s.day == '11/29')

def f_beginners(s):
  return s.site == Site.san_pablo and (s.day == '12/4' or s.day == '12/6') and \
    s.field == 2

def f_open(s):
  free_gilman_dates = ['12/6','12/20','1/17']
  free_san_pablo_dates = ['12/20','1/17']
  return (s.site == Site.gilman and s.day not in free_gilman_dates and \
    s.time == Time.late and thurs(s.day)) or \
    (s.site == Site.san_pablo and s.day not in free_san_pablo_dates and \
    s.field == 1 and thurs(s.day))

def gen_slots(site, dates, time, num_fields):
  slots = []
  for d in dates:
    for n in range(1,num_fields+1):
      slots += [Slot(d, site, time, n)]
  return slots

def gen_season():
  tues_san_pablo = gen_slots(Site.san_pablo, tuesdays, Time.full, 2)
  thurs_san_pablo = gen_slots(Site.san_pablo, thursdays, Time.full, 2)
  tues_gilman = gen_slots(Site.gilman, tuesdays, Time.early, 2)
  tues_gilman += gen_slots(Site.gilman, tuesdays, Time.late, 2)
  thurs_gilman = gen_slots(Site.gilman, thursdays, Time.late, 2)
  season = tues_san_pablo + tues_gilman + thurs_gilman + thurs_san_pablo
  for f in [f_san_pablo_first_week, f_beginners, f_open]:
    season = filter(lambda x: not f(x), season)
  return season

def gen_teams(n):
  return map(lambda x: Team('Team %u' % x), range(1,n+1))

def gen_games(teams):
  games = []
  for t1 in teams:
    for t2 in teams:
      if t1 != t2 and not t1.played(t2):
        games += [Game(t1, t2)]
  return games

def remove_conflicts(teams, games):
  for t in teams:
    i = len(t.conflicting_games())
    for cg in t.conflicting_games():
      d = cg.slot.day
      for g in games:
        if cg.ok_to_swap(g):
          cg.swap_slot(g)
          break
      if cg.slot.day == d:
        print 'couldnt swap'
    print '%s %u to %u' % (t, i, len(t.conflicting_games()))

def reset_slots(games):
  for g in games:
    g.slot = None

def schedule(games, slots):
  num_attempts = 0
  while True:
    num_attempts += 1
    to_schedule = list(games)
    random.shuffle(to_schedule)
    reset_slots(to_schedule)
    for s in slots:
      for g in to_schedule:      
        if g.t1.free_on(s.day) and g.t2.free_on(s.day):
          g.schedule(s)
          to_schedule.remove(g)
          break
    # print len(slots), len(to_schedule)
    if len(to_schedule) == 0:
      break
  print 'took %u attempts' % num_attempts

def main():
  slots = gen_season()
  teams = gen_teams(12)
  games = gen_games(teams)

  # random.shuffle(slots)
  # for (g,s) in zip(games, slots):
  #   g.schedule(s)
  schedule(games, slots)

  # remove_conflicts(teams[:2], games)
  # remove_conflicts(teams, games)
  # remove_conflicts(teams, games)
  # remove_conflicts(teams, games)

  # teams[2].print_schedule()
  # print teams[2].conflicting_games()
  # for g in teams[0].conflicting_games():
  #   print g

  # for t in teams:
  #   for g in t.conflicting_games():
  #     print g

  # for t in teams:
  #   print t.conflicting_games()

  # print games[0]
  # print games[1]
  # games[0].swap_slot(games[1])
  # print games[0]
  # print games[1]

  # for g in games:
  #   print g
  # for s in slots():
  #   print s
  # print len(slots)
  # for t in teams:
  #   print t
  # print len(games)

if __name__ == '__main__':
	main()