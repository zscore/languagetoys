"""
Let's find pairs of words that blend nicely, like
book + hookup --> bookup

Strategy: given a wordlist, first remove generative affixes like un-
and -ly. Find all reasonably-long substrings of every word. Match
suffixes of candidate first words with midparts of candidate second
words.

TODO: get better at stripping affixes
  (though that's not always a win: e.g.:
  contendresse                   contendress + tendresse)
  (also: bunchawed from bunch and unchawed)

TODO: currently we're matching suffixes against prefixes instead
of midparts, so the motivating example above doesn't even appear...

TODO: the pronunciations should blend, not just the spelling.
"""

import re

raw_words = set(unicode(line.rstrip('\n'), 'utf8').lower()
                for line in open('words')) #open('/usr/share/dict/words'))

left_noise = """
  be bi em en di duo im iso non oct octo out pre quad quadra quadri re
  sub tri un uni
""".split()
right_noise = """
  ability able adian age an ation d ed en ent er es escent ful ian ic
  ies ily iness ing ish ite ize less let log like liness ly ness og
  ogy proof r ress ry s ship tion y
""".split()

def noisy(w):
    for ln in left_noise:
        if w.startswith(ln) and w[len(ln):] in raw_words:
            return True
    for rn in right_noise:
        if w.endswith(rn) and w[:-len(rn)] in raw_words:
            return True
    for i in range(1, len(w)):
        p, s = w[:i], w[i:]
        if p in raw_words and s in raw_words:
            return True
    return False

words = set(w for w in raw_words if not noisy(w))

if False:
    for word in sorted(words):
        print word
    import sys
    sys.exit(0)

prefixes = {}
for w in words:
    if 3 < len(w):
        for i in range(3, len(w)+1):
            p = w[:i]
            prefixes.setdefault(p, []).append(w)
               
suffixes = {}
for w in words:
    if 3 < len(w):
        for i in range(len(w)-3):
            p = w[i:]
            suffixes.setdefault(p, []).append(w)

common = set()
for prefix, prefix_words in prefixes.iteritems():
    if prefix in suffixes:
        suffix_words = suffixes[prefix]
        if suffix_words != prefix_words:
            if any(not p.startswith(s)
                   and not s.endswith(p)
                   and (s + p[len(prefix):]) not in raw_words
                   for p in prefix_words
                   for s in suffix_words):
                common.add(prefix)

print len(common)
print max(common, key=len)

def portmanteaus(affix):
    for p in prefixes[affix]:
        for s in suffixes[affix]:
            if (not p.startswith(s) and not s.endswith(p)
                and (s + p[len(affix):]) not in raw_words):
                yield s, p, affix

import math
import pdist

def score((s, p, affix)):
    return -math.log10(pdist.Pw(s) * pdist.Pw(p) * 1.1**len(affix))
    L = len(s) + len(p) - len(affix)
    return -math.log10(pdist.Pw(s) * pdist.Pw(p) * 2**(-float(L)/len(affix)))

results = [(score(triple), triple)
           for affix in common
           for triple in portmanteaus(affix)]

for score, (s, p, affix) in sorted(results):
    combo = s + p[len(affix):]
    print '  %6.2f %-30s %s + %s' % (score, combo, s, p)
