import math
import random
import time

import numpy

from params import *
import numpy as np
import matplotlib.pyplot as plt
from chrom import Chromosome
from population import Population
"""
======================================
    根据期望时间生成一个随机服务时间的矩阵
    行数 = 人数
    列数 = 项目数
=======================================    
"""

def generate_time_table(people_total, project_total):
    res = np.zeros(shape=(project_total, people_total))
    for i in range(len(cost_time_lookup)):
        res[i, :] = np.random.exponential(cost_time_lookup[i], [1, people_total])

    res = res.flatten().astype(int)
    for i in range(len(res)):
        if res[i] == 0:
            res[i] = 1
    res = res.reshape(project_total, people_total)
    return res.T


class SGA:
    def __init__(self):
        self.pop = Population(POP_SIZE)

    def step(self, n):
        for i in range(n):
            self.pop.evolve_population()
        print(self.pop.get_best().fitness)
        return self.pop

class Metric:
    def __init__(self, maxF, W_sum, w_than_sum):
        self.makespan = maxF


def translate4simulation(seq, time_table):
    patients_table = [[] for _ in range(total_people)]
    queues_table = [[[] for _ in range(resource_look_up[sidx])] for sidx in range(project_num)]
    for operation in seq:
        patient_index, project_index = Chromosome.translate_operation(operation)
        cost_time = time_table[patient_index][project_index]
        patient_records = patients_table[patient_index]  # 客户的所有记录
        queues_records = queues_table[project_index]  # 项目服务台多个队列的所有记录

        # 获取客户最早有空时间
        patient_early_time = Chromosome.get_people_last_end(patient_records)
        # 获取最早空闲的队列及时间
        queue_index, project_early_time = Chromosome.get_early_queue(queues_records)
        # 确定占用时间片段
        start_time = max(patient_early_time, project_early_time)
        end_time = start_time + cost_time
        # 添加记录
        patient_records.append([project_index, queue_index, start_time, end_time])
        queues_records[queue_index].append([patient_index, start_time, end_time])

    W_sum = 0
    w_thanT_sum = 0
    tmp_lates = []
    for records in patients_table:
        assert len(records) == project_num  # 确保每个人都完成了8个项目
        records.sort(key=lambda e: e[3])
        tmp_lates.append(records[-1][3])
        for i in range(len(records)):
            if i == 0:
                wait_time = records[i][2] - 0
                if wait_time == 0:
                    continue
                W_sum += wait_time
                if wait_time - T_W > 0:
                    w_thanT_sum += (wait_time - T_W)
            else:
                wait_time = records[i][2] - records[i - 1][3]
                W_sum += wait_time
                if wait_time - T_W > 0:
                    w_thanT_sum += (wait_time - T_W)
    maxF = max(tmp_lates)
    fitness = maxF + W_sum + GAMMA2 * w_thanT_sum
    return fitness


def simulation(chromosome, simulation_num):
    """返回fitness的均值和方差"""
    fits = []
    for i in range(simulation_num):
        time_table = generate_time_table(total_people, project_num)
        fit = translate4simulation(chromosome.sequence, time_table)
        fits.append(fit)

    return np.mean(fits), np.var(fits)



if __name__ == '__main__':
    S_COUNT = 66000
    sga = SGA()
    pop = sga.step(100)
    first_simu = S_COUNT // pop.size
    means = []
    vars = []
    for dna in pop.members:
        m, v = simulation(dna, first_simu)
        means.append(m)
        vars.append(v)

    print(means)
    print(vars)
