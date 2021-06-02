
set -ex

IGNORE="/inputs/|script.background|docker_cid"
export outbucket="{{bucket}}"
export jobid=`ls /home/ubuntu/ |grep postrun.json|cut -f 1 -d.`

if [ -e "/data1/wdl/debug.tar.gz" ];then
	find  /data1/wdl/cromwell-executions/ -type f |egrep -v $IGNORE | xargs -n1 -i  aws s3 cp {} s3://$outbucket/$jobid.workflow/
	 aws s3 cp /data1/wdl/debug.tar.gz s3://$outbucket/$jobid.workflow/
	echo "Done" > /home/ubuntu/copy.done
	yaml=`find  /home/ubuntu/ -name "*yml"`
	aws s3 cp $yaml s3://$outbucket/$jobid.workflow/
	aws s3 cp  /home/ubuntu/copy.done s3://$outbucket/$jobid.workflow/
	sudo shutdown -h now
fi
