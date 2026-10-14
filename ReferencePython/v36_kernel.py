"""Exact infinite-tape local column-isometry decision for ±1 moves.
Checks all potentially overlapping source pairs modulo irrelevant tape cells.
Does NOT establish surjectivity / full unitarity.
"""
from fractions import Fraction as F
import json,sys,itertools
Z=(F(0),F(0));ONE=(F(1),F(0))
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def mul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def adj(a):return a[0],-a[1]
def amp(raw):
 if not isinstance(raw,list) or len(raw)!=4 or any(type(x)!=int for x in raw) or raw[1]<=0 or raw[3]<=0:raise ValueError('amplitude')
 v=F(raw[0],raw[1]),F(raw[2],raw[3])
 if [v[0].numerator,v[0].denominator,v[1].numerator,v[1].denominator]!=raw:raise ValueError('noncanonical')
 return v
def parse(spec):
 n=spec['states']
 if type(n)!=int or not 1<=n<=8:raise ValueError('states 1..8')
 if not isinstance(spec['rules'],list) or len(spec['rules'])>256:raise ValueError('rules budget')
 rules={}
 for r in spec['rules']:
  if not isinstance(r,list) or len(r)!=6:raise ValueError('rule')
  q,a,qp,b,d,x=r
  if any(type(v)!=int for v in (q,a,qp,b,d)) or not (0<=q<n and 0<=qp<n and a in (0,1) and b in (0,1) and d in (-1,1)):raise ValueError('indices')
  v=amp(x)
  if v==Z:raise ValueError('zero rule')
  key=q,a,qp,b,d
  if key in rules:raise ValueError('duplicate')
  rules[key]=v
 return n,rules
def out(c,rules):
 q,h,t=c;result={}
 for (q0,a0,qp,b,d),v in rules.items():
  if q!=q0 or (h in t)!=bool(a0):continue
  nt=t-{h} if b==0 else t|{h}
  k=(qp,h+d,frozenset(nt))
  result[k]=add(result.get(k,Z),v)
 return {k:v for k,v in result.items() if v!=Z}
def inner(x,y):
 s=Z
 for k,v in x.items():
  if k in y:s=add(s,mul(adj(v),y[k]))
 return s
def check(spec):
 n,rules=parse(spec);tested=0
 for delta in (-2,0,2):
  sites=sorted({0,delta})
  for bits0 in itertools.product((0,1),repeat=len(sites)):
   t0=frozenset(s for s,b in zip(sites,bits0) if b)
   for bits1 in itertools.product((0,1),repeat=len(sites)):
    t1=frozenset(s for s,b in zip(sites,bits1) if b)
    for q in range(n):
     x=(q,0,t0);ox=out(x,rules)
     for qp in range(n):
      y=(qp,delta,t1);oy=out(y,rules)
      result=inner(ox,oy);expected=ONE if x==y else Z
      tested+=1
      if result!=expected:
       return {'verified':False,'reason':'infinite-tape column overlap or norm','tested':tested,
               'source_a':[q,0,sorted(t0)],'source_b':[qp,delta,sorted(t1)],
               'actual':[[v.numerator,v.denominator] for v in result],
               'expected':[[v.numerator,v.denominator] for v in expected]}
 return {'verified':True,'reason':'INFINITE_TAPE_ISOMETRY','tested':tested,'states':n,
         'surjectivity':'NOT_CHECKED','unitarity':'NOT_ESTABLISHED'}
if __name__=='__main__':
 try:
  r=check(json.load(sys.stdin));print(json.dumps(r));sys.exit(0 if r['verified'] else 1)
 except (ValueError,TypeError,KeyError,IndexError,OverflowError) as e:
  print(json.dumps({'verified':False,'reason':str(e)}));sys.exit(2)