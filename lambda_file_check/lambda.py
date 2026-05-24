""""
The  purpose of this function is to fetch the s3 file if the file format is csv and the file is empty and if the file is 
not empty then it will trigger the glue job at the time of file arrival.
"""
#Required Imports
import json
import boto3
import io
import os
import csv

s3=boto3.client("s3") # Use boto3 to call s3 services

def lambda_handler(event,context): #use lambda_handler to define the function and give argumnents if something have to pass
    try:
        #Read the bucket and file name
        bucket=event['Records'][0]['s3']['bucket']['name']
        file_name=event['Records'][0]['s3']['object']['key']
        target_bucket=os.environ["target_bucket"]

        #Read the csv file from s3

        response=s3.get_object(
                    Bucket=bucket,
                    Key=file_name

        )
        content_csv=response['Body'].read().decode('utf-8') # Here data comes as stream and then data has read andthe it converted into readable format


        #process the csv content
        processed_row=[]
        reader=csv.reader(io.StringIO(content_csv)) # This will convert the string(send from conent_csv)  into python row[list of object] data so that python undertstand the data 
        header=next(reader) # This will extract the header from the file as this is not part of the data

        for row in reader:
            if all(row):
                processed_row.append(row)

        # write processed data to in memory back to csv
        output_csv=io.StringIO()
        writer=csv.writer(output_csv)
        writer.writerow(header)
        writer.writerows(processed_row) 

        #write data to final s3 folder

        write_processed_file=file_name.replace('raw/','processed-data/')
        s3.put_object(
            Bucket=target_bucket,
            Key=write_processed_file,
            Body=output_csv.getvalue()
        )

        print(f"processed_file:{write_processed_file}")
    except Exception as e:
        print(f"error while processing the data:{str(e)}")
        raise e           








        

