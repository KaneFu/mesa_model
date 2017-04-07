# -*- coding: utf-8 -*-
from mesa import Agent
import random
import numpy as np
import pandas as pd


class Individual(Agent):
    """Individual"""
    def __init__(self,unique_id,model,firm =None,wage=5000,financial=10000,
                saving=10000,consume=3000,f_return=0,ratio=0.5,contract=48):
        super().__init__(unique_id,model)
        self.employed = True
        self.firm = firm
        self.w = wage
        self.f = financial
        self.s = saving
        self.c = consume
        self.f_return = f_return
        self.ratio = ratio   ##投资存款比例
        self.ability = np.random.randint(60,100)
        self.contract = contract
        self.income = self.w
        # self.employer = 

####!!!!!!!!consume需要改
    def step(self):
        self.f_return = np.random.lognormal(self.model.y,self.model.square) - 1
        # self.f = self.f*(1+self.f_return)
        # self.s = self.s*(1+self.model.r_saving)
        new_income = self.f_return*self.f + self.s*self.model.r_saving + self.w
        # print(new_income)
        
        if self.income > self.c:
            self.f = self.f*(1+self.f_return) + (self.income-self.c)*self.ratio
            self.s = self.s*(1+self.model.r_saving)+(self.income-self.c)*(1-self.ratio)
        else:
            self.s = self.s - self.c + self.income
            self.f = self.f + min(self.s,0)
            self.s = max(self.s,0)
            self.f = max(self.f,0)  #银行自助补给

        self.income = new_income
        # c = 700*ln(0.02*income + 4)
        self.c = max(min(700*np.log(max(0.02*self.income+4,1)),self.income),self.model.min_cost)
        #####
        
        if not self.employed:
            # if self.firm:
            #     if self not in self.firm.staff_apply:
            #         self.firm.staff_apply.append(self)
            for i in self.model.schedule.w_sorted[:self.model.M]:
                if self not in self.model.schedule.firms[i].staff_apply:
                    self.model.schedule.firms[i].staff_apply.append(self)


class Firm(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model,price=100,cost=0,sell_q=100,supply=2000,
                yield_num=2000,wage=5000,asset=100000,debt=5000,debt_r=0.04/12,alpha=50,
                sigma = 0.05):
        super().__init__(unique_id, model)
        self.staff = []
        # len(self.staff) = len(self.staff)
        self.p = price
        self.c = cost
        self.q = sell_q    #卖掉的货物
          

        self.Y = yield_num
        self.supply = supply #剩余的货物
        self.w = wage
        self.A = asset
        self.debt = debt
        self.debt_r = debt_r
        self.expenditure = model.firm_expense  #firm开销
        self.alpha = alpha
        self.sigma = sigma  #percent to invest on R&D
        self.pi = 0 #profit
        self.vacancy = 0
        self.staff_apply = []
        self.bankrupt = False

    def step(self):
        # print(self.q)
        self.pi = (self.p - self.c)*self.q  - (1+self.debt_r)*self.debt
        # print(self.p,self.q,self.c,self.debt,self.pi)
        self.debt = 0
        self.A = self.A + self.pi - max(self.pi,0)*self.sigma 
        if self.A < 0:
            self.go_bankrupt()
            return 
        W = self.w*len(self.staff)
        ###至少保留0.3的资产
        loan_money = max((W-0.7*self.A),0) 
        self.p_min = self.c + (W+(1+self.debt_r)*self.debt)/self.Y
        if loan_money:
            print("loan!!!!")
            self.A = 0.3*self.A
            self.loan(loan_money)

        if self.Y > self.q:
            if self.p >= self.model.schedule.avg_p:
                self.p = max(self.p_min, self.p * (1-np.random.uniform(0,self.model.h_eta)))
            else:
                self.Y = self.Y*(1-np.random.uniform(0,self.model.h_rho))
        else:
            if self.p >= self.model.schedule.avg_p:
                self.Y = self.Y*(1+np.random.uniform(0,self.model.h_rho))
            else:
                self.p = self.p * (1 + np.random.uniform(0,self.model.h_eta))

        # self.supply += self.Y

        self.alpha = self.alpha #+ 0.2
        #np.random.exponential(self.sigma*max(self.pi,0)*self.model.labor_trans)
        staff_demand = int(self.Y / self.alpha)
        # self.c = self.c - max(self.sigma*self.pi,0)*self.model.cost_trans

        if loan_money and staff_demand < len(self.staff):
            self.fire(len(self.staff)- staff_demand)
        ###将到期工作者开除,从申请者选入
        self.vacancy = max(staff_demand - self.labor_contract(),0)
        # print(self.vacancy)
        if len(self.staff_apply) == 0:
            pass
        elif len(self.staff_apply) >= self.vacancy:
            for candi in self.staff_apply[:self.vacancy]:
                self.hire(candi)
            self.vacancy = 0
        else:
            self.vacancy -= len(self.staff_apply)
            for candi in self.staff_apply:
                self.hire(candi)

        if self.vacancy:
            self.w = self.w*(1+np.random.uniform(0,self.model.h_xi))

        # self.sigma = self.sigma + 0.00001*(self.pi - W)*0.01
        self.supply = self.Y
        self.q = 0


    def loan(self,money):
        self.debt_r = self.model.r_bar*(1+self.model.phi*money/self.A)
        if self.debt_r <= self.model.debt_r_max:
            self.debt = money
            self.A += money
        else:
            self.debt = self.model.var_phi*money
            self.A += self.debt

    def go_bankrupt(self):
        print(">>>>>>>>>firm "+str(self.unique_id)+": go bankcrupt!!>>>>>>>>")
        self.bankrupt = True
        for staff in self.staff:
            staff.employed = False
            staff.w = 0
            staff.firm = None
        self.staff = []
        self.model.firm_num -= 1
        self.model.schedule.firms.remove(self)

    def labor_contract(self):
        for staff in self.staff:
            if staff.contract <=0:
                # print("contract time!")
                staff.employed = False
                staff.w = 0
                self.staff.remove(staff)
        # print ('s'+str(len(self.staff)))
        return len(self.staff)

    def fire(self,fire_num):
        # print ("need to fire!")
        if len(self.staff) < fire_num:
            print("not enough staff to fire!")
            return
        fire_staff = random.sample(self.staff,fire_num)
        for staff_ in fire_staff:
            staff_.employed = False
            staff_.firm = None
            staff_.w = 0
            self.staff.remove(staff_)

    def hire(self,candi):
        candi.firm = self
        candi.employed = True
        candi.contract = np.random.randint(36,120)
        candi.w = self.w
        # self.staff_apply.remove(candi)
        # if candi not in self.staff:
        self.staff.append(candi)
        for firm in self.model.schedule.firms:
            if candi in firm.staff_apply:
                firm.staff_apply.remove(candi)
