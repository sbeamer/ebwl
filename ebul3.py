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
  def game_on(self, d):
    return filter(lambda g: g.slot.day == d, self.schedule)[0]
  def num_gilman(self):
    sites = map(lambda x: x.slot.site, self.schedule)
    return sites.count(Site.gilman)
  def days_that(self, pred):
    return map(lambda x: x.slot.day, filter(pred, self.schedule))
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
  def sum_gilman(self):
    return 10*max(self.t1.num_gilman(),self.t2.num_gilman()) + min(self.t1.num_gilman(),self.t2.num_gilman())
    # return max(self.t1.num_gilman(),self.t2.num_gilman())
    return self.t1.num_gilman() + self.t2.num_gilman()
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

def reset_slots(games):
  for g in games:
    g.slot = None

def schedule(games, slots, teams):
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

def games_on(d, games):
  return filter(lambda x: x.slot.day == d, games)

def num_failing(teams, k):
  return len(filter(lambda t: t.num_gilman() < k, teams))

def try_to_balance_sites(teams, games, min_per):
  for t in teams:
    while t.num_gilman() < min_per:
      # print t, t.num_gilman()
      dates_to_swap = t.days_that(lambda x: x.slot.site == Site.san_pablo)
      # print dates_to_swap
      games_to_swap = sum(map(lambda d: games_on(d,games), dates_to_swap), [])
      games_to_swap = filter(lambda g: g.slot.site == Site.gilman, games_to_swap)
      games_to_swap.sort(key=Game.sum_gilman, reverse=True)
      # make sure not self?
      target = games_to_swap[0]
      target.swap_slot(t.game_on(target.slot.day))
      # print t, t.num_gilman()

def shuffle_sites(games):
  for d in tuesdays:
    games_on_d = games_on(d, games)
    perm_indices = range(len(games_on_d))
    random.shuffle(perm_indices)
    for (g,i) in zip(games_on_d, perm_indices):
      g.swap_slot(games_on_d[i])

def balance_sites(teams, games):
  num_avail = sum(map(lambda x: x.num_gilman(), teams))
  min_per = num_avail/len(teams)
  # print min_per, num_avail
  while num_failing(teams, min_per) > 0:
    print num_failing(teams, min_per)
    shuffle_sites(games)
    try_to_balance_sites(teams, games, min_per)

def main():
  slots = gen_season()
  teams = gen_teams(12)
  games = gen_games(teams)

  # random.shuffle(slots)
  # for (g,s) in zip(games, slots):
  #   g.schedule(s)
  schedule(games, slots, teams)

  balance_sites(teams, games)

  # teams[0].print_schedule()
  # print teams[0].days_that(lambda x: x.slot.site == Site.gilman)

  # print games_on('11/27', games)

  for t in teams:
    print t, t.num_gilman()

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