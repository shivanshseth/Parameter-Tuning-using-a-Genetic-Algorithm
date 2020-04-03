import random
import json
import datetime
import numpy as np
from client_moodle import get_errors,submit
from sklearn.discriminant_analysis import softmax as sft

team_id = 'oWWGKhmdis1hyUyJWgHPHDRcOrTLIF98xSuWuUMzLSHWkAeieT'
overfit = [10, 0.1240317450077846, -6.211941063144333, 0.04933903144709126, 0.03810848157715883, 8.132366097133624e-05, -6.018769160916912e-05, -1.251585565299179e-07, 3.484096383229681e-08, 4.1614924993407104e-11, -6.732420176902565e-12]

population_size = 40

iteration_count = 10

param_min = -10
param_max = 10

param_size = 11

data_collected = []
mutation_deviation = 100
prob_of_mutation = 50

mating_pool_size = 15


def sample_err(params):
    err=0
    for i in range(param_size):
        if i==5:
            err -= 7.88036547e+50*(params[i]**2)
        else:
            err += 7.88036547e+50*(params[i]**2)
    return [err,err]

class Population:   
    def __init__(self): 
        self.people = []
        self.errors = []
        self.probabilities = []
        self.trace = {}
        self.trace['init_population'] = []
        self.trace['mating_pool'] = []
        self.trace['after_cross'] = []
        self.trace['after_mutation'] = []
        
    def init_random(self):
        self.people = [Person() for i in range(population_size)]
        self.people[0].params = overfit
        with open('combined_results3', 'r') as infile:
            results = json.load(infile)
            results.sort(key=lambda i: sum(i[1]) + 0.5* abs(i[1][1] - i[1][0]))
            for i in range(population_size - 2):
                self.people[i].params = results[i][0]
            for i in range(population_size - 2, population_size):
                self.people[i].params = [-9.101740268747474, 9.524213164652e-05, -0.602807945, 0.0531732844, 0.00364211004, 8.04257095e-06, -5.93648214e-06, -1.33858797e-08, 3.53670061e-09, 4.40909332e-12, -6.88185338e-13]
                self.people[i].mutate()
        self.trace['init_population'] = [{'sno': i, 'params': list(self.people[i].params)} for i in range(population_size)]        
    def cal_errors(self):
        self.errors = np.array([person.cal_error() for person in self.people])

    def cal_probs(self):
        self.probabilities = sft([self.errors])[0]
        # self.probabilities = [abs(err)/sum(abs(self.errors)) for err in self.errors]
        print(self.probabilities)
    
    def generate_new_child(self, parents = False, parents_sno = False):

        if not parents:
            parents_sno = np.random.choice(range(population_size), 2, replace=True, p=self.probabilities)
            parents_sno = [int(i) for i in parents_sno]
            parents = [self.people[i] for i in parents_sno]
        # self.trace['mating_pool'].append([{'sno': i, 'params': list(self.people[i].params), 'probability': self.probabilities[i], 'error': self.people[i].get_error()} for i in parents_sno])
        child1 = Person()
        child2 = Person()
        partition = np.random.randint(0, param_size)
        child1.params = np.concatenate((parents[0].params[:partition+1], parents[1].params[partition+1:]))
        child2.params = np.concatenate((parents[1].params[:partition+1], parents[0].params[partition+1:]))
        children = [child1, child2]
        # print()
        # for i in children:
        #     self.trace['after_cross'].append({'parent_sno': parents_sno, 'params': list(i.params)})
        children[0].mutate()
        children[1].mutate()
        # for i in children: 
        #     self.trace['after_mutation'].append({'parent_sno': parents_sno, 'params': list(i.params)})
        return children

    def get_next_generation(self):
        self.trace['init_population'] = [{'sno': i, 'params': list(self.people[i].params)} for i in range(population_size)]
        next_generation = []
        self.people.sort(key=lambda i: sum(i.get_error()))
        mating_pool = [self.people[i] for i in range(mating_pool_size)]
        for i in range(mating_pool_size//2):
            child1, child2 = self.generate_new_child([mating_pool[i], mating_pool[i+1]], [i, i+1])
            next_generation.append(child1)
            next_generation.append(child2)
        for i in range(population_size - len(next_generation)):
            self.people[i].mutate()
            next_generation.append(self.people[i])
        # next_generation = [self.generate_new_child() for i in range(population_size)]
        # next_generation = [ child for i in range(population_size//2) for child in self.generate_new_child()]
        return next_generation
    
    def get_trace(self):
        return self.trace


class Person:
    params = []

    def __init__(self, is_overfit = True, no_mutation = False):
        if is_overfit:
            self.params = np.array(overfit)
        else:
            self.params = np.array([random.uniform(param_min,param_max) for i in range(param_size)])
        if not no_mutation:
            self.mutate()

    def mutate(self):
            # for i in range(param_size):
            #     prob = np.random.randint(0,100)
            #     if(prob<prob_of_mutation):
            #         dev = abs(1)/(mutation_deviation)
            #         self.params[i] *= 1 + random.uniform(-dev, dev)
            #         if prob < 0.05 * prob_of_mutation:
            #             self.params[i] += random.uniform(-1, 1)
            #         self.params[i] = min(param_max,self.params[i])
            #         self.params[i] = max(param_min,self.params[i])
        prob = np.random.randint(0,100)
        if(prob<prob_of_mutation):
            i = random.randint(0, param_size - 1)
            dev = abs(1)/(mutation_deviation)
            self.params[i] *= 1 + random.uniform(-dev, dev)
            if prob < 0.05 * prob_of_mutation:
                self.params[i] += random.uniform(-1, 1)
            self.params[i] = min(param_max,self.params[i])
            self.params[i] = max(param_min,self.params[i])

    def define_parents(self, parents):
        partition = np.random.randint(0, param_size)
        self.params = np.concatenate((parents[0].params[:partition+1], parents[1].params[partition+1:]))
        self.mutate()

    def cal_error(self):
        # self.error =  sample_err(self.params)
        self.error = get_errors(team_id, list(self.params))
        data_collected.append((list(self.params), list(self.error)))
        return  (self.error[0] +  self.error[1] + 0.5* abs(self.error[1]-self.error[0]))
    
    def get_error(self):
        return self.error

if __name__ == "__main__":
    data_collected = []
    trace = []
    initial_population = Population()
    initial_population.init_random()
    for i in range(iteration_count):
        # data_collected = []
        print(i)
        initial_population.cal_errors()
        # initial_population.cal_probs()
        print(min(initial_population.errors))
        next_population = Population()
        next_population.people = initial_population.get_next_generation()
        trace.append(initial_population.get_trace())
        initial_population = next_population
        mutation_deviation += 0.5
        prob_of_mutation -= 0.5
    with open('results/'+str(datetime.datetime.now()), 'w') as outfile:
        # data = json.load(outfile)
        # data.extend(data_collected)
        json.dump(data_collected, outfile, indent=2)
    with open('trace/' + str(datetime.datetime.now()), 'w') as outfile:
        # data = json.load(outfile)
        # data.extend(data_collected)
        json.dump(trace, outfile, indent=2)
        pass
# print(trace)