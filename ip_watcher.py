#!/usr/bin/python3
# -*- coding: utf-8 -*-
# import commands
import subprocess
import re
import yaml
import linecache
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import os
from apscheduler.schedulers.blocking import BlockingScheduler


def makedir(dir_name):
    if os.path.lexists(dir_name):
        os.chdir(dir_name)
    else:
        os.makedirs(dir_name)
        os.chdir(dir_name)


# 将文件编码改为utf-8
# 改变文件编码utf-8 防止gbk编码文件无法打开
def encode_file(path):
    # 改变文件编码utf-8 防止gbk编码文件无法打开
    fp = open(path, 'rb')
    fps = fp.read()
    fp.close()
    try:
        fps = fps.decode('utf-8')
    except:
        fps = fps.decode('gbk')
    fps = fps.encode('utf-8')
    fp = open(path, 'wb')
    fp.write(fps)
    fp.close()


# 检查邮箱地址,返回正确邮箱地址
def check_mail(file):
    mail_list = []
    encode_file(file)
    mail_results = linecache.getlines(file)
    for mail in mail_results:
        mail = mail.strip()
        if '@' in mail:
            mail_list.append(mail)
    # print('收件人', mail_list)
    # log('收件人 {}'.format(mail_list))
    return mail_list


# # 打印log
def log(string):
    log_file = 'log.txt'
    with open(log_file, 'a', encoding='utf-8') as logf:
        logf.write('[{}] {}\n'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), string))


def send_mail(mail_file, my_mail_user, my_mail_pass, send_name, send_subject, send_msg):
    print("开始发送邮件")
    log("开始发送邮件")
    # 第三方 SMTP 服务
    # 邮箱	    POP3服务器（端口995）	SMTP服务器（端口465或587）
    # qq.com	pop.qq.com	            smtp.qq.com
    mail_host = "smtp.qq.com"           # 设置服务器
    mail_port = "465"
    receivers = check_mail(mail_file)
    if receivers == []:
        print("收件人邮箱列表为空，检查脚本同文件夹下是否有{}以及里面是否有邮箱".format(mail_file))
        print("收件人邮箱列表为空，自动调整收件人为自己")
        receivers = [my_mail_user]
        log("收件人邮箱列表为空，检查脚本同文件夹下是否有{}以及里面是否有邮箱".format(mail_file))
        log("收件人邮箱列表为空，自动调整收件人为自己")
    print('收件人 {}'.format([receivers]))
    log('收件人 {}'.format(receivers))
    receiver_name = ""
    try:
        msg = MIMEMultipart()
        message = MIMEText(str(send_msg), 'plain', 'utf-8')              # 邮件内容
        msg['From'] = formataddr([send_name, my_mail_user])            # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        for receiver in receivers:
            msg['To'] = formataddr([receiver_name, receiver])        # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['Subject'] = send_subject                               # 邮件的主题，也可以说是标题
        msg.attach(message)

        server = smtplib.SMTP_SSL(mail_host, mail_port)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_mail_user, my_mail_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_mail_user, receivers, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        print("邮件发送成功")
        log("邮件发送成功")
    except smtplib.SMTPException as e:
        print("Error: 无法发送邮件")
        print(e)
        log("Error: 无法发送邮件")
        log(e)


def test_ip_ports(ip, port):
    cmd = "tcping.exe -n 10 {} {}".format(str(ip), str(port))
    #   用subprocess库获取返回值。
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out, err = p.communicate()
    outstr = out.decode('utf-8')
    # for line in out.splitlines():
    #     print(line)
    if err:
        print(err)
        return err
    else:
        print(outstr)
        return outstr


def get_success_fail_num(results_str):
    # results_list = results_str.split('\r\n')
    # success_num_line = results_list[len(results_list) - 3]
    pattern = re.compile(r"probes sent(.*?)\(", re.S)
    success_num_line = re.findall(pattern, results_str)[0]
    pattern_success = re.compile(r'\d+')
    success_fail_num = re.findall(pattern_success, success_num_line)  # [0, 4] success_num = 0, fail_num = 4
    return success_fail_num

# 主要任务
def loop(conf):
    try:
        ip_file = conf['ip_file']
        min_port = conf['min_port']
        max_port = conf['max_port']
        common_ports = conf['common_ports']
        mail_file = conf['mail_file']
        mail_user = conf['mail_user']
        mail_passwd = conf['mail_passwd']
        send_name = conf['send_name']
        send_subject = conf['send_subject']
        send_msg = conf['send_msg']
        encode_file(ip_file)
        encode_file(mail_file)
    except Exception as e:
        err_msg = "配置文件有误"
        print(err_msg)
        log(err_msg)
        print(e)
        log(e)

    ip_list = linecache.getlines(ip_file)
    if ip_list:
        pass
    else:
        err_msg = "获取的ip列表为空，检查是否存在文件 {} 和文件内容是否为空".format(ip_file)
        print(err_msg)
        log(err_msg)
    ports_list = []
    if min_port and max_port:
        ports_list = [i for i in range(min_port, max_port+1)]
    else:
        pass
    ports_list = ports_list + common_ports
    ports_list = list(set(ports_list))
    if ports_list:
        pass
    else:
        err_msg = "获取的port列表为空，检查配置文件中是否配置了端口项 'max_port','min_port','common_ports'".format(ip_file)
        print(err_msg)
        log(err_msg)

    # 邮件标志位，是否发送邮件
    send_mail_flag = False
    for ip in ip_list:
        for port in ports_list:
            ip = ip.strip()
            output = test_ip_ports(ip, port)
            success_fail_num = get_success_fail_num(output)
            if success_fail_num:
                success_num = success_fail_num[0]
                fail_num = success_fail_num[1]
                msg = "{} : {}  {} successful,{} failed".format(ip, port, success_num, fail_num)
                print(msg)
                log(msg)
                send_msg = send_msg + msg + '\n'
                if int(fail_num) >= int(success_num):
                    # 失败数 大于 成功数 更改邮件标志位，发送提醒邮件
                    send_mail_flag = True
                else:
                    pass
            else:
                err_msg = "{} : {} 获取tcp端口连接 成功数和失败数 失败".format(ip, port)
                print(err_msg)
                log(err_msg)
    # 判断邮件标志位
    if send_mail_flag == True:
        try:
            send_mail(mail_file, mail_user, mail_passwd, send_name, send_subject, send_msg)
        except:
            err_msg = "邮件发送失败"
            print(err_msg)
            log(err_msg)
    else:
        pass


if __name__ == '__main__':
    conf_file = "./ip_watcher.yaml"
    with open(conf_file, 'r', encoding='utf-8') as r:
        conf = yaml.load(r, Loader=yaml.SafeLoader)[0]
        print(conf)
    scheduler = BlockingScheduler()
    # # scheduler.add_job(url_test, 'cron', day_of_week='*', hour='*')
    scheduler.add_job(loop, 'cron', day_of_week='*', hour='*', minute='*', args=[conf])
    print(scheduler.get_jobs())
    scheduler.start()
    # # 主要测试：
    # # loop(conf)