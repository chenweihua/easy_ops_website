#!/bin/sh


# echo "test ${1-hahaha}"
# echo "$0"
# cat << EOF > t.txt
# echo "aaa"
# EOF

for ip in `netstat -tplan |grep EST|awk '{print $5}'|awk -F ':' '{print $1}'`
do
    echo $ip
done