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


def load_slots(filename):
  f = open(filename)
  lines = f.readlines()
  no_returns = map(lambda s: s.strip(), lines)
  no_blanks = filter(lambda s: s!='', no_returns)
  return map(Slot, no_blanks)

def slot_stats(slots):
  print '%u total slots' % len(slots)
  field_counts = Counter(map(lambda slot: slot.location(), slots))
  for field, count in field_counts.items():
    print '  %s: %u' % (field, count),
  print '  Total: %u' % sum(field_counts.values())


def main():
  if len(sys.argv) < 2:
    print 'Please give schedule input csv'
    return
  filename = sys.argv[1]
  slots = load_slots(filename)
  # for s in slots:
  #   print s
  slot_stats(slots)


if __name__ == '__main__':
	main()
