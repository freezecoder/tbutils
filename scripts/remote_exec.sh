

echo "*/5  * * * * bash /home/ubuntu/sync_outputs.sh "  > resultupload.jobs
cat resultupload.jobs |crontab -
