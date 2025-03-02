from google.oauth2 import service_account
from google.cloud import documentai

# Path to your credentials file
credentials_path = "/Users/sadie/Documents/hackathon/ocr-reader-452416-1e75aaed777e.json"

try:
    # Try to load the credentials
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    
    # Print basic credential info
    print(f"Successfully loaded credentials!")
    print(f"Project ID: {credentials.project_id}")
    print(f"Service Account Email: {credentials.service_account_email}")
    
    # Try to list Document AI processors (to test permissions)
    client = documentai.DocumentProcessorServiceClient(credentials=credentials)
    parent = client.common_location_path(credentials.project_id, "us")
    
    processors = client.list_processors(parent=parent)
    print("\nAvailable Document AI processors:")
    for processor in processors:
        print(f"- {processor.display_name} (ID: {processor.name.split('/')[-1]})")
    
    print("\nCredentials are valid and have proper Document AI permissions!")
    
except Exception as e:
    print(f"Error: {e}")