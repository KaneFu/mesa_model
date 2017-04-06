from mesa import Agent
import random
from mesa.datacollection import DataCollector
import numpy as np
import pandas as pd


class Individual(Agent):
    """Individual"""
    def __init__(self,unique_id,firm,model):
        super().__init__(unique_id,model)
        self.employed = True
        self.firm = firm
        self.w = wage
        self.f = financial
        self.s = saving
        self.c = consume
        # self.A = asset
        self.f_return = 0
        self.ratio = ratio
        self.contract = contract
        # self.employer = 

    def step(self):
        self.f_return = np.random.normal(model.y,model.square)
        # self.f = self.f*(1+self.f_return)
        # self.s = self.s*(1+model.r_saving)
        income = self.f_return*self.f + self.s*model.r_saving + self.w
        self.f = self.f*(1+self.f_return) + max(income-self.c,0)*self.ratio
        self.s = self.s*(1+model.r_saving)+max(income-self.c,0)*(1-self.ratio)

        self.s = self.s - min(self.c,self.s)
        self.f = max(self.f - max(self.c-self.s,0),0)  #银行自助补给
        #####
        
        if not self.employed:
            if self.firm:
                self.firm.staff_apply.append(self)
            for i in range(model.firm_sort[:model.M]):
                if self not in model.firms[i].staff_apply:
                    model.firms[i].staff_apply.append(self)

        self.c = max(model.cost_ratio*income,model.min_cost)
            

class Firm(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model,staff,price):
        super().__init__(unique_id, model)
        self.staff = staff
        self.N = len(self.staff)
        self.p = price
        self.q = sell_q    #卖掉的货物
        self.supply = supply  #剩余的货物

        self.Y = yield_num
        self.w = wage
        self.A = asset
        self.debt = debt
        self.debt_r = debt_r
        self.c = model.c  #firm开销
        self.alpha = alpha
        self.sigma = sigma  #percent to invest on R&D
        self.pi = 0 #profit
        self.vacancy = 0
        self.staff_apply = []
        self.bankrupt = False

    def step(self):
        self.pi = self.p*self.q - self.c*self.A
        self.A = self.A + (1-self.sigma)*self.pi - (1+self.debt_r)*self.debt
        if self.A < 0:
            self.bankrupt()
        W = self.w*self.N
        loan_money = max(W-0.7*self.A,0)
        if loan_money:
            self.A = 0.3*self.A
            self.loan(loan_money)

        if self.supply > 0:
            if self.p > model.avg_p:
                self.p = max(self.p_min, self.p * (1-np.random.uniform(0,model.h_eta)))
            else:
                self.Y = self.Y*(1-np.random.uniform(0,model.h_rho))
        else:
            if self.p > model.avg_p:
                self.Y = self.Y*(1-np.random.uniform(0,model.h_rho))
            else:
                self.p = self.p * (1 + np.random.uniform(0,model.h_eta))

        self.alpha = self.alpha + np.random.exponential(self.sigma)
        staff_demand = int(self.Y / self.alpha)

        if loan_money and staff_demand < self.N:
            self.fire(self.N- staff_demand)
        ###将到期工作者开除,从申请者选入
        self.vacancy = max(staff_demand - self.labor_contract(),0)
        if len(self.staff_apply) == 0:
            pass
        elif len(self.staff_apply) >= self.vacancy:
            self.vacancy = 0
            for candi in self.staff_apply[:self.vacancy]:
                self.hire(candi)
        else:
            self.vacancy -= len(self.staff_apply)
            for candi in self.staff_apply:
                self.hire(candi)

        if self.vacancy:
            self.w = self.w*(1+np.random.uniform(0,model.h_xi))

        self.sigma = 0.1*exp(W/self.A)


    def loan(self,money):
        self.debt_r = model.r_bar*(1+model.phi*money/self.A)
        if self.debt_r <= model.debt_r_max:
            
            self.debt = money
            self.A += money
        else:
            self.debt = model.var_phi*money
            self.A += self.debt

    def bankrupt(self):
        self.bankrupt = True
        for staff in self.staff:
            staff.employed = False
            staff_.wage = 0
            staff.firm = None
        self.staff = []
        self.model.MyScheduler.frims.remove(self)

    def labor_contract(self):
        for staff in self.staff:
            if staff.contract <=0:
                staff.employed = False
                staff_.wage = 0
                self.staff.remove(staff)
        return len(self.staff)

    def fire(self,fire_num):
        if len(self.staff < fire_num):
            print("not enough staff to fire!")
            return
        fire_staff = random.sample(self.staff,fire_num)
        for staff_ in fire_staff:
            staff_.employed = False
            staff_.firm = None
            staff_.wage = 0
            self.staff.remove(staff_)

    def hire(self,candi):
        candi.firm = self
        candi.employed = True
        candi.contract = np.random.randint(12,120)
        candi.wage = self.wage
        self.staff.append(candi)

class MyScheduler:
    model = None
    steps = 0
    time = 0
    individuals = []
    firms = []
    banks = []

    def __init__(self,model):
        self.model = model
        self.steps = 0
        self.time = 0
        self.individuals = []
        self.firms = []
        # self.banks = []

    def step(self):
        self.steps +=1
        self.time +=1
        self.model.avg_p = np.mean([firm.p for firm in self.firms])
        self.model.firm_sort = np.argsort([firm.p for firm in self.firms])
        random.shuffle(self.individuals)
        firm_pointer = 0
        for indi in self.individuals:
            







    def get_firm_count(self):
        return len(self.firms)

    def get_individual_count(self):
        return len(self.individuals)

    def add_individual(self,individual):
        self.individuals.append(individual)

    def add_firm(self,firm):
        self.firms.append(firm)

    def add_bank(self,bank):
        self.banks.append(bank)

    def remove_firm(self,firm):
        while firm in self.firms:
            self.firms.remove(firm)



