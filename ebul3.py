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
    return map(lambda x: x.slot.site, self.schedule).count(Site.gilman)
  def num_late(self):
    return map(lambda x: x.slot.time, self.schedule).count(Time.late)
  def num_fall_early(self):
    fall = filter(lambda g: '11/' in g.slot.day or '12/' in g.slot.day, \
      self.schedule)
    return map(lambda x: x.slot.time, fall).count(Time.early)
  def days_that(self, pred):
    return map(lambda x: x.slot.day, filter(pred, self.schedule))
  def print_schedule(self):
    days = map(lambda g: g.slot.day, self.schedule)
    sched = zip(days,self.schedule)
    sched.sort()
    # self.schedule.sort(key=Game.slot)
    print self.name
    for (d,g) in sched:
      print ' ', g
  def not_double_booked(self):
    days = map(lambda g: g.slot.day, self.schedule)
    return len(days) == len(set(days))

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
    return 10*max(self.t1.num_gilman(),self.t2.num_gilman()) + \
      min(self.t1.num_gilman(),self.t2.num_gilman())
    # return max(self.t1.num_gilman(),self.t2.num_gilman())
    # return self.t1.num_gilman() + self.t2.num_gilman()
  def sum_late(self):
    return 10*max(self.t1.num_late(),self.t2.num_late()) + \
      min(self.t1.num_late(),self.t2.num_late())
  def short_str(self):
    return '%sv%s' % (self.t1, self.t2)
  def __str__(self):
    return '%s v %s, %s' % (self.t1, self.t2, self.slot)

tuesdays = ['11/27','12/4','12/11','12/18','1/8','1/15','1/22','1/29','2/5']
thursdays = ['11/29','12/6','12/13','12/20','1/10','1/17','1/24','1/31','2/7']
all_days = [d for days in zip(tuesdays, thursdays) for d in days]

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
  return map(lambda x: Team('T%u' % x), range(1,n+1))

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
  print '%u\tattempts to get legal dates' % num_attempts

def games_on(d, games):
  return filter(lambda x: x.slot.day == d, games)

def try_to_balance_sites(teams, games, min_per):
  for t in teams:
    while t.num_gilman() < min_per:
      dates_to_swap = t.days_that(lambda x: x.slot.site == Site.san_pablo)
      games_to_swap = sum(map(lambda d: games_on(d,games), dates_to_swap), [])
      games_to_swap = filter(lambda g: g.slot.site == Site.gilman, games_to_swap)
      games_to_swap.sort(key=Game.sum_gilman, reverse=True)
      target = games_to_swap[0]
      target.swap_slot(t.game_on(target.slot.day))

def shuffle_slots(games):
  for d in tuesdays:
    games_on_d = games_on(d, games)
    perm_indices = range(len(games_on_d))
    random.shuffle(perm_indices)
    for (g,i) in zip(games_on_d, perm_indices):
      g.swap_slot(games_on_d[i])

def balance_sites(teams, games):
  def num_failing(teams, k):
    return len(filter(lambda t: t.num_gilman() < k, teams))
  num_avail = sum(map(lambda x: x.num_gilman(), teams))
  min_per = num_avail/len(teams)
  attempts = 0
  while num_failing(teams, min_per) > 0:
    # print num_failing(teams, min_per),'failing gilman'
    shuffle_slots(games)
    try_to_balance_sites(teams, games, min_per)
    attempts+=1
  print '%u\tattempts to balance gilman' % attempts

def try_to_balance_times(teams, games, min_per):
  for t in teams:
    while t.num_late() < min_per:
      dates_to_swap = t.days_that(lambda x: x.slot.time == Time.early)
      games_to_swap = sum(map(lambda d: games_on(d,games), dates_to_swap), [])
      games_to_swap = filter(lambda g: g.slot.site == Site.gilman, games_to_swap)
      games_to_swap = filter(lambda g: g.slot.time == Time.late, games_to_swap)
      games_to_swap.sort(key=Game.sum_late, reverse=True)
      if len(games_to_swap) == 0:
        break
      target = games_to_swap[0]
      target.swap_slot(t.game_on(target.slot.day))

def shuffle_times(games):
  games = filter(lambda g: g.slot.site==Site.gilman, games)
  for d in tuesdays:
    games_on_d = games_on(d, games)
    perm_indices = range(len(games_on_d))
    random.shuffle(perm_indices)
    for (g,i) in zip(games_on_d, perm_indices):
      g.swap_slot(games_on_d[i])

def balance_times(teams, games):
  def num_failing(teams, k):
    return len(filter(lambda t: t.num_late() < k, teams))
  num_avail = sum(map(lambda x: x.num_late(), teams))
  min_per = num_avail/len(teams)
  # print min_per, num_avail
  attempts = 0
  while num_failing(teams, min_per) > 0:
    # print num_failing(teams, min_per),'failing times'
    shuffle_times(games)
    try_to_balance_times(teams, games, min_per)
    attempts+=1
  print '%u\tattempts to balance times' % attempts  

def print_season(games,sep='\t'):
  def game_str(games_on_d, site, time, field):
    for g in games_on_d:
      if g.slot.site == site and g.slot.time == time and g.slot.field == field:
        return g.short_str()
    return ''
  for d in all_days:
    games_on_d = games_on(d, games)
    print '%s%s%s%s%s%s%s%s%s%s%s%s%s' % (d,sep,
      game_str(games_on_d, Site.gilman, Time.early, 1), sep,
      game_str(games_on_d, Site.gilman, Time.early, 2), sep,
      game_str(games_on_d, Site.gilman, Time.late, 1), sep,
      game_str(games_on_d, Site.gilman, Time.late, 2), sep,
      game_str(games_on_d, Site.san_pablo, Time.full, 1), sep,
      game_str(games_on_d, Site.san_pablo, Time.full, 2))

def schedule_legal(teams):
  teams_legal = map(lambda t: t.not_double_booked(), teams)
  return reduce(lambda x,y: x and y, teams_legal)

def main():
  slots = gen_season()
  teams = gen_teams(12)
  games = gen_games(teams)

  # random.shuffle(slots)
  # for (g,s) in zip(games, slots):
  #   g.schedule(s)

  schedule(games, slots, teams)
  
  balance_sites(teams, games)
  
  balance_times(teams, games)

  # for t in teams:
  #   t.print_schedule()

  for t in teams:
    print t, t.num_gilman(), t.num_late(), t.num_fall_early(), t.not_double_booked()

  print 'Not double booked:', schedule_legal(teams)

  print_season(games,',')

if __name__ == '__main__':
	main()