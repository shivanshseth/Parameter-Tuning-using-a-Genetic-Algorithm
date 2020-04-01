import random
import json
import datetime
import numpy as np
from client_moodle import get_errors,submit
from sklearn.discriminant_analysis import softmax as sft

team_id = 'oWWGKhmdis1hyUyJWgHPHDRcOrTLIF98xSuWuUMzLSHWkAeieT'
overfit = [10, 0.1240317450077846, -6.211941063144333, 0.04933903144709126, 0.03810848157715883, 8.132366097133624e-05, -6.018769160916912e-05, -1.251585565299179e-07, 3.484096383229681e-08, 4.1614924993407104e-11, -6.732420176902565e-12]

population_size = 40

iteration_count = 20

param_min = -10
param_max = 10

param_size = 11

data_collected = []
mutation_deviation = 50
prob_of_mutation = 30


def sample_err(params):
    err=0
    for i in range(param_size):
        if i==5:
            err -= 7.88036547e+50*(params[i]**2)
        else:
            err += 7.88036547e+50*(params[i]**2)
    return [err,err]

class Population:   
    people = []

    errors = []

    probabilities = []

    def init_random(self):
        self.people = [Person() for i in range(population_size)]
        # self.people += [Person(True, True)]
        # self.people += [Person(True, True) for i in range(overfit_init_mutated)]
        # self.people += [Person() for i in range(population_size - (overfit_init_pop + overfit_init_mutated))]
        
        with open("combined_results",'r') as f:
            combined = json.load(f)
            combined.sort(key=lambda i: sum(i[1]) + 0.5 * abs(i[1][0] - i[1][1]))
            for i in range(population_size):
                self.people[i].params = combined[i][0]
            

    def cal_errors(self):
        self.errors = np.array([person.cal_error() for person in self.people])

    def cal_probs(self):
        # print(self.errors)
        # print(np.exp(self.errors))
        # print(np.sum(np.exp(self.errors), axis=0))
        # self.probabilities = np.exp(self.errors) / np.sum(np.exp(self.errors), axis=0)
        self.probabilities = sft([self.errors])[0]
        # self.probabilities = [abs(err)/sum(abs(self.errors)) for err in self.errors]
        # print(self.probabilities)
    
    def generate_new_child(self, parents = False):
        # parents = np.random.choice(self.people, 2, replace=True, p=self.probabilities)
        # child = Person()
        # child.define_parents(parents)
        if not parents:
            parents = np.random.choice(self.people, 2, replace=True, p=self.probabilities)
        child1 = Person()
        child2 = Person()
        partition = np.random.randint(0, param_size)
        child1.params = np.concatenate((parents[0].params[:partition+1], parents[1].params[partition+1:]))
        child2.params = np.concatenate((parents[1].params[:partition+1], parents[0].params[partition+1:]))
        child1.mutate()
        child2.mutate()
        return [child1, child2]

    def get_next_generation(self):
        next_generation = []
        # next_generation = [self.generate_new_child() for i in range(population_size)]
        next_generation = [ child for i in range(population_size) for child in self.generate_new_child()]
        return next_generation


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
            for i in range(param_size):
                prob = np.random.randint(0,100)
                if(prob<prob_of_mutation):
                    dev = abs(1)/(mutation_deviation)
                    self.params[i] *=  1 + random.uniform(-dev, dev)
                    if prob < 1.5:
                        self.params[i] += random.uniform(-1, 1)
                    self.params[i] = min(param_max,self.params[i])
                    self.params[i] = max(param_min,self.params[i])

    def define_parents(self, parents):
        partition = np.random.randint(0, param_size)
        self.params = np.concatenate((parents[0].params[:partition+1], parents[1].params[partition+1:]))
        self.mutate()

    def cal_error(self):
        # err =  sample_err(self.params)
        err = get_errors(team_id, list(self.params))
        data_collected.append((list(self.params), list(err)))
        return -( err[0] +  err[1] + 0.5* abs(err[1]-err[0]))

if __name__ == "__main__":
    data_collected = []

    initial_population = Population()
    initial_population.init_random()
    for i in range(iteration_count):
        # data_collected = []
        print(i)
        initial_population.cal_errors()
        initial_population.cal_probs()
        print(max(initial_population.errors))
        next_population = Population()
        next_population.people = initial_population.get_next_generation()
        initial_population = next_population
        mutation_deviation += 1
        prob_of_mutation -= 0.5
    with open('results/'+str(datetime.datetime.now()), 'w') as outfile:
        # data = json.load(outfile)
        # data.extend(data_collected)
        json.dump(data_collected, outfile, indent=2)