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

    def cal_errors(self):
        self.errors = np.array([person.cal_error() for person in self.people])

    def cal_probs(self):
        print(self.errors)
        # print(np.exp(self.errors))
        # print(np.sum(np.exp(self.errors), axis=0))
        # self.probabilities = np.exp(self.errors) / np.sum(np.exp(self.errors), axis=0)
        self.probabilities = sft([self.errors])[0]
        print(self.probabilities)
    
    def generate_new_child(self):
        # print(self.probabilities)
        # print(np.sum(self.probabilities))
        parents = np.random.choice(self.people, 2, replace=True, p=self.probabilities)
        child = Person()
        child.define_parents(parents)
        return child

    def get_next_generation(self):
        next_generation = []
        next_generation = [self.generate_new_child() for i in range(population_size)]
        return next_generation



class Person:
    params = []

    def __init__(self):
        # self.params = np.array([random.uniform(param_min,param_max) for i in range(param_size)])
        self.params = np.array(overfit)
        self.mutate()

    def mutate(self):
        for i in range(param_size):
            prob = np.random.randint(0,100)
            if(prob<15):
                self.params[i] = max(param_min, min(param_max, self.params[i] * random.uniform(-1.5, 1.5)))

    def define_parents(self, parents):
        partition = np.random.randint(0, param_size)
        self.params = np.concatenate((parents[0].params[:partition+1], parents[1].params[partition+1:]))
        self.mutate()

    def cal_error(self):
        # err =  sample_err(self.params)
        err = get_errors(team_id, list(self.params))

        data_collected.append((list(self.params), list(err)))
        # print(data_collected)
        # data.append((list(self.params), err))
        # outfile.seek(0)
        # json.dump(data, outfile, indent=2)

        return -np.mean(err)

        

if __name__ == "__main__":
    # err = get_errors(team_id, overfit)
    # print(err)
    # assert len(err) == 2

    data_collected = []

    initial_population = Population()
    initial_population.init_random()
    for i in range(iteration_count):
        print(i)
        initial_population.cal_errors()
        initial_population.cal_probs()
        print(max(initial_population.errors))
        next_population = Population()
        next_population.people = initial_population.get_next_generation()
        initial_population = next_population
    
    with open('results/'+str(datetime.datetime.now()), 'w') as outfile:
        # data = json.load(outfile)
        # data.extend(data_collected)
        json.dump(data_collected, outfile, indent=2)