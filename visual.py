from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule,TextElement
from mesa.visualization.ModularVisualization import ModularServer,VisualizationElement

from money_model import MoneyModel
import numpy as np

def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 0.5}

    if agent.wealth > 0:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
    else:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2
    return portrayal

# grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)
chart = ChartModule([
    {"Label": "Gini", "Color": "Black"}],
    data_collector_name='datacollector'
)



class HistogramModule(VisualizationElement):
    package_includes = ["Chart.min.js"]
    local_includes = ["HistogramModule.js"]

    def __init__(self, bins, canvas_height, canvas_width):
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.bins = bins
        new_element = "new HistogramModule({}, {}, {})"
        new_element = new_element.format(bins,
                                         canvas_width,
                                         canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        wealth_vals = [agent.wealth for agent in model.schedule.agents]
        hist = np.histogram(wealth_vals, bins=self.bins)[0]
        return [int(x) for x in hist]


class HistModule2(VisualizationElement):
    package_includes = ["Chart.min.js"]
    local_includes = ["HistogramModule.js"]

    def __init__(self, bins, canvas_height, canvas_width):
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.bins = bins
        new_element = "new HistogramModule({}, {}, {})"
        new_element = new_element.format(bins,
                                         canvas_width,
                                         canvas_height)
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        wealth_vals = [agent.wealth for agent in model.schedule.agents]
        wealth_sum = float(np.sum(wealth_vals))
        vals_sort = np.sort(wealth_vals)  #small_ big
        val_ind = np.linspace(0,len(vals_sort),10,dtype=np.int32)
        wealth_pct = [np.sum(vals_sort[val_ind[i]:val_ind[i+1]])/wealth_sum for i in range(9)]
        return wealth_pct



class TextModule(VisualizationElement):
    package_includes = ["TextModule.js"]
    def __init__(self,):
        self.js_code = "elements.push(new TextModule());"

    def render(self,model):
        step_num = 'step_num : %d,<br>' % model.schedule.steps
        agent_num = 'agent_num: %d' % model.schedule.get_agent_count()
        return step_num+agent_num

text = TextModule()
histogram_element = HistogramModule(list(range(50)), 200, 500)
pie_element = HistModule2(list(range(1,11)),300,300)
# print(type(histogram_element))
# model = MoneyModel(1000,100,100)
# model.run_model()
server = ModularServer(MoneyModel,
                       [chart,histogram_element,pie_element,text],
                       "Money Model",
                       1000, 10, 10)

server.port = 8521
server.launch()
