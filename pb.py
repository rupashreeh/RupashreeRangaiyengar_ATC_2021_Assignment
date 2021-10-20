import sys
import re
import operator
import math
from z3 import *
from prettytable import PrettyTable
from operator import itemgetter

binaryStrings=[]
states={'Error'}
vars=[]
alphabet=dict()

def main(argv):

    #The first argument is the formula in the string format
    s=sys.argv[1]
    print("The formula is:  "+str(s))
    
    #Total number of arguments
    numArgs = sys.argv[2]

    print("The number of arguments are: "+str(numArgs))
    
    #The succeeding command line arguments are variables in the range x1,x2,x3, ... xn
    vars = sys.argv[3:]
    print("The variable values are:  "+str(vars))

    #Create local variables of the form x1,x2,x3 ... xn. This step is necessary before running eval function

    for i in range(1, 100):
      locals()['x{0}'.format(i)] = Int('x%d'%i)

    #Evaluate the string and convert it to the z3 formula. 
    f=eval(s)
    solution =evaluate(f,vars)
    return
  

def evaluate(f,vars):
    result=[]
    f1 = f.decl().name()
    num = f.num_args()
    if num == 0:
       return
    else:
        if num == 1:
           f2 = f.arg(0)
        else:
           f2 = f.arg(0)
           f3 = f.arg(1)
   
    if f1 in {"and"}:
        return solveAnd(f2,f3,vars)
    elif f1 in {"not"}:
        return solveNot(f2,vars,result)
    elif f1 in {"or"}:
        return solveOr(f2,f3,vars)
    else:
        if f1 == ">=":
           return solveGreaterThanOrEquals(f2, f3, vars)
        elif f1 == "<=":
           return solveLessThanOrEquals(f2, f3, vars)
        elif f1 == "<":
           return solveLessThan(f2, f3, vars)
        elif f1 == ">":
           return solveGreaterThan(f2, f3, vars)    
        else:
           return solveEquals(f2, f3, vars)

def solveEquals(f2, f3, variables):
 response = {}
 text=str(f2)
 fun = f2
 variables_count = text.count("x")
 pattern = "(\d+)?(\\*)?([a-z])(\d+)"
 coeff = []
 opers =[]
 i=0  
 binaryStrings.clear()
 # Parse the variables and co-effiecients 
 varList = []
 
 #map the correct variable to the correct value from input
 varPosMap={}
 v1 = findOccurrences(text,'x')
 for i in range(0, len(v1)):
      xString = 'x'+text[v1[i]+1]
      varPosMap[xString]=v1[i]
 #print(v1)
 vmap=dict(sorted(varPosMap.items(), key=lambda item: item[1]))

 #create the var value map
 varList = vmap.keys()
 varValMap = dict(zip(varList, variables))
 
 # state list selection based on number of variables
 arr = [None] * variables_count
 generateAllBinaryStrings(variables_count,arr,0)

 formulaStr=str(f2)+" == "+str(f3)
 
 #the initial state is b. Add that to the set of states with I appended
 b=str(f3)+'I'
 states.add(b)
 
 #Compute the transition table using the presburger
 c = Int(str(f3))
 transitions=[]
 prettyTransitions=[]
 wSum=set()
 allStates=[]
 initialStates=[]
 initialStates.append(str(f3).strip())
 finalStates=[]
 allStates.append('States')
 pattern = "(\d+)?([A-Z])*"

 m=0
 wSum=getStates(str(f2).strip(),c,binaryStrings,varList)
 #print(wSum)
 while m < len(wSum):
  c = list(wSum)[m]
  prettyTransitions.append(str(c))
  for k in range(0,len(binaryStrings)):
    weighted_sum = computeWSForEquals(str(f2),binaryStrings[k],c, varList)
    if weighted_sum.is_integer():
        if weighted_sum == 0 :
           states.add(str(c))
           finalStates.append(str(c).strip())
           brr=[str(c).strip(),",".join(map(str, binaryStrings[k])),str(int(weighted_sum))]
           transitions.append(brr)
           prettyTransitions.append(str(int(weighted_sum)))
        else:
           states.add(int(weighted_sum))
           brr=[str(c).strip(),",".join(map(str, binaryStrings[k])),str(int(weighted_sum))]
           transitions.append(brr)
           prettyTransitions.append(str(int(weighted_sum)))
    else:
           brr=[str(c).strip(),",".join(map(str, binaryStrings[k])),"Error"]
           transitions.append(brr)
           prettyTransitions.append('Error') 
  m=m+1
 
 for n in range(0, len(binaryStrings)):
    allStates.append(",".join(map(str, binaryStrings[n])))
 t = PrettyTable(allStates)

 bStrings = len(binaryStrings)
 prettyTransitions=[]
 
 o=0
 while o < len(transitions):
    prettyArray=[]
    state = transitions[o][0]
    if state in initialStates:
        state = state + 'I'
    if state in finalStates:
        state = state + 'F'

    prettyArray.append(state)
    for p in range(0,bStrings):
        prettyArray.append(transitions[o][2])
        o=o+1
    prettyTransitions.append(prettyArray)
 
 for q in range(0, len(prettyTransitions)):
     t.add_row(prettyTransitions[q])
 
 print(formulaStr)
 print(t)
  #evaluate the formula
 for i in range(1, 100):
    locals()['x{0}'.format(i)] = Int('x%d'%i)

 f = eval(formulaStr)
 output=formulaStr +" and "
 for i in varValMap.keys():
     output = output+i+"="+varValMap[i]+" "
 x=bool(False)
 if evaulateExpr(formulaStr, varValMap):
    output = output + " is TRUE"
    bool(True)
    print(output)
 else:
    output = output + " is FALSE"
    print(output)

 response["finalStates"]=set(finalStates)
 response["initialStates"]= set(initialStates)
 response["transitions"]= transitions
 response["prettytable"]=t
 response["variables"] =varList
 response["values"]=variables
 response["count"]=variables_count
 response["binaryStrings"]=binaryStrings
 response["formula"]=formulaStr
 response["allStates"]=wSum
 response["evalExpr"]=x
 finalStates=[int(i) for i in finalStates]
 response["notStates"]=wSum.difference(set(finalStates))
 return response

def getStates(formulaStr, c, binaryStrings,varlist):
    states = set()
    states.add(c)
    states.add(0)
    m=0
    while m < len(states):
        c = list(states)[m]
        k=0  
        while k < len(binaryStrings):
            #print(binaryStrings[k])
            weighted_sum = computeWSForEquals(formulaStr,binaryStrings[k],c, varlist)
            k=k+1            
            #print(weighted_sum)
            if weighted_sum.is_integer():
                states.add(int(weighted_sum))
        m=m+1        
        states=set([int(str(i).strip()) for i in list(states)])
    return states

def getStatesLessThanOrEquals(formulaStr, c, binaryStrings,varlist):
    states = set()
    states.add(c)
    states.add(-1)
    states.add(0)
    m=0
    while m < len(states):
        c = list(states)[m]
        #print(c)
        k=0  
        while k < len(binaryStrings):
            weighted_sum = computeWSForLessThanOrEquals(formulaStr,binaryStrings[k],c, varlist)
            #print(weighted_sum)
            states.add(int(weighted_sum))
            k=k+1            
            
        m=m+1        
        #print(states)
        states=set([int(str(i).strip()) for i in list(states)])
    return states

def getStatesLessThan(formulaStr, c, binaryStrings,varlist):
    states = set()
    states.add(c)
    states.add(0)
    m=0
    while m < len(states):
        c = list(states)[m]
        k=0  
        while k < len(binaryStrings):
            #print(binaryStrings[k])
            weighted_sum = computeWSForLessThan(formulaStr,binaryStrings[k],c, varlist)
            k=k+1            
            #print(weighted_sum)
            states.add(int(weighted_sum))
        m=m+1  
        states=set([int(str(i).strip()) for i in list(states)])      
        #print(states)
    return states

def getStatesGreaterThan(formulaStr, c, binaryStrings,varlist):
    states = set()
    states.add(c)
    states.add(0)
    m=0
    while m < len(states):
        c = list(states)[m]
        k=0  
        while k < len(binaryStrings):
            #print(binaryStrings[k])
            weighted_sum = computeWSForGreaterThan(formulaStr,binaryStrings[k],c, varlist)
            k=k+1            
            #print(weighted_sum)
            states.add(int(weighted_sum))
        m=m+1        
        #print(states)
        states=set([int(str(i).strip()) for i in list(states)])
    return states
    
def getStatesGreaterThanOrEquals(formulaStr, c, binaryStrings,varlist):
    states = set()
    states.add(c)
    states.add(0)
    m=0
    while m < len(states):
        c = list(states)[m]
        k=0  
        while k < len(binaryStrings):
            #print(binaryStrings[k])
            weighted_sum = computeWSForGreaterThanOrEquals(formulaStr,binaryStrings[k],c, varlist)
            k=k+1            
            #print(weighted_sum)
            states.add(int(weighted_sum))
        m=m+1        
        #print(states)
        states=set([int(str(i).strip()) for i in list(states)])
    return states

def evaulateExpr(formulaStr, varValMap):
  for value in varValMap:
      formulaStr = formulaStr.replace(value,varValMap.get(value))
      #print(formulaStr)
  g = eval(formulaStr)
  return g

def evaulateExprForNot(formulaStr, varValMap):
  for value in varValMap:
      formulaStr = formulaStr.replace(value,varValMap.get(value))
  g = eval(formulaStr)
  return g

def getExprValue(formulaStr, varValMap):
  #print(varValMap)
  for value in varValMap:
      formulaStr = formulaStr.replace(value,varValMap.get(value))
  #print(formulaStr)
  g = eval(formulaStr)
  #print(g)
  return g

def computeWSForEquals(formulaStr, arr,c, varlist):
    arrStr=[str(i) for i in arr]
    #print(arrStr)
    #print(varlist)
    bMap=dict(zip(varlist,arrStr))
    #print(bMap)
    exprValue = getExprValue(formulaStr, bMap)
    val = str((c-exprValue)/2)
    #print(val)
    return eval(val)

def computeWSForLessThanOrEquals(formulaStr, arr,c, varlist):
    arrStr=[str(i) for i in arr]
   
    bMap=dict(zip(varlist,arrStr))
    #print(bMap)
    exprValue = getExprValue(formulaStr, bMap)
    val = str((c-exprValue)/2)  
    #print(val)
   
    finalVal = math.floor(eval(val))

    return finalVal

def computeWSForLessThan(formulaStr, arr,c, varlist):
    arrStr=[str(i) for i in arr]
   
    bMap=dict(zip(varlist,arrStr))
    exprValue = getExprValue(formulaStr, bMap)
    val = str((c-exprValue)/2)  
    #print(val)
    finalVal = math.ceil(eval(val))

    return finalVal

def computeWSForGreaterThanOrEquals(formulaStr, arr,c, varlist):
    arrStr=[str(i) for i in arr]
   
    bMap=dict(zip(varlist,arrStr))
    #print(bMap)
    exprValue = getExprValue(formulaStr, bMap)
    val = str((c-exprValue)/2)  
    #print(val)
   
    finalVal = math.floor(eval(val))

    return finalVal

def computeWSForGreaterThan(formulaStr, arr,c, varlist):
    arrStr=[str(i) for i in arr]
   
    bMap=dict(zip(varlist,arrStr))
    exprValue = getExprValue(formulaStr, bMap)
    val = str((c-exprValue)/2)  
    #print(val)
    finalVal = math.ceil(eval(val))

    return finalVal

def printStringFromList(arr,n):
    string=[]
    for i in range(0, len(arr)):
        string.append(arr[i])
    return string

def generateAllBinaryStrings(n, arr, i):
   
    if i == n:
        binaryStrings.append(printStringFromList(arr,n))
        return 
     
    # First assign "0" at ith position
    # and try for all other permutations
    # for remaining positions
    arr[i] = 0
    generateAllBinaryStrings(n, arr, i + 1)
 
    # And then assign "1" at ith position
    # and try for all other permutations
    # for remaining positions
    arr[i] = 1
    generateAllBinaryStrings(n, arr, i + 1)


def solveLessThanOrEquals(f2, f3, variables):
 response=dict()
 text=str(f2)
 fun = f2
 variables_count = text.count("x")
 pattern = "(\d+)?(\\*)?([a-z])(\d+)"
 varlist = []
 i=0  
 binaryStrings.clear()

 # Parse the variables  
 #map the correct variable to the correct value from input
 varPosMap={}
 v1 = findOccurrences(text,'x')
 for i in range(0, len(v1)):
      xString = 'x'+text[v1[i]+1]
      varPosMap[xString]=v1[i]
 #print(v1)
 vmap=dict(sorted(varPosMap.items(), key=lambda item: item[1]))
 

 #create the var value map
 varlist = vmap.keys()
 varValMap = dict(zip(varlist, variables))
 
 # state list selection based on number of variables
 arr = [None] * variables_count
 generateAllBinaryStrings(variables_count,arr,0)
 
 formulaStr=str(f2)+" <= "+str(f3)
 
 #the initial state is b. Add that to the set of states with I appended
 b=str(f3)
 states.add(b+'I')
 
 #Compute the transition table using the presburger
 c = Int(str(f3))
 transitions=[]
 prettyTransitions=[]
 wSum=set()
 allStates=[]
 initialStates=[]
 initialStates.append(str(f3).strip())
 finalStates=[]
 allStates.append('States')
 pattern = "(\d+)?([A-Z])*"
 
 m=0
 wSum=getStatesLessThanOrEquals(str(f2).strip(),c,binaryStrings,varlist)
 #print(wSum)
 while m < len(wSum):
  c = list(wSum)[m]
  prettyTransitions.append(str(c))
  for k in range(0,len(binaryStrings)):
    weighted_sum = computeWSForLessThanOrEquals(str(f2),binaryStrings[k],c, varlist)
    if weighted_sum == 0 :
           states.add(str(c))
           brr=[str(c),",".join(map(str, binaryStrings[k])),str(int(weighted_sum))]
           transitions.append(brr)
           prettyTransitions.append(str(int(weighted_sum)))
    else:
           states.add(int(weighted_sum))
           brr=[str(c),",".join(map(str, binaryStrings[k])),str(int(weighted_sum))]
           transitions.append(brr)
           prettyTransitions.append(str(int(weighted_sum)))
  m=m+1
 
 for n in range(0, len(binaryStrings)):
    allStates.append(",".join(map(str, binaryStrings[n])))
 t = PrettyTable(allStates)

 bStrings = len(binaryStrings)
 prettyTransitions=[]
 
 o=0
 #print(wSum)
 statesList = list(wSum)
 #print(statesList)
 for i in range(0, len(statesList)):
    if int(str(statesList[i])) >= 0:
       finalStates.append(str(statesList[i]))

 while o < len(transitions):
    prettyArray=[]
    state = transitions[o][0]
    if state in initialStates:
        if int(str(state)) >= 0:
            state = state + 'IF'
        else:
            state = state + 'I'
    if state in finalStates:
        state = state + 'F'

    prettyArray.append(state)
    for p in range(0,bStrings):
        prettyArray.append(transitions[o][2])
        o=o+1
    prettyTransitions.append(prettyArray)
 
 for q in range(0, len(prettyTransitions)):
     t.add_row(prettyTransitions[q])
 
 print(t)
  #evaluate the formula
 for i in range(1, 100):
    locals()['x{0}'.format(i)] = Int('x%d'%i)

 f = eval(formulaStr)
 output=formulaStr +" and "
 for i in varValMap.keys():
     output = output+i+"="+varValMap[i]+" "
 if evaulateExpr(formulaStr, varValMap):
    output = output + " is TRUE"
    print(output)
 else:
    output = output + " is FALSE"
    print(output)
 
 response["finalStates"]=set(finalStates)
 response["initialStates"]= set(initialStates)
 response["transitions"]= transitions
 response["prettytable"]=t
 response["variables"] =varlist
 response["values"]=variables
 response["count"]=variables_count
 response["binaryStrings"]=binaryStrings
 response["formula"]=formulaStr
 response["allStates"]=wSum
 response["evalExpr"]=evaulateExpr(formulaStr, varValMap)
 finalStates=[int(i) for i in finalStates]
 response["notStates"]=wSum.difference(set(finalStates))
 return response

def solveLessThan(f2, f3, variables):
 response=dict()        
 text=str(f2)
 fun = f2
 variables_count = text.count("x")
 pattern = "(\d+)?(\\*)?([a-z])(\d+)"
 varlist = []
 i=0  
 binaryStrings.clear()

 # Parse the variables  
 #map the correct variable to the correct value from input
 varPosMap={}
 v1 = findOccurrences(text,'x')
 for i in range(0, len(v1)):
      xString = 'x'+text[v1[i]+1]
      varPosMap[xString]=v1[i]
 #print(v1)
 vmap=dict(sorted(varPosMap.items(), key=lambda item: item[1]))
 
 #create the var value map
 varlist = vmap.keys()
 varValMap = dict(zip(varlist, variables))
 
 # state list selection based on number of variables
 arr = [None] * variables_count
 generateAllBinaryStrings(variables_count,arr,0)
 
 formulaStr=str(f2)+" < "+str(f3)
 print(formulaStr)

 #the initial state is b. Add that to the set of states with I appended
 b=str(f3)
 states.add(b+'I')
 
 #Compute the transition table using the presburger
 c = Int(str(f3))
 #print(c)
 transitions=[]
 prettyTransitions=[]
 wSum=set()
 allStates=[]
 initialStates=[]
 initialStates.append(str(f3).strip())
 finalStates=[]
 allStates.append('States')
 pattern = "(\d+)?([A-Z])*"
 #print(binaryStrings)

 m=0
 wSum=getStatesLessThan(str(f2),c,binaryStrings,varlist)
 #print("The size is: "+ str(wSum))

 while m < len(wSum):
  c = list(wSum)[m]
  prettyTransitions.append(str(c))
  for k in range(0,len(binaryStrings)):
    weighted_sum = computeWSForLessThan(str(f2),binaryStrings[k],c, varlist)
    if weighted_sum == 0 :
           states.add(str(c))
           brr=[str(c),",".join(map(str, binaryStrings[k])),str(int(weighted_sum))]
           transitions.append(brr)
           prettyTransitions.append(str(int(weighted_sum)))
    else:
           states.add(int(weighted_sum))
           brr=[str(c),",".join(map(str, binaryStrings[k])),str(int(weighted_sum))]
           transitions.append(brr)
           prettyTransitions.append(str(int(weighted_sum)))
  m=m+1
 
 for n in range(0, len(binaryStrings)):
    allStates.append(",".join(map(str, binaryStrings[n])))
 t = PrettyTable(allStates)

 bStrings = len(binaryStrings)
 prettyTransitions=[]
 
 o=0
 #print(wSum)
 statesList = list(wSum)
 #print(statesList)
 for i in range(0, len(statesList)):
    if int(str(statesList[i])) > 0:
       finalStates.append(str(statesList[i]))

 while o < len(transitions):
    prettyArray=[]
    state = transitions[o][0]
    if state in initialStates:
        if int(str(state)) > 0:
            state = state + 'IF'
        else:
            state = state + 'I'
    if state in finalStates:
        state = state + 'F'

    prettyArray.append(state)
    for p in range(0,bStrings):
        prettyArray.append(transitions[o][2])
        o=o+1
    prettyTransitions.append(prettyArray)
 
 for q in range(0, len(prettyTransitions)):
     t.add_row(prettyTransitions[q])
 
 print(t)
  #evaluate the formula
 for i in range(1, 100):
    locals()['x{0}'.format(i)] = Int('x%d'%i)

 f = eval(formulaStr)
 output=formulaStr +" and "
 for i in varValMap.keys():
     output = output+i+"="+varValMap[i]+" "
 if evaulateExpr(formulaStr, varValMap):
    output = output + " is TRUE"
    print(output)
 else:
    output = output + " is FALSE"
    print(output)
 response["finalStates"]=set(finalStates)
 response["initialStates"]= set(initialStates)
 response["transitions"]= transitions
 response["prettytable"]=t
 response["variables"] =varlist
 response["values"]=variables
 response["count"]=variables_count
 response["binaryStrings"]=binaryStrings
 response["formula"]=formulaStr
 response["allStates"]=wSum
 response["evalExpr"]=evaulateExpr(formulaStr, varValMap)
 finalStates=[int(i) for i in finalStates]
 response["notStates"]=wSum.difference(set(finalStates))
 return response     

def solveGreaterThanOrEquals(f2, f3, variables):
 response=dict()        
 text=str(f2)
 fun = f2
 variables_count = text.count("x")
 pattern = "(\d+)?(\\*)?([a-z])(\d+)"
 varlist = []
 i=0  
 binaryStrings.clear()

 # Parse the variables  
 #map the correct variable to the correct value from input
 varPosMap={}
 v1 = findOccurrences(text,'x')
 for i in range(0, len(v1)):
      xString = 'x'+text[v1[i]+1]
      varPosMap[xString]=v1[i]
 #print(v1)
 vmap=dict(sorted(varPosMap.items(), key=lambda item: item[1]))
 
 #create the var value map
 varlist = vmap.keys()
 varValMap = dict(zip(varlist, variables))
 
 # state list selection based on number of variables
 arr = [None] * variables_count
 generateAllBinaryStrings(variables_count,arr,0)
 
 formulaStr=str(f2)+" >= "+str(f3)
 print(formulaStr)

 #the initial state is b. Add that to the set of states with I appended
 b=str(f3)
 states.add(b+'I')
 
 #Compute the transition table using the presburger
 c = Int(str(f3))
 transitions=[]
 prettyTransitions=[]
 wSum=set()
 allStates=[]
 initialStates=[]
 initialStates.append(str(f3).strip())
 finalStates=[]
 allStates.append('States')
 pattern = "(\d+)?([A-Z])*"

 m=0
 wSum=getStatesGreaterThanOrEquals(str(f2),c,binaryStrings,varlist)
 while m < len(wSum):
  c = list(wSum)[m]
  prettyTransitions.append(str(c))
  for k in range(0,len(binaryStrings)):
    weighted_sum = computeWSForGreaterThanOrEquals(str(f2),binaryStrings[k],c, varlist)
    if weighted_sum == 0 :
           states.add(str(c).strip())
           brr=[str(c).strip(),",".join(map(str, binaryStrings[k])),str(int(weighted_sum)).strip()]
           transitions.append(brr)
           prettyTransitions.append(str(int(weighted_sum)))
    else:
           states.add(str(int(weighted_sum)).strip())
           brr=[str(c).strip(),",".join(map(str, binaryStrings[k])),str(int(weighted_sum)).strip()]
           transitions.append(brr)
           prettyTransitions.append(str(int(weighted_sum)))
  m=m+1
 
 for n in range(0, len(binaryStrings)):
    allStates.append(",".join(map(str, binaryStrings[n])))
 t = PrettyTable(allStates)

 bStrings = len(binaryStrings)
 prettyTransitions=[]
 
 o=0
 statesList = list(wSum)
 for i in range(0, len(statesList)):
    if int(str(statesList[i])) >= 0:
       finalStates.append(str(statesList[i]))
 
 finalStates = [int(i) for i in finalStates]
 finalStates = wSum.difference(set(finalStates))
 
 finalStatesStr = [str(i) for i in finalStates]
 while o < len(transitions):
    prettyArray=[]
    state = transitions[o][0]
    #print(state)
    if state in initialStates:
        if int(str(state)) >= 0:
            state = state + 'IF'
        else:
            state = state + 'I'
    if state in finalStatesStr:
        state = state + 'F'

    prettyArray.append(state)
    for p in range(0,bStrings):
        prettyArray.append(transitions[o][2])
        o=o+1
    prettyTransitions.append(prettyArray)
 
 for q in range(0, len(prettyTransitions)):
     t.add_row(prettyTransitions[q])
 
 print(t)
  #evaluate the formula
 for i in range(1, 100):
    locals()['x{0}'.format(i)] = Int('x%d'%i)

 f = eval(formulaStr)
 output=formulaStr +" and "
 for i in varValMap.keys():
     output = output+i+"="+varValMap[i]+" "
 x=bool('False')
 if evaulateExpr(formulaStr, varValMap):
    output = output + " is TRUE"
    x=bool('True')
    print(output)
 else:
    output = output + " is FALSE"
    print(output)
 response["finalStates"]=finalStates
 response["initialStates"]= set(initialStates)
 response["transitions"]= transitions
 response["prettytable"]=t
 response["variables"] =varlist
 response["values"]=variables
 response["count"]=variables_count
 response["binaryStrings"]=binaryStrings
 response["formula"]=formulaStr
 response["allStates"]=wSum
 response["evalExpr"]=x
 response["notStates"]=wSum.difference(finalStates)
 #print(response)
 return response       
   
def solveGreaterThan(f2, f3, variables):        
 response=dict()
 text=str(f2)
 fun = f2
 variables_count = text.count("x")
 pattern = "(\d+)?(\\*)?([a-z])(\d+)"
 varlist = []
 i=0  
 binaryStrings.clear()

 # Parse the variables  
 #map the correct variable to the correct value from input
 varPosMap={}
 v1 = findOccurrences(text,'x')
 for i in range(0, len(v1)):
      xString = 'x'+text[v1[i]+1]
      varPosMap[xString]=v1[i]
 #print(v1)
 vmap=dict(sorted(varPosMap.items(), key=lambda item: item[1]))
 
 #create the var value map
 varlist = vmap.keys()
 varValMap = dict(zip(varlist, variables))
 
 # state list selection based on number of variables
 arr = [None] * variables_count
 generateAllBinaryStrings(variables_count,arr,0)
 
 formulaStr=str(f2)+" >"+str(f3)
 
 #the initial state is b. Add that to the set of states with I appended
 b=str(f3)
 states.add(b+'I')
 
 #Compute the transition table using the presburger
 c = Int(str(f3))
 transitions=[]
 prettyTransitions=[]
 wSum=set()
 allStates=[]
 initialStates=[]
 initialStates.append(str(f3).strip())
 finalStates=[]
 allStates.append('States')
 pattern = "(\d+)?([A-Z])*"
 
 m=0
 wSum=getStatesGreaterThan(str(f2),c,binaryStrings,varlist)
 while m < len(wSum):
  c = list(wSum)[m]
  prettyTransitions.append(str(c))
  for k in range(0,len(binaryStrings)):
    weighted_sum = computeWSForGreaterThan(str(f2),binaryStrings[k],c, varlist)
    if weighted_sum == 0 :
           states.add(str(c))
           brr=[str(c),",".join(map(str, binaryStrings[k])),str(int(weighted_sum))]
           transitions.append(brr)
           prettyTransitions.append(str(int(weighted_sum)))
    else:
           states.add(int(weighted_sum))
           brr=[str(c),",".join(map(str, binaryStrings[k])),str(int(weighted_sum))]
           transitions.append(brr)
           prettyTransitions.append(str(int(weighted_sum)))
  m=m+1

 print(formulaStr)
 
 for n in range(0, len(binaryStrings)):
    allStates.append(",".join(map(str, binaryStrings[n])))
 t = PrettyTable(allStates)

 bStrings = len(binaryStrings)
 prettyTransitions=[]
 
 o=0
 statesList = list(wSum)
 for i in range(0, len(statesList)):
    if int(str(statesList[i])) > 0:
       finalStates.append(int(str(statesList[i])))
 
 finalStates = wSum.difference(set(finalStates))
 
 finalStatesStr=[str(i) for i in finalStates]
 while o < len(transitions):
    prettyArray=[]
    state = transitions[o][0]
    if state in initialStates:
        if int(str(state)) > 0:
            finalStatesStr.append(state)
            state = state + 'IF'
        else:
            state = state + 'I'
    if state in finalStatesStr:
        state = state + 'F'

    prettyArray.append(state)
    for p in range(0,bStrings):
        prettyArray.append(transitions[o][2])
        o=o+1
    prettyTransitions.append(prettyArray)
 
 for q in range(0, len(prettyTransitions)):
     t.add_row(prettyTransitions[q])
 
 print(t)
  #evaluate the formula
 for i in range(1, 100):
    locals()['x{0}'.format(i)] = Int('x%d'%i)

 f = eval(formulaStr)
 output=formulaStr +" and "
 for i in varValMap.keys():
     output = output+i+"="+varValMap[i]+" "
 if evaulateExpr(formulaStr, varValMap):
    output = output + " is TRUE"
    print(output)
 else:
    output = output + " is FALSE"
    print(output)
 
 response["finalStates"]=set(finalStatesStr)
 response["initialStates"]= set(initialStates)
 response["transitions"]= transitions
 response["prettytable"]=t
 response["variables"] =varlist
 response["values"]=variables
 response["count"]=variables_count
 response["binaryStrings"]=binaryStrings
 response["formula"]=formulaStr
 response["allStates"]=wSum
 response["evalExpr"]=evaulateExpr(formulaStr, varValMap)
 response["notStates"]=wSum.difference(finalStates)

 return response             
  

def Diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

def solveAnd(input1,input2, vars):
  binaryStrings.clear() 
  response1=dict()
  response2 =dict()
  result=[]
  first = str(input1.decl())
  #print(first)
  if first == "Not":
     response1 = solveNot(input1.arg(0), vars,result)
  else:
     f2 = input1.arg(0)
     f3 = input1.arg(1)
     if first == ">=":
           response1 = solveGreaterThanOrEquals(f2, f3, vars)
     elif first == "<=":
           response1= solveLessThanOrEquals(f2, f3, vars)
     elif first == "<":
           response1= solveLessThan(f2, f3, vars)
     elif first == ">":
           response1= solveGreaterThan(f2, f3, vars)    
     else:
           response1= solveEquals(f2, f3, vars)
 
  
  second = str(input2.decl())
  #print(second)
  #print(input2)
  if second == "Not":
     response2 = solveNot(input2.arg(0), vars,result)
  else:
     f4 = input2.arg(0)
     f5 = input2.arg(1)
    
     if second == "=":
           response2 = solveGreaterThanOrEquals(f4, f5, vars)
     elif second == "<=":
           response2= solveLessThanOrEquals(f4, f5, vars)
     elif second == "<":
           response2= solveLessThan(f4, f5, vars)
     elif second == ">":
           response2= solveGreaterThan(f4, f5, vars)    
     else:
           response2= solveEquals(f4, f5, vars)
  
  response = subAnd(response1, response2, vars)
  return response


def solveOr(input1,input2, vars):
  binaryStrings.clear() 
  response1=dict()
  response2 =dict()
  result=[]
  first = str(input1.decl())
  #print(first)
  if first == "Not":
     response1 = solveNot(input1.arg(0), vars,result)
  else:
     f2 = input1.arg(0)
     f3 = input1.arg(1)
     if first == ">=":
           response1 = solveGreaterThanOrEquals(f2, f3, vars)
     elif first == "<=":
           response1= solveLessThanOrEquals(f2, f3, vars)
     elif first == "<":
           response1= solveLessThan(f2, f3, vars)
     elif first == ">":
           response1= solveGreaterThan(f2, f3, vars)    
     else:
           response1= solveEquals(f2, f3, vars)
 
  
  second = str(input2.decl())
  #print(second)
  #print(input2)
  if second == "Not":
     response2 = solveNot(input2.arg(0), vars,result)
  else:
     f4 = input2.arg(0)
     f5 = input2.arg(1)
    
     if second == "=":
           response2 = solveGreaterThanOrEquals(f4, f5, vars)
     elif second == "<=":
           response2= solveLessThanOrEquals(f4, f5, vars)
     elif second == "<":
           response2= solveLessThan(f4, f5, vars)
     elif second == ">":
           response2= solveGreaterThan(f4, f5, vars)    
     else:
           response2= solveEquals(f4, f5, vars)
  
  response = subOr(response1, response2, vars)
  return response

def findOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

def solveNot(input, vars, result):
   
  response=[]
  if len(result) > 0:
      response = result
  else:
      for i in range(1, 100):
        locals()['x{0}'.format(i)] = Int('x%d'%i)

      f = eval(str(input))

      f1 = input.decl().name()
      num = input.num_args()
      if num == 1:
               f2 = input.arg(0)
      else:
               f2 = input.arg(0)
               f3 = input.arg(1)

      if f1 == "==":
               response = solveEquals(f2, f3, vars)
      if f1 == "not":
               response = solveNot(f2, vars,result)
      elif f1 == "<=":
               response= solveLessThanOrEquals(f2, f3, vars)
      elif f1 == "<":
               response= solveLessThan(f2, f3, vars)
      elif f1 == ">":
               response= solveGreaterThan(f2, f3, vars)    
      else:
               response= solveGreaterThanOrEquals(f2, f3, vars)

  bStates=[]
  bStates.append("States")
  allStates = (response.get("allStates"))
  finalStates = response.get("finalStates")
  negation=response.get("notStates")
  binaryStrings = response.get("binaryStrings")
  transitions = response.get("transitions")
  variables = response.get("variables")
  values = response.get("values")
  formula = response.get("formula")
  initialStates = response.get("initialStates")
  #print(negation)
  formulaStr = "not("+formula+")"
  print(formulaStr)
  
  variables_count = formula.count("x")
  varlist = []
  i=0  

  # Parse the variables  
  #map the correct variable to the correct value from input
  varPosMap={}
  v1 = findOccurrences(str(formula),'x')
  for i in range(0, len(v1)):
      xString = 'x'+(str(formula))[v1[i]+1]
      varPosMap[xString]=v1[i]
  #print(v1)
  vmap=dict(sorted(varPosMap.items(), key=lambda item: item[1]))
 
  #create the var value map
  varlist = vmap.keys()
  varValMap = dict(zip(varlist, vars))
 
  for n in range(0, len(binaryStrings)):
    bStates.append(",".join(map(str, binaryStrings[n])))
  t = PrettyTable(bStates)

  bStrings = len(binaryStrings)
  prettyTransitions=[]
 
  fStates = set()
  iStates = set()
  negation = [str(i) for i in negation]
  o=0
  while o < len(transitions):
    prettyArray=[]
    state = transitions[o][0]
    stateStr=transitions[o][0]
    #print(state)
    if state in initialStates:
        iStates.add(state)
        stateStr = state + 'I'
        
    if state in negation:
        fStates.add(state)
        stateStr = state + 'F'
        
    if state in negation and state in initialStates:
        stateStr = state+"IF"
        
    prettyArray.append(stateStr)
    for p in range(0,bStrings):
        prettyArray.append(transitions[o][2])
        o=o+1
    prettyTransitions.append(prettyArray)
 
  for q in range(0, len(prettyTransitions)):
     t.add_row(prettyTransitions[q])
 
  print(t)
  #evaluate the formula
  for i in range(1, len(variables)+1):
    locals()['x{0}'.format(i)] = Int('x%d'%i)

  output=formulaStr +" and "
  for i in varValMap.keys():
     output = output+i+"="+varValMap[i]+" "
     
  x=bool('False')
  if evaulateExprForNot(formulaStr, varValMap):
        output = output + " is TRUE"
        x=bool('True')
  else:
        output = output + " is FALSE"
  print(output)  

  finalStates = set([int(i) for i in finalStates])
  response["finalStates"]=allStates.difference(finalStates)
  response["initialStates"]= iStates
  response["transitions"]= transitions
  response["prettytable"]=t
  response["count"]=len(vars)
  response["binaryStrings"]=binaryStrings
  response["formula"]=formulaStr
  response["allStates"]=states
  response["evalExpr"]=x
  response["notStates"]=set(states).difference(fStates)
  response["variables"] = variables
  response["values"]=values
  response["notStates"]=finalStates
  response["allStates"]=allStates
  #print(response)
  return response  

def subAnd(responseOne, responseTwo, vars):
    response=dict()
    statesOne = responseOne.get("allStates")
    statesTwo = responseTwo.get("allStates")
    transitionsOne = responseOne.get("transitions")
    transitionsTwo = responseTwo.get("transitions")
    formulaOne = responseOne.get("formula")
    formulaTwo = responseTwo.get("formula")
    finalStatesOne = responseOne.get("finalStates")
    finalStatesTwo = responseTwo.get("finalStates")
    initialStatesOne = responseOne.get("initialStates")
    initialStatesTwo = responseTwo.get("initialStates")
    varCountOne=formulaOne.count('x')
    varCountTwo=formulaTwo.count('x')
    evalExprOne = responseOne.get("evalExpr")
    evalExprTwo = responseTwo.get("evalExpr")
    transitions=[]
   
    variablesOne=set()
    binaryStrings.clear()

    totalStates = set()
    #map the correct variable to the correct value from input
    varPosMapOne={}
    v1 = findOccurrences(formulaOne,'x')
    v2 = findOccurrences(formulaTwo,'x')
   
    for i in range(0, len(v1)):
      xString = 'x'+formulaOne[v1[i]+1]
      varPosMapOne[xString]=v1[i]
    vmapOne=dict(sorted(varPosMapOne.items(), key=lambda item: item[1]))
   
    #create the var value map
    varListOne = set(vmapOne.keys())
    #map the correct variable to the correct value from input
    varPosMapTwo={}
    for i in range(0, len(v2)):
      xString = 'x'+formulaTwo[v2[i]+1]
      varPosMapTwo[xString]=v2[i]
   
    vmapTwo=dict(sorted(varPosMapTwo.items(), key=lambda item: item[1]))

    #create the var value map
    varListTwo= set(vmapTwo.keys())
    
    #pick the larger binary string as the alphabet
    finalAlphabetLength=0
    if len(varListOne) >= len(varListTwo):
       finalAlphabet = len(varListOne)
    else:
       finalAlphabet = len(varListTwo)

    arrFinal = [None] * finalAlphabet
    generateAllBinaryStrings(finalAlphabet,arrFinal,0)
   
    bStrings=[]
    for n in range(0, len(binaryStrings)):
         bStrings.append(",".join(map(str, binaryStrings[n])))

    bStrings=[str(i) for i in bStrings]
    
    if len(varListOne) > len(varListTwo):
       firstAutomaton = transitionsOne
       secondAutomaton = transitionsTwo
       firstStates = statesOne
       secondStates = statesTwo
       f1varlen = len(varListOne)
       f2varlen = len(varListTwo)
       initialStatesOne = initialStatesOne
       initialStatesTwo = initialStatesTwo
       finalStatesOne  = finalStatesOne
       finalStatesTwo = finalStatesTwo
    else: 
       firstAutomaton = transitionsTwo
       secondAutomaton = transitionsOne
       firstStates = statesTwo
       secondStates = statesOne
       f1varlen = len(varListTwo)
       f2varlen = len(varListOne)
       initialStatesOne = initialStatesTwo
       initialStatesTwo = initialStatesOne
       finalStatesOne  = finalStatesTwo
       finalStatesTwo = finalStatesOne
    
    
    states = set()
    states=computeAllStates(firstStates,secondStates)
   
    #morph transitions
    mt1 = morphTransitions(firstAutomaton, firstStates)
    mt2 = morphTransitions(secondAutomaton, secondStates)
    
    #print formula
    print("And("+formulaOne+","+formulaTwo+")")
    ftStates = []
    ftStates.append("States")
    for n in range(0, len(binaryStrings)):
         ftStates.append(",".join(map(str, binaryStrings[n])))

    states = list(states)
    tab = PrettyTable(ftStates)   
    
    fStates=set()
    iStates=set()
    transitions=[]
    for i in range(0, len(states)):
        st = states[i]
        s = st.split(",")
        t1 =mt1[int(s[0])]
        t2 =mt2[int(s[1])]
        result=[]
        tresult =[]
        stateStr = "<"+st+">"
         #For And the final states are only those which are final in both
        if s[0] in initialStatesOne and s[1] in initialStatesTwo:
           stateStr = stateStr + "I"
           iStates.add(st)
         
        if s[0] in finalStatesOne and s[1] in finalStatesTwo:
           stateStr = stateStr + "F"
           fStates.add(st)
         
        result.append(stateStr)
        output = computeStatesForAndOr(s[0],s[1],t1,t2,bStrings, f1varlen,f2varlen)
        for p in range(0, len(output)):
            result.append("<"+output[p]+">")
        tab.add_row(result)
 
        brr = []
    
        for i in range(0,len(bStrings)):
            brr.append([st,bStrings[i], result[i+1]]) 
            transitions.append(brr)
    
    print(tab)
    x = bool('False')
    if evalExprOne and evalExprTwo:
        ans = "And("+formulaOne+","+formulaTwo+")" + " is TRUE"
        x = bool('True')
    else:
        ans = "And("+formulaOne+","+formulaTwo+")" + " is FALSE"
    print(ans) 


    response["finalStates"]=fStates
    response["initialStates"]= iStates
    response["transitions"]= transitions
    response["prettytable"]=tab
    response["count"]=len(vars)
    response["binaryStrings"]=binaryStrings
    response["formula"]="And("+formulaOne+","+formulaTwo+")"
    response["allStates"]=states
    response["evalExpr"]=x
    response["notStates"]=set(states).difference(fStates)

    #print(response)
    return response

def computeStatesForAndOr(startStateOne, startstateTwo, transition1, transition2, bStrings, f1varlen, f2varlen):
    state=[]
    t1= morphtransitionsBtoF(transition1)
    t2 = morphtransitionsBtoF(transition2)
   
    for i in range(0,len(bStrings)):
        s = bStrings[i].replace(",","")
        first = s[0:f1varlen]
        second = s[0:f2varlen]
        state.append(t1[first] + ","+t2[second])

    return state

def subOr(responseOne, responseTwo, vars):
    response=dict()
    statesOne = responseOne.get("allStates")
    statesTwo = responseTwo.get("allStates")
    transitionsOne = responseOne.get("transitions")
    transitionsTwo = responseTwo.get("transitions")
    formulaOne = responseOne.get("formula")
    formulaTwo = responseTwo.get("formula")
    finalStatesOne = responseOne.get("finalStates")
    finalStatesTwo = responseTwo.get("finalStates")
    initialStatesOne = responseOne.get("initialStates")
    initialStatesTwo = responseTwo.get("initialStates")
    varCountOne=formulaOne.count('x')
    varCountTwo=formulaTwo.count('x')
    evalExprOne = responseOne.get("evalExpr")
    evalExprTwo = responseTwo.get("evalExpr")
    transitions=[]
   
    variablesOne=set()
    binaryStrings.clear()

    totalStates = set()
    #map the correct variable to the correct value from input
    varPosMapOne={}
    v1 = findOccurrences(formulaOne,'x')
    v2 = findOccurrences(formulaTwo,'x')
   
    for i in range(0, len(v1)):
      xString = 'x'+formulaOne[v1[i]+1]
      varPosMapOne[xString]=v1[i]
    vmapOne=dict(sorted(varPosMapOne.items(), key=lambda item: item[1]))
   
    #create the var value map
    varListOne = set(vmapOne.keys())
    #map the correct variable to the correct value from input
    varPosMapTwo={}
    for i in range(0, len(v2)):
      xString = 'x'+formulaTwo[v2[i]+1]
      varPosMapTwo[xString]=v2[i]
   
    vmapTwo=dict(sorted(varPosMapTwo.items(), key=lambda item: item[1]))

    #create the var value map
    varListTwo= set(vmapTwo.keys())
    
    #pick the larger binary string as the alphabet
    finalAlphabetLength=0
    if len(varListOne) >= len(varListTwo):
       finalAlphabet = len(varListOne)
    else:
       finalAlphabet = len(varListTwo)

    arrFinal = [None] * finalAlphabet
    generateAllBinaryStrings(finalAlphabet,arrFinal,0)
   
    bStrings=[]
    for n in range(0, len(binaryStrings)):
         bStrings.append(",".join(map(str, binaryStrings[n])))

    bStrings=[str(i) for i in bStrings]
    
    if len(varListOne) > len(varListTwo):
       firstAutomaton = transitionsOne
       secondAutomaton = transitionsTwo
       firstStates = statesOne
       secondStates = statesTwo
       f1varlen = len(varListOne)
       f2varlen = len(varListTwo)
       initialStatesOne = initialStatesOne
       initialStatesTwo = initialStatesTwo
       finalStatesOne  = finalStatesOne
       finalStatesTwo = finalStatesTwo
    else: 
       firstAutomaton = transitionsTwo
       secondAutomaton = transitionsOne
       firstStates = statesTwo
       secondStates = statesOne
       f1varlen = len(varListTwo)
       f2varlen = len(varListOne)
       initialStatesOne = initialStatesTwo
       initialStatesTwo = initialStatesOne
       finalStatesOne  = finalStatesTwo
       finalStatesTwo = finalStatesOne
    
    
    states = set()
    states=computeAllStates(firstStates,secondStates)
   
    #morph transitions
    mt1 = morphTransitions(firstAutomaton, firstStates)
    mt2 = morphTransitions(secondAutomaton, secondStates)
    
    #print formula
    print("And("+formulaOne+","+formulaTwo+")")
    ftStates = []
    ftStates.append("States")
    for n in range(0, len(binaryStrings)):
         ftStates.append(",".join(map(str, binaryStrings[n])))

    states = list(states)
    tab = PrettyTable(ftStates)   
    
    fStates=set()
    iStates=set()
    transitions=[]
    for i in range(0, len(states)):
        st = states[i]
        s = st.split(",")
        t1 =mt1[int(s[0])]
        t2 =mt2[int(s[1])]
        result=[]
        tresult =[]
        stateStr = "<"+st+">"
         #For And the final states are only those which are final in both
        if s[0] in initialStatesOne or s[1] in initialStatesTwo:
           stateStr = stateStr + "I"
           iStates.add(st)
         
        if s[0] in finalStatesOne or s[1] in finalStatesTwo:
           stateStr = stateStr + "F"
           fStates.add(st)
         
        result.append(stateStr)
        output = computeStatesForAndOr(s[0],s[1],t1,t2,bStrings, f1varlen,f2varlen)
        for p in range(0, len(output)):
            result.append("<"+output[p]+">")
        tab.add_row(result)
 
        brr = []
    
        for i in range(0,len(bStrings)):
            brr.append([st,bStrings[i], result[i+1]]) 
            transitions.append(brr)
    
    print(tab)
    x = bool('False')
    if evalExprOne and evalExprTwo:
        ans = "And("+formulaOne+","+formulaTwo+")" + " is TRUE"
        x = bool('True')
    else:
        ans = "And("+formulaOne+","+formulaTwo+")" + " is FALSE"
    print(ans) 


    response["finalStates"]=fStates
    response["initialStates"]= iStates
    response["transitions"]= transitions
    response["prettytable"]=tab
    response["count"]=len(vars)
    response["binaryStrings"]=binaryStrings
    response["formula"]="And("+formulaOne+","+formulaTwo+")"
    response["allStates"]=states
    response["evalExpr"]=x
    response["notStates"]=set(states).difference(fStates)

    #print(response)
    return response
 

def computeAllStates(statesOne, statesTwo):
    states=set()
    for i in statesOne:
        for j in statesTwo:
            states.add(str(i).strip()+","+str(j).strip())
    return states

def morphtransitionsBtoF(transitions):
    t =dict()

    for i in range(0, len(transitions)):
        p = transitions[i]
        t[p[0].replace(",","")] = p[1]
    return t

def morphTransitions(transitions, states):
    mt =dict()
      
    for m in states:
      fArr=[]
      for i in range(0,len(transitions)):
        arr=[]  
        p=transitions[i]
        if int(p[0])==m:
           arr=[p[1], p[2]]
           fArr.append(arr)
      mt[m]=fArr

    return mt

def computeTransitions(transitionsOne, transitionsTwo, binaryString):
    response=dict()
    x=0
    y=0
    combinedStates=[]
    while x < len(transitionsOne):
        arr=[]
        rowOne = transitionsOne[x]
        arr.append(rowOne[0])
        while y < len(transitionsTwo):
          rowTwo = transitionsTwo[y]
          arr.append(rowTwo[0])       
          combinedStates.append(arr)
    print(combinedStates)
    return response

if __name__ == "__main__":
    main(sys.argv[1])  
