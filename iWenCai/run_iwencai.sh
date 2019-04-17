#!/bin/bash

# 脚本功能：iwencai spider　启动脚本
    # 1.判断脚本是否再运行
    # 2.统计每次抓取运行时间、新闻抓取数量
# 启动方式: /bin/bash run_iwencai.sh


# 爬虫程序的路径
spider_path=$(pwd)
# 爬虫的名字
spider_name=iwencai

# 运行的日志文件名
run_log_filename=$spider_path/logs/run.log
# 爬虫的日志文件名
spider_log_filename=$spider_path/logs/spider.log
# 爬取数据的存储文件
spider_data_filename=$spider_path/data/products.json
# 锁 文件名
lock_filename=$spider_path/spider.lock


<<!
    函数功能：记录日志
    接受参数：
        参数１： LINENO
        参数２： 日志等级－INFO
        参数３： 日志信息
        参数４： 日志信息
    返回值： 无
!
log_msg(){
    echo "$(date +'%Y-%m-%d %H:%M:%S')-[$(whoami)] $0 [line: $1]-$2:---------$3: 【$4】--------" >> $run_log_filename
}


<<!
    函数功能： 运行sina_news spider、分析日志
    接受参数： 无
    返回值： 无
!
run_spider(){
    # 创建锁文件
    touch $lock_filename && echo "WARNING: Do not delete at will!" >> $lock_filename
    # 分割线
    echo ==============================================================start============================================================ >> $run_log_filename
    # 开始时间（时间戳）
    st=$(date +%s)
    # 记录开始时间
    log_msg $LINENO "INFO" "start $spider_name spider" "$(date +'%Y-%m-%d %H:%M:%S')"
    # 开启爬虫
    cd $spider_path && scrapy crawl $spider_name >> $spider_log_filename 2>&1
    # 结束时间（时间戳）
    et=$(date +%s)
    [ $((et-st)) -lt 60 ] && log_msg $LINENO "WARNING" "error msg" "运行时间小于60秒，请确认程序是否正常"
    # 记录结束时间
    log_msg $LINENO "INFO" "end spider" "$(date +'%Y-%m-%d %H:%M:%S')"
    # 记录运行时间
    log_msg $LINENO "INFO" "run time" "$(((et-st)/60))Minute"
    # 记录日志：抓取数据数量
    log_msg $LINENO "INFO" "spider data num" $(cat $spider_data_filename | wc -l)
    # 分割线
    echo ===============================================================end============================================================= >> $run_log_filename
    # 删除锁文件
    rm $lock_filename
}


<<!
    函数功能：run函数  执行run_spider函数启动爬虫
    参数：无
    返回值：无
!
run(){
    # 判断是否存在锁文件　记录日志或开启爬虫
    [ -f $lock_filename ] && log_msg $LINENO "WARNING" "$spider_name spider running" "$(date +'%Y-%m-%d %H:%M:%S')" && exit 0 || run_spider
}


<<!
    函数功能：主函数  无限循环Run函数
    参数：无
    返回值：无
!
main(){
        # 执行run函数
        run
}



# 执行主函数
main

