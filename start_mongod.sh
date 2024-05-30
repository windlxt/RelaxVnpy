#!/bin/bash

# 获取进程ID，查询MongoDB是否已启动，并将查询结果写入 o.txt 文件
pgrep mongod>o.txt
# 读取 o.txt 文件内容
file_content=$(cat o.txt)
# 判断 file_content 是否为空。如果不空，说明MongoDB已启动；如果为空，则启动 MongoDB
if [ "$file_content" ]
then
  # 文件内容就是MongoDB进程的ID
  echo MongoDB 已启动, 进程ID是: "$file_content"
  exit
else
  # 防止没有正常关闭，出现错误，删除 mongodb/data/db/*.lock，输出重定向到 o.txt
  rm -vf /home/lxt/mongodb/data/db/*.lock>o.txt
  # 修复mongodb，输出重定向到 o.txt
  mongod -repair>o.txt
  # 使用 mongod 命令执行 mongod.conf 文件。MongoDB安装在设定位置，并且配置文件位于/home/lxt/mongodb/mongod.conf
  # 使用 root 权限，并自动输入密码，输出重定向到 o.txt
  sudo -S /home/lxt/mongodb/mongodb6/bin/mongod -f /home/lxt/mongodb/mongod.conf>o.txt<<EOF
lxt78929
EOF
echo
fi

# 判断 MongoDB 是否启动成功
# 获取启动信息，并判断是否包含 successfully, 字符串。如果包含，说明启动成功；如果没有，启动失败。
if grep -q "successfully" o.txt
then
# 查询进程信息，获取 MongoDB进程的ID，输出重定向到 o.txt
  pgrep mongod>o.txt
  echo MongoDB 启动成功!进程ID是: "$(cat o.txt)"
# echo grep -oE '^[0-9]+' o.txt | head -n 1
else
  echo MongoDB 启动失败!
fi
