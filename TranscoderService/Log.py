import logging
import boto3
import time



class Logger:
    CloudWatchLogsClient = None
    LogGroupName = ""
    InstanceID = "None"

    SysLog = None

    def __init__(self):

        self.SysLog = logging.getLogger()

        try:
            self.CloudWatchLogsClient = boto3.client('logs', region_name="eu-central-1")

        except Exception as e:
            self.SysLog.error("Cannot Get Cloudwatch log client " + str(e))

    def SetUp(self,InstanceID):
        self.InstanceID = str(InstanceID)
        try:
            self.CloudWatchLogsClient.create_log_stream(
                logGroupName=self.LogGroupName,
                logStreamName=self.InstanceID
                )
        except Exception as e:
            self.SysLog.error("Cannot Setup Stream " + str(e))
            self.CloudWatchLogsClient = None


    def CloudWatchLogger(self,Message):

        if not self.CloudWatchLogsClient:
            return

        response = self.CloudWatchLogsClient.put_log_events(
        logGroupName=self.LogGroupName,
        logStreamName=self.InstanceID,
        logEvents=[
            {
                'timestamp': int(time.time()*1000),
                'message': Message
            },
        ]
    )


    def error(self, LogMessage):
        try:
            self.SysLog.error(LogMessage)
            self.CloudWatchLogger(Message=LogMessage)

        except Exception as e:
            self.SysLog.error("Cannot Send Logs to CLoudwatch " + str(e))

    def info(self, LogMessage):
        try:
            self.SysLog.info(LogMessage)
            self.CloudWatchLogger(Message=LogMessage)

        except Exception as e:
            self.SysLog.error("Cannot Send Logs to CLoudwatch " + str(e))


log = Logger()

if __name__ == "__main__":
    log

    log.SetUp(InstanceID="111")
    log.error("TEst")

