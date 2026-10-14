"""Exact local tests for U U* = I on infinite binary finite-support tape."""
import itertools,json,sys
from fractions import Fraction as F
from v36_kernel import parse,check as column_check,Z,ONE,add,mul,adj
def predecessors(q,head,tape,rules):
 o={}
 for (source_q,a,target_q,b,d),v in rules.items():
  if target_q!=q:continue
  source_head=head-d
  if int(source_head in tape)!=b:continue
  source_tape=frozenset((tape-{source_head}) if a==0 else (tape|{source_head}))
  key=(source_q,source_head,source_tape)
  o[key]=add(o.get(key,Z),adj(v))
 return {k:v for k,v in o.items() if v!=Z}
def inner(x,y):
 acc=Z
 for k,v in x.items():
  if k in y:acc=add(acc,mul(adj(v),y[k]))
 return acc
def row_check(spec):
 n,rules=parse(spec)
 tested=0
 for delta in (-2,0,2):
  sites=sorted({-1,1,delta-1,delta+1})
  for first in itertools.product((0,1),repeat=len(sites)):
   t0=frozenset(s for s,b in zip(sites,first) if b)
   for second in itertools.product((0,1),repeat=len(sites)):
    t1=frozenset(s for s,b in zip(sites,second) if b)
    for q in range(n):
     x=(q,0,t0); px=predecessors(*x,rules)
     for qp in range(n):
      y=(qp,delta,t1)
      actual=inner(px,predecessors(*y,rules))
      expected=ONE if x==y else Z
      tested+=1
      if actual!=expected:
       return {'verified':False,'reason':'ROW_OR_COMPLETENESS_FAILURE','tested':tested,
               'target_a':[q,0,sorted(t0)],'target_b':[qp,delta,sorted(t1)],
               'actual':[[v.numerator,v.denominator] for v in actual],
               'expected':[[v.numerator,v.denominator] for v in expected]}
 return {'verified':True,'reason':'INFINITE_TAPE_COISOMETRY','tested':tested}
def full_check(spec):
 col=column_check(spec)
 if not col['verified']:return {'verified':False,'reason':'COLUMN_FAILURE','detail':col}
 row=row_check(spec)
 if not row['verified']:return {'verified':False,'reason':'ROW_FAILURE','detail':row}
 return {'verified':True,'reason':'INFINITE_TAPE_UNITARY','column_checks':col['tested'],
         'row_checks':row['tested'],'states':col['states'],
         'mathematical_scope':'finite local criterion; exact Q(i); human reduction'}
if __name__=='__main__':
 try:
  result=full_check(json.load(sys.stdin))
  print(json.dumps(result));sys.exit(0 if result['verified'] else 1)
 except (ValueError,TypeError,KeyError,IndexError) as e:
  print(json.dumps({'verified':False,'reason':str(e)}));sys.exit(2)