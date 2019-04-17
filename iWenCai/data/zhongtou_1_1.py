#!/usr/bin/env python
# -*- coding=utf8 -*-

import json
import pandas as pd
import numpy as np
from data_frame2excel import DataFrame2Excel


datafile_path = "./products.json"

with open(datafile_path) as f:
    data = (json.loads(line) for line in f)
    df = pd.DataFrame(data)

# 根据日期分组
date_group = df.groupby("date")
# 获取每日A股所有股票的成交额之和
dates_turnover = date_group["turnover"].sum()
# 将数据由Series转为DataFrame
dates_turnover = pd.DataFrame({"date": dates_turnover.index, "turnover": dates_turnover.values})
# print dates_turnover
with DataFrame2Excel("dates_turnover.xlsx", "w") as b:
    b.data_frame2sheet(dates_turnover, "dates_turnover")

# 用于存储每日成交额排名前50的股票信息
date_turnovers_rank = {}
# 获取所有的日期
dates = date_group.groups.keys()
# 取出每日数据中成交额排名前50的股票信息
for date in dates:
    # 当前日期的数据
    date_data = date_group.get_group(date)
    # 按成交额排序 并截取前50行 取指定列的数据
    rank_data = date_data.sort_values('turnover', ascending=False)[0:50][["stock_code", "stock_abbreviation", "trading_volume", "turnover"]]
    # 重设行索引
    # rank_data.index = range(1, 51)
    # rank_data.index.name = "date_rank"
    # 添加排名字段
    rank_data.insert(0, "date_rank", range(1, 51))
    # rank_data.T.to_dict("dict")
    date_turnovers_rank[date] = rank_data

with DataFrame2Excel("rank_data.xlsx", "w") as b:
    b.data_frames2sheets(date_turnovers_rank)


if __name__ == '__main__':
	pass


#########################################################################
# File Name: zhongtou_1_a.py
# Author: sgs
# mail: sgs921107@163.com
# Created Time: Fri 05 Apr 2019 04:46:20 PM CST
#########################################################################
