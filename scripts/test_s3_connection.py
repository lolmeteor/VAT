"""
Тест подключения к S3 Reg.ru
"""
import boto3
import os
import urllib3
from botocore.exceptions import ClientError
from botocore.config import Config
from dotenv import load_dotenv

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Загружаем переменные окружения
load_dotenv()

def test_s3_connection():
    print("🔍 Тестируем подключение к S3 Reg.ru...")
    
    # Настройки S3 - правильный способ для Reg.ru
    s3_client = boto3.client(
        's3',
        endpoint_url=os.getenv('S3_ENDPOINT_URL'),
        aws_access_key_id=os.getenv('S3_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY'),
        region_name=os.getenv('S3_REGION'),
        verify=False  # Отключаем SSL проверку
    )
    
    bucket_name = os.getenv('S3_BUCKET_NAME')
    print(f"📦 Бакет: {bucket_name}")
    print(f"🌐 Endpoint: {os.getenv('S3_ENDPOINT_URL')}")
    
    try:
        # Проверяем доступ к бакету
        print(f"\n1. Проверяем доступ к бакету...")
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
        print("✅ Подключение к S3 успешно!")
        
        if 'Contents' in response:
            print(f"📁 Найдено файлов в бакете: {len(response['Contents'])}")
            for obj in response['Contents'][:3]:
                print(f"   - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("📁 Бакет пустой")
        
        # Тестируем загрузку файла
        test_content = b"Test upload from Python - VAT Project"
        test_key = "test/python-connection-test.txt"
        
        print(f"\n2. Загружаем тестовый файл: {test_key}")
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        print("✅ Файл успешно загружен!")
        
        # Проверяем что файл загрузился
        print(f"\n3. Скачиваем тестовый файл...")
        response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
        downloaded_content = response['Body'].read()
        print(f"✅ Содержимое файла: {downloaded_content.decode()}")
        
        # Генерируем публичную ссылку
        file_url = f"{os.getenv('S3_ENDPOINT_URL')}/{bucket_name}/{test_key}"
        print(f"🔗 Публичная ссылка: {file_url}")
        
        # Удаляем тестовый файл
        print(f"\n4. Удаляем тестовый файл...")
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("✅ Тестовый файл удален!")
        
        print(f"\n🎉 S3 подключение работает корректно!")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ Ошибка S3 ({error_code}): {error_message}")
        
        if error_code == 'NoSuchBucket':
            print("💡 Бакет не существует. Проверьте название бакета.")
        elif error_code == 'AccessDenied':
            print("💡 Нет доступа. Проверьте ключи доступа.")
        elif error_code == 'InvalidAccessKeyId':
            print("💡 Неверный Access Key ID.")
        elif error_code == 'SignatureDoesNotMatch':
            print("💡 Неверный Secret Access Key.")
            
        return False
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return False

if __name__ == "__main__":
    success = test_s3_connection()
    exit(0 if success else 1)
