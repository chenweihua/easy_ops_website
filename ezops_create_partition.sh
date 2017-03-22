#!/bin/sh
#
#每隔一段时间(crontab调用)，新增util_access_info表的partition
#by yss
#20161007
#
Host='localhost'
DayNow=`date '+%Y-%m-%d' --date='+30 day'`
DayNow1=`date '+%Y%m%d' --date='+30 day'`
Sql="alter table easy_ops.util_access_info add partition (partition p${DayNow1} values less than(TO_DAYS('${DayNow}')))"
#echo $Sql
`mysql -h$Host -P3306 -uroot -pdatacenter@secu -N -e "$Sql"`
