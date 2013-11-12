import copy
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
  def num_scheduled(self):
    return len(filter(lambda g: g.slot != None, self.schedule))
  def game_on(self, d):
    return filter(lambda g: g.slot != None and g.slot.day == d, self.schedule)[0]
  def num_gilman(self):
    return map(lambda x: x.slot != None and x.slot.site, self.schedule).count(Site.gilman)
  def num_late(self, fall_only=False):
    return map(lambda x: x.slot != None and (not fall_only or x.slot.day in fall) and x.slot.time, self.schedule).count(Time.late)
  def num_fall(self):
    fall = filter(lambda g: g.slot != None and '12/' in g.slot.day, \
      self.schedule)
    return len(fall)
  def num_fall_early(self):
    fall = filter(lambda g: g.slot != None and '12/' in g.slot.day, \
      self.schedule)
    return map(lambda x: x.slot.time, fall).count(Time.early)
  def days_that(self, pred):
    return map(lambda x: x.slot.day, filter(pred, self.schedule))
  def print_schedule(self):
    print self.name
    for d in all_days:
      if not self.free_on(d):
        print ' ', self.game_on(d)
    # days = map(lambda g: g.slot.day, self.schedule)
    # sched = zip(days,self.schedule)
    # sched.sort()
    # # self.schedule.sort(key=Game.slot)
    # print self.name
    # for (d,g) in sched:
    #   print ' ', g
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
  def sum_scheduled(self):
    # return 10*max(self.t1.num_scheduled(), self.t2.num_scheduled()) + \
    #   min(self.t1.num_scheduled(), self.t2.num_scheduled())
    return self.t1.num_scheduled() + self.t2.num_scheduled()
  def sum_gilman(self):
    return max(self.t1.num_gilman(),self.t2.num_gilman()) + \
      min(self.t1.num_gilman(),self.t2.num_gilman())
    # return max(self.t1.num_gilman(),self.t2.num_gilman())
    # return self.t1.num_gilman() + self.t2.num_gilman()
  def sum_late(self):
    return max(self.t1.num_late(),self.t2.num_late()) + \
      min(self.t1.num_late(),self.t2.num_late())
  def sum_late_fall(self):
    return max(self.t1.num_late(True),self.t2.num_late(True)) + \
      min(self.t1.num_late(True),self.t2.num_late(True))
  def sum_fall(self):
    return max(self.t1.num_fall(),self.t2.num_fall()) + \
      min(self.t1.num_fall(),self.t2.num_fall())
  def short_str(self):
    return '%sv%s' % (self.t1, self.t2)
  def __str__(self):
    return '%s v %s, %s' % (self.t1, self.t2, self.slot)

tues2012 = ['12/3','12/10','12/17']
tues2013 = ['1/7','1/14','1/21','1/28','2/4','2/11']
thurs2012 = ['12/5','12/12','12/19']
thurs2013 = ['1/9','1/16','1/23','1/30','2/6','2/13']
tuesdays = tues2012 + tues2013
thursdays = thurs2012 + thurs2013
fall = tues2012 + thurs2012
winter = tues2013 + thurs2013
all_days = [d for days in zip(tuesdays, thursdays) for d in days]

def tues(d):
  return d in tuesdays

def thurs(d):
  return d in thursdays

def f_san_pablo_blocked(s):
  blocked_days = ['1/7', '2/4', '2/11']
  return s.site == Site.san_pablo and s.day in blocked_days

def f_open(s):
  one_field_nights = ['1/7', '2/11']
  return ((s.site == Site.gilman and s.time == Time.late and s.day in tues2013) \
    and not (s.day in one_field_nights and s.field == 1)) \
    or (s.site == Site.gilman and s.day == '2/13')

def gen_slots(site, dates, time, num_fields):
  slots = []
  for d in dates:
    for n in range(1,num_fields+1):
      slots += [Slot(d, site, time, n)]
  return slots

def gen_season():
  tues_san_pablo = gen_slots(Site.san_pablo, tues2013, Time.full, 2)
  thurs_san_pablo = gen_slots(Site.san_pablo, thurs2013, Time.full, 2)
  tues_gilman = gen_slots(Site.gilman, tues2012, Time.early, 4)
  tues_gilman += gen_slots(Site.gilman, tues2013, Time.early, 2)
  tues_gilman += gen_slots(Site.gilman, tuesdays, Time.late, 2)
  thurs_gilman = gen_slots(Site.gilman, thursdays, Time.late, 2)
  season = tues_san_pablo + tues_gilman + thurs_gilman + thurs_san_pablo
  for f in [f_open, f_san_pablo_blocked]:
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

def schedule_deterministic(games, slots, teams):
  to_schedule = list(games)
  slots.sort(key=lambda s: s.day)
  for s in slots:
    d = s.day
    available_games = filter(lambda g: g.t1.free_on(s.day) and
                                       g.t2.free_on(s.day), to_schedule)
    # print len(available_games),
    # available_games = filter(lambda g: g.t1.num_scheduled() == g.t2.num_scheduled(), available_games)
    # print len(available_games)
    random.shuffle(available_games)
    available_games.sort(key=Game.sum_scheduled)
    if len(available_games) == 0:
      return False
    g = available_games[0]
    g.schedule(s)
    to_schedule.remove(g)
    # print 'scheduled', g, len(available_games)
  return to_schedule

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
  for d in all_days:
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
    if (attempts == 1000):
      print '\taborting balancing sites after 1000 attempts'
      return False
    # print '\t', num_failing(teams, min_per)
  print '%u\tattempts to balance gilman' % attempts
  return True

def try_to_balance_times(teams, games, min_per, fall_only):
  for t in teams:
    while t.num_late(fall_only) < min_per:
      dates_to_swap = t.days_that(lambda x: x.slot!=None and x.slot.time == Time.early)
      games_to_swap = sum(map(lambda d: games_on(d,games), dates_to_swap), [])
      games_to_swap = filter(lambda g: g.slot.site == Site.gilman, games_to_swap)
      games_to_swap = filter(lambda g: g.slot.time == Time.late, games_to_swap)
      if fall_only:
        games_to_swap.sort(key=Game.sum_late_fall, reverse=True)
      else:
        games_to_swap.sort(key=Game.sum_late, reverse=True)
      if len(games_to_swap) == 0:
        break
      target = games_to_swap[0]
      target.swap_slot(t.game_on(target.slot.day))

def shuffle_times(games):
  games = filter(lambda g: g.slot.site==Site.gilman, games)
  valid_days = set(map(lambda g: g.slot.day, games))
  for d in valid_days:
    games_on_d = games_on(d, games)
    perm_indices = range(len(games_on_d))
    random.shuffle(perm_indices)
    for (g,i) in zip(games_on_d, perm_indices):
      g.swap_slot(games_on_d[i])

def balance_times(teams, games, max_attempts, fall_only=False):
  def num_failing(teams, k):
    return len(filter(lambda t: t.num_late(fall_only) < k, teams))
  num_avail = sum(map(lambda x: x.num_late(fall_only), teams))
  min_per = num_avail/len(teams)
  # print min_per, num_avail
  attempts = 0
  while num_failing(teams, min_per) > 0:
    # print num_failing(teams, min_per),'failing times'
    shuffle_times(games)
    try_to_balance_times(teams, games, min_per, fall_only)
    attempts+=1
    if (attempts % max_attempts) == 0:
      print '\taborting balancing times after %u attempts' % max_attempts
      return False
      # print '\t',attempts
  print '%u\tattempts to balance times' % attempts
  return True

def print_season(games,sep='\t'):
  def game_str(games_on_d, site, time, field):
    for g in games_on_d:
      if g.slot.site == site and g.slot.time == time and g.slot.field == field:
        return g.short_str()
    return ''
  for d in all_days:
    games_on_d = games_on(d, games)
    print '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (d,sep,
      game_str(games_on_d, Site.gilman, Time.early, 1), sep,
      game_str(games_on_d, Site.gilman, Time.early, 2), sep,
      game_str(games_on_d, Site.gilman, Time.early, 3), sep,
      game_str(games_on_d, Site.gilman, Time.early, 4), sep,
      game_str(games_on_d, Site.gilman, Time.late, 1), sep,
      game_str(games_on_d, Site.gilman, Time.late, 2), sep,
      game_str(games_on_d, Site.san_pablo, Time.full, 1), sep,
      game_str(games_on_d, Site.san_pablo, Time.full, 2))

def schedule_legal(teams):
  teams_legal = map(lambda t: t.not_double_booked(), teams)
  return reduce(lambda x,y: x and y, teams_legal)


def main():
  nf = []
  while(1):
    slots = gen_season()
    teams = gen_teams(12)
    games = gen_games(teams)

    random.seed(5)
    slots2012 = filter(lambda x: x.day in tues2012, slots)
    unscheduled = schedule_deterministic(games, slots2012, teams)
    if not unscheduled:
      break
    s2 = filter(lambda x: x.day in thurs2012, slots)
    unscheduled = schedule_deterministic(unscheduled, s2, teams)
    if not unscheduled:
      break
    scheduled = filter(lambda g: g not in unscheduled, games)
    # if not balance_times(teams, scheduled):
    #   break
    # for t in teams:
    #   print t, t.num_scheduled()

    slots = filter(lambda x: x.day in winter, slots)
    random.seed()
    schedule(unscheduled, slots, teams)

    if not balance_sites(teams, unscheduled):
      continue
    if not balance_times(teams, games, 100):
      continue
    # if not balance_times(teams, scheduled, 1000, True):
    #   continue
    num_fail = len(filter(lambda t: t.num_fall_early() != 2, teams))
    print num_fail, 'nf'
    if num_fail  != 2:
      nf += [num_fail]
      continue
    break

  print nf

  for t in teams:
    t.print_schedule()

  for t in teams:
    print t, t.num_gilman(), t.num_late(), t.num_fall(), t.num_fall_early()#, t.not_double_booked()

  # 
  # print 'Not double booked:', schedule_legal(teams)
  # 
  print_season(games,',')

if __name__ == '__main__':
	main()