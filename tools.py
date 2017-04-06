# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import random
from collections import defaultdict


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
        self.avg_p = 0
        self.ps_sorted = range(len(self.firms))
        self.w_sorted = range(len(self.firms))
        # self.banks = []

    def step(self):
        self.steps +=1
        self.time +=1
        self.avg_p = np.mean([firm.p for firm in self.firms])
        self.ps_sorted = np.argsort([firm.p for firm in self.firms])
        self.w_sorted = np.argsort(-1*np.array([firm.w for firm in self.firms]))
        random.shuffle(self.individuals)
        pointer = 0
        for indi in self.individuals:
            # indi.step()
            consume = indi.c
            indi.contract -= 1
            while pointer<len(self.firms) and (self.firms[self.ps_sorted[pointer]].supply > 0 and consume>0):
                consume_num = int(consume / self.firms[self.ps_sorted[pointer]].p)
                if self.firms[self.ps_sorted[pointer]].supply <= consume_num:
                    self.firms[self.ps_sorted[pointer]].supply = 0
                    self.firms[self.ps_sorted[pointer]].q += consume_num
                    consume -= consume_num*self.firms[self.ps_sorted[pointer]].p
                    pointer+=1
                else:
                    self.firms[self.ps_sorted[pointer]].supply -= consume_num
                    self.firms[self.ps_sorted[pointer]].q += consume_num
                    consume = 0
            indi.step()
        for firm in self.firms:
            firm.step()

    def get_firm_count(self):
        return len(self.firms)

    def get_individual_count(self):
        return len(self.individuals)

    def add_individual(self,individual):
        self.individuals.append(individual)

    def add_firm(self,firm):
        self.firms.append(firm)

    def remove_firm(self,firm):
        while firm in self.firms:
            self.firms.remove(firm)



class MyCollector:
    """ Class for collecting data generated by a Mesa model.

    A DataCollector is instantiated with dictionaries of names of model- and
    agent-level variables to collect, associated with functions which actually
    collect them. When the collect(...) method is called, it executes these
    functions one by one and stores the results.

    """
    model_reporters = {}
    agent_reporters = {}

    model_vars = {}
    agent_vars = {}
    tables = {}

    model = None

    def __init__(self, model_reporters={}, agent_reporters={}, tables={}):
        """ Instantiate a DataCollector with lists of model and agent reporters.

        Both model_reporters and agent_reporters accept a dictionary mapping a
        variable name to a method used to collect it.
        For example, if there was only one model-level reporter for number of
        agents, it might look like:
            {"agent_count": lambda m: m.schedule.get_agent_count() }
        If there was only one agent-level reporter (e.g. the agent's energy),
        it might look like this:
            {"energy": lambda a: a.energy}

        The tables arg accepts a dictionary mapping names of tables to lists of
        columns. For example, if we want to allow agents to write their age
        when they are destroyed (to keep track of lifespans), it might look
        like:
            {"Lifespan": ["unique_id", "age"]}

        Args:
            model_reporters: Dictionary of reporter names and functions.
            agent_reporters: Dictionary of reporter names and functions.

        """
        self.model_reporters = {}
        self.agent_reporters = {}

        self.model_vars = {}
        self.agent_vars = {}
        self.tables = {}

        for name, func in model_reporters.items():
            self._new_model_reporter(name, func)

        for name, func in agent_reporters.items():
            self._new_agent_reporter(name, func)

        for name, columns in tables.items():
            self._new_table(name, columns)

    def _new_model_reporter(self, reporter_name, reporter_function):
        """ Add a new model-level reporter to collect.

        Args:
            reporter_name: Name of the model-level variable to collect.
            reporter_function: Function object that returns the variable when
                               given a model instance.

        """
        self.model_reporters[reporter_name] = reporter_function
        self.model_vars[reporter_name] = []

    def _new_agent_reporter(self, reporter_name, reporter_function):
        """ Add a new agent-level reporter to collect.

        Args:
            reporter_name: Name of the agent-level variable to collect.
            reporter_function: Function object that returns the variable when
                               given an agent object.

        """
        self.agent_reporters[reporter_name] = reporter_function
        self.agent_vars[reporter_name] = []

    def _new_table(self, table_name, table_columns):
        """ Add a new table that objects can write to.

        Args:
            table_name: Name of the new table.
            table_columns: List of columns to add to the table.

        """
        new_table = {column: [] for column in table_columns}
        self.tables[table_name] = new_table

    def collect(self, model):
        """ Collect all the data for the given model object. """
        if self.model_reporters:
            for var, reporter in self.model_reporters.items():
                self.model_vars[var].append(reporter(model))

        if self.agent_reporters:
            for var, reporter in self.agent_reporters.items():
                agent_records = []
                for agent in model.schedule.individuals:
                    agent_records.append((agent.unique_id, reporter(agent)))
                self.agent_vars[var].append(agent_records)

    def add_table_row(self, table_name, row, ignore_missing=False):
        """ Add a row dictionary to a specific table.

        Args:
            table_name: Name of the table to append a row to.
            row: A dictionary of the form {column_name: value...}
            ignore_missing: If True, fill any missing columns with Nones;
                            if False, throw an error if any columns are missing

        """
        if table_name not in self.tables:
            raise Exception("Table does not exist.")

        for column in self.tables[table_name]:
            if column in row:
                self.tables[table_name][column].append(row[column])
            elif ignore_missing:
                self.tables[table_name][column].append(None)
            else:
                raise Exception("Could not insert row with missing column")

    def get_model_vars_dataframe(self):
        """ Create a pandas DataFrame from the model variables.

        The DataFrame has one column for each model variable, and the index is
        (implicitly) the model tick.

        """
        return pd.DataFrame(self.model_vars)

    def get_agent_vars_dataframe(self):
        """ Create a pandas DataFrame from the agent variables.

        The DataFrame has one column for each variable, with two additional
        columns for tick and agent_id.

        """
        data = defaultdict(dict)
        for var, records in self.agent_vars.items():
            for step, entries in enumerate(records):
                for entry in entries:
                    agent_id = entry[0]
                    val = entry[1]
                    data[(step, agent_id)][var] = val
        df = pd.DataFrame.from_dict(data, orient="index")
        df.index.names = ["Step", "AgentID"]
        return df

    def get_table_dataframe(self, table_name):
        """ Create a pandas DataFrame from a particular table.

        Args:
            table_name: The name of the table to convert.

        """
        if table_name not in self.tables:
            raise Exception("No such table.")
        return pd.DataFrame(self.tables[table_name])


