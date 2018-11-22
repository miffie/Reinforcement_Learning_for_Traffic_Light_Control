import numpy as np

from RL_brain import DeepQNetwork
#from cnn_brain import DeepQNetwork
import argparse
import matplotlib.pyplot as plt
import pickle
import gzip
import time
import tkinter as tk
from env import crossing
from visual import Visual
np.set_printoptions(threshold=np.inf)

#print(env.observation_space.shape[0])
parser = argparse.ArgumentParser(description='Train or test neural net motor controller.')
parser.add_argument('--train', dest='train', action='store_true', default=False)
parser.add_argument('--test', dest='test', action='store_true', default=True)
args = parser.parse_args()



grid_x=4
grid_y=1

RL = DeepQNetwork(n_actions=2,
                  #n_features=env.observation_space.shape[0],
                  n_features=5, #2*5
                #   learning_rate=0.01, 
                  e_greedy=0.9,
                  replace_target_iter=100, memory_size=2000,
                  e_greedy_increment=0.001,)


# window = tk.Tk()
# window.title('my window')
# window.geometry('1000x1000')
# canvas = tk.Canvas(window, bg='white', height=1000, width=1000)

x=[]
y=[]
for i in range(grid_x):
    x.append(i+1)
for i in range(grid_y):
    y.append(i+1)

times=100
bias=6
bias_t=20
bias_=40
b=2
q_states=[[([1] * 4) for i in range(grid_y+1)]for j in range(grid_x+1)]
#print(q_states)
for xx in x:
    for yy in y:
        #q_states is the inner/peripheral property of crossroads
        if xx==1:
            q_states[xx][yy][2]=0 #0 for peripherial road, 1 for inner road
        if xx==grid_x:
            q_states[xx][yy][3]=0
        if yy==1:
            q_states[xx][yy][0]=0
        if yy==grid_y:
            q_states[xx][yy][1]=0
       

light_states=[[0 for i in range(grid_y+1)]for j in range(grid_x+1)]
# print(light_states)
def int2bin(n, count=24):  #10 -> binary
    """returns the binary of integer n, using count number of digits"""
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])

def crossroads_map(x,y):
    cross={}  #dictionary of crossroads
    for xx in x:
        for yy in y:
            lab=str(xx)+str(yy)
            cross_=crossing(car_nums=np.array([0,0,0,0]),light_state=0,q_states=q_states[xx][yy])
            cross[lab]=cross_
    return cross  
            # cross[]={''}



# cross1=crossing(light_state=0,q_states=[0,0,0,1])
# cross2=crossing(light_state=0,q_states=[0,0,1,0])


step_set=[]
reward_set=[]
# def flatten(a):
#     for each in a:
#         if not isinstance(each, Iterable) or isinstance(each, str):
#             yield each
#         else:
#             yield from flatten(each)
    



if args.train:
    cross=crossroads_map(x,y)
    visual=Visual()
    obs=[]
    for xx in x:
        for yy in y:
            lab=str(xx)+str(yy)
            obs.append(np.concatenate((cross[lab].car_nums,cross[lab].light_state),axis=None))
            # obs=np.array(obs).reshape(-1)
            # cross[lab]=crossing(light_state=0,q_states=q_states[xx][yy])
    # flatten(obs)
    # print('obs',obs[2])
    learning_rate=0.01
    for steps in range(10000000):
        # for xx in x:
        #     for yy in y:
        #         lab=str(xx)+str(yy)
                # print('before: ',lab,cross[lab].car_nums)
        # visual.visual_before(cross,x,y,times,b,bias,bias_t)
        action_set=[[0 for i in range(grid_y+1)]for j in range(grid_x+1)]
        peri_cars=[[([0] * 4) for i in range(grid_y+1)]for j in range(grid_x+1)]
        in_cars=[[([0] * 4) for i in range(grid_y+1)]for j in range(grid_x+1)]
        #light state changes, cars numbers change, interactions between crossroads and peripherals
        for xx in x:
            for yy in y:
                lab=str(xx)+str(yy)
                action_set[xx][yy]=RL.choose_action(obs[(xx-1)*grid_y+yy-1])
                peri_cars[xx][yy], in_cars[xx][yy]=cross[lab].state_change(action_set[xx][yy])           
        
        

        #interactions among crossroads        
        for xx in x:
            for yy in y:
                lab=str(xx)+str(yy)
                if cross[lab].q_states[0]==1:
                    if yy-1>0 and in_cars[xx][yy-1][0]>0:
                        cross_=cross[lab]
                        cross_.car_nums[0]+=in_cars[xx][yy-1][0]
                        cross[lab]=cross_
                        # print('!!!!!!!!!')
                        # cross[lab].car_nums[0]+=in_cars[xx][yy-1][0]
                if cross[lab].q_states[1]==1:
                    if yy+1<=grid_y and  in_cars[xx][yy+1][1]>0:
                        cross_=cross[lab]
                        cross_.car_nums[1]+=in_cars[xx][yy+1][1]
                        cross[lab]=cross_
                        # print('!!!!!!!!!')
                        # cross[lab].car_nums[1]+=in_cars[xx][yy+1][1]
                if cross[lab].q_states[2]==1:
                    if xx-1>0 and  in_cars[xx-1][yy][2]>0:
                        cross_=cross[lab]
                        cross_.car_nums[2]+=in_cars[xx-1][yy][2]
                        cross[lab]=cross_
                        # cross[lab].car_nums[2]+=in_cars[xx-1][yy][2]
                if cross[lab].q_states[3]==1:
                    if xx+1<=grid_x and  in_cars[xx+1][yy][3]>0:
                        cross_=cross[lab]
                        cross_.car_nums[3]+=in_cars[xx+1][yy][3]
                        cross[lab]=cross_
                        # cross[lab].car_nums[3]+=in_cars[xx+1][yy][3]
                # print(lab,cross[lab].car_nums)
        
        # visual.visual_peri(peri_cars,x,y,times,b,bias,bias_,bias_t,grid_x,grid_y)

        reward=0
        
        for xx in x:
            for yy in y:
                lab=str(xx)+str(yy)
                for i in range (4): 
                    reward = reward - cross[lab].car_nums[i]**2 - cross[lab].car_nums[i]**2
                # print(lab,cross[lab].car_nums)
        # visual.visual_after(cross,x,y,times,b,bias,bias_t)
        # time.sleep(10)
        obs_=[]
        for xx in x:
            for yy in y:
                lab=str(xx)+str(yy)
                obs_.append(np.concatenate((cross[lab].car_nums,cross[lab].light_state),axis=None))
                # obs_=np.concatenate((obs_, cross[lab].car_nums, cross[lab].light_state), axis=None)
                RL.store_transition(obs[(xx-1)*grid_y+yy-1],action_set[xx][yy],reward,obs_[(xx-1)*grid_y+yy-1])
        if steps%1000000==0:
            learning_rate = learning_rate*0.5
            print('lr: ', learning_rate)
        
        if steps>200:
            RL.learn(learning_rate)
        if steps%50==0:
            print(steps,reward)
        if steps%100==0:
            plt.plot(step_set,reward_set)
            plt.savefig('train2.png')
        if steps%1000==0:
            RL.store()
        reward_set.append(reward)
        step_set.append(steps)
        #plt.scatter(steps, reward)
        obs=obs_
        
    # window.mainloop()
    plt.plot(step_set,reward_set)
    plt.savefig('train2.png')
    RL.store()
    plt.show()
    #RL.plot_cost()
if args.test:
    RL.test_set()
    cross=crossroads_map(x,y)
    # visual=Visual()
    obs=[]
    Q1_set=[]
    Q2_set=[]
    Q3_set=[]
    Q4_set=[]
    step_set=[]
    reward_set=[]
    for xx in x:
        for yy in y:
            lab=str(xx)+str(yy)
            obs.append(np.concatenate((cross[lab].car_nums,cross[lab].light_state),axis=None))

    RL.restore()
    for steps in range(1000):
        for xx in x:
            for yy in y:
                lab=str(xx)+str(yy)
                # print('before: ',lab,cross[lab].car_nums)
        # visual.visual_before(cross,x,y,times,b,bias,bias_t)

        # action=RL.choose_action(obs)
        action_set=[[0 for i in range(grid_y+1)]for j in range(grid_x+1)]
        peri_cars=[[([0] * 4) for i in range(grid_y+1)]for j in range(grid_x+1)]
        in_cars=[[([0] * 4) for i in range(grid_y+1)]for j in range(grid_x+1)]
        #light state changes, cars numbers change, interactions between crossroads and peripherals
        for xx in x:
            for yy in y:
                lab=str(xx)+str(yy)
                action_set[xx][yy]=RL.choose_action(obs[(xx-1)*grid_y+yy-1])
                peri_cars[xx][yy], in_cars[xx][yy]=cross[lab].state_change(action_set[xx][yy])     
        # for xx in x:
        #     for yy in y:
        #         lab=str(xx)+str(yy)
        #         action_set[xx][yy]=int(int2bin(action,grid_x*grid_y)[(xx-1)*grid_y+yy-1])
        #         # print('light state: ',lab, cross[lab].light_state)
        #         peri_cars[xx][yy], in_cars[xx][yy]=cross[lab].state_change(action_set[xx][yy])
 
        #interactions among crossroads 
        print(action_set)       
        for xx in x:
            for yy in y:
                lab=str(xx)+str(yy)
                
                if cross[lab].q_states[0]==1:
                    if yy-1>0 and in_cars[xx][yy-1][0]>0:
                        cross_=cross[lab]
                        cross_.car_nums[0]+=in_cars[xx][yy-1][0]
                        cross[lab]=cross_
                        # print('!!!!!!!!!')
                        # cross[lab].car_nums[0]+=in_cars[xx][yy-1][0]
                if cross[lab].q_states[1]==1:
                    if yy+1<=grid_y and  in_cars[xx][yy+1][1]>0:
                        cross_=cross[lab]
                        cross_.car_nums[1]+=in_cars[xx][yy+1][1]
                        cross[lab]=cross_
                        # print('!!!!!!!!!')
                        # cross[lab].car_nums[1]+=in_cars[xx][yy+1][1]
                if cross[lab].q_states[2]==1:
                    if xx-1>0 and  in_cars[xx-1][yy][2]>0:
                        cross_=cross[lab]
                        cross_.car_nums[2]+=in_cars[xx-1][yy][2]
                        cross[lab]=cross_
                        # cross[lab].car_nums[2]+=in_cars[xx-1][yy][2]
                if cross[lab].q_states[3]==1:
                    if xx+1<=grid_x and  in_cars[xx+1][yy][3]>0:
                        cross_=cross[lab]
                        cross_.car_nums[3]+=in_cars[xx+1][yy][3]
                        cross[lab]=cross_
                        # cross[lab].car_nums[3]+=in_cars[xx+1][yy][3]
                # print(lab,cross[lab].car_nums)
                if xx==1:
                    Q1_set.append(cross[lab].car_nums[2])
                elif xx==2:
                    Q2_set.append(cross[lab].car_nums[2])
                elif xx==3:
                    Q3_set.append(cross[lab].car_nums[2])
                elif xx==4:
                    Q4_set.append(cross[lab].car_nums[2])

        # visual.visual_peri(peri_cars,x,y,times,b,bias,bias_,bias_t,grid_x,grid_y)

        reward=0
        
        for xx in x:
            for yy in y:
                lab=str(xx)+str(yy)
                for i in range (4): 
                    reward = reward - cross[lab].car_nums[i]**2 - cross[lab].car_nums[i]**2
                # print(lab,cross[lab].car_nums)
        # visual.visual_after(cross,x,y,times,b,bias,bias_t)
        # time.sleep(10)
        obs_=[]
        for xx in x:
            for yy in y:
                lab=str(xx)+str(yy)
                obs_.append(np.concatenate((cross[lab].car_nums,cross[lab].light_state),axis=None))
       

        # if steps>200:
        #     RL.learn()
        if steps%50==0:
            print(steps,reward)
        if steps%100==0:
            plt.plot(step_set,reward_set)
            plt.savefig('test2.png')
        reward_set.append(reward)
        step_set.append(steps)
        #plt.scatter(steps, reward)
        obs=obs_
        
    # window.mainloop()
    # plt.plot(step_set,reward_set)
    plot_len=100
    ax1=plt.subplot(2,1,1)
    plt.sca(ax1)
    plt.plot(step_set[:plot_len],reward_set[:plot_len])
    # plt.xlabel('Steps',fontsize=15)
    plt.ylabel('-Loss',fontsize=15)


    ax2=plt.subplot(2,1,2)
    plt.sca(ax2)
    # print(car_num_set['22'][1])
    
    
    plt.plot(step_set[:plot_len], Q1_set[:plot_len],'--',label='X1')
    plt.plot(step_set[:plot_len], Q2_set[:plot_len],label='X2')
    plt.plot(step_set[:plot_len], Q3_set[:plot_len],label='X3')
    plt.plot(step_set[:plot_len], Q4_set[:plot_len],label='X4')
    plt.xlabel('Steps',fontsize=15)
    plt.ylabel('Cars Numbers',fontsize=15)
    # set legend
    leg = plt.legend(loc=4,prop={'size': 15})
    legfm = leg.get_frame()
    legfm.set_edgecolor('black') # set legend fame color
    legfm.set_linewidth(0.5)   # set legend fame linewidth

    plt.savefig('test.png')

    plt.show()

        
        
