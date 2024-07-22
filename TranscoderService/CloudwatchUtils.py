import boto3
from Log import *

CloudwatchClient = boto3.client("cloudwatch", region_name="eu-central-1")
Namespace = "Transcoder"
MetricName = "ScaleIn"
DimensionName = "Server"
DimensionValue = "1"
Value = 1


def SendCloudwatchKillSignal():
    try:
        MetricData =[
            {
                'MetricName': MetricName,
                'Dimensions': 
                [
                    {
                        'Name': DimensionName,
                        'Value': DimensionValue
                    },
                ],
                'Value': Value
            },
        ]
    
        response = CloudwatchClient.put_metric_data(Namespace=Namespace, MetricData=MetricData)

        return 1

    except Exception as e:
        log.error("Error Sending Cloudwatch metrics "+ str(e))
        return 0

if __name__ == "__main__":

    print("Return : " + str(SendCloudwatchKillSignal()))
