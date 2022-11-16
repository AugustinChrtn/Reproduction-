import numpy as np
import copy
import pygame
import seaborn as sns
import pandas as pd
import pickle
import time
import matplotlib.pyplot as plt


from Lopesworld import Lopes_State
from Lopes_no_stat import Lopes_nostat

from greedyMB import Epsilon_MB_Agent
from RmaxLP import RmaxLP_Agent
from Rmax import Rmax_Agent
from BEB import BEB_Agent
from BEBLP import BEBLP_Agent
from Representation import Graphique
from policy_Functions import value_iteration,get_optimal_policy,policy_evaluation


def play(environment, agent, trials=200, max_step=500, screen=0,photos=[10,20,50,100,199,300,499],accuracy=0.01,pas_VI=50):
    reward_per_episode = []
    step_number=[]
    policy_value_error=[]
    pol_updated=False
    val_iteration,_=value_iteration(environment,agent.gamma,accuracy)
    for trial in range(trials):
        if screen : take_picture(agent,trial,environment,photos) #Visualisation
        
        cumulative_reward, step, game_over= 0,0,False
        while not game_over :
            if type(environment).__name__ =='Lopes_nostat' and not pol_updated:
                if environment.changed :
                    pol_updated=True
                    val_iteration,_=value_iteration(environment,agent.gamma,accuracy)
            if agent.step_counter%pas_VI==0:
                policy_value_error.append(policy_evaluation(environment,get_optimal_policy(agent,environment,agent.gamma,accuracy),agent.gamma,accuracy)[environment.first_location]-val_iteration[environment.first_location]) 
            old_state = environment.current_location
            action = agent.choose_action() 
            reward , terminal = environment.make_step(action) #reward and if state is terminal
            new_state = environment.current_location            
            agent.learn(old_state, reward, new_state, action)                
            cumulative_reward += reward
            step += 1
            if terminal == True or step==max_step:
                game_over = True
                environment.current_location=environment.first_location
                step_number.append(agent.step_counter)
        reward_per_episode.append(cumulative_reward)
    return reward_per_episode,step_number,policy_value_error

def loading_environments():
    environments_parameters={}
    all_environments={}
    for number_world in range(1,21):
        transitions_lopes=np.load('Mondes/Transitions_Lopes_no_stat '+str(number_world)+'.npy',allow_pickle=True)
        transitions_lopes_i_variable=np.load('Mondes/Transitions_Lopes_'+str(number_world)+'.npy',allow_pickle=True)
        environments_parameters["Lopes_{0}".format(number_world)]={'transitions':transitions_lopes_i_variable}
        
        environments_parameters["Lopes_nostat_{0}".format(number_world)]={'transitions':transitions_lopes_i_variable,'transitions_no_stat':transitions_lopes}
        environments_parameters["Lopes_{0}".format(number_world)]={'transitions':transitions_lopes_i_variable}
        all_environments["Lopes_nostat_{0}".format(number_world)]=Lopes_nostat
        all_environments["Lopes_{0}".format(number_world)]=Lopes_State
    return all_environments,environments_parameters

### PICTURES ###

def take_picture(agent,trial,environment,photos):
            if trial in photos:
                    value=copy.deepcopy(agent.Q)
                    img=picture_world(environment,value)
                    if type(agent).__name__ in ['BEB_Agent','Rmax_Agent','BEBLP_Agent','RmaxLP_Agent']:
                        pygame.image.save(img.screen,"Images/Solo/"+type(agent).__name__+"_"+type(environment).__name__+"_"+str(trial)+".png")
                    else : pygame.image.save(img.screen,"Images/"+type(agent).__name__+"_"+type(environment).__name__+"_"+str(trial)+".png")
                    if type(agent).__name__=='Rmax_Agent': bonus=copy.deepcopy(agent.R)
                    if type(agent).__name__=='BEB_Agent': bonus=copy.deepcopy(agent.bonus)
                    if type(agent).__name__=='BEBLP_Agent': bonus=copy.deepcopy(agent.bonus)
                    if type(agent).__name__=='RmaxLP_Agent': bonus=copy.deepcopy(agent.R)
                    if type(agent).__name__ in ['BEB_Agent','Rmax_Agent','BEBLP_Agent','RmaxLP_Agent']:
                        img2=picture_world(environment,bonus)
                        pygame.image.save(img2.screen,"Images/Solo/"+type(agent).__name__+"_bonus"+"_"+type(environment).__name__+str(trial)+".png")
                        merging_two_images(environment,"Images/Solo/"+type(agent).__name__+"_"+type(environment).__name__+"_"+str(trial)+".png","Images/Solo/"+type(agent).__name__+"_bonus"+"_"+type(environment).__name__+str(trial)+".png","Images/"+type(agent).__name__+"_"+type(environment).__name__+" Q_table (left) and bonus (right) "+str(trial)+".png")

def merging_two_images(environment,img1,img2,path):
    pygame.init()
    image1 = pygame.image.load(img1)
    image2 = pygame.image.load(img2)

    screen = pygame.Surface((environment.height*100+200,environment.height*50+100))
    
    screen.fill((0,0,0))   
    screen.blit(image1, (50,  50))
    screen.blit(image2, (environment.height*50+150, 50))

    pygame.image.save(screen,path)

        
def normalized_table(table,environment):
    max_every_state=np.zeros((environment.height,environment.width))
    action_every_state=dict()
    for state in table.keys():
        q_values = table[state]
        max_value_state=max(q_values.values())
        max_every_state[state]=max_value_state
        
        best_action = np.random.choice([k for k, v in q_values.items() if v == max_value_state])
        action_every_state[state]=best_action
    mini,maxi=np.min(max_every_state),np.max(max_every_state)
    if mini < 0 : max_every_state-=mini
    if maxi !=0 : max_every_state/=maxi     
    return max_every_state,action_every_state
 
def picture_world(environment,table):       
    max_Q,best_actions=normalized_table(table,environment)
    init_loc=[environment.first_location[0],environment.first_location[1]]
    screen_size = environment.height*50
    cell_width = 45
    cell_height = 45
    cell_margin = 5
    gridworld = Graphique(screen_size,cell_width, cell_height, cell_margin,environment.grid,environment.reward_states,init_loc,max_Q,best_actions)
    return gridworld

### SAVING PARAMETERS ####

def save_pickle(dictionnaire,path):
    with open(path, 'wb') as f:
        pickle.dump(dictionnaire, f) 

def open_pickle(path):
    with open(path, 'rb') as file:
        return pickle.load(file)

##### EXTRACTING RESULTS ####


def extracting_results(results):
    pass
######## VISUALISATION ########

def convert_from_default(dic):
    from collections import defaultdict
    if isinstance(dic,defaultdict):
        return dict((key,convert_from_default(value)) for key,value in dic.items())
    else : return dic


def plot3D(table_3D,x_name='beta',y_name='gamma'):
    dataframe=pd.DataFrame({x_name:table_3D[:,0], y_name:table_3D[:,1], 'values':table_3D[:,2]})
    data_pivoted = dataframe.pivot(x_name, y_name, "values")
    sns.heatmap(data_pivoted,cmap='Blues')


####### GET STATS #####

def convergence(array,longueur=30,variation=0.2,absolu=0.1,artefact=3):
    for i in range(len(array)-longueur):
        table=array[i:i+longueur]
        mean=np.mean(table)
        if mean >0:
            mauvais=0
            valid=True
            for element in table : 
                if element < (1-variation)*mean-absolu>element or element > (1+variation)*mean+absolu:
                    mauvais+=1
                    if mauvais > artefact:
                        valid=False
            if valid : 
                return [len(array)-len(array[i+1:]),np.mean(array[i+1:]),np.var(array[i+1:])]            
    return [len(array)-1,np.mean(array),np.var(array)]

    

