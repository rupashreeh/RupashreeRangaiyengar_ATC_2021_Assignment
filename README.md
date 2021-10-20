                                               ** ATC Project** 

Some of the ways that you can run this code:

Ensure that python3 site-packages are available at the commandline prompt. I have the following imports:
import sys
import re
import operator
import math
from z3 import *
from prettytable import PrettyTable
from operator import itemgetter

Implemented Methods:

solveAnd() - f1 and f2 
solveOr() - f1 or f2
solveNot() - ~f1
=
<=
>=
<
>

1. python3 <path-where-file-is-downloaded>/pb.py "x1<=2" 1 10
2. python3 <path-where-file-is-downloaded>/pb.py "x1<=2" 1 1
3. python3 <path-where-file-is-downloaded>/pb.py "x1+x2<=5" 2 2 1
4. python3 <path-where-file-is-downloaded>/pb.py "x1+x2<=5" 2 4 3
5. python3 <path-where-file-is-downloaded>/pb.py "And(x1<=2,x1+x2<=5)" 2 1 3
6. python3 <path-where-file-is-downloaded>/pb.py "And(x1<=2,x1+x2<=5)" 2 1 6
7. python3 <path-where-file-is-downloaded>/pb.py "Not(x1+x2<=2)" 2 1 2
8. python3 <path-where-file-is-downloaded>/pb.py "And(Not(x1+x2<=2),x2<=1)" 2 5 3
9. python3 <path-where-file-is-downloaded>/pb.py "Not(Not(x1+x2<=2))" 2 1 2
10. python3 <path-where-file-is-downloaded>/pb.py "Or(x1+x2<=2,Not(x2<=1))" 2 5 3
11. python3 <path-where-file-is-downloaded>/pb.py "2*x7+x2<=5" 2 1 2
  

Note: My examples folder contains images of my local run of the code. It is done on a Macbook Pro with macOs Catalina. 
      I have not run this on a windows machine at all and do not know how it would behave.
     
      The order in which variables are given is taken in the same order. No order is imposed on variabe reading
   
      Spaces in the commands have no effect and are taken without the spaces: Example python3 python3 <path-where-file-is-downloaded>/pb.py "2*x7 + x2 <= 5" 2 1 2
 
