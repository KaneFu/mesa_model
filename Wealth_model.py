# -*- coding: utf-8 -*-
from mesa import Agent,Model
import random
import numpy as np
import pandas as pd
from tools import MyScheduler,MyCollector
from agents import Individual,Firm


def gini(model):
    agent_wealths = [ indi.f+indi.s for indi in model.schedule.individuals]
    x = sorted(agent_wealths)
    N = model.indi_num
    if sum(x) == 0:
        return 0
    B = sum( xi * (N-i) for i,xi in enumerate(x) ) / (N*sum(x))
    return (1 + (1/N) - 2*B)

def unemploy_rate(model):
    employed = [indi.employed for indi in model.schedule.individuals]
    return 1 - np.sum(employed)/float(len(employed))

class WealthModel(Model):
    def __init__(self, indi_num, firm_num):
        self.indi_num = indi_num
        self.firm_num = firm_num
        self.schedule = MyScheduler(self)
        self.y = 0.02
        self.square = 0.01
        self.r_saving = 0.03/12
        # self.firm_sort = range(firm_num)
        self.M = 5
        self.cost_ratio = 0.1
        self.min_cost = 500
        self.c = 0.02
        # self.avg_p = 
        self.h_eta = 0.15
        self.h_rho = 0.2
        self.h_xi = 0.1
        self.r_bar = 0.04/12
        self.phi = 1.5
        self.debt_r_max = 0.07/12
        self.var_phi = 0.8
        
        for i in range(self.firm_num):
            firm = Firm(i, self)
            self.schedule.add_firm(firm)

        for j in range(self.indi_num):
            indi = Individual(j,self)
            self.schedule.add_individual(indi)
            firm = random.sample(self.schedule.firms,1)[0]
            indi.firm = firm
            firm.staff.append(indi)

            # Add the agent to a random grid cell

        self.datacollector = MyCollector(
            model_reporters={"Gini":gini,"Unemploy":unemploy_rate},
            agent_reporters={"Wealth": lambda a: a.f+a.s})

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        # self.show_vacancy()
        # self.show_wage()
        # self.show_saving()
        # self.show_employed()
        # self.show_staff_apply()
        self.show_consume()

    def show_wage(self):
        wages = [firm.w for firm in self.schedule.firms]
        print (wages)

    def show_saving(self):
        wealths = [indi.s for indi in self.schedule.individuals]
        print (wealths)

    def show_finance(self):
        finance = [indi.f for indi in self.schedule.individuals]
        print (finance)

    def show_vacancy(self):
        vacancy = [firm.vacancy for firm in self.schedule.firms]
        print (vacancy)

    def show_employed(self):
        employed = [indi.employed for indi in self.schedule.individuals]
        print (employed)

    def show_staff_apply(self):
        staff_apply = [indi.unique_id for indi in self.schedule.firms[3].staff_apply]
        print (staff_apply)
    def show_consume(self):
        consume = [indi.c for indi in self.schedule.individuals]
        print(consume)


model = WealthModel(indi_num=500,firm_num=10)
for i in range(200):
    print(i)
    model.step()