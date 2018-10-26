import time

stuff = "GET"
starttime=time.time()

for i in range(10000):
 print(' ')


endtime=time.time()

timeelapsed = endtime - starttime

print("Time elapsed is:", timeelapsed,"seconds")
if(stuff=="GET"):
 print("Great success....")


print("STARTING TEST............\n")


testerlist=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,'BREAK',19,20,21,22,23,'BREAKMAX',24,25,26]



startpoint=0
endpoint=0
i=len(testerlist)
i=i-1
found=0
foundagain=0
besttimes=[]


while i !=-1:
 if testerlist[i] == 'BREAKMAX':
	startpoint = i-1
        found=1
        break
 i-=1



print(testerlist)

print('Startpoint',startpoint)


i=startpoint

if (found==1):
 while i !=-1:
   if (testerlist[i]=='BREAK' or testerlist[i]=='BREAKMAX'):
     foundagain=1
     break
   else:
    besttimes.append(testerlist[i])
   i-=1


print("Best times are:", besttimes)
 
        
  
   

