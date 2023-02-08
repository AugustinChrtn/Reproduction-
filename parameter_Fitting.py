import numpy as np
import time
from main_Functions import loading_environments,getting_simulations_to_do,main_function,plot1D

import matplotlib.pyplot as plt
import seaborn as sns
import copy

from matplotlib.colors import TwoSlopeNorm

### Parameter fitting ##

def range_parameters_agent(list1,list2):
    list_of_params=[]
    for elem1 in range(1,len(list1)) :
        for elem2 in range(1,len(list2)):
            list_of_params.append({list1[0]:list1[elem1],list2[0]:list2[elem2]})
    return list_of_params


def get_agent_parameters(name_agent,basic_parameters,list_1,list_2):
    agent_parameters=[]
    list_of_new_parameters=range_parameters_agent(list_1, list_2)
    for dic in list_of_new_parameters:
        d=copy.deepcopy(basic_parameters)
        for key,value in dic.items() : 
            d[name_agent][key]=value
        agent_parameters.append(d)
    return agent_parameters

def get_mean_and_CI_fitting(dictionary,name_agent,names_environments,number_of_iterations,first_hyperparameters,second_hyperparameters):
    mean={(name_agent,h_1,h_2): np.average([dictionary[name_environment,name_agent,i,h_1,h_2] for i in range(number_of_iterations) for name_environment in names_environments],axis=0)  
                                                 for h_1 in first_hyperparameters for h_2 in second_hyperparameters}    
    CI={(name_agent,h_1,h_2):np.std([dictionary[name_environment,name_agent,i,h_1,h_2] for name_environment in names_environments for i in range(number_of_iterations)],axis=0)/np.sqrt(number_of_iterations*len(names_environments)) 
                         for h_1 in first_hyperparameters for h_2 in second_hyperparameters}
    return mean,CI

def extracting_results(opti_pol_error,real_pol_error,agents_tested,names_environments,number_of_iterations,first_hyperparameters,second_hyperparameters):
    mean_pol_opti,CI_pol_opti=get_mean_and_CI_fitting(opti_pol_error,names_environments,agents_tested,number_of_iterations,first_hyperparameters,second_hyperparameters)    
    mean_pol_real,CI_pol_real=get_mean_and_CI_fitting(real_pol_error,names_environments,agents_tested,number_of_iterations,first_hyperparameters,second_hyperparameters)
    return mean_pol_opti,CI_pol_opti,mean_pol_real,CI_pol_real


def get_best_performance(pol_error,name_agent,first_hyperparameters,second_hyperparameters,range_of_the_mean):
    avg_pol_error = {(name_agent,hp_1,hp_2):np.average(pol_error_value[-range_of_the_mean:]) for (name_agent,hp_1,hp_2),pol_error_value in pol_error.items()}
    array_result=np.zeros((len(first_hyperparameters)-1,len(second_hyperparameters)-1))
    for index_hp_1,hp_1 in enumerate(first_hyperparameters[1:]) :
        for index_hp_2,hp_2 in enumerate(second_hyperparameters[1:]) :
            array_result[(index_hp_1,index_hp_2)]=avg_pol_error[name_agent,hp_1,hp_2]
    return array_result

def save_results_parametter_fitting(pol_opti,CI_pol_opti,pol_real,CI_pol_real,name_agent,first_hyperparameters,second_hyperparameters,play_parameters,name_environments):
    time_end=str(round(time.time()%1e7))
    np.save('Parameter fitting/Data/'+name_agent+'_'+name_environments[0]+'_pol_opti_'+time_end+'.npy',pol_opti)
    np.save('Parameter fitting/Data/'+name_agent+'_'+name_environments[0]+'_CI_pol_opti_'+time_end+'.npy',CI_pol_opti)
    np.save('Parameter fitting/Data/'+name_agent+'_'+name_environments[0]+'_pol_real_'+time_end+'.npy',pol_real)
    np.save('Parameter fitting/Data/'+name_agent+'_'+name_environments[0]+'_CI_pol_real_'+time_end+'.npy',CI_pol_real)
    return time_end

def plot_from_saved(name_agent,first_hyperparameters,second_hyperparameters,step_between_VI,name_environments,time_end,optimal):
    if optimal :
        pol=np.load('Parameter fitting/Data/'+name_agent+'_'+name_environments[0]+'_pol_opti_'+time_end+'.npy',allow_pickle=True)[()]
        CI_pol=np.load('Parameter fitting/Data/'+name_agent+'_'+name_environments[0]+'_CI_pol_opti_'+time_end+'.npy',allow_pickle=True)[()]
    else : 
        pol=np.load('Parameter fitting/Data/'+name_agent+'_'+name_environments[0]+'_pol_real_'+time_end+'.npy',allow_pickle=True)[()]
        CI_pol=np.load('Parameter fitting/Data/'+name_agent+'_'+name_environments[0]+'_CI_pol_real_'+time_end+'.npy',allow_pickle=True)[()]
    plot_parameter_fitting(pol,CI_pol,name_agent,first_hyperparameters,second_hyperparameters,step_between_VI,name_environments,time_end,optimal)

def plot_parameter_fitting(pol,CI_pol,name_agent,first_hyperparameters,second_hyperparameters,step_between_VI,name_environments,time_end,optimal):
    
    markers=['^','o','x','*','s']
    colors=['#9d02d7','#0000ff',"#ff7763","#ffac1e","#009435"]
    array_avg_pol_last_500=get_best_performance(pol,name_agent,first_hyperparameters,second_hyperparameters,10)
    
    plot_2D(array_avg_pol_last_500,first_hyperparameters,second_hyperparameters)
    if optimal :
        plt.title(name_agent+' optimal policy - last 500 steps')
        plt.savefig('Parameter fitting/Heatmaps/heatmap_'+name_agent+' optimal_policy '+name_environments[0]+time_end+'.pdf',bbox_inches = 'tight')
    else : 
        plt.title(name_agent+' agent policy - last 500 steps')
        plt.savefig('Parameter fitting/Heatmaps/heatmap_'+name_agent+' real_policy '+name_environments[0]+time_end+'.pdf',bbox_inches = 'tight')
    plt.close() 
    
    curve_number=0
    for hp_1 in first_hyperparameters[1:] :
        plot1D(ylim=[-12.5,0.5],xlabel="Steps",ylabel="Policy value error",title='')
        for hp_2 in second_hyperparameters[1:] :
            yerr0 = pol[name_agent,hp_1,hp_2] - CI_pol[name_agent,hp_1,hp_2]
            yerr1 = pol[name_agent,hp_1,hp_2] + CI_pol[name_agent,hp_1,hp_2]

            plt.fill_between([step_between_VI*i for i in range(len(pol[name_agent,hp_1,hp_2]))], yerr0, yerr1, color=colors[curve_number], alpha=0.2)

            plt.plot([step_between_VI*i for i in range(len(pol[name_agent,hp_1,hp_2]))],pol[name_agent,hp_1,hp_2],color=colors[curve_number],
                     label=str(second_hyperparameters[0])+"="+str(hp_2),ms=4,marker=markers[curve_number])
            curve_number+=1
            if curve_number == 5 or hp_2 == second_hyperparameters[-1]: 
                plt.legend()
                if optimal : 
                    plt.title(name_agent+" optimal policy with "+str(first_hyperparameters[0])+" = "+str(hp_1))
                    plt.savefig('Parameter fitting/1DPlots/pol_error_opti_'+name_agent+'_'+name_environments[0]+str(hp_2)+"_"+str(time.time())+'.pdf',bbox_inches = 'tight')
                else : 
                    plt.title(name_agent+" agent policy with "+str(first_hyperparameters[0])+" = "+str(hp_1))
                    plt.savefig('Parameter fitting/1DPlots/pol_error_real_'+name_agent+'_'+name_environments[0]+str(hp_2)+"_"+str(time.time())+'.pdf',bbox_inches = 'tight')
                plt.close()
                curve_number=0
                if hp_2 != second_hyperparameters[-1]: plot1D(ylim=[-12.5,0.5],xlabel="Steps",ylabel="Policy value error",title='')

def plot_2D(array_result,first_hyperparameters,second_hyperparameters):
    fig=plt.figure(dpi=300)
    fig.add_subplot(1, 1, 1)
    #rdgn = sns.diverging_palette(h_neg=130, h_pos=10, s=99, l=55, sep=3, as_cmap=True)
    divnorm = TwoSlopeNorm(vmin=-12, vcenter=-1, vmax=0)
    sns.heatmap(array_result, cmap='bwr', norm=divnorm,cbar=True,annot=np.round(array_result,1),
                cbar_kws={"ticks":[-12,-1,0]},annot_kws={"size": 35 / (np.sqrt(len(array_result))+2.5)})
    #linewidths=0.05, linecolor='black'
    plt.xlabel(second_hyperparameters[0])
    plt.ylabel(first_hyperparameters[0])
    plt.xticks([i+0.5 for i in range(len(second_hyperparameters[1:]))],second_hyperparameters[1:])
    plt.yticks([i+0.5 for i in range(len(first_hyperparameters[1:]))],first_hyperparameters[1:])
            
    
    

def fit_parameters_agent(environments,name_agent,nb_iters,first_hp,second_hp,agent_basic_parameters,starting_seed,play_parameters):
    
    every_simulation=getting_simulations_to_do(environments,[name_agent],range(nb_iters),first_hp[1:],second_hp[1:])
    seeds_agent=[starting_seed+i for i in range(len(every_simulation))]
    agent_parameters=nb_iters*len(environments)*get_agent_parameters(name_agent,agent_basic_parameters,first_hp, second_hp)
    opti_pol_errors,real_pol_errors,reward_pol_errors=main_function(seeds_agent,every_simulation,play_parameters,agent_parameters)
    mean_pol_opti,CI_pol_opti,mean_pol_real,CI_pol_real=extracting_results(opti_pol_errors,real_pol_errors,environments,name_agent,nb_iters,first_hp[1:],second_hp[1:])
    time_end=save_results_parametter_fitting(mean_pol_opti,CI_pol_opti,mean_pol_real,CI_pol_real,name_agent,first_hp,second_hp,play_parameters,environments)
    for optimal in [False,True]:plot_from_saved(name_agent,first_hp,second_hp,play_parameters["step_between_VI"],environments,time_end,optimal)


# Parameter fitting for each agent #


environments_parameters=loading_environments()
play_params={'trials':100, 'max_step':30, 'screen':False,'photos':[10,20,50,80,99],'accuracy_VI':0.01,'step_between_VI':50}


#Reproduction of Lopes et al. (2012)

environments=['Lopes']
nb_iters=20

agent_parameters={'ε-greedy':{'gamma':0.95,'epsilon':0.3},
            'R-max':{'gamma':0.95, 'm':8,'Rmax':1,'m_uncertain_states':12,'condition':'informative'},
            'BEB':{'gamma':0.95,'beta':7,'coeff_prior':2,'condition':'informative'},
            'ζ-EB':{'gamma':0.95,'beta':7,'step_update':10,'alpha':1,'prior_LP':0.01},
            'ζ-R-max':{'gamma':0.95,'Rmax':1,'m':2,'step_update':10,'alpha':1,'prior_LP':0.01}}

"""
agent_name='R-max'
starting_seed=10000

first_hp= ['m']+[1]+[i for i in range(5,41,5)]
second_hp=['m_uncertain_states']+[1]+[i for i in range(5,41,5)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)


first_hp= ['m']+[i for i in range(2,15,2)]
second_hp=['m_uncertain_states']+[i for i in range(2,21,2)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)


agent_parameters['R-max']['condition']='uninformative'
first_hp= ['gamma']+[0.95]
second_hp=['m']+[i for i in range(2,21,2)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)


agent_name='ζ-R-max'
starting_seed=20000

first_hp= ['m']+[round(i*0.1,1) for i in range(5,41,5)]
second_hp=['alpha']+[0.1]+[round(i*0.1,1) for i in range(5,41,5)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)

first_hp= ['m']+[round(i*0.1,1) for i in range(20,31,2)]
second_hp=['alpha']+[round(i*0.1,1) for i in range(1,21,3)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)

first_hp= ['gamma']+[0.95]
second_hp=['prior_LP']+[10**(i) for i in range(-5,4)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)


agent_name='BEB'
starting_seed=30000

first_hp= ['coeff_prior']+[2]
second_hp=['beta']+[0.1]+[1]+[2]+[3]+[4]+[i for i in range(5,26,5)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)

first_hp= ['beta']+[10]
second_hp=['coeff_prior']+[10**i for i in range(-1,4)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)


agent_parameters['BEB']['condition']='uninformative'

first_hp= ['coeff_prior']+[0.001]
second_hp=['beta']+[0.1]+[i for i in range(1,10)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)


agent_name='ζ-EB'
starting_seed=40000

first_hp= ['beta']+[0.1]+[i for i in range(1,20,2)]
second_hp=['alpha']+[0.1]+[round(0.5*i,1) for i in range(1,9)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)

first_hp= ['alpha']+[round(0.5*i,1) for i in range(1,11)]
second_hp=['prior_LP']+[10**(i) for i in range(-3,2)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)

first_hp= ['beta']+[0.1]+[round(0.1*i,1) for i in range(2,11,2)]
second_hp=['alpha']+[0.1]+[round(0.5*i,1) for i in range(1,9)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)


agent_name='ε-greedy'
starting_seed=50000
first_hp= ['gamma']+[0.95]
second_hp=['epsilon']+[0.001]+[0.01]+[0.05]+[round(i*0.1,1) for i in range(1,4,1)]+[round(i*0.1,1) for i in range(5,11,2)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)

"""
#Parameter fitting for the environments with a reward of -1

environments=['Stationary_Lopes_-1_'+str(number_world) for number_world in range(1,11)]
nb_iters=10

agent_parameters={'ε-greedy':{'gamma':0.95,'epsilon':0.3},
            'R-max':{'gamma':0.95, 'm':8,'Rmax':1,'m_uncertain_states':12,'condition':'informative'},
            'BEB':{'gamma':0.95,'beta':7,'coeff_prior':2,'condition':'informative'},
            'ζ-EB':{'gamma':0.95,'beta':7,'step_update':10,'alpha':1,'prior_LP':0.01},
            'ζ-R-max':{'gamma':0.95,'Rmax':1,'m':2,'step_update':10,'alpha':1,'prior_LP':0.01}}


agent_name='R-max'
starting_seed=60000


first_hp= ['m']+[1]+[i for i in range(5,41,5)]
second_hp=['m_uncertain_states']+[1]+[i for i in range(5,41,5)]

fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)

"""
agent_name='ζ-R-max'
starting_seed=70000


first_hp= ['m']+[round(i*0.1,1) for i in range(5,41,5)]
second_hp=['alpha']+[0.1]+[round(i*0.1,1) for i in range(5,31,5)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)


agent_name='BEB'
starting_seed=80000

first_hp= ['coeff_prior']+[2]
second_hp=['beta']+[0.1]+[1]+[2]+[3]+[4]+[i for i in range(5,26,5)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)


agent_name='ζ-EB'
starting_seed=90000

first_hp= ['beta']+[0.1]+[i for i in range(1,20,2)]
second_hp=['alpha']+[0.1]+[round(0.5*i,1) for i in range(1,9)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)

agent_name='ε-greedy'
starting_seed=100000
first_hp= ['gamma']+[0.95]
second_hp=['epsilon']+[0.001]+[0.01]+[0.05]+[round(i*0.1,1) for i in range(1,4,1)]+[round(i*0.1,1) for i in range(5,11,2)]
fit_parameters_agent(environments,agent_name,nb_iters,first_hp,second_hp,{agent_name:agent_parameters[agent_name]},starting_seed,play_params)
"""