import boto3
import uuid
from botocore.exceptions import NoCredentialsError, ClientError
from fastapi import HTTPException, status
from src.core.config import settings  

s3 = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

def upload_file_to_s3(file_data, filename: str):
    """
    Upload a file to S3 and return the public URL
    
    Args:
        file_data: File object or file-like object
        filename: Original filename
        
    Returns:
        str: Public URL of the uploaded file
        
    Raises:
        HTTPException: If upload fails
    """
    try:
        # Generate a unique filename to avoid conflicts
        file_extension = filename.split('.')[-1] if '.' in filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
        
        # Upload file to S3
        s3.upload_fileobj(
            file_data, 
            settings.S3_BUCKET_NAME, 
            unique_filename,
            ExtraArgs={'ContentType': _get_content_type(filename)}
        )
        
        # Generate public URL
        url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
        return url
        
    except NoCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AWS credentials not configured"
        )
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to S3: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during file upload: {str(e)}"
        )

def _get_content_type(filename: str) -> str:
    """
    Determine content type based on file extension
    
    Args:
        filename: Name of the file
        
    Returns:
        str: MIME content type
    """
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    
    content_types = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'txt': 'text/plain',
        'csv': 'text/csv',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xls': 'application/vnd.ms-excel',
    }
    
    return content_types.get(extension, 'application/octet-stream')
