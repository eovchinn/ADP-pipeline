import operator
import random
def qlearning():
	#1:up,2:down,3:left,4:right
	q={(1,1):-1,(1,2):0,(1,3):-1,(1,4):0,(2,1):-1,(2,2):0,(2,3):0,(2,4):0,(3,1):-1,(3,2):100,(3,3):0,(3,4):-1,(4,1):0,(4,2):0,(4,3):-1,(4,4):0,(5,1):0,(5,2):0,(5,3):0,(5,4):100,(6,1):-1,(6,2):-1,(6,3):-1,(6,4):-1,(7,1):0,(7,2):-1,(7,3):-1,(7,4):0,(8,1):0,(8,2):-1,(8,3):0,(8,4):0,(9,1):100,(9,2):-1,(9,3):0,(9,4):-1}
	
	reward={(3,2):0,(3,3):0,(5,1):0,(5,2):0,(5,3):0,(5,4):0,(9,1):0,(9,3):0}
	v_cnt={(3,2):0,(3,3):0,(5,1):0,(5,2):0,(5,3):0,(5,4):0,(9,1):0,(9,3):0}
	
	q_prev=copy(q)
	current_s=random.randint(1,9)
	#print current_s
	while not get_next_q(q,current_s,reward,v_cnt)[0]==-1:
		q=get_next_q(q,current_s,reward,v_cnt)[0]
		current_s=get_next_q(q,current_s,reward,v_cnt)[1]
		print get_next_q(q,current_s,reward,v_cnt)[2]
		reward=get_next_q(q,current_s,reward,v_cnt)[2]
		v_cnt=get_next_q(q,current_s,reward,v_cnt)[3]
	print calculate_e(reward,v_cnt)
	cnt=0
	while True:
		print cnt
		#do
		if check_stop(q,q_prev):
			cnt=cnt+1
			if cnt>10:
				break
		else:
			cnt=0
		reward={(3,2):0,(3,3):0,(5,1):0,(5,2):0,(5,3):0,(5,4):0,(9,1):0,(9,3):0}
		v_cnt={(3,2):0,(3,3):0,(5,1):0,(5,2):0,(5,3):0,(5,4):0,(9,1):0,(9,3):0}
		q_prev=copy(q)
		current_s=random.randint(1,9)
		print current_s
		while not get_next_q(q,current_s,reward,v_cnt)[0]==-1:
			q=get_next_q(q,current_s,reward,v_cnt)[0]
			current_s=get_next_q(q,current_s,reward,v_cnt)[1]
			reward=get_next_q(q,current_s,reward,v_cnt)[2]
			v_cnt=get_next_q(q,current_s,reward,v_cnt)[3]
		print calculate_e(reward,v_cnt)
		print sorted(q.iteritems(), key=operator.itemgetter(0))
	return q

def calculate_e(reward,v_cnt):
	e={}
	for e1 in reward:
		e[e1]=float(reward[e1]/v_cnt[e1])
	return e
	
def copy(dict):
	dict1={}
	for e in dict:
		dict1[e]=dict[e]
	return dict1
	
def random_move():
	r=random.random()
	j=0
	if r>=0 and r<0.25:
		j=1
	elif r>=0.25 and r<0.5:
		j=2
	elif r>=0.5 and r<0.75:
		j=3
	elif r>=0.75 and r<=1:
		j=4
	return j
	
def get_next_q(q,current_s,reward,v_cnt):
	r_value={(3,2):100,(3,3):0,(5,1):0,(5,2):0,(5,3):0,(5,4):100,(9,1):100,(9,3):0}
	if current_s==6:
		return (-1,-1)
	while True:
		j=random_move()
		j=get_actual_move(j,current_s,q)
		i=current_s
		next_s=current_s
		if q[(i,j)]!= -1:
			q[(i,j)]=get_immediate_r(q,(i,j))+0.9*max(get_possible(q,(i,j)))
			next_s=get_next_s(q,(i,j))
			if (i,j) in r_value:
				reward[(i,j)]=reward[(i,j)]+r_value[(i,j)]
				v_cnt[(i,j)]=v_cnt[(i,j)]+1
			break
		
	return (q,next_s,reward,v_cnt)
	
def get_actual_move(j,current_s,q):
	r=random.random()
	poss_m=[]
	for i in range(1,5):
		if i!=j:
			if q[(current_s,i)]!= -1:
				poss_m.append(i)
	poss_m_num=len(poss_m)
	prob=float(0.24/poss_m_num)		
	if r<=0.76:
		move=j
	else:
		for x in range(poss_m_num):
			if r>0.76+x*prob and r<=0.76+(x+1)*prob:
				move=poss_m[x]
	return move	

def get_immediate_r(q,(i,j)):
	next_s=get_next_s(q,(i,j))
	if next_s==6:
		return 100
	else:
		return 0
	
def check_stop(q,q_prev):
	flag=0
	for e1 in q:
		if q[e1]!=q_prev[e1]:
			#flag=1 not equal
			flag=1
			break
	if flag == 0:
		return True
	return False

def get_next_s(q,(i,j)):
	next_s=0
	if j==1:
		if not q[(i,j)]==-1:
			next_s=i-3
	elif j==2:
		if not q[(i,j)]==-1:
			next_s=i+3
	elif j==3:
		if not q[(i,j)]==-1:
			next_s=i-1
	elif j==4:
		if not q[(i,j)]==-1:
			next_s=i+1
	return next_s
	
def get_possible(q,(i,j)):
	next_s=get_next_s(q,(i,j))
	possible_q=[]
	for x in range(1,5):
		if not q[next_s,x]== -1:
			possible_q.append(q[next_s,x])
	return possible_q

def max(list):
	max=0
	for i in list:
		if i>max:
			max=i
	return max
	
if __name__== '__main__' :
	final_q=qlearning()
	print sorted(final_q.iteritems(), key=operator.itemgetter(0))
