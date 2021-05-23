
import boto3
import mimetypes


ACCESS_KEY_ID = 'AKIATZ2MM3E7VZUU7BSM'
ACCESS_SEC = 'bYGr7UlGvl3obEyF4kJ+kG36GOOj/jUB0biKpuxa'

def upload_file(file, file_name):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=ACCESS_SEC)
    try:
        bucket = 'uva-soccerlogger'
        content_type = file.content_type
        extension = mimetypes.guess_extension(content_type)
        s3.put_object(Body=file, Bucket=bucket, Key=file_name + extension, ContentType=content_type, Metadata={
            'Content-Type': content_type
        })
        print("Upload Successful")
        return True, f"https://{bucket}.s3.us-east-1.amazonaws.com/{file_name+extension}"
    except Exception as e:
        print(e)
        return False, ""